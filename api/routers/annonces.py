from datetime import datetime

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query

from api.auth.middleware import get_current_user
from api.database import db
from api.models.annonce import AnnonceCreate
from api.utils import serialize_doc, utc_now_iso

router = APIRouter()


@router.get("/")
async def list_annonces(
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
    if zone:
        query["zone"] = zone
    if type_bien:
        query["type_bien"] = type_bien
    if type_offre:
        query["type_offre"] = type_offre
    if periode:
        query["periode"] = periode
    if prix_min is not None or prix_max is not None:
        price_query = {}
        if prix_min is not None:
            price_query["$gte"] = prix_min
        if prix_max is not None:
            price_query["$lte"] = prix_max
        query["prix"] = price_query

    total = await db["annonces"].count_documents(query)
    cursor = db["annonces"].find(query).skip((page - 1) * limit).limit(limit)
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
    annonce = await db["annonces"].find_one({"_id": ObjectId(id)})
    if not annonce:
        raise HTTPException(status_code=404, detail="Annonce introuvable")
    return serialize_doc(annonce)


@router.post("/")
async def create_annonce(payload: AnnonceCreate, user=Depends(get_current_user)):
    annee = payload.annee
    trimestre = payload.trimestre
    periode = payload.periode
    date_annonce = payload.date_annonce

    if not (annee and trimestre and periode):
        try:
            dt = datetime.fromisoformat((date_annonce or utc_now_iso()).replace("Z", "+00:00"))
            annee = annee or dt.year
            trimestre = trimestre or ((dt.month - 1) // 3 + 1)
            periode = periode or f"{annee}-Q{trimestre}"
        except ValueError:
            pass

    doc = payload.model_dump(exclude_none=True)
    doc.update(
        {
            "annee": annee,
            "trimestre": trimestre,
            "periode": periode,
            "created_at": utc_now_iso(),
            "created_by": user["id"],
            "statut": "en_attente",
        }
    )
    result = await db["annonces"].insert_one(doc)
    created = await db["annonces"].find_one({"_id": result.inserted_id})
    return serialize_doc(created)
