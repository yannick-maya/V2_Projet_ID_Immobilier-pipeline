import os

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB", "id_immobilier")

if not MONGO_URI:
    raise RuntimeError("MONGO_URI manquante")

client = AsyncIOMotorClient(MONGO_URI)
db = client[MONGO_DB]
