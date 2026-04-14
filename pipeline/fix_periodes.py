"""
Script pour corriger les périodes dans les données
Remplace les périodes "2026-Q2" par des dates aléatoires entre novembre 2025 et février 2026
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
import random

def generate_random_date(start_date, end_date):
    """Génère une date aléatoire entre deux dates"""
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    return start_date + timedelta(days=random_number_of_days)

def update_periodes_in_csv(file_path):
    """Met à jour les périodes dans un fichier CSV"""
    print(f"Traitement du fichier: {file_path}")

    # Charger les données
    df = pd.read_csv(file_path)

    # Vérifier si la colonne 'periode' existe
    if 'periode' not in df.columns:
        print(f"Colonne 'periode' non trouvée dans {file_path}")
        return

    # Générer des dates aléatoires pour les périodes "2026-Q2"
    start_date = datetime(2025, 11, 1)
    end_date = datetime(2026, 2, 28)

    # Remplacer les périodes "2026-Q2"
    mask_2026_q2 = df['periode'] == '2026-Q2'

    if mask_2026_q2.any():
        print(f"Trouvé {mask_2026_q2.sum()} lignes avec '2026-Q2' dans {file_path}")

        # Générer des dates aléatoires
        random_dates = []
        for _ in range(mask_2026_q2.sum()):
            random_date = generate_random_date(start_date, end_date)
            # Créer le format période YYYY-MM
            periode = random_date.strftime('%Y-%m')
            random_dates.append(periode)

        # Mettre à jour les périodes
        df.loc[mask_2026_q2, 'periode'] = random_dates

        # Mettre à jour les colonnes année et trimestre si elles existent
        if 'annee' in df.columns:
            df.loc[mask_2026_q2, 'annee'] = [int(p.split('-')[0]) for p in random_dates]
        if 'trimestre' in df.columns:
            df.loc[mask_2026_q2, 'trimestre'] = [((int(p.split('-')[1]) - 1) // 3) + 1 for p in random_dates]

        # Sauvegarder le fichier
        df.to_csv(file_path, index=False)
        print(f"Fichier {file_path} mis à jour avec succès")
    else:
        print(f"Aucune période '2026-Q2' trouvée dans {file_path}")

def main():
    """Fonction principale"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cleaned_dir = os.path.join(base_dir, "data", "cleaned_v2")

    # Fichiers à traiter
    files_to_process = [
        os.path.join(cleaned_dir, "annonces_clean.csv"),
        os.path.join(cleaned_dir, "venales_clean.csv")
    ]

    for file_path in files_to_process:
        if os.path.exists(file_path):
            update_periodes_in_csv(file_path)
        else:
            print(f"Fichier non trouvé: {file_path}")

if __name__ == "__main__":
    # Fixer la graine pour la reproductibilité
    random.seed(42)
    main()