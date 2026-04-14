"""
Dashboard Streamlit - ID Immobilier
Indice Intelligent du Marche Immobilier au Togo
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
import mysql.connector
import unicodedata
import re
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="ID Immobilier - Togo",
    page_icon="🏠",
    layout="wide"
)

# ── Connexion MySQL ────────────────────────────────────────────────────────────
@st.cache_resource
def get_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DB", "id_immobilier"),
        buffered=True
    )

def run_query(query):
    conn = get_connection()
    return pd.read_sql(query, conn)

@st.cache_data(ttl=3600)
def load_statistiques():
    return run_query("""
        SELECT s.*, z.nom AS zone_nom
        FROM statistiques_zone s
        JOIN zone_geographique z ON s.id_zone = z.id
    """)

@st.cache_data(ttl=3600)
def load_annonces():
    return run_query("""
        SELECT a.prix, a.prix_m2, a.titre,
               b.type_bien, b.type_offre, b.surface_m2,
               z.nom AS zone,
               s.nom AS source
        FROM annonce a
        JOIN bien_immobilier b ON a.id_bien = b.id
        JOIN zone_geographique z ON b.id_zone = z.id
        JOIN source_donnees s ON a.id_source = s.id
        WHERE a.prix_m2 IS NOT NULL AND a.prix_m2 > 0
    """)

@st.cache_data(ttl=3600)
def load_venales():
    return run_query("""
        SELECT vv.prix_m2_officiel, vv.surface_m2, vv.valeur_totale,
               z.nom AS zone
        FROM valeur_venale vv
        JOIN zone_geographique z ON vv.id_zone = z.id
        WHERE vv.prix_m2_officiel IS NOT NULL
    """)

@st.cache_data(ttl=3600)
def load_comparaison_otr_marche():
    """Charge les données pour comparer prix marché vs prix OTR"""
    return run_query("""
        SELECT
            a.prix_m2 as prix_marche_m2,
            vv.prix_m2_officiel as prix_otr_m2,
            (a.prix_m2 - vv.prix_m2_officiel) as ecart_absolu,
            ((a.prix_m2 - vv.prix_m2_officiel) / vv.prix_m2_officiel * 100) as ecart_pourcent,
            CASE
                WHEN (a.prix_m2 - vv.prix_m2_officiel) / vv.prix_m2_officiel > 0.20 THEN 'Surévalué (>20%)'
                WHEN (a.prix_m2 - vv.prix_m2_officiel) / vv.prix_m2_officiel < -0.20 THEN 'Sous-évalué (<-20%)'
                ELSE 'Conforme (±20%)'
            END as statut_evaluation,
            b.type_bien,
            z.nom as zone,
            a.titre
        FROM annonce a
        JOIN bien_immobilier b ON a.id_bien = b.id
        JOIN zone_geographique z ON b.id_zone = z.id
        LEFT JOIN valeur_venale vv ON vv.id_zone = z.id
        WHERE a.prix_m2 IS NOT NULL
        AND vv.prix_m2_officiel IS NOT NULL
        AND a.prix_m2 > 0
        ORDER BY ecart_pourcent DESC
    """)

@st.cache_data(ttl=3600)
def load_evolution_prix():
    """Charge l'évolution des prix par période"""
    return run_query("""
        SELECT
            DATE_FORMAT(a.date_annonce, '%Y-%m') as periode,
            AVG(a.prix_m2) as prix_marche_moyen,
            AVG(vv.prix_m2_officiel) as prix_otr_moyen,
            COUNT(a.id) as nb_annonces,
            b.type_bien,
            z.nom as zone
        FROM annonce a
        JOIN bien_immobilier b ON a.id_bien = b.id
        JOIN zone_geographique z ON b.id_zone = z.id
        LEFT JOIN valeur_venale vv ON vv.id_zone = z.id
        WHERE a.prix_m2 IS NOT NULL AND a.date_annonce IS NOT NULL
        GROUP BY DATE_FORMAT(a.date_annonce, '%Y-%m'), b.type_bien, z.nom
        ORDER BY periode DESC, zone, type_bien
    """)

@st.cache_data(ttl=3600)
def load_sources():
    return run_query("""
        SELECT s.nom AS source, COUNT(a.id) AS nombre_annonces
        FROM source_donnees s
        LEFT JOIN annonce a ON a.id_source = s.id
        GROUP BY s.id, s.nom
        ORDER BY nombre_annonces DESC
    """)

@st.cache_data(ttl=3600)
def load_indice_par_type():
    return run_query("""
        SELECT
            b.type_bien,
            b.type_offre,
            z.nom AS zone_nom,
            AVG(a.prix_m2) AS prix_moyen_m2,
            COUNT(a.id) AS nb_annonces
        FROM annonce a
        JOIN bien_immobilier b ON a.id_bien = b.id
        JOIN zone_geographique z ON b.id_zone = z.id
        WHERE a.prix_m2 IS NOT NULL AND a.prix_m2 > 0
        GROUP BY b.type_bien, b.type_offre, z.nom
        HAVING COUNT(a.id) >= 2
        ORDER BY prix_moyen_m2 DESC
    """)

