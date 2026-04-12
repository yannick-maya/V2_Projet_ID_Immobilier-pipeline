"""
Chargement des données OTR (Valeurs Vénale) dans MongoDB
"""

import os
import pandas as pd
from dotenv import load_dotenv
from pymongo import MongoClient, UpdateOne

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")

def get_db():
    mongo_uri = os.getenv("MONGO_URI")
    mongo_db = os.getenv("MONGO_DB", "id_immobilier")
    if not mongo_uri:
        raise RuntimeError("MONGO_URI manquante dans le .env")
    client = MongoClient(mongo_uri)
    return client, client[mongo_db]

def load_otr():
    client, db = get_db()
    try:
        # Charger le CSV OTR
        otr_path = os.path.join(RAW_DIR, "valeursvenales.csv")
        if not os.path.exists(otr_path):
            print("Fichier valeursvenales.csv non trouvé")
            return

        df = pd.read_csv(otr_path, sep=',', encoding='utf-8')
        print(f"Chargement de {len(df)} lignes OTR")

        # Nettoyer et préparer les données
        df = df.dropna(subset=['Préfecture', 'Zone', 'Quartier', 'Type de bien'])
        df['Valeur vénale (FCFA)'] = pd.to_numeric(df['Valeur vénale (FCFA)'], errors='coerce')
        df['Surface (m²)'] = pd.to_numeric(df['Surface (m²)'], errors='coerce')
        df['Valeur/m² (FCFA)'] = pd.to_numeric(df['Valeur/m² (FCFA)'], errors='coerce')
        df = df.dropna(subset=['Valeur vénale (FCFA)'])

        # Créer la clé unique pour matching
        df['zone_key'] = df['Préfecture'].str.upper() + '_' + df['Zone'].str.upper() + '_' + df['Quartier'].str.upper()

        # Insérer dans MongoDB
        ops = []
        for _, row in df.iterrows():
            doc = {
                "prefecture": row['Préfecture'],
                "zone": row['Zone'],
                "quartier": row['Quartier'],
                "type_offre": row['Type d\'offre'],
                "type_bien": row['Type de bien'],
                "valeur_venale": float(row['Valeur vénale (FCFA)']),
                "surface_m2": float(row['Surface (m²)']) if pd.notna(row['Surface (m²)']) else None,
                "valeur_m2": float(row['Valeur/m² (FCFA)']) if pd.notna(row['Valeur/m² (FCFA)']) else None,
                "source": row['source'],
                "annee": int(row['annee']) if pd.notna(row['annee']) else None,
                "trimestre": int(row['trimestre']) if pd.notna(row['trimestre']) else None,
                "periode": row['periode'],
                "zone_key": row['zone_key']
            }
            ops.append(
                UpdateOne(
                    {"zone_key": doc["zone_key"], "type_bien": doc["type_bien"]},
                    {"$set": doc},
                    upsert=True
                )
            )

        if ops:
            result = db["valeurs_venales"].bulk_write(ops, ordered=False)
            print(f"OTR insérées: {result.upserted_count}, mises à jour: {result.modified_count}")

    finally:
        client.close()

if __name__ == "__main__":
    load_otr()