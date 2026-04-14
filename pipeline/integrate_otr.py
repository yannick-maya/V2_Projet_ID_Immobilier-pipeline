"""
Script pour intégrer les données OTR (valeurs vénales) dans les annonces
Calcule les écarts entre prix marché et prix officiel
Version MongoDB
"""

import pandas as pd
import numpy as np
import os
from pymongo import MongoClient
from datetime import datetime
import math

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calcule la distance en km entre deux points GPS"""
    R = 6371  # Rayon de la Terre en km

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return R * c

def find_closest_otr_price(annonce, venales_data):
    """
    Trouve le prix OTR le plus proche pour une annonce donnée
    Matching assoupli : uniquement par zone, sans contrainte de type ou distance
    """
    annonce_zone = annonce.get('zone', '').lower().strip()
    if not annonce_zone:
        return None

    # Chercher les vénales dans la même zone (matching flexible)
    candidates = []
    for venale in venales_data:
        venale_zone = venale.get('zone', '').lower().strip()
        if not venale_zone:
            continue

        # Matching flexible de zone
        if annonce_zone in venale_zone or venale_zone in annonce_zone:
            candidates.append(venale)
        else:
            # Essayer avec mots communs
            annonce_words = set(annonce_zone.split())
            venale_words = set(venale_zone.split())
            if annonce_words & venale_words:  # Au moins un mot en commun
                candidates.append(venale)

    if not candidates:
        return None

    # Retourner le premier candidat (prix moyen par zone)
    # On pourrait améliorer en faisant une moyenne des prix dans la zone
    return candidates[0]

def update_annonces_with_otr():
    """Met à jour les annonces avec les données OTR"""

    # Connexion MongoDB
    mongo_url = os.getenv('MONGODB_URL', 'mongodb://localhost:27017/')
    client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
    db = client['id_immobilier']

    print("Chargement des données vénales...")
    venales = list(db['venales'].find({}))
    print(f"Chargé {len(venales)} données vénales")

    print("Traitement des annonces...")
    # Traiter toutes les annonces (pas seulement VENTE, car OTR peut s'appliquer à tous types)
    annonces = list(db['annonces'].find({}))

    updated_count = 0
    total_count = len(annonces)

    print(f"Traitement de {total_count} annonces...")

    for i, annonce in enumerate(annonces):
        if i % 500 == 0:
            print(f"Traitement: {i}/{total_count} - Mis à jour: {updated_count}")

        # Trouver le prix OTR le plus proche
        closest_otr = find_closest_otr_price(annonce, venales)

        if closest_otr:
            prix_otr_m2 = closest_otr.get('prix_m2_officiel')
            prix_marche_m2 = annonce.get('prix_m2')

            if prix_otr_m2 and prix_marche_m2 and prix_marche_m2 > 0:
                # Calculer l'écart
                difference_absolue = prix_marche_m2 - prix_otr_m2
                difference_pourcent = (difference_absolue / prix_otr_m2) * 100

                # Déterminer le statut
                if difference_pourcent > 20:
                    statut = "surévalué"
                elif difference_pourcent < -20:
                    statut = "sous-évalué"
                else:
                    statut = "conforme"

                # Mettre à jour l'annonce
                update_data = {
                    'prix_otr': float(prix_otr_m2),
                    'difference_otr': float(difference_pourcent),
                    'statut_otr': statut,
                    'otr_source': closest_otr.get('source', 'valeursvenales'),
                    'date_otr_integration': datetime.now()
                }

                db['annonces'].update_one(
                    {'_id': annonce['_id']},
                    {'$set': update_data}
                )

                updated_count += 1

    print(f"Mise à jour terminée: {updated_count}/{total_count} annonces mises à jour avec données OTR")

    # Statistiques finales
    stats = list(db['annonces'].aggregate([
        {'$match': {'statut_otr': {'$exists': True}}},
        {'$group': {
            '_id': '$statut_otr',
            'count': {'$sum': 1},
            'avg_difference': {'$avg': '$difference_otr'}
        }}
    ]))

    print("\nStatistiques des écarts OTR:")
    for stat in stats:
        print(f"{stat['_id']}: {stat['count']} annonces, écart moyen: {stat['avg_difference']:.2f}%")

    # Statistiques par zone
    print("\nTop 10 zones par nombre d'annonces avec OTR:")
    zone_stats = list(db['annonces'].aggregate([
        {'$match': {'statut_otr': {'$exists': True}}},
        {'$group': {
            '_id': '$zone',
            'count': {'$sum': 1},
            'avg_difference': {'$avg': '$difference_otr'}
        }},
        {'$sort': {'count': -1}},
        {'$limit': 10}
    ]))

    for stat in zone_stats:
        print(f"{stat['_id']}: {stat['count']} annonces, écart moyen: {stat['avg_difference']:.2f}%")

if __name__ == "__main__":
    update_annonces_with_otr()