@st.cache_data(ttl=3600)
def load_indice_carte():
    """
    Charge les vraies tendances (HAUSSE / STABLE / BAISSE) depuis
    la table indice_immobilier calculée par index.py.
    On agrège par zone pour avoir un seul point par zone sur la carte.
    """
    return run_query("""
        SELECT
            z.nom                       AS zone_nom,
            AVG(i.prix_moyen_m2)        AS prix_moyen_m2,
            AVG(i.indice_valeur)        AS indice_valeur,
            (
                SELECT ii2.tendance
                FROM indice_immobilier ii2
                WHERE ii2.id_zone = i.id_zone
                GROUP BY ii2.tendance
                ORDER BY COUNT(*) DESC
                LIMIT 1
            )                           AS tendance,
            COUNT(*)                    AS nb_indices
        FROM indice_immobilier i
        JOIN zone_geographique z ON i.id_zone = z.id
        GROUP BY i.id_zone, z.nom
        ORDER BY indice_valeur DESC
    """)


# ═══════════════════════════════════════════════════════════════════════════════
# COORDONNÉES GPS — Quartiers de Lomé et villes du Togo
# Source : OpenStreetMap / Relevés terrain
# Format : "nom_normalisé": [latitude, longitude]
# ═══════════════════════════════════════════════════════════════════════════════

