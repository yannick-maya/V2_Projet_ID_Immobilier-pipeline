"""
scraper_coinafrique.py
======================
Scrape les annonces immobilières de tg.coinafrique.com (BeautifulSoup)
et sauvegarde les données BRUTES dans data/raw/scraped/.

Ce script ne fait AUCUN nettoyage — c'est le job de Spark dans le pipeline.

Usage :
    python scraper_coinafrique.py
    python scraper_coinafrique.py --pages 60
    python scraper_coinafrique.py --pages 10 --output data/raw/scraped/test.csv
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import argparse
import logging
from urllib.parse import urljoin
from datetime import datetime
from pathlib import Path

# ─── CONFIG ──────────────────────────────────────────────────────────────────

BASE_URL     = "https://tg.coinafrique.com"
CATEGORY_URL = f"{BASE_URL}/categorie/immobilier"
DELAY        = 1.5   # secondes entre chaque annonce (respecter le serveur)
PAGE_DELAY   = 2     # secondes entre chaque page

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
log = logging.getLogger(__name__)

HEADERS = {
    "User-Agent"     : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept"         : "text/html,application/xhtml+xml,application/xml;q=0.9",
    "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
}

# ─── SCRAPER ─────────────────────────────────────────────────────────────────

class CoinAfriqueScraperTogo:
    """Scrape tg.coinafrique.com et sauvegarde les données brutes en CSV."""

    def __init__(self, max_pages: int = 60):
        self.max_pages   = max_pages
        self.session     = requests.Session()
        self.session.headers.update(HEADERS)
        self.all_listings = []

    # ── 1. Récupération des URLs par page ─────────────────────────────────────

    def get_page_urls(self, page_num: int) -> list:
        """Retourne la liste des URLs d'annonces sur une page."""
        url = f"{CATEGORY_URL}?page={page_num}"
        try:
            resp = self.session.get(url, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            seen = set()
            urls = []
            for link in soup.find_all("a", href=re.compile(r"/annonce/")):
                href = link.get("href")
                if href and "/annonce/" in href:
                    full_url = urljoin(BASE_URL, href)
                    if full_url not in seen:
                        seen.add(full_url)
                        urls.append(full_url)
            return urls
        except Exception as e:
            log.warning(f"Page {page_num} — erreur : {e}")
            return []

    # ── 2. Extraction d'une annonce ───────────────────────────────────────────

    def extract_listing(self, url: str) -> dict | None:
        """Extrait les champs bruts d'une annonce. Retourne None si erreur."""
        try:
            time.sleep(DELAY)
            resp = self.session.get(url, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            body = soup.get_text()

            # Titre
            h1    = soup.find("h1")
            titre = h1.get_text(strip=True) if h1 else None

            # Prix brut (on laisse Spark nettoyer le format)
            prix = None
            for pattern in [
                r"(\d[\d\s,.]*)\\s*(?:CFA|FCFA|F\s*CFA)",
                r"(\d[\d\s,.]+)\s*(?:CFA|FCFA)",
                r"(\d+(?:[.,]\d+)?(?:\s*\d+)*)\s*(?:CFA|FCFA)",
            ]:
                m = re.search(pattern, body, re.I)
                if m:
                    prix = m.group(1).strip() + " CFA"
                    break

            # Localisation brute
            localisation = None
            for selector in [
                lambda s: s.find(["span","div","p","a"],
                                  class_=re.compile(r"location|ville|quartier|address|lieu", re.I)),
                lambda s: s.find(["span","div"],
                                  {"itemprop": re.compile(r"address|location", re.I)}),
            ]:
                el = selector(soup)
                if el:
                    localisation = el.get_text(strip=True)
                    break

            # Type offre depuis le titre
            titre_lower = (titre or "").lower()
            if "vente" in titre_lower or "vendre" in titre_lower:
                offre = "vendre"
            elif "location" in titre_lower or "louer" in titre_lower:
                offre = "louer"
            else:
                offre = None

            # Type de bien depuis le titre
            type_bien = None
            for mot, val in [
                ("villa", "Villa"), ("appartement", "Appartement"),
                ("terrain", "Terrain"), ("immeuble", "Immeuble"),
                ("bureau", "Bureau"), ("commerce", "Commerce"),
                ("chambre", "Chambre"), ("studio", "Studio"),
                ("magasin", "Magasin"), ("boutique", "Boutique"),
            ]:
                if mot in titre_lower:
                    type_bien = val
                    break

            # Nombre de pièces depuis le titre
            m = re.search(r"(\d+)\s*(?:pièces?|chambres?)", titre or "", re.I)
            piece = m.group(1) if m else None

            # Surface depuis titre + description
            desc_el = soup.find(["div","p"], class_=re.compile(r"description|detail", re.I))
            desc    = desc_el.get_text(strip=True) if desc_el else ""
            m = re.search(r"(\d+(?:\.\d+)?)\s*(?:m²|m2|lots?)", titre + " " + desc, re.I)
            surface = m.group(1) if m else None

            # Référence depuis l'URL
            m = re.search(r"/annonce/[^/]+/[^/]+-(\d+)", url)
            reference = m.group(1) if m else None

            return {
                "source"      : "CoinAfrique",
                "reference"   : reference,
                "titre"       : titre,
                "offre"       : offre,
                "type_bien"   : type_bien,
                "localisation": localisation,
                "prix"        : prix,
                "piece"       : piece,
                "surface"     : surface,
                "url"         : url,
            }

        except Exception as e:
            log.warning(f"Annonce {url} — erreur : {e}")
            return None

    # ── 3. Scraping complet ───────────────────────────────────────────────────

    def scrape(self) -> list:
        log.info(f"Démarrage scraping CoinAfrique ({self.max_pages} pages)…")
        total = 0

        for page_num in range(1, self.max_pages + 1):
            log.info(f"Page {page_num}/{self.max_pages}…")
            urls = self.get_page_urls(page_num)

            if not urls:
                log.warning(f"Page {page_num} vide — on continue")
                continue

            for url in urls:
                data = self.extract_listing(url)
                if data:
                    self.all_listings.append(data)
                    total += 1

            log.info(f"  Page {page_num} — {len(urls)} annonces | Total : {total}")
            time.sleep(PAGE_DELAY)

        log.info(f" Scraping terminé : {total} annonces")
        return self.all_listings

    # ── 4. Sauvegarde ─────────────────────────────────────────────────────────

    def save(self, path: str = None) -> str:
        if not self.all_listings:
            log.warning("Aucune donnée à sauvegarder.")
            return ""

        if path is None:
            ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = f"data/raw/scraped/coinafrique_{ts}.csv"

        Path(path).parent.mkdir(parents=True, exist_ok=True)
        df = pd.DataFrame(self.all_listings)
        df.to_csv(path, index=False, encoding="utf-8-sig")   # séparateur virgule (standard pipeline)
        log.info(f"💾  Sauvegardé : {path} ({len(df)} lignes)")
        return path

    # ── 5. Pipeline complet ───────────────────────────────────────────────────

    def run(self, output_path: str = None) -> pd.DataFrame:
        """scrape → save."""
        self.scrape()
        self.save(output_path)
        return pd.DataFrame(self.all_listings)


# ─── POINT D'ENTRÉE ──────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Scraper brut CoinAfrique → CSV raw")
    parser.add_argument("--pages",  type=int, default=60,
                        help="Nombre de pages à scraper (défaut: 60)")
    parser.add_argument("--output", type=str, default=None,
                        help="Chemin CSV de sortie")
    args = parser.parse_args()

    scraper = CoinAfriqueScraperTogo(max_pages=args.pages)
    df      = scraper.run(output_path=args.output)

    print(f"\n {len(df)} annonces sauvegardées")
    print(f"Colonnes brutes : {df.columns.tolist()}")
    print(df.head(3).to_string())


if __name__ == "__main__":
    main()