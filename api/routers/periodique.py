from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from datetime import datetime
import pandas as pd

from api.database import db
from api.utils import serialize_doc

router = APIRouter()

@router.get("/test")
async def test_endpoint():
    """Endpoint de test pour vérifier que le routeur fonctionne"""
    return {"message": "Routeur periodique fonctionne", "status": "ok"}

@router.get("/annonces")
async def get_donnees_periodiques_annonces(
    periode: Optional[str] = Query(None, description="Période au format YYYY-MM"),
    zone: Optional[str] = Query(None, description="Zone géographique"),
    type_bien: Optional[str] = Query(None, description="Type de bien"),
    limit: int = Query(100, description="Nombre maximum de résultats")
):
    """
    Récupère les données d'annonces par période
    """
    query = {}

    if periode:
        query["periode"] = periode
    if zone:
        query["zone"] = {"$regex": zone, "$options": "i"}
    if type_bien:
        query["type_bien"] = type_bien

    try:
        cursor = db["annonces"].find(query).limit(limit)
        annonces = []
        async for doc in cursor:
            annonces.append(serialize_doc(doc))

        return {
            "success": True,
            "data": annonces,
            "count": len(annonces),
            "periode": periode,
            "filtres": {
                "zone": zone,
                "type_bien": type_bien
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des données: {str(e)}")

@router.get("/venales")
async def get_donnees_periodiques_venales(
    periode: Optional[str] = Query(None, description="Période au format YYYY-MM"),
    zone: Optional[str] = Query(None, description="Zone géographique"),
    type_bien: Optional[str] = Query(None, description="Type de bien"),
    limit: int = Query(100, description="Nombre maximum de résultats")
):
    """
    Récupère les données vénales (OTR) par période
    """
    query = {}

    if periode:
        query["periode"] = periode
    if zone:
        query["zone"] = {"$regex": zone, "$options": "i"}
    if type_bien:
        query["type_bien"] = type_bien

    try:
        cursor = db["venales"].find(query).limit(limit)
        venales = []
        async for doc in cursor:
            venales.append(serialize_doc(doc))

        return {
            "success": True,
            "data": venales,
            "count": len(venales),
            "periode": periode,
            "filtres": {
                "zone": zone,
                "type_bien": type_bien
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des données vénales: {str(e)}")

@router.get("/comparaison")
async def get_comparaison_periodique(
    periode: Optional[str] = Query(None, description="Période au format YYYY-MM"),
    zone: Optional[str] = Query(None, description="Zone géographique"),
    type_bien: Optional[str] = Query(None, description="Type de bien")
):
    """
    Compare les prix du marché avec les valeurs OTR pour une période donnée
    """
    try:
        # Récupérer les données d'annonces
        query_annonces = {"type_offre": "VENTE"}
        if periode:
            query_annonces["periode"] = periode
        if zone:
            query_annonces["zone"] = {"$regex": zone, "$options": "i"}
        if type_bien:
            query_annonces["type_bien"] = type_bien

        cursor_annonces = db["annonces"].find(query_annonces)
        annonces = []
        async for doc in cursor_annonces:
            annonces.append(serialize_doc(doc))

        # Récupérer les données vénales
        query_venales = {}
        if periode:
            query_venales["periode"] = periode
        if zone:
            query_venales["zone"] = {"$regex": zone, "$options": "i"}
        if type_bien:
            query_venales["type_bien"] = type_bien

        cursor_venales = db["venales"].find(query_venales)
        venales = []
        async for doc in cursor_venales:
            venales.append(serialize_doc(doc))

        # Calculer les statistiques de comparaison
        stats_annonces = {}
        stats_venales = {}

        if annonces:
            df_annonces = pd.DataFrame(annonces)
            if "prix_m2" in df_annonces.columns:
                prix_marche = df_annonces["prix_m2"].dropna()
                if not prix_marche.empty:
                    stats_annonces = {
                        "prix_moyen_m2": float(prix_marche.mean()),
                        "prix_median_m2": float(prix_marche.median()),
                        "prix_min_m2": float(prix_marche.min()),
                        "prix_max_m2": float(prix_marche.max()),
                        "nombre_annonces": len(prix_marche)
                    }

        if venales:
            df_venales = pd.DataFrame(venales)
            if "prix_m2_officiel" in df_venales.columns:
                prix_otr = df_venales["prix_m2_officiel"].dropna()
                if not prix_otr.empty:
                    stats_venales = {
                        "prix_moyen_m2": float(prix_otr.mean()),
                        "prix_median_m2": float(prix_otr.median()),
                        "prix_min_m2": float(prix_otr.min()),
                        "prix_max_m2": float(prix_otr.max()),
                        "nombre_venales": len(prix_otr)
                    }

        # Calculer l'écart si les deux datasets ont des données
        ecart = None
        if stats_annonces and stats_venales:
            ecart_moyen = stats_annonces["prix_moyen_m2"] - stats_venales["prix_moyen_m2"]
            ecart_pourcent = (ecart_moyen / stats_venales["prix_moyen_m2"]) * 100 if stats_venales["prix_moyen_m2"] > 0 else 0
            ecart = {
                "ecart_absolu_m2": float(ecart_moyen),
                "ecart_pourcent": float(ecart_pourcent),
                "interpretation": "surévalué" if ecart_moyen > 0 else "sous-évalué"
            }

        return {
            "success": True,
            "periode": periode,
            "zone": zone,
            "type_bien": type_bien,
            "marche": stats_annonces,
            "otr": stats_venales,
            "comparaison": ecart,
            "details": {
                "annonces_count": len(annonces),
                "venales_count": len(venales)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la comparaison: {str(e)}")

@router.get("/evolution")
async def get_evolution_periodique(
    zone: Optional[str] = Query(None, description="Zone géographique"),
    type_bien: Optional[str] = Query(None, description="Type de bien"),
    limit_periodes: int = Query(12, description="Nombre de périodes récentes à analyser")
):
    """
    Analyse l'évolution des prix sur les dernières périodes
    """
    try:
        # Récupérer les périodes disponibles (triées par date décroissante)
        periodes_pipeline = [
            {"$group": {"_id": "$periode"}},
            {"$sort": {"_id": -1}},
            {"$limit": limit_periodes}
        ]

        periodes_docs = await db["annonces"].aggregate(periodes_pipeline).to_list(length=limit_periodes)
        periodes = [doc["_id"] for doc in periodes_docs if doc["_id"]]

        evolution_data = []

        for periode in sorted(periodes):
            # Données marché
            query_marche = {"periode": periode, "type_offre": "VENTE"}
            if zone:
                query_marche["zone"] = {"$regex": zone, "$options": "i"}
            if type_bien:
                query_marche["type_bien"] = type_bien

            cursor_marche = db["annonces"].find(query_marche)
            annonces = []
            async for doc in cursor_marche:
                annonces.append(serialize_doc(doc))

            # Données OTR
            query_otr = {"periode": periode}
            if zone:
                query_otr["zone"] = {"$regex": zone, "$options": "i"}
            if type_bien:
                query_otr["type_bien"] = type_bien

            cursor_otr = db["venales"].find(query_otr)
            venales = []
            async for doc in cursor_otr:
                venales.append(serialize_doc(doc))

            # Calculer moyennes
            prix_marche_moyen = None
            prix_otr_moyen = None

            if annonces:
                df_annonces = pd.DataFrame(annonces)
                if "prix_m2" in df_annonces.columns:
                    prix_marche = df_annonces["prix_m2"].dropna()
                    if not prix_marche.empty:
                        prix_marche_moyen = float(prix_marche.mean())

            if venales:
                df_venales = pd.DataFrame(venales)
                if "prix_m2_officiel" in df_venales.columns:
                    prix_otr = df_venales["prix_m2_officiel"].dropna()
                    if not prix_otr.empty:
                        prix_otr_moyen = float(prix_otr.mean())

            evolution_data.append({
                "periode": periode,
                "prix_marche_moyen_m2": prix_marche_moyen,
                "prix_otr_moyen_m2": prix_otr_moyen,
                "nombre_annonces": len(annonces),
                "nombre_venales": len(venales)
            })

        return {
            "success": True,
            "zone": zone,
            "type_bien": type_bien,
            "evolution": evolution_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'analyse d'évolution: {str(e)}")