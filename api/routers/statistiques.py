from fastapi import APIRouter

from api.database import db
from api.utils import serialize_doc

router = APIRouter()


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