COORDS_TOGO = {
    # ── CENTRE DE LOMÉ ──────────────────────────────────────────────────────
    "lome":                 [6.1375,  1.2123],
    "lome centre":          [6.1375,  1.2123],
    "centre ville":         [6.1375,  1.2123],
    "grand marche":         [6.1350,  1.2200],
    "marche":               [6.1350,  1.2200],
    "port":                 [6.1270,  1.2150],

    # ── QUARTIERS NORD ───────────────────────────────────────────────────────
    "agoe":                 [6.1950,  1.2220],
    "agoe nyive":           [6.1950,  1.2220],
    "agoe assiyeye":        [6.2050,  1.2150],
    "agoe cacaveli":        [6.1850,  1.2400],
    "agoe demakpoe":        [6.2100,  1.2050],
    "agoe zongo":           [6.2000,  1.2200],
    "agoe logopoe":         [6.2150,  1.2100],
    "adetikope":            [6.2400,  1.1850],
    "togblekope":           [6.2200,  1.1950],
    "kpogan":               [6.2300,  1.2000],
    "sagbado":              [6.1900,  1.2150],
    "gbossime":             [6.1850,  1.2100],
    "avedji":               [6.1780,  1.2180],
    "avenu":                [6.1700,  1.2300],
    "aveno":                [6.1700,  1.2300],
    "avenou":               [6.1700,  1.2300],
    "lege":                 [6.1750,  1.2350],
    "legbassito":           [6.1750,  1.2400],
    "adidogome":            [6.1700,  1.1900],
    "adidogome assiyeye":   [6.1750,  1.1850],
    "adidogome baguida":    [6.1650,  1.1950],
    "gbedome":              [6.1800,  1.1950],
    "doulassame":           [6.1580,  1.2200],
    "doulasame":            [6.1580,  1.2200],
    "assiyeye":             [6.1800,  1.2000],

    # ── QUARTIERS NORD-OUEST ─────────────────────────────────────────────────
    "djidjole":             [6.1600,  1.1900],
    "cassablanca":          [6.1550,  1.1800],
    "casablanca":           [6.1550,  1.1800],
    "assivito":             [6.1500,  1.1950],
    "kegue":                [6.1500,  1.2400],
    "nukafu":               [6.1600,  1.2480],
    "zanguera":             [6.1650,  1.2500],
    "zanguera nord":        [6.1700,  1.2520],

    # ── QUARTIERS CENTRE-NORD ────────────────────────────────────────────────
    "tokoin":               [6.1520,  1.2100],
    "tokoin hopital":       [6.1480,  1.2150],
    "tokoin forever":       [6.1560,  1.2080],
    "tokoin tameta":        [6.1540,  1.2050],
    "tokoin nord":          [6.1560,  1.2100],
    "tokoin est":           [6.1520,  1.2200],
    "tokoin ouest":         [6.1520,  1.2000],
    "hedzranawoe":          [6.1430,  1.2180],
    "hedzranawo":           [6.1430,  1.2180],
    "hedranawe":            [6.1430,  1.2180],
    "amoutive":             [6.1400,  1.2050],
    "amoutive nord":        [6.1430,  1.2050],
    "amoutive sud":         [6.1380,  1.2050],
    "nyekonakpoe":          [6.1450,  1.2250],
    "nyekonakpoe nord":     [6.1480,  1.2250],
    "nyekonakpoe sud":      [6.1420,  1.2250],

    # ── QUARTIERS CENTRE ─────────────────────────────────────────────────────
    "be":                   [6.1320,  1.2300],
    "be kpota":             [6.1280,  1.2350],
    "be apeyeme":           [6.1350,  1.2350],
    "be klikame":           [6.1300,  1.2400],
    "be ouest":             [6.1320,  1.2250],
    "be nord":              [6.1370,  1.2300],
    "cacaveli":             [6.1550,  1.2650],
    "cacaveli nord":        [6.1600,  1.2650],
    "cacaveli sud":         [6.1500,  1.2650],
    "baguida":              [6.1167,  1.3500],
    "baguida nord":         [6.1200,  1.3450],
    "baguida village":      [6.1150,  1.3550],

    # ── QUARTIERS SUD-OUEST ──────────────────────────────────────────────────
    "ablogame":             [6.1280,  1.2050],
    "ablogame nord":        [6.1310,  1.2050],
    "kodjoviakope":         [6.1180,  1.2100],
    "kodjoviakope nord":    [6.1210,  1.2100],
    "aflao gare":           [6.1080,  1.1950],
    "aflao":                [6.1080,  1.1950],
    "gbenyedzi":            [6.1150,  1.2200],
    "gbenye":               [6.1150,  1.2200],
    "attiegan":             [6.1200,  1.2000],
    "attiegann":            [6.1200,  1.2000],
    "akodessewa":           [6.1250,  1.2600],
    "akodesewa":            [6.1250,  1.2600],
    "akodesewa nord":       [6.1280,  1.2600],
    "zebe":                 [6.1180,  1.2500],
    "apeyeme":              [6.1350,  1.2380],
    "bionkoli":             [6.1220,  1.2300],
    "dekon":                [6.1300,  1.2150],
    "dekon nord":           [6.1330,  1.2150],
    "kpota":                [6.1280,  1.2350],
    "kpota nord":           [6.1310,  1.2350],
    "katanga":              [6.1350,  1.2120],
    "bamelie":              [6.1400,  1.2300],
    "bamelie nord":         [6.1430,  1.2300],
    "adawlato":             [6.1460,  1.2180],
    "legoun":               [6.1550,  1.2300],
    "legon":                [6.1550,  1.2300],
    "totsi":                [6.1500,  1.2250],
    "assomè":               [6.1420,  1.2400],
    "assome":               [6.1420,  1.2400],
    "gbagba":               [6.1380,  1.2450],
    "ahanoukope":           [6.1600,  1.1800],
    "ahanoukopé":           [6.1600,  1.1800],
    "wuiti":                [6.1650,  1.2100],
    "wuite":                [6.1650,  1.2100],
    "sogbossito":           [6.1500,  1.2600],
    "sogbossito nord":      [6.1530,  1.2600],
    "sito":                 [6.1500,  1.2600],
    "atikoume":             [6.1350,  1.2000],
    "atikoumé":             [6.1350,  1.2000],
    "atikoume nord":        [6.1380,  1.2000],

    # ── ZONE AÉROPORT / EST ───────────────────────────────────────────────────
    "aeroport":             [6.1657,  1.2545],
    "aeroport nord":        [6.1700,  1.2545],
    "tokoin aeroport":      [6.1600,  1.2500],
    "tokoin aéroport":      [6.1600,  1.2500],
    "tsiame":               [6.1700,  1.2600],
    "amegame":              [6.1450,  1.2650],
    "amégame":              [6.1450,  1.2650],

    # ── ZONE CÔTIÈRE EST ─────────────────────────────────────────────────────
    "cinkasse":             [6.1050,  1.2800],
    "avepozo":              [6.1000,  1.3000],
    "avepozo nord":         [6.1050,  1.3000],
    "agbalepedogan":        [6.1100,  1.3200],
    "agbalepedo":           [6.1100,  1.3200],
    "kpogan sud":           [6.1050,  1.3500],
    "gbetsogo":             [6.1150,  1.3300],

    # ── AUTRES PRÉFECTURES DE LOMÉ ────────────────────────────────────────────
    "golfe 1":              [6.1375,  1.2123],
    "golfe 2":              [6.1450,  1.2050],
    "golfe 3":              [6.1550,  1.2050],
    "golfe 4":              [6.1650,  1.2000],
    "golfe 5":              [6.1750,  1.2050],
    "golfe 6":              [6.1850,  1.2100],
    "golfe 7":              [6.1950,  1.2200],

    # ── VILLES DU TOGO ────────────────────────────────────────────────────────
    "kara":                 [9.5508,  1.1860],
    "kara centre":          [9.5508,  1.1860],
    "atakpame":             [7.5333,  1.1333],
    "atakpamé":             [7.5333,  1.1333],
    "sokode":               [8.9833,  1.1333],
    "sokodé":               [8.9833,  1.1333],
    "dapaong":              [10.8667, 0.2000],
    "tsevie":               [6.4233,  1.2139],
    "tsévié":               [6.4233,  1.2139],
    "notse":                [6.9500,  1.1667],
    "notsé":                [6.9500,  1.1667],
    "vogan":                [6.3000,  1.5500],
    "aneho":                [6.2333,  1.5967],
    "aného":                [6.2333,  1.5967],
    "tabligbo":             [6.5833,  1.5000],
    "kpalime":              [6.9000,  0.6333],
    "kpalimé":              [6.9000,  0.6333],
    "badou":                [7.5833,  0.5833],
    "kante":                [9.9500,  1.3667],
    "kanté":                [9.9500,  1.3667],
    "bassar":               [9.2500,  0.7833],
    "mango":                [10.3667, 0.4667],
    "blitta":               [8.3167,  0.9833],
    "tchamba":              [9.0333,  1.4167],
    "sotouboua":            [8.5667,  0.9833],
    "akloa":                [6.9833,  0.5833],
    "agou":                 [6.8167,  0.6667],
    "kouve":                [6.7333,  0.7333],

    # ── ZONES PÉRIURBAINES ────────────────────────────────────────────────────
    "vakpossito":           [6.2500,  1.2000],
    "zio":                  [6.3000,  1.1500],
    "agu":                  [6.3500,  1.1500],
    "gboto":                [6.3000,  1.2000],
    "kovie":                [6.2700,  1.2300],
    "kovié":                [6.2700,  1.2300],
    "gblainvie":            [6.2600,  1.2100],
}


