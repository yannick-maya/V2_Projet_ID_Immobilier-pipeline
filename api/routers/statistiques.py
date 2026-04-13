import math
import unicodedata
from collections import Counter
from statistics import median

from fastapi import APIRouter, Query

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
        return {"mean": 0.0, "median": 0.0, "count": 0, "min": 0.0, "max": 0.0}
    return {
        "mean": round(sum(trimmed) / len(trimmed), 2),
        "median": round(float(median(trimmed)), 2),
        "count": len(values),
        "min": round(min(trimmed), 2),
        "max": round(max(trimmed), 2),
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
                "min": metrics["min"],
                "max": metrics["max"],
            }
        )
    return grouped


def _build_match_query(
    zone: str | None = None,
    type_bien: str | None = None,
    type_offre: str | None = None,
    periode: str | None = None,
):
    clauses = []
    if zone:
        clauses.append({"zone": {"$regex": f"^{zone.strip()}$", "$options": "i"}})
    if type_bien:
        clauses.append({"type_bien": {"$regex": f"^{type_bien.strip()}$", "$options": "i"}})
    if type_offre:
        clauses.append({"type_offre": {"$regex": f"^{type_offre.strip()}$", "$options": "i"}})
    if periode:
        clauses.append(
            {
                "$or": [
                    {"periode": {"$regex": f"^{periode.strip()}$", "$options": "i"}},
                    {"year_month": {"$regex": f"^{periode.strip()}$", "$options": "i"}},
                ]
            }
        )
    if not clauses:
        return {}
    if len(clauses) == 1:
        return clauses[0]
    return {"$and": clauses}


async def _load_annonces(query: dict) -> list[dict]:
    projection = {
        "zone": 1,
        "type_bien": 1,
        "type_offre": 1,
        "source": 1,
        "prix": 1,
        "prix_otr": 1,
        "prix_m2": 1,
        "periode": 1,
        "year_month": 1,
        "observation_year": 1,
        "observation_month": 1,
        "surface_m2": 1,
        "statut_otr": 1,
        "difference_otr": 1,
    }
    return [serialize_doc(doc) async for doc in db["annonces"].find(query, projection)]


async def _load_indices(query: dict) -> list[dict]:
    return [
        serialize_doc(doc)
        async for doc in db["indices"].find(
            query,
            {
                "zone": 1,
                "type_bien": 1,
                "tendance": 1,
                "year_month": 1,
                "periode": 1,
                "indice_valeur": 1,
                "nombre_annonces": 1,
            },
        )
    ]


def _build_timeline(rows: list[dict]) -> list[dict]:
    buckets: dict[str, list[float]] = {}
    for row in rows:
        period = str(row.get("year_month") or row.get("periode") or "").strip()
        price_m2 = _safe_float(row.get("prix_m2"))
        if not period or price_m2 is None:
            continue
        buckets.setdefault(period, []).append(price_m2)

    timeline = []
    for period, values in sorted(buckets.items()):
        metrics = _compute_metrics(values)
        timeline.append(
            {
                "periode": period,
                "prix_moyen_m2": metrics["mean"],
                "prix_median_m2": metrics["median"],
                "volume": metrics["count"],
            }
        )
    return timeline


def _build_source_comparison(rows: list[dict]) -> list[dict]:
    buckets: dict[str, dict] = {}
    for row in rows:
        source = str(row.get("source") or "").strip()
        price_m2 = _safe_float(row.get("prix_m2"))
        if not source or price_m2 is None:
            continue
        bucket = buckets.setdefault(source, {"prices": [], "prices_total": []})
        bucket["prices"].append(price_m2)
        total_price = _safe_float(row.get("prix"))
        if total_price is not None:
            bucket["prices_total"].append(total_price)

    comparison = []
    for source, values in buckets.items():
        metrics = _compute_metrics(values["prices"])
        prix_total_metrics = _compute_metrics(values["prices_total"])
        comparison.append(
            {
                "label": source,
                "count": metrics["count"],
                "prix_moyen_m2": metrics["mean"],
                "prix_median_m2": metrics["median"],
                "prix_moyen_total": prix_total_metrics["mean"],
            }
        )
    comparison.sort(key=lambda row: row["count"], reverse=True)
    return comparison


def _build_zone_comparison(rows: list[dict], limit: int = 8) -> list[dict]:
    grouped = sorted(_group_market_data(rows, "zone", min_count=2), key=lambda item: item["count"], reverse=True)
    return grouped[:limit]


