import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="ID Immobilier - Demo TDR", layout="wide")
page = st.sidebar.radio("Pages", [
    "Tableau de bord principal",
    "Indice et tendances",
    "Scoring IA Random Forest",
    "OKR et KPIs pipeline",
    "Gouvernance des données",
])

np.random.seed(42)
zones = ["Tokoin", "Adidogome", "Avedji", "Baguida", "Hedzranawoe"]
df = pd.DataFrame({
    "zone": np.random.choice(zones, 100),
    "prix_m2": np.random.randint(50000, 350000, 100),
    "score_ia": np.random.uniform(0.5, 0.98, 100),
})

if page == "Tableau de bord principal":
    st.title("Demo TDR - Dashboard")
    c1, c2, c3 = st.columns(3)
    c1.metric("Annonces", len(df))
    c2.metric("Prix moyen", f"{df.prix_m2.mean():,.0f} FCFA/m²")
    c3.metric("Zones", df.zone.nunique())
    st.bar_chart(df.groupby("zone")["prix_m2"].mean())

elif page == "Indice et tendances":
    st.title("Indice et tendances")
    trend = df.groupby("zone")["prix_m2"].mean().reset_index()
    trend["indice"] = trend["prix_m2"] / trend["prix_m2"].mean() * 100
    trend["tendance"] = trend["indice"].apply(lambda x: "HAUSSE" if x > 105 else ("BAISSE" if x < 95 else "STABLE"))
    st.dataframe(trend, use_container_width=True)

elif page == "Scoring IA Random Forest":
    st.title("Scoring IA")
    st.write("Simulation du scoring IA (Random Forest)")
    st.dataframe(df[["zone", "prix_m2", "score_ia"]].head(20), use_container_width=True)

elif page == "OKR et KPIs pipeline":
    st.title("OKR & KPI")
    st.progress(0.92, text="Taux de succès pipeline")
    st.progress(0.88, text="Qualité des données")
    st.progress(0.81, text="Couverture zones")

else:
    st.title("Gouvernance des données")
    st.write("Catalogue des sources, qualité, conformité et traçabilité.")
    st.dataframe(pd.DataFrame({
        "source": ["ImmoAsk", "CoinAfrique", "Facebook", "OTR"],
        "qualite": ["Bonne", "Bonne", "Moyenne", "Excellente"],
        "frequence": ["Quotidienne", "Quotidienne", "Hebdomadaire", "Mensuelle"],
    }), use_container_width=True)
