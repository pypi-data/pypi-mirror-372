from typing import Iterable, Tuple, Optional, Dict
from esi.clients import EsiClientProvider
from decimal import Decimal
from datetime import datetime, timezone as dt_tz
import logging

# Try to get (data, response). If lib returns only data, fall back gracefully.
esi = EsiClientProvider()  # nie wymuszamy also_return_response – obsłużymy obie ścieżki
client = esi.client
logger = logging.getLogger(__name__)



def _to_utc_dt(val):
    """Przyjmij ISO8601 string lub datetime i zwróć datetime w UTC, albo None."""
    if isinstance(val, datetime):
        return val.astimezone(dt_tz.utc) if val.tzinfo else val.replace(tzinfo=dt_tz.utc)
    if isinstance(val, str):
        try:
            return datetime.fromisoformat(val.replace("Z", "+00:00")).astimezone(dt_tz.utc)
        except Exception:
            return None
    return None

def fetch_corp_public(corp_id: int) -> dict:
    """Fetch public corporation info."""
    return esi.client.Corporation.get_corporations_corporation_id(
        corporation_id=corp_id
    ).result()


def corp_logo_url(corp_id: int, size: int = 128) -> str:
    """Build CCP image server URL for corp logo."""
    return f"https://images.evetech.net/corporations/{corp_id}/logo?size={size}"


def _result_with_optional_response(op) -> Tuple[list, Optional[object]]:
    """
    Return (data, response) if the client supports it, otherwise (data, None).
    Works across different django-esi/bravado versions.
    """
    # 1) Spróbuj parametru with_response (niektóre wersje go wspierają)
    try:
        data, resp = op.result(with_response=True)  # type: ignore
        return data, resp
    except TypeError:
        # metoda nie przyjmuje with_response
        pass
    except ValueError:
        # zwróciła samą listę, ale próbowaliśmy rozpakować
        pass

    # 2) Spróbuj bez żadnych parametrów – może provider globalnie zwraca (data, response)
    try:
        out = op.result()
        if isinstance(out, tuple) and len(out) == 2:
            data, resp = out
            return data, resp
        # w przeciwnym wypadku to najpewniej sama lista
        return out, None
    except Exception:
        # przekaż dalej – wyższa warstwa złapie i potraktuje brak danych
        raise


def iter_corp_wallet_journal(token, corporation_id: int, division: int = 1) -> Iterable[dict]:
    """
    Iterate over corporation wallet journal entries for a given division.
    Tries to use X-Pages if available; otherwise probes pages until empty/404.
    """
    headers = {"Authorization": f"Bearer {token.valid_access_token()}"}

    # --- First page ---
    try:
        op = esi.client.Wallet.get_corporations_corporation_id_wallets_division_journal(
            corporation_id=corporation_id,
            division=division,
            page=1,
            _request_options={"headers": headers},
        )
        data, resp = _result_with_optional_response(op)
    except Exception:
        # brak uprawnień/pusty/dowolny błąd – traktujemy jak brak danych
        return

    if not data:
        return

    # Yield page 1
    for row in data:
        yield row

    # If we have X-Pages header, use it
    total_pages = None
    try:
        if resp is not None and hasattr(resp, "headers"):
            xpages = resp.headers.get("X-Pages")
            if xpages is not None:
                total_pages = int(xpages)
    except Exception:
        total_pages = None  # fallback poniżej

    # --- Remaining pages ---
    if total_pages and total_pages > 1:
        # Stricte po X-Pages
        for page in range(2, total_pages + 1):
            try:
                op = esi.client.Wallet.get_corporations_corporation_id_wallets_division_journal(
                    corporation_id=corporation_id,
                    division=division,
                    page=page,
                    _request_options={"headers": headers},
                )
                data, _ = _result_with_optional_response(op)
            except Exception:
                break
            if not data:
                break
            for row in data:
                yield row
    else:
        page = 2
        while True:
            try:
                op = esi.client.Wallet.get_corporations_corporation_id_wallets_division_journal(
                    corporation_id=corporation_id,
                    division=division,
                    page=page,
                    _request_options={"headers": headers},
                )
                data, _ = _result_with_optional_response(op)
            except Exception:
                break
            if not data:
                break
            for row in data:
                yield row
            page += 1


def sum_corp_bounty_tax_for_month(token, corporation_id: int, year: int, month: int):
    """
    Sumuje wpływy corp z rattingu (bounty_prizes/bounty_prize), które REALNIE
    wpadły do corp wallet w podanym (year, month). Zwraca (total_decimal, seen_rows_count).
    Dodatkowo robi krótki 'peek' z pierwszych rekordów każdej dywizji.
    """
    ACCEPTED_REF_TYPES = {"bounty_prizes", "bounty_prize"}

    total = Decimal("0")
    seen = 0

    # --- PEEK: pokaż po 3 surowe wiersze z każdej dywizji (bez filtra daty) ---
    if logger.isEnabledFor(logging.DEBUG):
        for division in range(1, 8):
            raw_shown = 0
            for row in iter_corp_wallet_journal(token, corporation_id, division=division):
                if raw_shown >= 3:
                    break
                if not isinstance(row, dict):
                    logger.warning("[PEEK] corp=%s div=%s non-dict row: %r", corporation_id, division, row)
                    continue
                logger.warning(
                    "[PEEK] corp=%s div=%s raw row: date=%s ref_type=%s amount=%s",
                    corporation_id, division, row.get("date"), row.get("ref_type"), row.get("amount")
                )
                raw_shown += 1

    # --- Właściwe liczenie z filtrem miesiąca ---
    ref_counts: Dict[str, int] = {}
    sample_rows = []

    for division in range(1, 8):
        div_total = Decimal("0")
        div_seen = 0
        div_any = 0

        for row in iter_corp_wallet_journal(token, corporation_id, division=division):
            if not isinstance(row, dict):
                # dziwny wpis – pomijamy, ale nie wysypujemy taska
                continue

            dt = _to_utc_dt(row.get("date"))
            if not dt or dt.year != year or dt.month != month:
                continue

            div_any += 1
            rtype = row.get("ref_type", "") or ""
            ref_counts[rtype] = ref_counts.get(rtype, 0) + 1

            if len([s for s in sample_rows if s["division"] == division]) < 5:
                sample_rows.append({
                    "division": division,
                    "date": row.get("date"),
                    "ref_type": rtype,
                    "amount": row.get("amount"),
                    "context_id": row.get("context_id"),
                    "reason": row.get("reason"),
                })

            if rtype not in ACCEPTED_REF_TYPES:
                continue

            amt = row.get("amount")
            if amt is None:
                continue

            try:
                div_total += Decimal(str(amt))
                div_seen += 1
            except Exception:
                continue

        if div_any:
            logger.debug(
                "corp %s div %s: %04d-%02d rows=%s matched=%s sum=%s",
                corporation_id, division, year, month, div_any, div_seen, div_total
            )
        total += div_total
        seen += div_seen

    logger.debug("corp %s %04d-%02d: SEEN=%s TOTAL=%s", corporation_id, year, month, seen, total)

    if seen == 0:
        logger.warning(
            "No bounty rows matched. Ref_type distribution for %s %04d-%02d: %s",
            corporation_id, year, month, ref_counts or "{}"
        )
        if sample_rows:
            for s in sample_rows:
                logger.warning(
                    "Sample row: div=%s date=%s ref_type=%s amount=%s context_id=%s reason=%s",
                    s["division"], s["date"], s["ref_type"], s["amount"], s["context_id"], s["reason"]
                )
        else:
            logger.warning("No journal rows in selected month at all for corp %s.", corporation_id)

    return total, seen


