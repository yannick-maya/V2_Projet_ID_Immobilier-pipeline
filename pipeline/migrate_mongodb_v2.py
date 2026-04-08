from __future__ import annotations

import os
from collections import Counter

from dotenv import load_dotenv
from pymongo import MongoClient, UpdateOne

try:
    from pipeline.geo_temporal import build_zone_document, derive_time_fields, infer_geo_hierarchy, now_iso
except ModuleNotFoundError:
    from geo_temporal import build_zone_document, derive_time_fields, infer_geo_hierarchy, now_iso

load_dotenv()


def get_db():
    mongo_uri = os.getenv("MONGO_URI")
    mongo_db = os.getenv("MONGO_DB", "id_immobilier")
    if not mongo_uri:
        raise RuntimeError("MONGO_URI manquante dans le .env")
    client = MongoClient(mongo_uri)
    return client, client[mongo_db]


def backfill_annonces(db):
    ops = []
    zone_counts = Counter()
    total = 0
    for annonce in db["annonces"].find({}):
        total += 1
        zone_value = annonce.get("zone")
        geo_fields = infer_geo_hierarchy(zone_value)
        time_fields = derive_time_fields(
            date_annonce=annonce.get("date_annonce"),
            created_at=annonce.get("created_at"),
            fallback_iso=annonce.get("created_at") or now_iso(),
        )
        update_doc = {
            "zone_display": geo_fields["zone_name"],
            "zone_id": geo_fields["zone_id"],
            "zone_slug": geo_fields["zone_slug"],
            "geo": geo_fields["geo"],
            **time_fields,
        }
        zone_id = geo_fields.get("zone_id")
        if zone_id:
            zone_counts[zone_id] += 1
        ops.append(UpdateOne({"_id": annonce["_id"]}, {"$set": update_doc}))

        if len(ops) >= 500:
            db["annonces"].bulk_write(ops, ordered=False)
            ops = []

    if ops:
        db["annonces"].bulk_write(ops, ordered=False)
    return total, zone_counts


def rebuild_zones(db, zone_counts):
    ops = []
    for zone_id, count in zone_counts.items():
        annonce = db["annonces"].find_one({"zone_id": zone_id}, {"zone_display": 1, "zone": 1})
        zone_doc = build_zone_document((annonce or {}).get("zone_display") or (annonce or {}).get("zone"), source_count=count)
        if not zone_doc:
            continue
        zone_doc["source_count"] = count
        ops.append(
            UpdateOne(
                {"_id": zone_doc["_id"]},
                {"$set": zone_doc, "$setOnInsert": {"created_at": now_iso()}},
                upsert=True,
            )
        )
    if ops:
        db["zones"].bulk_write(ops, ordered=False)
    return len(ops)


def run():
    print("Migration MongoDB v2 en cours...")
    client, db = get_db()
    try:
        annonces_total, zone_counts = backfill_annonces(db)
        zones_total = rebuild_zones(db, zone_counts)
        print(f"  Annonces retro-enrichies : {annonces_total}")
        print(f"  Zones canoniques creees  : {zones_total}")
        print("Relance ensuite:")
        print("  python pipeline/indicators.py")
        print("  python pipeline/index.py")
    finally:
        client.close()


if __name__ == "__main__":
    run()