def normalize(name: str) -> str:
    """Normalise un nom de zone : minuscule, sans accents, sans ponctuation."""
    if not isinstance(name, str):
        return ""
    # Minuscule
    name = name.lower().strip()
    # Supprimer accents
    name = unicodedata.normalize("NFD", name)
    name = "".join(c for c in name if unicodedata.category(c) != "Mn")
    # Supprimer ponctuation sauf tirets/espaces
    name = re.sub(r"[^\w\s-]", "", name)
    # Normaliser espaces multiples
    name = re.sub(r"\s+", " ", name).strip()
    return name


def get_coords(zone_name: str):
    """
    Cherche les coordonnées GPS d'une zone.
    Stratégie :
      1. Correspondance exacte après normalisation
      2. Correspondance partielle (la zone contient un nom connu)
      3. Correspondance inverse (un nom connu est contenu dans la zone)
      4. None si rien trouvé
    """
    key = normalize(zone_name)
    if not key:
        return None

    # 1. Correspondance exacte
    if key in COORDS_TOGO:
        return COORDS_TOGO[key]

    # 2. La zone contient un nom connu (ex: "Adidogomé Extension" → "adidogome")
    for ref_key, coords in COORDS_TOGO.items():
        if ref_key in key:
            return coords

    # 3. Un nom connu est contenu dans la zone (ex: "Lomé Tokoin" → "tokoin")
    for ref_key, coords in COORDS_TOGO.items():
        if key in ref_key:
            return coords

    # 4. Mots en commun (≥ 2 mots correspondants)
    key_words = set(key.split())
    best_match = None
    best_score = 0
    for ref_key, coords in COORDS_TOGO.items():
        ref_words = set(ref_key.split())
        common = len(key_words & ref_words)
        if common > best_score and common >= 2:
            best_score = common
            best_match = coords
    if best_match:
        return best_match

    return None


# ══════════════════════════════════════════════════════════════════════════════
# NAVIGATION — sélecteur de page dans la sidebar
# ══════════════════════════════════════════════════════════════════════════════
st.sidebar.title("ID Immobilier")
page = st.sidebar.radio(
    "Navigation",
    ["Tableau de bord", "Toutes les annonces"],
    index=0
)
st.sidebar.divider()

# ── Chargement des données (commun aux deux pages) ─────────────────────────────
try:
    df_stats    = load_statistiques()
    df_annonces = load_annonces()
    df_venales  = load_venales()
    df_sources  = load_sources()
    df_indice   = load_indice_par_type()
