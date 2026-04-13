from __future__ import annotations

import math
import os
import re
import unicodedata
from datetime import datetime, timedelta, timezone
from hashlib import md5
from typing import Any


LOME_PREFIXES = {
    "agoe": ("Lome", "Golfe", "Maritime"),
    "agoe": ("Lome", "Golfe", "Maritime"),
    "adidogome": ("Lome", "Golfe", "Maritime"),
    "avedji": ("Lome", "Golfe", "Maritime"),
    "tokoin": ("Lome", "Golfe", "Maritime"),
    "hedzranawoe": ("Lome", "Golfe", "Maritime"),
    "baguida": ("Lome", "Golfe", "Maritime"),
    "be": ("Lome", "Golfe", "Maritime"),
    "djidjole": ("Lome", "Golfe", "Maritime"),
    "djidjolee": ("Lome", "Golfe", "Maritime"),
    "kegue": ("Lome", "Golfe", "Maritime"),
    "nukafu": ("Lome", "Golfe", "Maritime"),
    "zanguera": ("Lome", "Golfe", "Maritime"),
    "aflao": ("Lome", "Golfe", "Maritime"),
    "sagbado": ("Lome", "Golfe", "Maritime"),
    "legbassito": ("Lome", "Agoe-Nyive", "Maritime"),
    "adetikope": ("Lome", "Agoe-Nyive", "Maritime"),
    "totsi": ("Lome", "Golfe", "Maritime"),
    "dekon": ("Lome", "Golfe", "Maritime"),
    "avenou": ("Lome", "Golfe", "Maritime"),
    "agoe nyive": ("Lome", "Agoe-Nyive", "Maritime"),
}