def _build_terrain_otr_comparison(rows: list[dict], limit: int = 8) -> tuple[list[dict], list[dict]]:
    terrain_rows = []
    for row in rows:
        if str(row.get("type_bien") or "").strip().upper() != "TERRAIN":
            continue
        prix = _safe_float(row.get("prix"))
        prix_otr = _safe_float(row.get("prix_otr"))
        if prix is None or prix_otr is None or prix_otr <= 0:
            continue
        difference_pct = round(((prix - prix_otr) / prix_otr) * 100, 2)
        terrain_rows.append(
            {
                "zone": str(row.get("zone") or "").strip() or "Terrain",
                "periode": str(row.get("year_month") or row.get("periode") or "").strip(),
                "prix": prix,
                "prix_otr": prix_otr,
                "prix_m2": _safe_float(row.get("prix_m2")),
                "difference_pct": difference_pct,
                "statut_otr": str(row.get("statut_otr") or "").strip(),
            }
        )

    sorted_points = sorted(terrain_rows, key=lambda item: abs(item["difference_pct"] or 0), reverse=True)[:limit]

    bins = [
        {"label": "Très sous-évalué", "predicate": lambda value: value < -50},
        {"label": "Sous-évalué", "predicate": lambda value: -50 <= value < -20},
        {"label": "Conforme", "predicate": lambda value: -20 <= value <= 20},
        {"label": "Sur-évalué", "predicate": lambda value: value > 20},
    ]

    histogram = [
        {"label": bin_item["label"], "count": sum(1 for item in terrain_rows if bin_item["predicate"](item["difference_pct"]))}
        for bin_item in bins
    ]

    return sorted_points, histogram


def _build_project_overview() -> dict:
    return {
        "title": "ID Immobilier",
        "subtitle": "Indice intelligent du marche immobilier au Togo",
        "description": (
            "La plateforme consolide des annonces immobilieres multi-sources, calcule le prix au m2, "
            "compare les prix de marche aux valeurs venales et produit un indice par zone et type de bien."
        ),
        "functionalites": [
            "analyses par zone geographique",
            "suivi temporel mensuel et trimestriel",
            "comparaison entre sources de donnees",
            "simulation de prix d'un bien",
            "tableaux de bord interactifs utilisateurs et administrateurs",
        ],
        "mvp": [
            "selection d'une zone",
            "visualisation du prix moyen au m2",
            "consultation de l'indice immobilier",
            "comparaison de plusieurs zones et sources",
        ],
    }


@router.get("/options")
async def statistics_options():
    annonces = db["annonces"]
    indices = db["indices"]
    zones_collection = db["zones"]

    zones = _clean_text(await zones_collection.distinct("name")) or _clean_text(await annonces.distinct("zone"))
    types_bien = _clean_text(await annonces.distinct("type_bien"))
    types_offre = _clean_text(await annonces.distinct("type_offre"))
    periodes = _clean_text(
        list(await annonces.distinct("year_month"))
        + list(await annonces.distinct("periode"))
        + list(await indices.distinct("year_month"))
        + list(await indices.distinct("periode"))
        + list(await db["statistiques"].distinct("periode"))
    )

    return {
        "zones": zones,
        "types_bien": types_bien,
        "types_offre": types_offre,
        "periodes": periodes,
    }


@router.get("/project")
async def project_information():
    return _build_project_overview()


