"""
Phase 5 - Calcul de l'indice ID Immobilier (MongoDB)
Indice = (prix_moyen_periode / prix_moyen_periode_reference) * 100
Reference = premier trimestre disponible pour chaque zone + type_bien
"""

import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from pymongo import MongoClient, UpdateOne

load_dotenv()


def get_db():
    mongo_uri = os.getenv("MONGO_URI")
    mongo_db = os.getenv("MONGO_DB", "id_immobilier")
    if not mongo_uri:
        raise RuntimeError("MONGO_URI manquante dans le .env")
    client = MongoClient(mongo_uri)
    return client, client[mongo_db]


def tendance(indice):
    if indice > 105:
        return "HAUSSE"
    if indice < 95:
        return "BAISSE"
    return "STABLE"


def aggreger_prix_moyens(db):
    pipeline_agg = [
        {"$match": {"prix_m2": {"$gt": 0}, "zone_id": {"$exists": True, "$ne": None}}},
        {
            "$group": {
                "_id": {
                    "zone": "$zone",
                    "zone_id": "$zone_id",
                    "zone_slug": "$zone_slug",
                    "type_bien": "$type_bien",
                    "periode": "$periode",
                    "year_month": "$year_month",
                    "observation_year": "$observation_year",
                    "observation_month": "$observation_month",
                    "observation_quarter": "$observation_quarter",
                    "annee": "$annee",
                    "trimestre": "$trimestre",
                },
                "prix_moyen_m2": {"$avg": "$prix_m2"},
                "nombre_annonces": {"$sum": 1},
            }
        },
    ]
    return list(db["annonces"].aggregate(pipeline_agg))


def calculer_indices(rows):
    grouped = {}
    for row in rows:
        grp = row.get("_id", {})
        zone = grp.get("zone")
        zone_id = grp.get("zone_id")
        zone_slug = grp.get("zone_slug")
        type_bien = grp.get("type_bien")
        year_month = grp.get("year_month")
        observation_year = grp.get("observation_year")
        observation_month = grp.get("observation_month")
        observation_quarter = grp.get("observation_quarter")
        annee = grp.get("annee")
        trimestre = grp.get("trimestre")
        periode = grp.get("periode")
        prix_moyen = float(row.get("prix_moyen_m2", 0))
        nb = int(row.get("nombre_annonces", 0))

        if zone is None or zone_id is None or type_bien is None or year_month is None:
            continue

        key = (zone_id, type_bien)
        grouped.setdefault(key, []).append(
            {
                "zone": zone,
                "zone_id": zone_id,
                "zone_slug": zone_slug,
                "type_bien": type_bien,
                "periode": periode,
                "year_month": year_month,
                "observation_year": int(observation_year) if observation_year is not None else 9999,
                "observation_month": int(observation_month) if observation_month is not None else 99,
                "observation_quarter": int(observation_quarter) if observation_quarter is not None else 9,
                "annee": int(annee) if annee is not None else 9999,
                "trimestre": int(trimestre) if trimestre is not None else 9,
                "prix_moyen_m2": round(prix_moyen, 2),
                "nombre_annonces": nb,
            }
        )

    documents = []
    for (_, _), values in grouped.items():
        values = sorted(values, key=lambda x: (x["observation_year"], x["observation_month"]))
        prix_ref = values[0]["prix_moyen_m2"] if values else 0
        if prix_ref <= 0:
            continue

        for val in values:
            indice = round((val["prix_moyen_m2"] / prix_ref) * 100, 4)
            documents.append(
                {
                    "zone": val["zone"],
                    "zone_id": val["zone_id"],
                    "zone_slug": val["zone_slug"],
                    "type_bien": val["type_bien"],
                    "periode": val["periode"],
                    "year_month": val["year_month"],
                    "observation_year": val["observation_year"],
                    "observation_month": val["observation_month"],
                    "observation_quarter": val["observation_quarter"],
                    "annee": val["annee"],
                    "trimestre": val["trimestre"],
                    "prix_reference_m2": prix_ref,
                    "prix_moyen_m2": val["prix_moyen_m2"],
                    "nombre_annonces": val["nombre_annonces"],
                    "indice_valeur": indice,
                    "tendance": tendance(indice),
                }
            )
    return documents


def upsert_indices(db, docs):
    now_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    ops = []
    for doc in docs:
        key = {
            "zone_id": doc["zone_id"],
            "type_bien": doc["type_bien"],
            "year_month": doc["year_month"],
        }
        ops.append(
            UpdateOne(
                key,
                {"$set": {**doc, "updated_at": now_iso}, "$setOnInsert": {"created_at": now_iso}},
                upsert=True,
            )
        )

    if not ops:
        return {"inserted": 0, "updated": 0, "matched": 0}

    result = db["indices"].bulk_write(ops, ordered=False)
    return {
        "inserted": result.upserted_count,
        "updated": result.modified_count,
        "matched": result.matched_count,
    }


def run():
    print("Calcul des indices MongoDB...")
    client, db = get_db()
    try:
        rows = aggreger_prix_moyens(db)
        docs = calculer_indices(rows)
        logs = upsert_indices(db, docs)
        print(f"  Agrégats source   : {len(rows)}")
        print(f"  Indices calculés  : {len(docs)}")
        print(f"  Insérés           : {logs['inserted']}")
        print(f"  Mis à jour        : {logs['updated']}")
        print(f"  Déjà existants    : {logs['matched']}")
    finally:
        client.close()


if __name__ == "__main__":
    run()
