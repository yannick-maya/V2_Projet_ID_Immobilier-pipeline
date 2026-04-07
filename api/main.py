import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.database import db
from api.routers.admin import router as admin_router
from api.routers.annonces import router as annonces_router
from api.routers.auth import router as auth_router
from api.routers.favoris import router as favoris_router
from api.routers.indice import router as indice_router
from api.routers.scoring import router as scoring_router
from api.routers.statistiques import router as stats_router

app = FastAPI(
    title="ID Immobilier API",
    description="API de la plateforme de données immobilières du Togo",
    version="2.0.0",
)

cors_origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000,http://127.0.0.1:3001",
)
allow_origins = [origin.strip() for origin in cors_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_indexes():
    await db["annonces"].create_index([("titre", "text"), ("description", "text")], name="idx_text_annonces")
    await db["annonces"].create_index([("zone", 1)], name="idx_zone")
    await db["annonces"].create_index([("type_bien", 1)], name="idx_type_bien")
    await db["annonces"].create_index([("periode", 1)], name="idx_periode")
    await db["annonces"].create_index([("localisation", "2dsphere")], name="idx_localisation_2dsphere")


@app.get("/")
async def health():
    return {"service": "id-immobilier-api", "status": "ok"}


app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(annonces_router, prefix="/annonces", tags=["Annonces"])
app.include_router(stats_router, prefix="/statistiques", tags=["Statistiques"])
app.include_router(indice_router, prefix="/indice", tags=["Indice"])
app.include_router(scoring_router, prefix="/scoring", tags=["Scoring"])
app.include_router(favoris_router, prefix="/favoris", tags=["Favoris"])
app.include_router(admin_router, prefix="/admin", tags=["Admin"])
