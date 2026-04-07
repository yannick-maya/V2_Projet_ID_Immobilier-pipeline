import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { annoncesApi, indiceApi, statsApi } from "../services/api";

const Home = () => {
  const [stats, setStats] = useState([]);
  const [annonces, setAnnonces] = useState([]);
  const [tendances, setTendances] = useState(null);

  useEffect(() => {
    statsApi.list().then((res) => setStats(res.data.data || [])).catch(() => setStats([]));
    annoncesApi.list({ page: 1, limit: 200 }).then((res) => setAnnonces(res.data.data || [])).catch(() => setAnnonces([]));
    indiceApi.tendances().then((res) => setTendances(res.data)).catch(() => setTendances(null));
  }, []);

  const kpis = useMemo(() => {
    const totalAnnonces = stats.length ? stats.reduce((acc, s) => acc + (s.nombre_annonces || 0), 0) : annonces.length;
    const zones = new Set([...stats.map((s) => s.zone), ...annonces.map((a) => a.zone)].filter(Boolean)).size;
    const prixMoyen = stats.length
      ? Math.round(stats.reduce((sum, item) => sum + (item.prix_moyen_m2 || 0), 0) / Math.max(stats.length, 1))
      : Math.round(annonces.reduce((sum, item) => sum + (item.prix_m2 || 0), 0) / Math.max(annonces.length, 1));
    const periodes = new Set([...stats.map((s) => s.periode), ...annonces.map((a) => a.periode)].filter(Boolean)).size || 1;
    const sources = new Set(annonces.map((a) => a.source).filter(Boolean)).size || 0;
    return { totalAnnonces, zones, prixMoyen, periodes, sources };
  }, [stats, annonces]);

  const topZones = useMemo(() => {
    return [...stats]
      .filter((item) => item.zone && item.prix_moyen_m2)
      .sort((a, b) => (b.prix_moyen_m2 || 0) - (a.prix_moyen_m2 || 0))
      .slice(0, 6);
  }, [stats]);

  const trendCards = ["HAUSSE", "STABLE", "BAISSE"];

  return (
    <div className="space-y-10">
      <section className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-[#065A82] via-[#1C7293] to-[#00B4D8] px-8 py-16 text-white shadow-xl md:px-12">
        <div className="absolute -right-8 -top-8 h-32 w-32 rounded-full bg-white/20 blur-xl" />
        <div className="absolute bottom-4 left-8 h-20 w-20 rounded-full bg-[#F59E0B]/30 blur-xl" />
        <div className="relative max-w-4xl space-y-6">
          <span className="inline-flex rounded-full bg-white/15 px-4 py-1 text-sm font-medium">Plateforme immobilière intelligente - Lomé / Togo</span>
          <h1 className="text-4xl font-black leading-tight md:text-6xl">Votre décision immobilière commence avec la donnée.</h1>
          <p className="max-w-3xl text-base text-white/90 md:text-xl">
            ID Immobilier centralise les annonces, calcule les indices par zone et te donne une vision claire du marché.
          </p>
          <div className="flex flex-wrap gap-3">
            <Link to="/recherche" className="rounded-xl bg-[#F59E0B] px-5 py-3 font-semibold text-[#0B3954] hover:bg-[#f7b344]">Explorer les annonces</Link>
            <Link to="/indice" className="rounded-xl border border-white/35 bg-white/10 px-5 py-3 font-semibold text-white hover:bg-white/20">Voir les tendances</Link>
          </div>
        </div>
      </section>

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
        <div className="card-kpi"><p className="kpi-label">Annonces</p><p className="kpi-value">{kpis.totalAnnonces.toLocaleString()}</p></div>
        <div className="card-kpi"><p className="kpi-label">Zones couvertes</p><p className="kpi-value">{kpis.zones.toLocaleString()}</p></div>
        <div className="card-kpi"><p className="kpi-label">Prix moyen</p><p className="kpi-value">{kpis.prixMoyen.toLocaleString()} FCFA/m²</p></div>
        <div className="card-kpi"><p className="kpi-label">Périodes</p><p className="kpi-value">{kpis.periodes.toLocaleString()}</p></div>
        <div className="card-kpi"><p className="kpi-label">Sources</p><p className="kpi-value">{kpis.sources.toLocaleString()}</p></div>
      </section>

      <section className="grid gap-6 lg:grid-cols-[1.5fr_1fr]">
        <div className="rounded-2xl border border-slate-100 bg-white p-6 shadow-lg">
          <h2 className="text-2xl font-bold text-[#0B3954]">Top zones les plus chères</h2>
          <p className="mt-1 text-sm text-slate-500">Classement automatique depuis MongoDB.</p>
          <div className="mt-5 grid gap-3 md:grid-cols-2">
            {topZones.map((zone, idx) => (
              <div key={`${zone.zone}-${idx}`} className="rounded-xl border border-slate-100 bg-slate-50 p-4">
                <p className="font-bold text-slate-800">#{idx + 1} {zone.zone}</p>
                <p className="mt-1 text-sm text-slate-500">{zone.type_bien || "Tous biens"} · {zone.type_offre || "Tous"}</p>
                <p className="mt-2 text-lg font-extrabold text-[#065A82]">{Number(zone.prix_moyen_m2 || 0).toLocaleString()} FCFA/m²</p>
                <p className="text-xs text-slate-500">{zone.nombre_annonces || 0} annonces</p>
              </div>
            ))}
            {topZones.length === 0 && <p className="text-sm text-slate-500">Aucune statistique disponible pour le moment.</p>}
          </div>
        </div>

        <div className="rounded-2xl border border-slate-100 bg-white p-6 shadow-lg">
          <h2 className="text-2xl font-bold text-[#0B3954]">Tendances</h2>
          <p className="mt-1 text-sm text-slate-500">Synthèse des indices par zone.</p>
          <div className="mt-5 space-y-3">
            {trendCards.map((key) => (
              <div key={key} className="flex items-center justify-between rounded-xl border border-slate-100 p-3">
                <div>
                  <p className="font-semibold text-slate-800">{key}</p>
                  <p className="text-xs text-slate-500">Zones concernées</p>
                </div>
                <p className="text-xl font-black text-[#065A82]">{tendances?.[key]?.count || 0}</p>
              </div>
            ))}
          </div>
          <div className="mt-6 rounded-xl bg-[#F0F7FB] p-4 text-sm text-slate-700">
            La carte n'est plus affichée à l'accueil. Elle apparaît désormais uniquement dans la page Recherche quand une zone est saisie.
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;