CITY_PREFIXES = {
    "kara": ("Kara", "Kozah", "Kara"),
    "atakpame": ("Atakpame", "Ogou", "Plateaux"),
    "atakpamee": ("Atakpame", "Ogou", "Plateaux"),
    "sokode": ("Sokode", "Tchaoudjo", "Centrale"),
    "dapaong": ("Dapaong", "Tone", "Savanes"),
    "tsevie": ("Tsevie", "Zio", "Maritime"),
    "vogan": ("Vogan", "Vo", "Maritime"),
    "aneho": ("Aneho", "Lacs", "Maritime"),
    "tabligbo": ("Tabligbo", "Yoto", "Maritime"),
    "kpalime": ("Kpalime", "Kloto", "Plateaux"),
    "badou": ("Badou", "Wawa", "Plateaux"),
    "mango": ("Mango", "Oti", "Savanes"),
    "blitta": ("Blitta", "Blitta", "Centrale"),
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip().lower()
    if not text or text == "nan":
        return ""
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    text = re.sub(r"[^\w\s/-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def slugify(value: Any) -> str:
    normalized = normalize_text(value)
    return normalized.replace("/", "-").replace(" ", "-")


def title_case_zone(value: Any) -> str | None:
    normalized = normalize_text(value)
    if not normalized:
        return None
    return " ".join(part.capitalize() for part in normalized.split())


def parse_datetime(value: Any) -> datetime | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() == "nan":
        return None

    iso_candidates = [
        text,
        text.replace("Z", "+00:00"),
        text.replace("/", "-"),
    ]
    for candidate in iso_candidates:
        try:
            parsed = datetime.fromisoformat(candidate)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed.astimezone(timezone.utc)
        except ValueError:
            continue

    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d", "%d-%m-%Y %H:%M:%S", "%d/%m/%Y %H:%M:%S"):
        try:
            parsed = datetime.strptime(text, fmt).replace(tzinfo=timezone.utc)
            return parsed
        except ValueError:
            continue
    return None


def _parse_period_hints(
    year_month: Any = None,
    periode: Any = None,
    annee: Any = None,
    trimestre: Any = None,
) -> datetime | None:
    year_month_text = str(year_month or "").strip()
    if re.fullmatch(r"\d{4}-\d{2}", year_month_text):
        try:
            return datetime.strptime(f"{year_month_text}-01", "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            pass

    periode_text = str(periode or "").strip().upper()
    match = re.fullmatch(r"(\d{4})-Q([1-4])", periode_text)
    if match:
        year = int(match.group(1))
        quarter = int(match.group(2))
        month = ((quarter - 1) * 3) + 1
        return datetime(year, month, 1, tzinfo=timezone.utc)

    try:
        year = int(annee) if annee is not None else None
        quarter = int(trimestre) if trimestre is not None else None
    except (TypeError, ValueError):
        year = None
        quarter = None

    if year and quarter and 1 <= quarter <= 4:
        month = ((quarter - 1) * 3) + 1
        return datetime(year, month, 1, tzinfo=timezone.utc)

    return None


def _synthetic_observation_datetime(seed_value: Any = None) -> datetime:
    start_period = os.getenv("ID_IMMO_START_PERIOD", "2025-10")
    end_period = os.getenv("ID_IMMO_END_PERIOD", "2026-02")

    start_dt = _parse_period_hints(year_month=start_period) or datetime(2025, 10, 1, tzinfo=timezone.utc)
    end_dt = _parse_period_hints(year_month=end_period) or datetime(2026, 2, 1, tzinfo=timezone.utc)
    if end_dt < start_dt:
        start_dt, end_dt = end_dt, start_dt

    month_starts = []
    cursor = start_dt.replace(day=1)
    limit = end_dt.replace(day=1)
    while cursor <= limit:
        month_starts.append(cursor)
        next_month = cursor.replace(day=28) + timedelta(days=4)
        cursor = next_month.replace(day=1)

    if not month_starts:
        month_starts = [datetime.now(timezone.utc).replace(day=1)]

    seed_text = str(seed_value or "id-immobilier")
    digest = md5(seed_text.encode("utf-8")).hexdigest()
    month_index = int(digest[:8], 16) % len(month_starts)
    day_offset = int(digest[8:16], 16) % 28
    base = month_starts[month_index]
    return base + timedelta(days=day_offset)


def derive_time_fields(
    date_annonce: Any = None,
    created_at: Any = None,
    fallback_iso: str | None = None,
    year_month: Any = None,
    periode: Any = None,
    annee: Any = None,
    trimestre: Any = None,
    seed_value: Any = None,
) -> dict[str, Any]:
    posted_dt = parse_datetime(date_annonce)
    collected_dt = parse_datetime(created_at)
    hinted_dt = _parse_period_hints(year_month=year_month, periode=periode, annee=annee, trimestre=trimestre)
    observation_dt = (
        posted_dt
        or hinted_dt
        or collected_dt
        or parse_datetime(fallback_iso)
        or _synthetic_observation_datetime(seed_value=seed_value)
    )

    observation_year = observation_dt.year
    observation_month = observation_dt.month
    observation_quarter = ((observation_month - 1) // 3) + 1

    return {
        "source_posted_at": posted_dt.isoformat().replace("+00:00", "Z") if posted_dt else None,
        "source_scraped_at": collected_dt.isoformat().replace("+00:00", "Z") if collected_dt else fallback_iso,
        "observation_date": observation_dt.date().isoformat(),
        "observation_year": observation_year,
        "observation_month": observation_month,
        "observation_quarter": observation_quarter,
        "year_month": f"{observation_year}-{observation_month:02d}",
        "periode": f"{observation_year}-Q{observation_quarter}",
        "annee": observation_year,
        "trimestre": observation_quarter,
    }


def infer_geo_hierarchy(zone_name: Any) -> dict[str, Any]:
    display_name = title_case_zone(zone_name)
    normalized = normalize_text(zone_name)
    slug = slugify(zone_name)

    city = None
    prefecture = None
    region = None

    if normalized in LOME_PREFIXES:
        city, prefecture, region = LOME_PREFIXES[normalized]
    elif normalized in CITY_PREFIXES:
        city, prefecture, region = CITY_PREFIXES[normalized]
    else:
        for key, values in {**LOME_PREFIXES, **CITY_PREFIXES}.items():
            if normalized.startswith(key):
                city, prefecture, region = values
                break

    return {
        "zone_name": display_name,
        "zone_slug": slug or None,
        "zone_id": f"zone:{slug}" if slug else None,
        "geo": {
            "country": "Togo",
            "region": region or "A classifier",
            "prefecture": prefecture or "A classifier",
            "city": city or display_name,
            "district": display_name,
            "label": " > ".join(part for part in ["Togo", region or None, prefecture or None, city or None, display_name or None] if part),
        },
    }


def build_zone_document(zone_name: Any, source_count: int = 0) -> dict[str, Any] | None:
    zone_name_clean = title_case_zone(zone_name)
    if not zone_name_clean:
        return None
    geo = infer_geo_hierarchy(zone_name_clean)
    return {
        "_id": geo["zone_id"],
        "slug": geo["zone_slug"],
        "name": zone_name_clean,
        "country": "Togo",
        "region": geo["geo"]["region"],
        "prefecture": geo["geo"]["prefecture"],
        "city": geo["geo"]["city"],
        "district": geo["geo"]["district"],
        "label": geo["geo"]["label"],
        "synonyms": sorted({zone_name_clean, normalize_text(zone_name)}),
        "source_count": int(source_count),
        "updated_at": now_iso(),
    }


def safe_float(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number):
        return None
    return number
