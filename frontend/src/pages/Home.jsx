import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import MarketOverview from "../components/MarketOverview";
import { useAuth } from "../context/AuthContext";
import { statsApi } from "../services/api";

const Home = () => {
  const { user } = useAuth();
  const [overview, setOverview] = useState(null);
  const hasUser = useMemo(() => Boolean(user), [user]);

  useEffect(() => {
    statsApi.overview().then((res) => setOverview(res.data)).catch(() => setOverview(null));
  }, []);

  return (
    <div className="space-y-6">
      <section className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-[#065A82] via-[#1C7293] to-[#00B4D8] px-6 py-12 text-white shadow-xl md:px-10">
        <div className="absolute -right-8 -top-8 h-32 w-32 rounded-full bg-white/20 blur-xl" />
        <div className="absolute bottom-4 left-8 h-20 w-20 rounded-full bg-[#F59E0B]/30 blur-xl" />
        <div className="relative max-w-4xl space-y-6">
          <span className="inline-flex rounded-full bg-white/15 px-4 py-1 text-sm font-medium">Plateforme immobiliere intelligente - Lome / Togo</span>
          <h1 className="text-4xl font-black leading-tight md:text-5xl">Le marche immobilier, pilote par le prix au m2.</h1>
          <p className="max-w-3xl text-base text-white/90 md:text-xl">
            ID Immobilier recentre l'analyse sur les statistiques de marche par bien, par zone et par type, au lieu d'exposer partout les prix bruts.
          </p>
          <div className="flex flex-wrap gap-3">
            <Link to="/recherche" className="rounded-xl bg-[#F59E0B] px-5 py-3 font-semibold text-[#0B3954] hover:bg-[#f7b344]">Explorer les annonces</Link>
            {hasUser ? (
              <Link to="/dashboard" className="rounded-xl border border-white/35 bg-white/10 px-5 py-3 font-semibold text-white hover:bg-white/20">Ouvrir mon accueil</Link>
            ) : (
              <Link to="/login" className="rounded-xl border border-white/35 bg-white/10 px-5 py-3 font-semibold text-white hover:bg-white/20">Se connecter pour plus de graphiques</Link>
            )}
          </div>
        </div>
      </section>

      <MarketOverview overview={overview} compact={!hasUser} isAuthenticated={hasUser} />
    </div>
  );
};

export default Home;
