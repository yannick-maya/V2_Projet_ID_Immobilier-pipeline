from fastapi import APIRouter, Depends, HTTPException

from api.auth.middleware import get_current_admin
from api.database import db
from api.utils import parse_object_id, serialize_doc

router = APIRouter()


@router.get("/users")
async def list_users(admin=Depends(get_current_admin)):
    users = []
    async for u in db["users"].find({}):
        u.pop("hashed_password", None)
        users.append(serialize_doc(u))
    return {"total": len(users), "data": users}


@router.put("/users/{id}")
async def update_user(id: str, payload: dict, admin=Depends(get_current_admin)):
    try:
        object_id = parse_object_id(id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Identifiant utilisateur invalide")

    allowed = {k: v for k, v in payload.items() if k in {"role", "blocked", "nom", "prenom"}}
    await db["users"].update_one({"_id": object_id}, {"$set": allowed})
    user = await db["users"].find_one({"_id": object_id})
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    user.pop("hashed_password", None)
    return serialize_doc(user)


@router.delete("/users/{id}")
async def delete_user(id: str, admin=Depends(get_current_admin)):
    try:
        object_id = parse_object_id(id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Identifiant utilisateur invalide")
    await db["users"].delete_one({"_id": object_id})
    return {"message": "Utilisateur supprimé"}


@router.get("/annonces")
async def admin_annonces(admin=Depends(get_current_admin)):
    data = [serialize_doc(d) async for d in db["annonces"].find({})]
    return {"total": len(data), "data": data}


@router.put("/annonces/{id}/valider")
async def valider_annonce(id: str, admin=Depends(get_current_admin)):
    try:
        object_id = parse_object_id(id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Identifiant annonce invalide")
    await db["annonces"].update_one({"_id": object_id}, {"$set": {"statut": "valide"}})
    return {"message": "Annonce validée"}


@router.put("/annonces/{id}/refuser")
async def refuser_annonce(id: str, admin=Depends(get_current_admin)):
    try:
        object_id = parse_object_id(id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Identifiant annonce invalide")
    await db["annonces"].update_one({"_id": object_id}, {"$set": {"statut": "refuse"}})
    return {"message": "Annonce refusée"}


@router.get("/stats")
async def platform_stats(admin=Depends(get_current_admin)):
    # Récupérer les statistiques générales
    nb_users = await db["users"].count_documents({})

    # Pipeline pour compter les annonces par statut
    pipeline = [
        {"$group": {"_id": "$statut", "count": {"$sum": 1}}}
    ]
    counts = {row["_id"] or "inconnu": row["count"] async for row in db["annonces"].aggregate(pipeline)}

    # Récupérer les données de l'overview public
    from api.routers.statistiques import statistiques_overview
    overview_data = await statistiques_overview()

    # Statistiques temporelles (derniers 30 jours)
    from datetime import datetime, timedelta
    thirty_days_ago = datetime.now() - timedelta(days=30)

    pipeline_time = [
        {"$match": {"created_at": {"$gte": thirty_days_ago.isoformat()}}},
        {"$group": {
            "_id": {
                "$dateToString": {"format": "%Y-%m-%d", "date": {"$dateFromString": {"dateString": "$created_at"}}}
            },
            "count": {"$sum": 1},
            "prix_moyen": {"$avg": "$prix"}
        }},
        {"$sort": {"_id": 1}}
    ]

    time_series = {}
    async for row in db["annonces"].aggregate(pipeline_time):
        date = row["_id"]
        if date:
            time_series[date] = {
                "count": row["count"],
                "prix_moyen": round(row.get("prix_moyen", 0), 2)
            }

    # Statistiques OTR
    pipeline_otr = [
        {"$match": {"prix_otr": {"$exists": True}}},
        {"$group": {
            "_id": "$statut_otr",
            "count": {"$sum": 1}
        }}
    ]

    otr_stats = {}
    async for row in db["annonces"].aggregate(pipeline_otr):
        statut = row["_id"] or "non_evalue"
        otr_stats[statut] = row["count"]

    return {
        "nb_users": nb_users,
        "nb_annonces_par_statut": counts,
        "nb_connexions_aujourdhui": 0,
        "taux_rejet_pipeline": 0,
        "overview": overview_data,
        "statistiques_par_jour": time_series,
        "statistiques_otr": otr_stats,
    }


@router.get("/okr")
async def okr(admin=Depends(get_current_admin)):
    total_annonces = await db["annonces"].count_documents({})
    total_stats = await db["statistiques"].count_documents({})
    total_indices = await db["indices"].count_documents({})

    return {
        "pipeline_success_rate": 95 if total_annonces else 0,
        "data_quality_score": 90 if total_stats else 0,
        "okr": [
            {"label": "Couverture annonces", "value": min(100, total_annonces / 100)},
            {"label": "Statistiques calculées", "value": min(100, total_stats / 50)},
            {"label": "Indices calculés", "value": min(100, total_indices / 50)},
        ],
    }


@router.get("/pipeline")
async def pipeline_monitoring(admin=Depends(get_current_admin)):
    return {
        "executions": [
            {"date": "latest", "status": "success", "tasks": ["ingestion", "cleaning", "modeling", "indicators", "index"]}
        ],
        "success_rate_12_weeks": 95,
    }
