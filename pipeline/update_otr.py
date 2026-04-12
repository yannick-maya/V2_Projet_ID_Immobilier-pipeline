"""
Mise à jour des annonces existantes avec comparaison OTR pour les terrains
"""

import os
from dotenv import load_dotenv
from pymongo import MongoClient, UpdateOne

try:
    from pipeline.geo_temporal import infer_geo_hierarchy
except ModuleNotFoundError:
    from geo_temporal import infer_geo_hierarchy

load_dotenv()

def get_db():
    mongo_uri = os.getenv("MONGO_URI")
    mongo_db = os.getenv("MONGO_DB", "id_immobilier")
    if not mongo_uri:
        raise RuntimeError("MONGO_URI manquante dans le .env")
    client = MongoClient(mongo_uri)
    return client, client[mongo_db]

def update_annonces_otr():
    client, db = get_db()
    try:
        # Récupérer toutes les annonces de type Terrain sans prix_otr
        annonces = list(db["annonces"].find({"type_bien": {"$regex": "^terrain$", "$options": "i"}, "prix_otr": {"$exists": False}}))
        print(f"Mise à jour de {len(annonces)} annonces Terrain")

        ops = []
        for annonce in annonces:
            zone = annonce.get("zone")
            prix = annonce.get("prix")
            if not zone or not prix:
                continue

            geo_fields = infer_geo_hierarchy(zone)
            prefecture = geo_fields.get("prefecture", "").upper()
            zone_geo = geo_fields.get("zone", "").upper()
            quartier = geo_fields.get("quartier", "").upper()

            if prefecture and zone_geo and quartier:
                zone_key = f"{prefecture}_{zone_geo}_{quartier}"
                otr_doc = db["valeurs_venales"].find_one({"zone_key": zone_key, "type_bien": "TERRAIN"})
                if otr_doc:
                    prix_otr = otr_doc.get("valeur_venale")
                    if prix_otr:
                        difference = ((prix - prix_otr) / prix_otr) * 100
                        update_doc = {
                            "prix_otr": prix_otr,
                            "difference_otr": round(difference, 2),
                            "statut_otr": "sous-evalue" if difference < -10 else "sur-evalue" if difference > 10 else "conforme"
                        }
                        ops.append(UpdateOne({"_id": annonce["_id"]}, {"$set": update_doc}))

        if ops:
            result = db["annonces"].bulk_write(ops, ordered=False)
            print(f"Annonces mises à jour: {result.modified_count}")

    finally:
        client.close()

if __name__ == "__main__":
    update_annonces_otr()