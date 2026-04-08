import math
from statistics import median

from fastapi import APIRouter
from pydantic import BaseModel

from api.database import db

router = APIRouter()


class ScoringRequest(BaseModel):
    zone: str
    type_bien: str
    type_offre: str
    surface_m2: float
    pieces: int | None = None


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
    ratio = index - lower
    return values[lower] + (values[upper] - values[lower]) * ratio


def _robust_values(values: list[float]) -> list[float]:
    cleaned = sorted(value for value in values if value and math.isfinite(value) and value > 0)
    if len(cleaned) < 8:
        return cleaned
    lower = _percentile(cleaned, 0.05)
    upper = _percentile(cleaned, 0.95)
    trimmed = [value for value in cleaned if lower <= value <= upper]
    return trimmed or cleaned


@router.post("/")
async def score(payload: ScoringRequest):
    query_exact = {
        "zone": payload.zone,
        "type_bien": payload.type_bien,
        "type_offre": payload.type_offre,
        "prix_m2": {"$gt": 0},
    }
    query_zone = {
        "zone": payload.zone,
        "prix_m2": {"$gt": 0},
    }
    query_global = {"prix_m2": {"$gt": 0}}

    async def robust_prix_m2(query):
        values = []
        async for doc in db["annonces"].find(query, {"prix_m2": 1}):
            try:
                value = float(doc.get("prix_m2"))
            except (TypeError, ValueError):
                continue
            if value > 0 and math.isfinite(value):
                values.append(value)

        trimmed = _robust_values(values)
        if not trimmed:
            return None, 0
        if len(trimmed) >= 5:
            reference = float(median(trimmed))
        else:
            reference = float(sum(trimmed) / len(trimmed))
        return reference, len(values)

    prix_m2_ref, n = await robust_prix_m2(query_exact)
    source = "exact"
    if not prix_m2_ref:
        prix_m2_ref, n = await robust_prix_m2(query_zone)
        source = "zone"
    if not prix_m2_ref:
        prix_m2_ref, n = await robust_prix_m2(query_global)
        source = "global"
    if not prix_m2_ref:
        prix_m2_ref, n = 75000.0, 0
        source = "default"

    # Ajustement léger selon nombre de pièces
    pieces = payload.pieces or 0
    factor_pieces = 1.0 + min(max(pieces - 2, -2), 4) * 0.03
    prix_m2_estime = prix_m2_ref * factor_pieces
    prix_total = prix_m2_estime * max(payload.surface_m2, 1)

    # Intervalle basé sur volatilité simple
    margin = 0.12 if n >= 30 else 0.18
    intervalle = [round(prix_total * (1 - margin), 2), round(prix_total * (1 + margin), 2)]

    indice_doc = await db["indices"].find_one(
        {"zone": payload.zone, "type_bien": payload.type_bien},
        sort=[("annee", -1), ("trimestre", -1)],
    )
    tendance = (indice_doc or {}).get("tendance", "STABLE")
    indice_valeur = float((indice_doc or {}).get("indice_valeur", 100))

    return {
        "source_reference": source,
        "observations": n,
        "prix_m2_reference": round(prix_m2_ref, 2),
        "prix_m2_estime": round(prix_m2_estime, 2),
        "prix_estime": round(prix_total, 2),
        "intervalle_confiance": intervalle,
        "indice_zone": tendance,
        "indice_valeur": indice_valeur,
    }