except Exception as e:
    st.error(f"Erreur de connexion MySQL : {e}")
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — TABLEAU DE BORD
# ══════════════════════════════════════════════════════════════════════════════
if page == "Tableau de bord":

    st.title("ID Immobilier — Indice Intelligent du Marche Immobilier au Togo")
    st.markdown("**Donnees : ImmoAsk · Facebook · CoinAfrique · Valeurs Venales OTR**")
    st.divider()

    # Filtres sidebar
    st.sidebar.subheader("Filtres")
    zones_dispo = sorted(df_stats["zone_nom"].unique().tolist())
    zone_sel = st.sidebar.selectbox("Zone", ["Toutes"] + zones_dispo)

    types_bien = sorted(df_stats["type_bien"].unique().tolist())
    type_sel = st.sidebar.multiselect("Type de bien", types_bien, default=types_bien)
    if not type_sel:
        type_sel = types_bien

    offre_sel = st.sidebar.radio("Type d'offre", ["Tous", "VENTE", "LOCATION"])

    # Filtrage
    df_f   = df_stats.copy()
    df_ann = df_annonces.copy()
    df_ind = df_indice.copy()

    if zone_sel != "Toutes":
        df_f   = df_f[df_f["zone_nom"] == zone_sel]
        df_ann = df_ann[df_ann["zone"] == zone_sel]
        df_ind = df_ind[df_ind["zone_nom"] == zone_sel]
    df_f   = df_f[df_f["type_bien"].isin(type_sel)]
    df_ann = df_ann[df_ann["type_bien"].isin(type_sel)]
    df_ind = df_ind[df_ind["type_bien"].isin(type_sel)]
    if offre_sel != "Tous":
        df_f   = df_f[df_f["type_offre"] == offre_sel]
        df_ann = df_ann[df_ann["type_offre"] == offre_sel]
        df_ind = df_ind[df_ind["type_offre"] == offre_sel]

    # KPIs
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Prix moyen / m2",    f"{df_f['prix_moyen_m2'].mean():,.0f} FCFA")
    k2.metric("Prix median / m2",   f"{df_f['prix_median_m2'].median():,.0f} FCFA")
    k3.metric("Annonces analysees", f"{df_f['nombre_annonces'].sum():,}")
    k4.metric("Zones couvertes",    f"{df_f['zone_nom'].nunique()}")
    k5.metric("Biens uniques",      f"{len(df_ann):,}")
    st.divider()

    # Sources
    st.subheader("Annonces par source de donnees")
    cs1, cs2 = st.columns([1, 2])
    with cs1:
        st.dataframe(df_sources, use_container_width=True, hide_index=True)
    with cs2:
        fig_src = px.pie(df_sources, values="nombre_annonces", names="source",
                         color_discrete_sequence=px.colors.qualitative.Set2,
                         title="Repartition par source")
        fig_src.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig_src, use_container_width=True)
    st.divider()

    # Top 20 zones
    st.subheader("Prix moyen au m2 par zone")
    df_bar = df_f.groupby("zone_nom")["prix_moyen_m2"].mean().reset_index()
    df_bar = df_bar.sort_values("prix_moyen_m2", ascending=True).tail(20)
    fig_bar = px.bar(df_bar, x="prix_moyen_m2", y="zone_nom", orientation="h",
                     color="prix_moyen_m2", color_continuous_scale="Oranges",
                     labels={"prix_moyen_m2": "Prix moyen / m2 (FCFA)", "zone_nom": "Zone"},
                     title="Top 20 zones — Prix moyen au m2")
    st.plotly_chart(fig_bar, use_container_width=True)
    st.divider()

    # Distribution
    st.subheader("Distribution des prix au m2")
    p95 = df_ann["prix_m2"].quantile(0.95)
    fig_hist = px.histogram(
        df_ann[df_ann["prix_m2"] <= p95], x="prix_m2", nbins=50,
        color="type_offre" if offre_sel == "Tous" else None,
        labels={"prix_m2": "Prix au m2 (FCFA)"},
        title="Distribution des prix au m2 (valeurs aberrantes exclues)",
        color_discrete_map={"VENTE": "#E67E22", "LOCATION": "#2980B9"}
    )
    fig_hist.update_layout(bargap=0.1)
    st.plotly_chart(fig_hist, use_container_width=True)
    st.divider()

    # Comparaison marche vs venales
    st.subheader("Prix Marche vs Valeurs Venales OTR")
    if not df_venales.empty:
        marche = df_ann.groupby("zone")["prix_m2"].mean().reset_index()
        marche.columns = ["zone", "prix_marche"]
        venales = df_venales.groupby("zone")["prix_m2_officiel"].mean().reset_index()
        venales.columns = ["zone", "prix_venale"]
        df_comp = marche.merge(venales, on="zone").sort_values("prix_marche", ascending=False).head(15)
        if not df_comp.empty:
            fig_comp = go.Figure([
                go.Bar(name="Prix Marche",  x=df_comp["zone"], y=df_comp["prix_marche"],  marker_color="#E67E22"),
                go.Bar(name="Valeur Venale", x=df_comp["zone"], y=df_comp["prix_venale"], marker_color="#2ECC71"),
            ])
            fig_comp.update_layout(barmode="group", title="Marche vs OTR (FCFA/m2)",
                                   legend=dict(orientation="h", yanchor="bottom", y=1.02))
            st.plotly_chart(fig_comp, use_container_width=True)
        else:
            st.info("Pas de zones en commun pour la comparaison.")
    else:
        st.info("Valeurs venales non disponibles.")
    st.divider()

    # Section Comparaison OTR vs Marché détaillée
    st.subheader("📊 Analyse Détaillée : Marché vs Valeurs OTR")

    # Charger les données de comparaison
    try:
        df_comparaison = load_comparaison_otr_marche()
        df_evolution = load_evolution_prix()

        if not df_comparaison.empty:
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### Distribution des Écarts OTR")
                fig_ecarts = px.histogram(
                    df_comparaison,
                    x="ecart_pourcent",
                    nbins=20,
                    color="statut_evaluation",
                    color_discrete_map={
                        "Surévalué (>20%)": "#E74C3C",
                        "Sous-évalué (<-20%)": "#27AE60",
                        "Conforme (±20%)": "#F39C12"
                    },
                    labels={"ecart_pourcent": "Écart par rapport à OTR (%)", "count": "Nombre d'annonces"},
                    title="Répartition des écarts prix marché / OTR"
                )
                st.plotly_chart(fig_ecarts, use_container_width=True)

            with col2:
                st.markdown("#### Écarts par Zone")
                df_zone_ecart = df_comparaison.groupby("zone").agg({
                    "ecart_pourcent": "mean",
                    "prix_marche_m2": "count"
                }).reset_index()
                df_zone_ecart.columns = ["zone", "ecart_moyen_pourcent", "nombre_annonces"]
                df_zone_ecart = df_zone_ecart.sort_values("ecart_moyen_pourcent", ascending=False).head(10)

                fig_zone = px.bar(
                    df_zone_ecart,
                    x="zone",
                    y="ecart_moyen_pourcent",
                    color="ecart_moyen_pourcent",
                    color_continuous_scale=["green", "yellow", "red"],
                    labels={"ecart_moyen_pourcent": "Écart moyen (%)", "zone": "Zone"},
                    title="Écart moyen par zone (Top 10)"
                )
                st.plotly_chart(fig_zone, use_container_width=True)

            # Graphique de dispersion : Prix marché vs Prix OTR
            st.markdown("#### Corrélation Prix Marché vs Prix OTR")
            fig_scatter = px.scatter(
                df_comparaison,
                x="prix_otr_m2",
                y="prix_marche_m2",
                color="statut_evaluation",
                color_discrete_map={
                    "Surévalué (>20%)": "#E74C3C",
                    "Sous-évalué (<-20%)": "#27AE60",
                    "Conforme (±20%)": "#F39C12"
                },
                labels={
                    "prix_otr_m2": "Prix OTR (FCFA/m²)",
                    "prix_marche_m2": "Prix Marché (FCFA/m²)"
                },
                title="Corrélation entre prix du marché et valeurs OTR",
                hover_data=["titre", "zone", "ecart_pourcent"]
            )

            # Ajouter la ligne de référence (prix marché = prix OTR)
            fig_scatter.add_trace(
                go.Scatter(
                    x=[df_comparaison["prix_otr_m2"].min(), df_comparaison["prix_otr_m2"].max()],
                    y=[df_comparaison["prix_otr_m2"].min(), df_comparaison["prix_otr_m2"].max()],
                    mode="lines",
                    name="Ligne de référence (Prix = OTR)",
                    line=dict(color="black", dash="dash")
                )
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

            # Statistiques récapitulatives
            st.markdown("#### 📈 Statistiques de Comparaison")
            stats_cols = st.columns(4)

            total_annonces = len(df_comparaison)
            surevalue = len(df_comparaison[df_comparaison["statut_evaluation"] == "Surévalué (>20%)"])
            sousvalue = len(df_comparaison[df_comparaison["statut_evaluation"] == "Sous-évalué (<-20%)"])
            conforme = len(df_comparaison[df_comparaison["statut_evaluation"] == "Conforme (±20%)"])

            with stats_cols[0]:
                st.metric("Total Annonces Comparées", f"{total_annonces:,}")
            with stats_cols[1]:
                st.metric("Surévaluées (>20%)", f"{surevalue:,}", f"{surevalue/total_annonces*100:.1f}%")
            with stats_cols[2]:
                st.metric("Sous-évaluées (<-20%)", f"{sousvalue:,}", f"{sousvalue/total_annonces*100:.1f}%")
            with stats_cols[3]:
                st.metric("Conformes (±20%)", f"{conforme:,}", f"{conforme/total_annonces*100:.1f}%")

        else:
            st.info("Données de comparaison OTR non disponibles.")

        # Évolution temporelle si disponible
        if not df_evolution.empty:
            st.markdown("#### 📅 Évolution Temporelle des Prix")
            fig_evolution = px.line(
                df_evolution,
                x="periode",
                y=["prix_marche_moyen", "prix_otr_moyen"],
                labels={
                    "periode": "Période",
                    "value": "Prix moyen (FCFA/m²)",
                    "variable": "Type de prix"
                },
                title="Évolution des prix marché vs OTR dans le temps",
                markers=True
            )
            fig_evolution.update_layout(
                legend_title_text="",
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            st.plotly_chart(fig_evolution, use_container_width=True)

    except Exception as e:
        st.warning(f"Erreur lors du chargement des données de comparaison: {e}")

    st.divider()

    # Carte — echantillon representatif
    st.subheader("Carte des prix au m2 — Zones representatives")

    df_zones = (df_f.groupby("zone_nom")["prix_moyen_m2"].mean()
                .reset_index().rename(columns={"zone_nom": "zone"})
                .dropna(subset=["prix_moyen_m2"]))

    rows_map, not_found = [], []
    for _, row in df_zones.iterrows():
        c = get_coords(row["zone"])
        if c:
            rows_map.append({"zone": row["zone"], "prix": float(row["prix_moyen_m2"]),
                             "lat": c[0], "lon": c[1]})
        else:
            not_found.append(row["zone"])

    df_geo = pd.DataFrame(rows_map) if rows_map else pd.DataFrame(columns=["zone","prix","lat","lon"])

    # Echantillon : 10 bas + 10 milieu + 10 haut
    def sample_zones(df, n=10):
        if len(df) <= n * 3:
            return df
        s = df.sort_values("prix").reset_index(drop=True)
        mid = len(s) // 2 - n // 2
        idx = sorted(set(list(range(n)) + list(range(mid, mid+n)) + list(range(len(s)-n, len(s)))))
        return s.iloc[idx]

    df_sample = sample_zones(df_geo, 10)

    cm1, cm2, cm3 = st.columns(3)
    cm1.metric("Zones dans la base", str(len(df_zones)))
    cm2.metric("Zones geocodees",    str(len(df_geo)))
    cm3.metric("Zones affichees",    str(len(df_sample)), delta="10 bas + 10 milieu + 10 haut")

    col_map, col_leg = st.columns([4, 1])

    with col_leg:
        st.markdown("**Legende**")
        st.markdown(
            "<div style='font-size:13px;line-height:2.2'>"
            "<span style='color:#dc3200;font-size:18px'>●</span>  Prix eleve<br>"
            "<span style='color:#dc8000;font-size:18px'>●</span>  Prix moyen<br>"
            "<span style='color:#28b432;font-size:18px'>●</span>  Prix bas<br>"
            "<small style='color:#888'>Taille proportionnelle au prix<br>Clic pour le detail</small>"
            "</div>", unsafe_allow_html=True
        )
        if not_found:
            with st.expander(f"{len(not_found)} zones sans GPS"):
                st.write("\n".join(sorted(not_found)[:40]))

    with col_map:
        has_outside = (df_sample["lat"] > 7.0).any() if not df_sample.empty else False
        if zone_sel != "Toutes" and not df_sample.empty:
            clat, clon, zoom = float(df_sample.iloc[0]["lat"]), float(df_sample.iloc[0]["lon"]), 13
        elif has_outside:
            clat, clon, zoom = 8.0, 1.1, 7
        else:
            clat, clon, zoom = 6.1550, 1.2200, 12

        m = folium.Map(location=[clat, clon], zoom_start=zoom, tiles="CartoDB positron")

        if not df_sample.empty:
            pmin, pmax = df_sample["prix"].min(), df_sample["prix"].max()
            pr = max(pmax - pmin, 1)
            seuil_bas  = pmin + pr * 0.33
            seuil_haut = pmin + pr * 0.66

            for _, row in df_sample.iterrows():
                ratio = (row["prix"] - pmin) / pr
                if ratio <= 0.5:
                    r, g, b = int(255*ratio*2), 180, 50
                else:
                    r, g, b = 220, int(180*(1-(ratio-0.5)*2)), 50
                couleur = f"#{r:02x}{g:02x}{b:02x}"
                niveau = "Bas" if ratio <= 0.33 else ("Moyen" if ratio <= 0.66 else "Eleve")

                folium.CircleMarker(
                    location=[row["lat"], row["lon"]],
                    radius=8 + ratio * 12,
                    color=couleur, fill=True, fill_color=couleur,
                    fill_opacity=0.82, weight=1.5,
                    popup=folium.Popup(
                        f"<div style='font-family:Arial;padding:6px;min-width:180px'>"
                        f"<b>{row['zone'].title()}</b><hr style='margin:4px 0'>"
                        f"<b style='color:{couleur}'>{niveau}</b><br>"
                        f"Prix : <b>{row['prix']:,.0f} FCFA/m2</b></div>",
                        max_width=210
                    ),
                    tooltip=f"{row['zone'].title()} — {niveau} — {row['prix']:,.0f} FCFA/m2"
                ).add_to(m)

            m.get_root().html.add_child(folium.Element(f"""
            <div style="position:fixed;bottom:30px;left:30px;z-index:1000;
                        background:white;padding:12px 16px;border-radius:8px;
                        border:1px solid #ddd;font-family:Arial;font-size:12px;
                        box-shadow:2px 3px 6px rgba(0,0,0,0.15)">
              <b>Prix moyen / m2</b><br><br>
              <span style="color:#dc3200;font-size:16px">●</span>
                Eleve &gt; {seuil_haut:,.0f} FCFA<br>
              <span style="color:#dc8000;font-size:16px">●</span>
                Moyen {seuil_bas:,.0f}–{seuil_haut:,.0f}<br>
              <span style="color:#28b432;font-size:16px">●</span>
                Bas &lt; {seuil_bas:,.0f} FCFA
            </div>"""))
        else:
            st.warning("Aucun point a afficher — ouvre le panneau 'zones sans GPS' pour calibrer.")

        st_folium(m, width=None, height=500, use_container_width=True)
        st.caption(f"Vert = moins cher  |  Orange = intermediaire  |  Rouge = plus cher  |  {len(df_sample)} zones affichees")
    st.divider()

    # Top 10 / Moins chers
    st.subheader("Biens les plus chers vs moins chers")
    ct, cb = st.columns(2)
    with ct:
        st.markdown("#### Top 10 — Plus chers")
        top10 = df_ann.nlargest(10, "prix_m2")[["titre","zone","type_bien","prix_m2","source"]].reset_index(drop=True)
        top10["prix_m2"] = top10["prix_m2"].apply(lambda x: f"{x:,.0f} FCFA")
        st.dataframe(top10, use_container_width=True, hide_index=True)
    with cb:
        st.markdown("#### Top 10 — Moins chers")
        bot10 = df_ann[df_ann["prix_m2"] > 100].nsmallest(10, "prix_m2")[["titre","zone","type_bien","prix_m2","source"]].reset_index(drop=True)
        bot10["prix_m2"] = bot10["prix_m2"].apply(lambda x: f"{x:,.0f} FCFA")
        st.dataframe(bot10, use_container_width=True, hide_index=True)
    st.divider()

    # Indice
    st.subheader("Indice ID Immobilier — par type de bien")
    if not df_ind.empty:
        prix_global = df_ind["prix_moyen_m2"].mean()
        df_ic = df_ind.groupby(["type_bien","type_offre"]).agg(
            prix_moyen_m2=("prix_moyen_m2","mean"), nb_annonces=("nb_annonces","sum")
        ).reset_index()
        df_ic["indice"] = (df_ic["prix_moyen_m2"] / prix_global * 100).round(2)
        df_ic["tendance"] = df_ic["indice"].apply(
            lambda x: "Au-dessus" if x > 105 else ("En-dessous" if x < 95 else "Dans la moyenne"))
        df_ic = df_ic.sort_values("indice", ascending=False)
        ci1, ci2 = st.columns([2, 1])
        with ci1:
            fig_ind = px.bar(df_ic, x="type_bien", y="indice", color="tendance",
                             color_discrete_map={"Au-dessus":"#E74C3C","Dans la moyenne":"#F39C12","En-dessous":"#27AE60"},
                             barmode="group",
                             facet_col="type_offre" if offre_sel == "Tous" else None,
                             labels={"indice":"Indice (Base 100)","type_bien":"Type de bien"},
                             title="Indice par type de bien (Base 100 = prix moyen global)",
                             text="indice")
            fig_ind.add_hline(y=100, line_dash="dash", line_color="gray", annotation_text="Base 100")
            fig_ind.update_traces(texttemplate="%{text:.1f}", textposition="outside")
            st.plotly_chart(fig_ind, use_container_width=True)
        with ci2:
            st.markdown("#### Detail")
            df_disp = df_ic[["type_bien","type_offre","prix_moyen_m2","indice","nb_annonces"]].copy()
            df_disp["prix_moyen_m2"] = df_disp["prix_moyen_m2"].apply(lambda x: f"{x:,.0f}")
            df_disp["indice"] = df_disp["indice"].apply(lambda x: f"{x:.1f}")
            st.dataframe(df_disp, use_container_width=True, hide_index=True)
        st.caption(f"Base = prix moyen global : {prix_global:,.0f} FCFA/m2")
    else:
        st.info("Pas assez de donnees pour calculer l'indice.")
    st.divider()

    # Tableau comparatif zones
    st.subheader("Tableau comparatif des zones")
    cols_ok = [c for c in ["zone_nom","type_bien","type_offre","prix_moyen_m2",
                            "prix_median_m2","nombre_annonces","ecart_valeur_venale"]
               if c in df_f.columns]
    st.dataframe(df_f[cols_ok].sort_values("prix_moyen_m2", ascending=False),
                 use_container_width=True, hide_index=True)

    # Exports sidebar
    st.sidebar.divider()
    st.sidebar.download_button("Exporter statistiques (CSV)",
        data=df_f.to_csv(index=False).encode("utf-8"),
        file_name="statistiques.csv", mime="text/csv")
    st.sidebar.download_button("Exporter annonces (CSV)",
        data=df_ann.to_csv(index=False).encode("utf-8"),
        file_name="annonces.csv", mime="text/csv")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — TOUTES LES ANNONCES
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Toutes les annonces":

    st.title("Tableau d'ensemble des annonces")
    st.markdown("Toutes les annonces validees et inserees dans la base de donnees.")
    st.divider()

    df = df_annonces.copy()

    # Filtres sidebar
    st.sidebar.subheader("Filtres")

    zones = sorted(df["zone"].dropna().unique().tolist())
    zone_sel2 = st.sidebar.selectbox("Zone", ["Toutes"] + zones)

    types2 = sorted(df["type_bien"].dropna().unique().tolist())
    type_sel2 = st.sidebar.multiselect("Type de bien", types2, default=types2)
    if not type_sel2:
        type_sel2 = types2

    offre_sel2 = st.sidebar.radio("Type d'offre", ["Tous", "VENTE", "LOCATION"])

    sources2 = sorted(df["source"].dropna().unique().tolist())
    source_sel2 = st.sidebar.multiselect("Source", sources2, default=sources2)
    if not source_sel2:
        source_sel2 = sources2

    pmin_val = float(df["prix"].min()) if not df.empty else 0.0
    pmax_val = float(df["prix"].max()) if not df.empty else 1e10
    prix_range = st.sidebar.slider("Fourchette de prix (FCFA)",
                                   min_value=pmin_val, max_value=pmax_val,
                                   value=(pmin_val, pmax_val), format="%.0f")

    search = st.sidebar.text_input("Recherche dans le titre", placeholder="ex: villa, terrain...")

    # Appliquer filtres
    df2 = df.copy()
    if zone_sel2 != "Toutes":
        df2 = df2[df2["zone"] == zone_sel2]
    df2 = df2[df2["type_bien"].isin(type_sel2)]
    df2 = df2[df2["source"].isin(source_sel2)]
    if offre_sel2 != "Tous":
        df2 = df2[df2["type_offre"] == offre_sel2]
    df2 = df2[(df2["prix"] >= prix_range[0]) & (df2["prix"] <= prix_range[1])]
    if search:
        df2 = df2[df2["titre"].str.contains(search, case=False, na=False)]

    # KPIs
    ka1, ka2, ka3, ka4 = st.columns(4)
    ka1.metric("Annonces affichees", f"{len(df2):,}")
    ka2.metric("Prix moyen",         f"{df2['prix'].mean():,.0f} FCFA"    if not df2.empty else "—")
    ka3.metric("Prix moyen / m2",    f"{df2['prix_m2'].mean():,.0f} FCFA" if not df2.empty else "—")
    ka4.metric("Surface moyenne",    f"{df2['surface_m2'].mean():,.0f} m2" if not df2.empty else "—")
    st.divider()

    # Tri
    cols_map = {"titre":"Titre","zone":"Zone","type_bien":"Type de bien",
                "type_offre":"Type d'offre","prix":"Prix (FCFA)",
                "prix_m2":"Prix / m2 (FCFA)","surface_m2":"Surface (m2)",
                "source":"Source","date_annonce":"Date"}
    cols_dispo = [c for c in cols_map if c in df2.columns]

    tc1, tc2 = st.columns([2, 1])
    with tc1:
        tri_opts = [cols_map[c] for c in ["prix","prix_m2","surface_m2"] if c in df2.columns]
        col_tri = st.selectbox("Trier par", tri_opts)
    with tc2:
        ordre = st.radio("Ordre", ["Decroissant", "Croissant"], horizontal=True)

    col_tri_raw = {v: k for k, v in cols_map.items()}.get(col_tri, "prix")
    if col_tri_raw in df2.columns:
        df2 = df2.sort_values(col_tri_raw, ascending=(ordre == "Croissant"))

    # Tableau
    df_aff = df2[cols_dispo].rename(columns=cols_map).copy()
    for col in ["Prix (FCFA)", "Prix / m2 (FCFA)", "Surface (m2)"]:
        if col in df_aff.columns:
            df_aff[col] = df_aff[col].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "—")

    st.dataframe(df_aff, use_container_width=True, hide_index=True, height=600)
    st.caption(f"{len(df2):,} annonces affichees sur {len(df):,} au total")

    # Exports
    st.divider()
    ex1, ex2 = st.columns(2)
    with ex1:
        st.download_button("Exporter la selection (CSV)",
            data=df2.to_csv(index=False).encode("utf-8"),
            file_name="annonces_selection.csv", mime="text/csv")
    with ex2:
        st.download_button("Exporter tout (CSV)",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="annonces_complet.csv", mime="text/csv")


# ── Footer commun ──────────────────────────────────────────────────────────────
st.divider()
st.caption("Projet ID Immobilier — Cours Introduction Big Data 2026  |  Donnees : ImmoAsk, Facebook, CoinAfrique, OTR Togo")