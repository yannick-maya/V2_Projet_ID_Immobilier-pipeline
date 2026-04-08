import math
import unicodedata
from collections import Counter, defaultdict
from statistics import median

from fastapi import APIRouter

from api.database import db
from api.utils import serialize_doc

router = APIRouter()


def _normalize_text(value: str | None) -> str:
    if not value:
        return ""
    normalized = unicodedata.normalize("NFD", str(value).strip().lower())
    return "".join(char for char in normalized if unicodedata.category(char) != "Mn")


def _clean_text(values: list[str | None]) -> list[str]:
    cleaned = []
    for value in values:
        text = str(value or "").strip()
        if not text or text.lower() == "nan":
            continue
        cleaned.append(text)
    return sorted(set(cleaned), key=lambda item: _normalize_text(item))


def _safe_float(value) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number) or number <= 0:
        return None
    return number


def _percentile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    if len(values) == 1:
        return values[0]
    index = (len(values) - 1) * q
    lower = math.floor(index)
    upper = math.ceil(index)
    if lower == upper:
        return values[lower]
    fraction = index - lower
    return values[lower] + (values[upper] - values[lower]) * fraction


def _trim_values(values: list[float], lower_q: float = 0.05, upper_q: float = 0.95) -> list[float]:
    cleaned = sorted(value for value in values if value is not None and math.isfinite(value) and value > 0)
    if len(cleaned) < 8:
        return cleaned
    lower = _percentile(cleaned, lower_q)
    upper = _percentile(cleaned, upper_q)
    trimmed = [value for value in cleaned if lower <= value <= upper]
    return trimmed or cleaned


def _compute_metrics(values: list[float]) -> dict:
    trimmed = _trim_values(values)
    if not trimmed:
        return {"mean": 0.0, "median": 0.0, "count": 0}
    return {
        "mean": round(sum(trimmed) / len(trimmed), 2),
        "median": round(float(median(trimmed)), 2),
        "count": len(values),
    }


def _group_market_data(rows: list[dict], field: str, min_count: int = 3) -> list[dict]:
    buckets: dict[str, dict] = {}
    for row in rows:
        raw_label = str(row.get(field) or "").strip()
        price_m2 = _safe_float(row.get("prix_m2"))
        if not raw_label or not price_m2:
            continue
        key = _normalize_text(raw_label)
        bucket = buckets.setdefault(key, {"labels": Counter(), "values": []})
        bucket["labels"][raw_label] += 1
        bucket["values"].append(price_m2)

    grouped = []
    for bucket in buckets.values():
        metrics = _compute_metrics(bucket["values"])
        if metrics["count"] < min_count:
            continue
        grouped.append(
            {
                "label": bucket["labels"].most_common(1)[0][0],
                "mean": metrics["mean"],
                "median": metrics["median"],
                "count": metrics["count"],
            }
        )
    return grouped


@router.get("/options")
async def statistics_options():
    annonces = db["annonces"]
    indices = db["indices"]

    zones = _clean_text(await annonces.distinct("zone"))
    types_bien = _clean_text(await annonces.distinct("type_bien"))
    types_offre = _clean_text(await annonces.distinct("type_offre"))
    periodes = _clean_text(
        list(await annonces.distinct("periode")) +
        list(await indices.distinct("periode")) +
        list(await db["statistiques"].distinct("periode"))
    )

    return {
        "zones": zones,
        "types_bien": types_bien,
        "types_offre": types_offre,
        "periodes": periodes,
    }


@router.get("/overview")
async def statistiques_overview(
    zone: str | None = None,
    type_bien: str | None = None,
    type_offre: str | None = None,
    periode: str | None = None,
):
    query = {}
    if zone:
        query["zone"] = zone
    if type_bien:
        query["type_bien"] = type_bien
    if type_offre:
        query["type_offre"] = type_offre
    if periode:
        query["periode"] = periode

    projection = {
        "zone": 1,
        "type_bien": 1,
        "type_offre": 1,
        "source": 1,
        "prix_m2": 1,
        "periode": 1,
    }
    annonces = [serialize_doc(doc) async for doc in db["annonces"].find(query, projection)]
    indices = [serialize_doc(doc) async for doc in db["indices"].find(query, {"zone": 1, "tendance": 1})]

    prices = [_safe_float(row.get("prix_m2")) for row in annonces]
    prices = [price for price in prices if price is not None]
    metrics = _compute_metrics(prices)

    grouped_zones = sorted(_group_market_data(annonces, "zone", min_count=5), key=lambda item: item["mean"], reverse=True)[:10]
    grouped_types = sorted(_group_market_data(annonces, "type_bien", min_count=5), key=lambda item: item["mean"], reverse=True)[:8]

    source_counts = Counter()
    for row in annonces:
        source = str(row.get("source") or "").strip()
        if not source or source.lower() == "nan":
            continue
        source_counts[source] += 1

    trend_counts = {"HAUSSE": set(), "STABLE": set(), "BAISSE": set()}
    for row in indices:
        trend = str(row.get("tendance") or "").strip().upper()
        zone_name = str(row.get("zone") or "").strip()
        if trend in trend_counts and zone_name:
            trend_counts[trend].add(zone_name)

    valid_periods = _clean_text([row.get("periode") for row in annonces])
    invalid_periods = sum(1 for row in annonces if str(row.get("periode") or "").strip().lower() == "nan")

    return {
        "kpis": {
            "annonces": len(annonces),
            "zones": len({str(row.get("zone") or "").strip() for row in annonces if str(row.get("zone") or "").strip()}),
            "prix_moyen_m2": metrics["mean"],
            "prix_median_m2": metrics["median"],
            "sources": len(source_counts),
        },
        "top_zones": grouped_zones,
        "sources": [
            {"label": label, "count": count}
            for label, count in source_counts.most_common()
        ],
        "types_bien": grouped_types,
        "tendances": {
            key: {"count": len(value), "zones": sorted(value)}
            for key, value in trend_counts.items()
        },
        "temporalite": {
            "periodes": valid_periods,
            "periodes_invalides": invalid_periods,
            "statut": "partielle" if invalid_periods else "ok",
        },
    }


@router.get("/")
async def list_statistiques(
    zone: str | None = None,
    type_bien: str | None = None,
    type_offre: str | None = None,
    periode: str | None = None,
):
    query = {}
    if zone:
        query["zone"] = zone
    if type_bien:
        query["type_bien"] = type_bien
    if type_offre:
        query["type_offre"] = type_offre
    if periode:
        query["periode"] = periode

    data = [serialize_doc(d) async for d in db["statistiques"].find(query)]
    return {"total": len(data), "data": data}


@router.get("/{zone}")
async def stats_zone(zone: str):
    details = [serialize_doc(d) async for d in db["statistiques"].find({"zone": zone})]
    historique = sorted(details, key=lambda x: (x.get("annee", 0), x.get("trimestre", 0)))
    return {"zone": zone, "total": len(details), "historique": historique}
