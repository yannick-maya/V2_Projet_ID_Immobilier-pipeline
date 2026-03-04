"""
Phase 1 - Ingestion des donnees
Lecture des 4 sources Excel + CSV scrapés et sauvegarde en CSV dans data/raw/
"""

import pandas as pd
import os
import glob

BASE_DIR     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCES_DIR  = os.path.join(BASE_DIR, "data", "raw", "sources")
SCRAPED_DIR  = os.path.join(BASE_DIR, "data", "raw", "scraped")
OUTPUT_DIR   = os.path.join(BASE_DIR, "data", "raw")

# Sources Excel statiques (fichiers collaborateurs)
SOURCES = {
    "immoask"       : "ImmoAsk.xlsx",
    "facebook"      : "Facebook_MarketPlace.xlsx",
    "coinafrique"   : "CoinAfrique_TogoImmobilier.xlsx",
    "valeursvenales": "Otr_Valeur_Venale.xlsx",
}

# Sources scrapées : nom_source → pattern de fichiers dans scraped/
SCRAPED_SOURCES = {
    "immoask_scraped"    : "immoask_*.csv",
    "coinafrique_scraped": "coinafrique_*.csv",
}


def get_latest_file(pattern: str) -> str | None:
    """Retourne le fichier le plus récent correspondant au pattern."""
    files = glob.glob(pattern)
    if not files:
        return None
    return max(files, key=os.path.getmtime)


def ingest_excel():
    """Ingestion des fichiers Excel statiques (inchangé)."""
    for source_name, filename in SOURCES.items():
        print(f"\n Ingestion Excel : {source_name}")

        path = os.path.join(SOURCES_DIR, filename)

        if not os.path.exists(path):
            print(f"   Fichier introuvable : {path}")
            print(f"   Place le fichier '{filename}' dans : {SOURCES_DIR}")
            continue

        df = pd.read_excel(path, engine="openpyxl")
        df["source"] = source_name

        output_path = os.path.join(OUTPUT_DIR, f"{source_name.lower()}.csv")
        df.to_csv(output_path, index=False, encoding="utf-8")

        print(f"   {len(df)} lignes | {len(df.columns)} colonnes")
        print(f"   Sauvegarde : {output_path}")


def ingest_scraped():
    """Ingestion des CSV scrapés : prend le fichier le plus récent pour chaque source."""
    if not os.path.exists(SCRAPED_DIR):
        print(f"\n Dossier scraped introuvable : {SCRAPED_DIR} — skip")
        return

    for source_name, pattern in SCRAPED_SOURCES.items():
        print(f"\n Ingestion scrapée : {source_name}")

        latest = get_latest_file(os.path.join(SCRAPED_DIR, pattern))

        if not latest:
            print(f"   Aucun fichier trouvé pour le pattern : {pattern}")
            print(f"   Lance d'abord : python scraper_immoask.py")
            continue

        print(f"   Fichier sélectionné : {os.path.basename(latest)}")

        df = pd.read_csv(latest, encoding="utf-8-sig")
        df["source"] = source_name

        output_path = os.path.join(OUTPUT_DIR, f"{source_name.lower()}.csv")
        df.to_csv(output_path, index=False, encoding="utf-8")

        print(f"   {len(df)} lignes | {len(df.columns)} colonnes")
        print(f"   Sauvegarde : {output_path}")


def ingest():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    ingest_excel()
    ingest_scraped()


if __name__ == "__main__":
    print(f"Racine du projet : {BASE_DIR}")
    print(f"Dossier sources  : {SOURCES_DIR}")
    print(f"Dossier scraped  : {SCRAPED_DIR}")
    ingest()
    print("\nIngestion terminee !")