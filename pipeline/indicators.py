"""
Phase 4 - Calcul des indicateurs statistiques (MongoDB)
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


def calculer_statistiques(db):
    pipeline_agg = [
        {"$match": {"prix_m2": {"$gt": 0}}},
        {
            "$group": {
                "_id": {
                    "zone": "$zone",
                    "type_bien": "$type_bien",
                    "type_offre": "$type_offre",
                    "periode": "$periode",
                    "annee": "$annee",
                    "trimestre": "$trimestre",
                },
                "prix_moyen_m2": {"$avg": "$prix_m2"},
                "prix_median_m2": {"$avg": "$prix_m2"},
                "prix_min_m2": {"$min": "$prix_m2"},
                "prix_max_m2": {"$max": "$prix_m2"},
                "nombre_annonces": {"$sum": 1},
            }
        },
    ]
    return list(db["annonces"].aggregate(pipeline_agg))


def upsert_statistiques(db, resultats):
    ops = []
    now_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    for row in resultats:
        grp = row.get("_id", {})
        doc = {
            "zone": grp.get("zone"),
            "type_bien": grp.get("type_bien"),
            "type_offre": grp.get("type_offre"),
            "periode": grp.get("periode"),
            "annee": grp.get("annee"),
            "trimestre": grp.get("trimestre"),
            "prix_moyen_m2": round(float(row.get("prix_moyen_m2", 0)), 2),
            "prix_median_m2": round(float(row.get("prix_median_m2", 0)), 2),
            "prix_min_m2": round(float(row.get("prix_min_m2", 0)), 2),
            "prix_max_m2": round(float(row.get("prix_max_m2", 0)), 2),
            "nombre_annonces": int(row.get("nombre_annonces", 0)),
            "updated_at": now_iso,
        }
        key = {
            "zone": doc["zone"],
            "type_bien": doc["type_bien"],
            "type_offre": doc["type_offre"],
            "periode": doc["periode"],
        }
        ops.append(
            UpdateOne(
                key,
                {"$set": doc, "$setOnInsert": {"created_at": now_iso}},
                upsert=True,
            )
        )

    if not ops:
        return {"inserted": 0, "updated": 0, "matched": 0}

    result = db["statistiques"].bulk_write(ops, ordered=False)
    return {
        "inserted": result.upserted_count,
        "updated": result.modified_count,
        "matched": result.matched_count,
    }


def run():
    print("Calcul des indicateurs MongoDB...")
    client, db = get_db()
    try:
        resultats = calculer_statistiques(db)
        logs = upsert_statistiques(db, resultats)
        print(f"  Agrégats calculés : {len(resultats)}")
        print(f"  Insérés           : {logs['inserted']}")
        print(f"  Mis à jour        : {logs['updated']}")
        print(f"  Déjà existants    : {logs['matched']}")
    finally:
        client.close()


if __name__ == "__main__":
    run()
