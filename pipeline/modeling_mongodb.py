"""
Phase 3 - Modelisation MongoDB
Insertion des annonces nettoyees dans MongoDB avec upsert et index.
"""

from __future__ import annotations

import os
import glob
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional, Tuple

import pandas as pd
from dotenv import load_dotenv
from pymongo import ASCENDING, MongoClient, UpdateOne

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEANED_DIR = os.path.join(BASE_DIR, "data", "cleaned_v2")

BATCH_SIZE = 500


def _to_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        if str(value).strip() == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _to_int(value: Any) -> Optional[int]:
    f = _to_float(value)
    if f is None:
        return None
    try:
        return int(f)
    except (TypeError, ValueError):
        return None


def _to_clean_str(value: Any, upper: bool = False, lower: bool = False) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    if upper:
        return text.upper()
    if lower:
        return text.lower()
    return text


def _derive_period_fields(date_annonce: Optional[str]) -> Tuple[Optional[str], Optional[int], Optional[int]]:
    if not date_annonce:
        return None, None, None
    try:
        parsed = datetime.fromisoformat(date_annonce.replace("Z", "+00:00"))
        year = parsed.year
        quarter = ((parsed.month - 1) // 3) + 1
        period = f"{year}-Q{quarter}"
        return period, year, quarter
    except ValueError:
        return None, None, None


def _build_localisation(row: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    localisation = row.get("localisation")
    if isinstance(localisation, dict):
        if localisation.get("type") == "Point" and isinstance(localisation.get("coordinates"), list):
            return localisation

    lon_keys = ["longitude", "lon", "lng", "x"]
    lat_keys = ["latitude", "lat", "y"]

    lon = None
    lat = None
    for key in lon_keys:
        lon = _to_float(row.get(key))
        if lon is not None:
            break
    for key in lat_keys:
        lat = _to_float(row.get(key))
        if lat is not None:
            break

    if lon is None or lat is None:
        return None
    if not (-180 <= lon <= 180 and -90 <= lat <= 90):
        return None

    return {"type": "Point", "coordinates": [lon, lat]}


def get_mongo():
    mongo_uri = os.getenv("MONGO_URI")
    mongo_db = os.getenv("MONGO_DB", "id_immobilier")

    if not mongo_uri:
        raise RuntimeError("Variable d'environnement MONGO_URI manquante.")

    client = MongoClient(mongo_uri)
    db = client[mongo_db]
    return client, db


def create_indexes(annonces_collection) -> None:
    annonces_collection.create_index([("zone", ASCENDING)], name="idx_zone")
    annonces_collection.create_index([("type_bien", ASCENDING)], name="idx_type_bien")
    annonces_collection.create_index([("periode", ASCENDING)], name="idx_periode")
    annonces_collection.create_index([("localisation", "2dsphere")], name="idx_localisation_2dsphere")


def _row_to_document(row: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    titre = _to_clean_str(row.get("titre"))
    zone = _to_clean_str(row.get("zone"))
    prix = _to_float(row.get("prix"))

    # Cle d'upsert minimale requise
    if not titre or not zone or prix is None:
        return None

    date_annonce = _to_clean_str(row.get("date_annonce"))
    periode = _to_clean_str(row.get("periode"))
    annee = _to_int(row.get("annee"))
    trimestre = _to_int(row.get("trimestre"))

    if not (periode and annee and trimestre):
        p, y, t = _derive_period_fields(date_annonce)
        periode = periode or p
        annee = annee or y
        trimestre = trimestre or t

    surface_m2 = _to_float(row.get("surface_m2"))
    prix_m2 = _to_float(row.get("prix_m2"))
    if prix_m2 is None and surface_m2 and surface_m2 > 0:
        prix_m2 = round(prix / surface_m2, 2)

    document = {
        "titre": titre,
        "prix": prix,
        "prix_m2": prix_m2,
        "surface_m2": surface_m2,
        "type_bien": _to_clean_str(row.get("type_bien")),
        "type_offre": _to_clean_str(row.get("type_offre"), upper=True),
        "zone": zone,
        "source": _to_clean_str(row.get("source"), lower=True),
        "periode": periode,
        "annee": annee,
        "trimestre": trimestre,
        "date_annonce": date_annonce,
    }

    localisation = _build_localisation(row)
    if localisation is not None:
        document["localisation"] = localisation

    # Nettoyage des champs None
    return {k: v for k, v in document.items() if v is not None}


def _flush_batch(annonces_collection, ops: List[UpdateOne]) -> Tuple[int, int, int]:
    if not ops:
        return 0, 0, 0
    result = annonces_collection.bulk_write(ops, ordered=False)
    inserted = result.upserted_count
    updated = result.modified_count
    matched = result.matched_count
    return inserted, updated, matched


def _iter_input_rows(dataset: Any):
    # Spark DataFrame
    if hasattr(dataset, "toLocalIterator"):
        for row in dataset.toLocalIterator():
            yield row.asDict(recursive=True)
        return

    # Pandas DataFrame
    if isinstance(dataset, pd.DataFrame):
        for _, row in dataset.iterrows():
            yield row.to_dict()
        return

    # Iterable de dicts
    for row in dataset:
        yield row


def insert_annonces(dataset, db) -> Dict[str, int]:
    """
    Insere les annonces via upsert batch.
    Cle d'unicite logique: titre + prix + zone
    """
    annonces_collection = db["annonces"]
    create_indexes(annonces_collection)

    total_processed = 0
    total_skipped = 0
    total_inserted = 0
    total_updated = 0
    total_matched = 0
    operations: List[UpdateOne] = []

    for row in _iter_input_rows(dataset):
        total_processed += 1
        doc = _row_to_document(row)
        if doc is None:
            total_skipped += 1
            continue

        now_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        filter_query = {
            "titre": doc["titre"],
            "prix": doc["prix"],
            "zone": doc["zone"],
        }

        operations.append(
            UpdateOne(
                filter_query,
                {
                    "$set": doc,
                    "$setOnInsert": {"created_at": now_iso},
                },
                upsert=True,
            )
        )

        if len(operations) >= BATCH_SIZE:
            inserted, updated, matched = _flush_batch(annonces_collection, operations)
            total_inserted += inserted
            total_updated += updated
            total_matched += matched
            operations = []

    inserted, updated, matched = _flush_batch(annonces_collection, operations)
    total_inserted += inserted
    total_updated += updated
    total_matched += matched

    logs = {
        "processed": total_processed,
        "skipped": total_skipped,
        "inserted": total_inserted,
        "updated": total_updated,
        "matched_existing": total_matched,
    }
    return logs


def _load_cleaned_annonces_spark():
    from pyspark.sql import SparkSession

    spark = SparkSession.builder.appName("IDImmobilier-Modeling-MongoDB").getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")

    annonces_pandas_csv = os.path.join(CLEANED_DIR, "annonces_clean.csv")
    annonces_spark_dir = os.path.join(CLEANED_DIR, "annonces")

    if os.path.exists(annonces_pandas_csv):
        df = spark.read.csv(annonces_pandas_csv, header=True, inferSchema=True)
        source_hint = annonces_pandas_csv
        total_rows = df.count()
    elif os.path.exists(annonces_spark_dir):
        df = spark.read.csv(annonces_spark_dir, header=True, inferSchema=True)
        source_hint = annonces_spark_dir
        total_rows = df.count()
    else:
        spark.stop()
        raise FileNotFoundError(
            "Aucun fichier d'annonces nettoyees trouve. "
            "Lance d'abord le cleaning (ex: python pipeline/cleaning_v2_spark.py)."
        )

    return spark, df, source_hint, total_rows


def _load_cleaned_annonces_local():
    annonces_pandas_csv = os.path.join(CLEANED_DIR, "annonces_clean.csv")
    annonces_spark_dir = os.path.join(CLEANED_DIR, "annonces")

    if os.path.exists(annonces_pandas_csv):
        df = pd.read_csv(annonces_pandas_csv, low_memory=False)
        return df, annonces_pandas_csv, len(df)

    part_files = glob.glob(os.path.join(annonces_spark_dir, "part-*.csv"))
    if part_files:
        df = pd.concat([pd.read_csv(f, low_memory=False) for f in part_files], ignore_index=True)
        return df, f"{annonces_spark_dir} ({len(part_files)} part files)", len(df)

    raise FileNotFoundError(
        "Aucun fichier d'annonces nettoyees trouve. "
        "Lance d'abord: python pipeline/cleaning_V2.py (local) "
        "ou python pipeline/cleaning_pyspark_v2.py (Spark)."
    )


def _load_cleaned_annonces_auto():
    use_spark = os.getenv("USE_SPARK", "auto").strip().lower()

    # Forcer local
    if use_spark in {"0", "false", "no", "local"}:
        dataset, source_hint, total_rows = _load_cleaned_annonces_local()
        return None, dataset, source_hint, total_rows, "pandas"

    # Auto / Spark: tente Spark puis fallback local
    if use_spark in {"1", "true", "yes", "spark", "auto"}:
        try:
            spark, dataset, source_hint, total_rows = _load_cleaned_annonces_spark()
            return spark, dataset, source_hint, total_rows, "spark"
        except ModuleNotFoundError:
            dataset, source_hint, total_rows = _load_cleaned_annonces_local()
            return None, dataset, source_hint, total_rows, "pandas"

    # Valeur inconnue => fallback local
    dataset, source_hint, total_rows = _load_cleaned_annonces_local()
    return None, dataset, source_hint, total_rows, "pandas"


def run() -> None:
    print("Connexion a MongoDB...")
    client, db = get_mongo()
    spark = None
    try:
        spark, dataset, source_hint, total_rows, engine = _load_cleaned_annonces_auto()
        print(f"Mode de chargement      : {engine}")
        print(f"Donnees chargees depuis : {source_hint}")
        print(f"Nombre de lignes        : {total_rows}")

        logs = insert_annonces(dataset, db)

        print("Insertion MongoDB terminee.")
        print(f"  Traitees         : {logs['processed']}")
        print(f"  Ignorees         : {logs['skipped']}")
        print(f"  Inserees         : {logs['inserted']}")
        print(f"  Mises a jour     : {logs['updated']}")
        print(f"  Deja existantes  : {logs['matched_existing']}")
    finally:
        if spark is not None:
            spark.stop()
        client.close()


if __name__ == "__main__":
    run()
