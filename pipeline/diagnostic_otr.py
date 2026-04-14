"""
Script de diagnostic pour comprendre pourquoi l'intégration OTR ne fonctionne pas
"""

import os
from pymongo import MongoClient

def diagnostic_otr():
    """Diagnostiquer les problèmes de matching OTR"""

    # Connexion MongoDB
    mongo_url = os.getenv('MONGODB_URL', 'mongodb://localhost:27017/')
    client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
    db = client['id_immobilier']

    print("=== DIAGNOSTIC OTR ===")

    # Statistiques générales
    total_annonces = db['annonces'].count_documents({'type_offre': 'VENTE'})
    total_venales = db['venales'].count_documents({})

    print(f"Total annonces VENTE: {total_annonces}")
    print(f"Total données vénales: {total_venales}")

    # Vérifier les champs requis
    annonces_with_prix_m2 = db['annonces'].count_documents({
        'type_offre': 'VENTE',
        'prix_m2': {'$exists': True, '$ne': None}
    })

    annonces_with_zone = db['annonces'].count_documents({
        'type_offre': 'VENTE',
        'zone': {'$exists': True, '$ne': None, '$ne': ''}
    })

    annonces_with_localisation = db['annonces'].count_documents({
        'type_offre': 'VENTE',
        'localisation': {'$exists': True}
    })

    venales_with_prix = db['venales'].count_documents({
        'prix_m2_officiel': {'$exists': True, '$ne': None}
    })

    venales_with_zone = db['venales'].count_documents({
        'zone': {'$exists': True, '$ne': None, '$ne': ''}
    })

    print(f"\nAnnonces avec prix_m2: {annonces_with_prix_m2}")
    print(f"Annonces avec zone: {annonces_with_zone}")
    print(f"Annonces avec localisation: {annonces_with_localisation}")
    print(f"Vénales avec prix_m2_officiel: {venales_with_prix}")
    print(f"Vénales avec zone: {venales_with_zone}")

    # Échantillons de zones
    print("\n=== ZONES ANNONCES ===")
    zones_annonces = db['annonces'].distinct('zone', {'type_offre': 'VENTE'})
    print(f"Zones annonces ({len(zones_annonces)}): {zones_annonces[:10]}...")

    print("\n=== ZONES VENALES ===")
    zones_venales = db['venales'].distinct('zone')
    print(f"Zones vénales ({len(zones_venales)}): {zones_venales[:10]}...")

    # Zones communes
    zones_communes = set(zones_annonces) & set(zones_venales)
    print(f"\nZones communes: {len(zones_communes)}")
    if zones_communes:
        print(f"Exemples: {list(zones_communes)[:5]}")

    # Types de bien
    print("\n=== TYPES DE BIEN ===")
    types_annonces = db['annonces'].distinct('type_bien', {'type_offre': 'VENTE'})
    print(f"Types annonces: {types_annonces}")

    types_venales = db['venales'].distinct('Type de bien')
    print(f"Types vénales: {types_venales}")

    # Test de matching manuel
    print("\n=== TEST MATCHING MANUEL ===")
    annonce_sample = db['annonces'].find_one({'type_offre': 'VENTE', 'zone': {'$exists': True}})
    venale_sample = db['venales'].find_one({'zone': {'$exists': True}})

    if annonce_sample and venale_sample:
        print(f"Annonce zone: '{annonce_sample.get('zone')}'")
        print(f"Vénale zone: '{venale_sample.get('zone')}'")

        # Test matching flexible
        annonce_zone = annonce_sample.get('zone', '').lower().strip()
        venale_zone = venale_sample.get('zone', '').lower().strip()

        if annonce_zone in venale_zone or venale_zone in annonce_zone:
            print("✓ Matching de zone possible")
        else:
            print("✗ Pas de matching de zone")

        # Test mots communs
        annonce_words = set(annonce_zone.split())
        venale_words = set(venale_zone.split())
        communs = annonce_words & venale_words
        print(f"Mots communs: {communs}")

if __name__ == "__main__":
    diagnostic_otr()