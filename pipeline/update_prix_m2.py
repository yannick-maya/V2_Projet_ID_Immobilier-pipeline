"""
Script pour calculer les prix au m² manquants dans MongoDB
"""

import os
from pymongo import MongoClient

def update_prix_m2():
    """Met à jour les prix au m² manquants pour les annonces"""

    # Connexion MongoDB
    mongo_url = os.getenv('MONGODB_URL', 'mongodb://localhost:27017/')
    client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
    db = client['id_immobilier']

    print("Calcul des prix au m² manquants...")

    # Récupérer les annonces sans prix_m2
    annonces = list(db['annonces'].find({
        'prix_m2': {'$exists': False},
        'prix': {'$exists': True, '$ne': None},
        'surface_m2': {'$exists': True, '$ne': None, '$gt': 0}
    }))

    updated_count = 0

    for annonce in annonces:
        prix = annonce.get('prix')
        surface = annonce.get('surface_m2')

        if prix and surface and surface > 0:
            prix_m2 = round(prix / surface, 2)

            # Mettre à jour l'annonce
            db['annonces'].update_one(
                {'_id': annonce['_id']},
                {'$set': {'prix_m2': prix_m2}}
            )

            updated_count += 1

            if updated_count % 500 == 0:
                print(f"Mis à jour: {updated_count} annonces")

    print(f"Total mis à jour: {updated_count} annonces")

    # Vérifier quelques exemples
    print("\nVérification des prix au m²:")
    samples = list(db['annonces'].find({'prix_m2': {'$exists': True}}).limit(3))
    for sample in samples:
        print(f"Prix: {sample.get('prix')}, Surface: {sample.get('surface_m2')}, Prix/m²: {sample.get('prix_m2')}")

if __name__ == "__main__":
    update_prix_m2()