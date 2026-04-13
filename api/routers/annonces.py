from fastapi import APIRouter, Depends, HTTPException, Query

from api.auth.middleware import get_current_user
from api.database import db
from api.models.annonce import AnnonceCreate
from api.utils import parse_object_id, serialize_doc, utc_now_iso
from pipeline.geo_temporal import derive_time_fields, infer_geo_hierarchy

router = APIRouter()


@router.get("/")
async def list_annonces(
    q: str | None = None,
    zone: str | None = None,
    type_bien: str | None = None,
    type_offre: str | None = None,
    prix_min: float | None = None,
    prix_max: float | None = None,
    periode: str | None = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
):
    query = {}
    if q:
        query["$or"] = [
            {"titre": {"$regex": q, "$options": "i"}},
            {"description": {"$regex": q, "$options": "i"}},
            {"zone": {"$regex": q, "$options": "i"}},
            {"zone_display": {"$regex": q, "$options": "i"}},
        ]
    if zone:
        query["$and"] = query.get("$and", []) + [{"zone": {"$regex": f"^{zone.strip()}$", "$options": "i"}}]
    if type_bien:
        query["$and"] = query.get("$and", []) + [{"type_bien": {"$regex": f"^{type_bien.strip()}$", "$options": "i"}}]
    if type_offre:
        query["$and"] = query.get("$and", []) + [{"type_offre": {"$regex": f"^{type_offre.strip()}$", "$options": "i"}}]
    if periode:
        query["$and"] = query.get("$and", []) + [{
            "$or": [
                {"periode": {"$regex": f"^{periode.strip()}$", "$options": "i"}},
                {"year_month": {"$regex": f"^{periode.strip()}$", "$options": "i"}},
            ]
        }]
    if prix_min is not None or prix_max is not None:
        price_query = {}
        if prix_min is not None:
            price_query["$gte"] = prix_min
        if prix_max is not None:
            price_query["$lte"] = prix_max
        query["$and"] = query.get("$and", []) + [{"prix": price_query}]

    if "$and" in query and len(query["$and"]) == 1 and "$or" not in query:
        query.update(query.pop("$and")[0])
    elif "$and" in query and not query["$and"]:
        query.pop("$and")

    total = await db["annonces"].count_documents(query)
    cursor = (
        db["annonces"]
        .find(query)
        .sort([("observation_year", -1), ("observation_month", -1), ("created_at", -1)])
        .skip((page - 1) * limit)
        .limit(limit)
    )
    data = [serialize_doc(d) async for d in cursor]

    return {"total": total, "page": page, "limit": limit, "data": data}


@router.get("/search")
async def search_annonces(q: str = Query(..., min_length=2)):
    query = {"$text": {"$search": q}}
    cursor = db["annonces"].find(query).limit(100)
    data = [serialize_doc(d) async for d in cursor]
    return {"total": len(data), "data": data}


@router.get("/{id}")
async def get_annonce(id: str):
    try:
        object_id = parse_object_id(id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Identifiant annonce invalide")

    annonce = await db["annonces"].find_one({"_id": object_id})
    if not annonce:
        raise HTTPException(status_code=404, detail="Annonce introuvable")
    return serialize_doc(annonce)


@router.post("/")
async def create_annonce(payload: AnnonceCreate, user=Depends(get_current_user)):
    annee = payload.annee
    trimestre = payload.trimestre
    periode = payload.periode
    date_annonce = payload.date_annonce

    time_fields = derive_time_fields(
        date_annonce=date_annonce,
        created_at=utc_now_iso(),
        fallback_iso=utc_now_iso(),
        year_month=payload.year_month,
        periode=payload.periode,
        annee=payload.annee,
        trimestre=payload.trimestre,
        seed_value=f"{payload.titre}|{payload.zone}|{payload.source}",
    )
    annee = annee or time_fields["annee"]
    trimestre = trimestre or time_fields["trimestre"]
    periode = periode or time_fields["periode"]
    geo_fields = infer_geo_hierarchy(payload.zone)

    doc = payload.model_dump(exclude_none=True)
    doc.update(
        {
            "annee": annee,
            "trimestre": trimestre,
            "periode": periode,
            "year_month": time_fields["year_month"],
            "observation_year": time_fields["observation_year"],
            "observation_month": time_fields["observation_month"],
            "observation_quarter": time_fields["observation_quarter"],
            "source_posted_at": time_fields["source_posted_at"],
            "source_scraped_at": time_fields["source_scraped_at"],
            "observation_date": time_fields["observation_date"],
            "zone_display": geo_fields["zone_name"],
            "zone_id": geo_fields["zone_id"],
            "zone_slug": geo_fields["zone_slug"],
            "geo": geo_fields["geo"],
            "created_at": utc_now_iso(),
            "created_by": user["id"],
            "statut": "en_attente",
        }
    )
    result = await db["annonces"].insert_one(doc)
    created = await db["annonces"].find_one({"_id": result.inserted_id})
    return serialize_doc(created)
