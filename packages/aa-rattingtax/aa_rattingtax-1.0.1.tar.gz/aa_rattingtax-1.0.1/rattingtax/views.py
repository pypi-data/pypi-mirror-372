from decimal import Decimal, ROUND_DOWN
from datetime import date
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _t
from django.utils import timezone

from allianceauth.authentication.models import CharacterOwnership
from allianceauth.services.hooks import get_extension_logger
from esi.decorators import token_required
from esi.clients import EsiClientProvider

from .models import Corporation, CorpTokenLink, TaxConfig, CorpMonthStat, AllianceSettings
from .tasks import pull_month_for_corp
from .esi import fetch_corp_public, corp_logo_url

logger = get_extension_logger(__name__)
esi = EsiClientProvider()

@login_required
@permission_required("rattingtax.basic_access", raise_exception=True)
def dashboard(request):
    today = date.today()

    # --- filters ---
    try:
        selected_month = int(request.GET.get("month") or today.month)
    except (TypeError, ValueError):
        selected_month = today.month
    try:
        selected_year = int(request.GET.get("year") or today.year)
    except (TypeError, ValueError):
        selected_year = today.year

    selected_corp_id = request.GET.get("corp")
    try:
        selected_corp_id = int(selected_corp_id) if selected_corp_id else None
    except (TypeError, ValueError):
        selected_corp_id = None

    # --- scope by permission ---
    if request.user.has_perm("rattingtax.view_all"):
        corps_qs = Corporation.objects.all().order_by("name")
    else:
        user_char_ids = list(
            CharacterOwnership.objects
            .filter(user=request.user)
            .values_list("character__character_id", flat=True)
        )
        visible_corp_ids = list(
            CorpTokenLink.objects
            .filter(character_id__in=user_char_ids)
            .values_list("corp__corporation_id", flat=True)
        )
        corps_qs = Corporation.objects.filter(
            corporation_id__in=visible_corp_ids
        ).order_by("name")

    corps = list(corps_qs)

    # --- global settings ---
    settings_obj = AllianceSettings.get_solo()
    try:
        alliance_rate = Decimal(str(settings_obj.alliance_rate_percent or 0))
    except Exception:
        alliance_rate = Decimal("0")

    try:
        flat_reduction = Decimal(str(settings_obj.flat_tax_reduction or 0))
    except Exception:
        flat_reduction = Decimal("0")

    rows = []
    for corp in corps:
        if selected_corp_id and corp.corporation_id != selected_corp_id:
            continue

        stat = (CorpMonthStat.objects
                .filter(corp=corp, year=selected_year, month=selected_month)
                .first())

        corp_tax_amount = Decimal(stat.corp_bounty_tax_amount) if stat else Decimal("0.00")

        cfg = getattr(corp, "tax_cfg", None)
        corp_rate = cfg.corp_tax_rate_percent if cfg else Decimal("0.00")

        # alliance tax before reduction
        alliance_tax_raw = (corp_tax_amount * alliance_rate / Decimal("100"))
        # apply flat reduction (not below zero), then normalizuj do 0.01
        alliance_tax_after = alliance_tax_raw - flat_reduction
        if alliance_tax_after < Decimal("0.00"):
            alliance_tax_after = Decimal("0.00")
        alliance_tax_after = alliance_tax_after.quantize(Decimal("0.01"), rounding=ROUND_DOWN)

        rows.append({
            "corp": corp,
            "corp_tax_amount": corp_tax_amount.quantize(Decimal("0.01")),
            "corp_rate": (corp_rate or Decimal("0.00")).quantize(Decimal("0.01")),
            "alliance_rate": (alliance_rate or Decimal("0.00")).quantize(Decimal("0.01")),
            "alliance_tax": alliance_tax_after,
        })

    context = {
        "corps": corps,
        "rows": rows,
        "selected_corp": selected_corp_id or "",
        "selected_month": selected_month,
        "selected_year": selected_year,
        "months": list(range(1, 13)),
        "years": [today.year, today.year - 1, today.year - 2],
        # to pokaże się w nagłówku
        "tax_reduction": flat_reduction.quantize(Decimal("0.01")),
    }
    return render(request, "rattingtax/dashboard.html", context)



@login_required
@permission_required("rattingtax.basic_access", raise_exception=True)
@token_required(scopes=["esi-wallet.read_corporation_wallets.v1"])
def connect_corp_token(request, token):
    """
    Link a corporation to a character token and kick a month pull.
    Uses the character's current corporation.
    """
    try:
        # 1) Character public
        char_id = token.character_id
        char_pub = esi.client.Character.get_characters_character_id(
            character_id=char_id
        ).result()
        char_name = char_pub.get("name", str(char_id))

        # 2) Corporation id from character public
        corp_id = int(char_pub["corporation_id"])

        # 3) Pull corporation public info (name/ticker/tax_rate)
        corp_pub = fetch_corp_public(corp_id)
        corp, created = Corporation.objects.get_or_create(
            corporation_id=corp_id,
            defaults={
                "name": corp_pub.get("name", ""),
                "ticker": corp_pub.get("ticker", ""),
                "logo_url": corp_logo_url(corp_id, 64),
            },
        )

        # Keep corp descriptive fields up to date
        changed = False
        new_name = corp_pub.get("name")
        new_ticker = corp_pub.get("ticker")
        new_logo = corp_logo_url(corp_id, 64)

        if new_name and corp.name != new_name:
            corp.name = new_name
            changed = True
        if new_ticker and corp.ticker != new_ticker:
            corp.ticker = new_ticker
            changed = True
        if new_logo and corp.logo_url != new_logo:
            corp.logo_url = new_logo
            changed = True
        if changed:
            corp.save()

        # Sync corp in-game tax (display only)
        tax_rate_val = corp_pub.get("tax_rate")
        if tax_rate_val is not None:
            tax_pct = (Decimal(str(tax_rate_val)) * Decimal("100")).quantize(Decimal("0.01"))
            TaxConfig.objects.update_or_create(
                corp=corp,
                defaults={"corp_tax_rate_percent": tax_pct},
            )
        else:
            TaxConfig.objects.get_or_create(corp=corp)

        # Store link (who authorized)
        CorpTokenLink.objects.update_or_create(
            corp=corp,
            defaults={"character_id": char_id, "character_name": char_name},
        )

        # Kick current month pull
        now = timezone.now()
        pull_month_for_corp.delay(corp.corporation_id, now.year, now.month)

        messages.success(
            request,
            _t("Connected corp token for %(corp)s via %(char)s.") % {
                "corp": corp.name,
                "char": char_name,
            },
        )
    except Exception as e:
        logger.exception("connect_corp_token failed")
        messages.error(
            request,
            _t("Error while connecting corp token: %(err)s") % {"err": str(e)},
        )

    return redirect("rattingtax:dashboard")
