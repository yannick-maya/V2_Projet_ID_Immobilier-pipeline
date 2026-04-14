"""
Script pour corriger les périodes dans MongoDB
"""

from pymongo import MongoClient
import random
from datetime import datetime, timedelta

def generate_random_date():
    start_date = datetime(2025, 11, 1)
    end_date = datetime(2026, 2, 28)
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    return start_date + timedelta(days=random_number_of_days)

def main():
    client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
    db = client['id_immobilier']

    # Mettre à jour les périodes dans les annonces
    annonces = list(db.annonces.find({'periode': '2026-Q2'}))
    print(f'Trouvé {len(annonces)} annonces avec période 2026-Q2')

    random.seed(42)  # Pour la reproductibilité
    updated = 0

    for annonce in annonces:
        random_date = generate_random_date()
        new_periode = random_date.strftime('%Y-%m')

        db.annonces.update_one(
            {'_id': annonce['_id']},
            {'$set': {'periode': new_periode}}
        )
        updated += 1

    print(f'Mis à jour {updated} annonces avec nouvelles périodes')

    # Vérifier
    sample = db.annonces.find_one()
    print(f'Sample annonce après mise à jour: période = {sample.get("periode")}')

if __name__ == "__main__":
    main()