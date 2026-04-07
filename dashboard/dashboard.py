"""Dashboard Streamlit MongoDB - ID Immobilier"""

import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
st.set_page_config(page_title="ID Immobilier Dashboard", page_icon="🏠", layout="wide")


def _load_collection(name: str):
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client[os.getenv("MONGO_DB", "id_immobilier")]
    data = list(db[name].find({}, {"_id": 0}))
    client.close()
    return pd.DataFrame(data)


@st.cache_data(ttl=3600)
def load_statistiques():
    return _load_collection("statistiques")


@st.cache_data(ttl=3600)
def load_annonces():
    return _load_collection("annonces")


@st.cache_data(ttl=3600)
def load_venales():
    return _load_collection("valeurs_venales")


@st.cache_data(ttl=3600)
def load_sources():
    df = _load_collection("annonces")
    if df.empty or "source" not in df.columns:
        return pd.DataFrame(columns=["source", "nombre_annonces"])
    return df.groupby("source").size().reset_index(name="nombre_annonces").sort_values("nombre_annonces", ascending=False)


@st.cache_data(ttl=3600)
def load_indices():
    return _load_collection("indices")


def apply_filters(df, zone_sel, type_bien_sel, type_offre_sel, periode_sel):
    if df.empty:
        return df
    out = df.copy()
    if zone_sel != "Toutes" and "zone" in out.columns:
        out = out[out["zone"] == zone_sel]
    if type_bien_sel != "Tous" and "type_bien" in out.columns:
        out = out[out["type_bien"] == type_bien_sel]
    if type_offre_sel != "Tous" and "type_offre" in out.columns:
        out = out[out["type_offre"] == type_offre_sel]
    if periode_sel != "Toutes" and "periode" in out.columns:
        out = out[out["periode"] == periode_sel]
    return out


def main():
    st.title("ID Immobilier - Dashboard MongoDB")

    df_stats = load_statistiques()
    df_annonces = load_annonces()
    df_indices = load_indices()
    df_sources = load_sources()

    all_df = [d for d in [df_stats, df_annonces, df_indices] if not d.empty]
    zones = sorted(set().union(*[set(d["zone"].dropna().unique().tolist()) for d in all_df if "zone" in d.columns])) if all_df else []
    types_bien = sorted(set().union(*[set(d["type_bien"].dropna().unique().tolist()) for d in all_df if "type_bien" in d.columns])) if all_df else []
    types_offre = sorted(set().union(*[set(d["type_offre"].dropna().unique().tolist()) for d in all_df if "type_offre" in d.columns])) if all_df else []
    periodes = sorted(set().union(*[set(d["periode"].dropna().unique().tolist()) for d in all_df if "periode" in d.columns])) if all_df else []

    st.sidebar.header("Filtres")
    zone_sel = st.sidebar.selectbox("Zone", ["Toutes"] + zones)
    type_bien_sel = st.sidebar.selectbox("Type de bien", ["Tous"] + types_bien)
    type_offre_sel = st.sidebar.selectbox("Type d'offre", ["Tous"] + types_offre)
    periode_sel = st.sidebar.selectbox("Periode", ["Toutes"] + periodes)

    stats_f = apply_filters(df_stats, zone_sel, type_bien_sel, type_offre_sel, periode_sel)
    annonces_f = apply_filters(df_annonces, zone_sel, type_bien_sel, type_offre_sel, periode_sel)
    indices_f = apply_filters(df_indices, zone_sel, type_bien_sel, type_offre_sel, periode_sel)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Annonces", f"{len(annonces_f):,}")
    c2.metric("Stats", f"{len(stats_f):,}")
    c3.metric("Indices", f"{len(indices_f):,}")
    prix_moy = annonces_f["prix_m2"].mean() if (not annonces_f.empty and "prix_m2" in annonces_f.columns) else 0
    c4.metric("Prix moyen m2", f"{prix_moy:,.0f} FCFA")

    tab1, tab2, tab3, tab4 = st.tabs(["Statistiques", "Annonces", "Indices", "Sources"])

    with tab1:
        st.dataframe(stats_f, use_container_width=True)
    with tab2:
        st.dataframe(annonces_f, use_container_width=True)
    with tab3:
        st.dataframe(indices_f, use_container_width=True)
    with tab4:
        st.dataframe(df_sources, use_container_width=True)


if __name__ == "__main__":
    main()
