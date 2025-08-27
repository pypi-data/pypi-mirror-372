import logging
from celery import shared_task
from decimal import Decimal
from django.utils import timezone
from django.db import transaction

from esi.models import Token
from .models import Corporation, CorpMonthStat, CorpTokenLink
from .esi import sum_corp_bounty_tax_for_month

logger = logging.getLogger(__name__)


def _get_token_for_corp(corp: Corporation):
    """
    Pick the freshest django-esi Token for the character linked to this corp.
    """
    link = getattr(corp, "token_link", None)
    if not link:
        return None
    return Token.objects.filter(character_id=link.character_id).order_by("-created").first()

@shared_task(bind=True, ignore_result=True)
def pull_month_for_corp(self, corporation_id: int, year: int, month: int):
    now = timezone.now()
    is_current = (year == now.year and month == now.month)

    try:
        corp = Corporation.objects.get(corporation_id=corporation_id)
    except Corporation.DoesNotExist:
        return

    token = _get_token_for_corp(corp)
    if not token:

        return

    total, seen = sum_corp_bounty_tax_for_month(token, corp.corporation_id, year, month)

    with transaction.atomic():
        stat, _ = CorpMonthStat.objects.select_for_update().get_or_create(
            corp=corp, year=year, month=month,
            defaults={"corp_bounty_tax_amount": total}
        )

        is_closed = getattr(stat, "closed", False)

        if is_closed and not is_current:
            return

        if seen > 0 or is_current:
            changed = (stat.corp_bounty_tax_amount != total)
            stat.corp_bounty_tax_amount = total

            if not is_current:
                if hasattr(stat, "closed"):
                    stat.closed = True
                    stat.save(update_fields=["corp_bounty_tax_amount", "closed"])
                else:
                    stat.save(update_fields=["corp_bounty_tax_amount"])
            else:
                if hasattr(stat, "closed") and stat.closed:
                    stat.closed = False
                    stat.save(update_fields=["corp_bounty_tax_amount", "closed"])
                elif changed:
                    stat.save(update_fields=["corp_bounty_tax_amount"])



@shared_task(bind=True, ignore_result=True)
def daily_refresh_current_month(self):
    """
    Recompute the current month for all linked corps once per day.
    If a corp has no token, it is skipped (and logged).
    """
    today = timezone.now().date()
    y, m = today.year, today.month

    # only corps which have a token link
    for link in CorpTokenLink.objects.select_related("corp").all():
        corp = link.corp
        tok = _get_token_for_corp(corp)
        if not tok:
            logger.warning("daily_refresh_current_month: no token for corp %s", corp.corporation_id)
            continue
        pull_month_for_corp.delay(corp.corporation_id, y, m)
        logger.debug(
            "pull_month_for_corp: corp=%s y-m=%s-%s seen=%s total=%s",
            corp.corporation_id, year, month, seen, total
        )

