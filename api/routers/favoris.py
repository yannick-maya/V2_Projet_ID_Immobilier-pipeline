from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException

from api.auth.middleware import get_current_user
from api.database import db
from api.utils import serialize_doc

router = APIRouter()


@router.get("/")
async def list_favoris(user=Depends(get_current_user)):
    user_doc = await db["users"].find_one({"_id": ObjectId(user["id"])})
    favoris = user_doc.get("favoris", []) if user_doc else []
    object_ids = []
    for fav in favoris:
        try:
            object_ids.append(ObjectId(fav))
        except Exception:
            continue

    annonces = [serialize_doc(d) async for d in db["annonces"].find({"_id": {"$in": object_ids}})] if object_ids else []
    return {"total": len(annonces), "data": annonces}


@router.post("/{annonce_id}")
async def add_favori(annonce_id: str, user=Depends(get_current_user)):
    annonce = await db["annonces"].find_one({"_id": ObjectId(annonce_id)})
    if not annonce:
        raise HTTPException(status_code=404, detail="Annonce introuvable")

    await db["users"].update_one({"_id": ObjectId(user["id"])}, {"$addToSet": {"favoris": annonce_id}})
    return {"message": "Favori ajouté"}


@router.delete("/{annonce_id}")
async def remove_favori(annonce_id: str, user=Depends(get_current_user)):
    await db["users"].update_one({"_id": ObjectId(user["id"])}, {"$pull": {"favoris": annonce_id}})
    return {"message": "Favori retiré"}
