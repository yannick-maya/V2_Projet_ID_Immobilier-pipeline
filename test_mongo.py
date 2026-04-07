import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

uri = os.getenv("MONGO_URI")
db_name = os.getenv("MONGO_DB", "id_immobilier")

if not uri:
    raise RuntimeError("MONGO_URI manquante dans .env")

client = MongoClient(uri, serverSelectionTimeoutMS=10000)
try:
    client.admin.command("ping")
    db = client[db_name]
    collections = db.list_collection_names()
    print("Connexion MongoDB Atlas OK")
    print(f"Base: {db_name}")
    print(f"Collections existantes: {collections}")
finally:
    client.close()