@router.get("/overview")
async def statistiques_overview(
    zone: str | None = None,
    type_bien: str | None = None,
    type_offre: str | None = None,
    periode: str | None = None,
):
    query = _build_match_query(zone=zone, type_bien=type_bien, type_offre=type_offre, periode=periode)
    annonces = await _load_annonces(query)
    indices = await _load_indices(query)

    prices = [_safe_float(row.get("prix_m2")) for row in annonces]
    prices = [price for price in prices if price is not None]
    metrics = _compute_metrics(prices)

    grouped_zones = sorted(_group_market_data(annonces, "zone", min_count=2), key=lambda item: item["mean"], reverse=True)[:10]
    grouped_types = sorted(_group_market_data(annonces, "type_bien", min_count=2), key=lambda item: item["mean"], reverse=True)[:8]
    source_comparison = _build_source_comparison(annonces)
    timeline = _build_timeline(annonces)
    zone_comparison = _build_zone_comparison(annonces)

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

    valid_periods = _clean_text([row.get("year_month") or row.get("periode") for row in annonces])
    invalid_periods = sum(1 for row in annonces if not str(row.get("year_month") or row.get("periode") or "").strip())
    otr_rows = [row for row in annonces if row.get("statut_otr")]
    ot_metrics = Counter(str(row.get("statut_otr")) for row in otr_rows if row.get("statut_otr"))
    terrain_otr_points, terrain_otr_histogram = _build_terrain_otr_comparison(annonces)

    return {
        "project": _build_project_overview(),
        "kpis": {
            "annonces": len(annonces),
            "zones": len({str(row.get("zone") or "").strip() for row in annonces if str(row.get("zone") or "").strip()}),
            "prix_moyen_m2": metrics["mean"],
            "prix_median_m2": metrics["median"],
            "prix_min_m2": metrics["min"],
            "prix_max_m2": metrics["max"],
            "sources": len(source_counts),
        },
        "top_zones": grouped_zones,
        "types_bien": grouped_types,
        "sources": [{"label": label, "count": count} for label, count in source_counts.most_common()],
        "comparaison_sources": source_comparison,
        "comparaison_zones": zone_comparison,
        "timeline": timeline,
        "terrain_otr_points": terrain_otr_points,
        "terrain_otr_histogram": terrain_otr_histogram,
        "par_zone": {item["label"]: {"prix_moyen": item["mean"], "prix_median": item["median"], "count": item["count"]} for item in grouped_zones},
        "par_type": {item["label"]: {"prix_moyen": item["mean"], "prix_median": item["median"], "count": item["count"]} for item in grouped_types},
        "tendances": {key: {"count": len(value), "zones": sorted(value)} for key, value in trend_counts.items()},
        "temporalite": {
            "periodes": valid_periods,
            "periodes_invalides": invalid_periods,
            "timeline_points": len(timeline),
            "statut": "partielle" if invalid_periods else "ok",
        },
        "ecarts_otr": {
            "annonces_comparees": len(otr_rows),
            "repartition": [{"label": key, "count": value} for key, value in ot_metrics.items()],
        },
    }


@router.get("/timeline")
async def statistiques_timeline(
    zone: str | None = None,
    type_bien: str | None = None,
    type_offre: str | None = None,
):
    query = _build_match_query(zone=zone, type_bien=type_bien, type_offre=type_offre)
    annonces = await _load_annonces(query)
    timeline = _build_timeline(annonces)
    return {"total": len(timeline), "data": timeline}


@router.get("/comparaison-sources")
async def comparaison_sources(
    zone: str | None = None,
    type_bien: str | None = None,
    type_offre: str | None = None,
):
    query = _build_match_query(zone=zone, type_bien=type_bien, type_offre=type_offre)
    annonces = await _load_annonces(query)
    data = _build_source_comparison(annonces)
    return {"total": len(data), "data": data}


@router.get("/comparaison-zones")
async def comparaison_zones(
    zones: list[str] = Query(default=[]),
    type_bien: str | None = None,
    type_offre: str | None = None,
):
    if zones:
        zone_clauses = [{"zone": {"$regex": f"^{value.strip()}$", "$options": "i"}} for value in zones if value.strip()]
        query = {"$and": [{"$or": zone_clauses}]} if zone_clauses else {}
        extra = _build_match_query(type_bien=type_bien, type_offre=type_offre)
        if extra:
            if "$and" in query:
                query["$and"].append(extra)
            else:
                query = {"$and": [extra]}
    else:
        query = _build_match_query(type_bien=type_bien, type_offre=type_offre)

    annonces = await _load_annonces(query)
    data = _build_zone_comparison(annonces, limit=max(8, len(zones) or 8))
    return {"total": len(data), "data": data}


@router.get("/")
async def list_statistiques(
    zone: str | None = None,
    type_bien: str | None = None,
    type_offre: str | None = None,
    periode: str | None = None,
):
    query = _build_match_query(zone=zone, type_bien=type_bien, type_offre=type_offre, periode=periode)
    data = [serialize_doc(d) async for d in db["statistiques"].find(query).sort([("year_month", 1), ("zone", 1)])]
    return {"total": len(data), "data": data}


@router.get("/{zone}")
async def stats_zone(zone: str):
    query = _build_match_query(zone=zone)
    details = [serialize_doc(d) async for d in db["statistiques"].find(query)]
    historique = sorted(details, key=lambda x: (x.get("annee", 0), x.get("trimestre", 0), x.get("year_month", "")))
    return {"zone": zone, "total": len(details), "historique": historique}
