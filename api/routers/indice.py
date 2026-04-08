from fastapi import APIRouter

from api.database import db
from api.utils import serialize_doc

router = APIRouter()


@router.get("/")
async def list_indices(
    zone: str | None = None,
    periode: str | None = None,
    year_month: str | None = None,
    tendance: str | None = None,
):
    query = {}
    if zone:
        query["zone"] = zone
    if periode:
        query["periode"] = periode
    if year_month:
        query["year_month"] = year_month
    if tendance:
        query["tendance"] = tendance

    data = [serialize_doc(d) async for d in db["indices"].find(query).sort([("observation_year", 1), ("observation_month", 1), ("zone", 1)])]
    return {"total": len(data), "data": data}


@router.get("/tendances")
async def tendances_resume():
    data = [serialize_doc(d) async for d in db["indices"].find({})]
    zones = {"HAUSSE": set(), "STABLE": set(), "BAISSE": set()}
    for d in data:
        t = d.get("tendance")
        z = d.get("zone")
        if t in zones and z:
            zones[t].add(z)

    return {
        "HAUSSE": {"count": len(zones["HAUSSE"]), "zones": sorted(zones["HAUSSE"])},
        "STABLE": {"count": len(zones["STABLE"]), "zones": sorted(zones["STABLE"])},
        "BAISSE": {"count": len(zones["BAISSE"]), "zones": sorted(zones["BAISSE"])},
    }


@router.get("/{zone}")
async def indice_zone(zone: str):
    data = [serialize_doc(d) async for d in db["indices"].find({"zone": zone})]
    data.sort(key=lambda x: (x.get("observation_year", x.get("annee", 0)), x.get("observation_month", 0), x.get("trimestre", 0)))
    return {"zone": zone, "historique": data}
