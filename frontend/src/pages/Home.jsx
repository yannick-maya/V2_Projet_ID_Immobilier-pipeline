import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import MarketOverview from "../components/MarketOverview";
import UserWelcomeCards from "../components/UserWelcomeCards";
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
        <div className="absolute -right-8 -top-8 h-32 w-32 rounded-full bg-white/20 blur-xl animate-pulse" />
        <div className="absolute bottom-4 left-8 h-20 w-20 rounded-full bg-[#F59E0B]/30 blur-xl animate-bounce" />
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-gradient-to-r from-white/5 to-transparent rounded-full blur-3xl" />
        <div className="absolute top-8 right-16 w-16 h-16 bg-[#F59E0B]/20 rounded-full blur-lg animate-pulse delay-1000" />
        <div className="absolute bottom-8 left-16 w-12 h-12 bg-white/15 rounded-full blur-md animate-bounce delay-500" />
        <div className="absolute top-16 left-1/4 w-8 h-8 bg-white/10 rounded-full blur-sm animate-ping" />
        <div className="absolute bottom-16 right-1/4 w-6 h-6 bg-[#F59E0B]/25 rounded-full blur-sm animate-pulse delay-700" />

        {/* Particules flottantes */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-1/4 left-1/4 w-2 h-2 bg-white/30 rounded-full animate-float"></div>
          <div className="absolute top-3/4 right-1/3 w-1 h-1 bg-[#F59E0B]/40 rounded-full animate-float-delayed"></div>
          <div className="absolute top-1/2 right-1/4 w-1.5 h-1.5 bg-white/20 rounded-full animate-float-slow"></div>
          <div className="absolute top-1/6 right-1/6 w-1 h-1 bg-white/25 rounded-full animate-float" style={{animationDelay: '1s'}}></div>
          <div className="absolute bottom-1/3 left-1/6 w-0.5 h-0.5 bg-[#F59E0B]/30 rounded-full animate-float-delayed" style={{animationDelay: '3s'}}></div>
        </div>
        <div className="relative max-w-4xl space-y-6">
          <span className="inline-flex rounded-full bg-white/15 px-4 py-1 text-sm font-medium backdrop-blur-sm border border-white/20 shadow-lg animate-fade-in">
            🏠 Plateforme immobilière intelligente - Lomé / Togo
          </span>
          <h1 className="text-4xl font-black leading-tight md:text-5xl animate-fade-in">
            Le marché immobilier, piloté par le prix au m².
          </h1>
          <p className="max-w-3xl text-base text-white/90 md:text-xl animate-fade-in-delayed">
            ID Immobilier recentre l'analyse sur les statistiques de marché par bien, par zone et par type,
            au lieu d'exposer partout les prix bruts. {hasUser && "Découvrez vos outils personnalisés ci-dessous."}
          </p>
          <div className="flex flex-wrap gap-3 animate-fade-in-slow">
            <Link to="/recherche" className="group rounded-xl bg-[#F59E0B] px-5 py-3 font-semibold text-[#0B3954] hover:bg-[#f7b344] hover:shadow-lg transition-all duration-300 transform hover:scale-105 shadow-xl">
              <span className="flex items-center">
                🚀 Explorer les annonces
                <svg className="ml-2 w-4 h-4 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </span>
            </Link>
            {hasUser ? (
              <Link to="/dashboard" className="group rounded-xl border border-white/35 bg-white/10 px-5 py-3 font-semibold text-white hover:bg-white/20 backdrop-blur-sm transition-all duration-300 shadow-lg hover:shadow-xl">
                <span className="flex items-center">
                  📊 Ouvrir mon tableau de bord
                  <svg className="ml-2 w-4 h-4 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </span>
              </Link>
            ) : (
              <Link to="/login" className="group rounded-xl border border-white/35 bg-white/10 px-5 py-3 font-semibold text-white hover:bg-white/20 backdrop-blur-sm transition-all duration-300 shadow-lg hover:shadow-xl">
                <span className="flex items-center">
                  🔐 Se connecter pour plus d'analyses expérimentales
                  <svg className="ml-2 w-4 h-4 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
                  </svg>
                </span>
              </Link>
            )}
          </div>
        </div>
      </section>

      {hasUser ? (
        <UserWelcomeCards />
      ) : (
        <MarketOverview overview={overview} compact={!hasUser} isAuthenticated={hasUser} />
      )}
    </div>
  );
};

export default Home;
