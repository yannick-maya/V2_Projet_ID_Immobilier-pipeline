import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { favorisApi } from "../services/api";

const Dashboard = () => {
  const { user } = useAuth();
  const [favorisCount, setFavorisCount] = useState(0);

  useEffect(() => {
    favorisApi.list().then((r) => setFavorisCount((r.data.data || []).length)).catch(() => setFavorisCount(0));
  }, []);

  return (
    <div className="space-y-6">
      <div className="rounded-2xl bg-white p-6 shadow-lg">
        <h2 className="text-2xl font-bold text-[#0B3954]">Bonjour {user?.prenom} {user?.nom}</h2>
        <p className="mt-1 text-slate-600">Bienvenue sur ton tableau de bord personnel.</p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <div className="card-kpi"><p className="kpi-label">Role</p><p className="kpi-value">{user?.role || "user"}</p></div>
        <div className="card-kpi"><p className="kpi-label">Favoris</p><p className="kpi-value">{favorisCount}</p></div>
        <div className="card-kpi"><p className="kpi-label">Compte</p><p className="kpi-value">Actif</p></div>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Link to="/recherche" className="rounded-2xl bg-white p-6 shadow-lg hover:bg-slate-50">
          <h3 className="text-lg font-bold text-[#0B3954]">Lancer une recherche</h3>
          <p className="mt-1 text-sm text-slate-500">Trouver des annonces par zone, type et budget.</p>
        </Link>
        <Link to="/simulateur" className="rounded-2xl bg-white p-6 shadow-lg hover:bg-slate-50">
          <h3 className="text-lg font-bold text-[#0B3954]">Simuler un prix</h3>
          <p className="mt-1 text-sm text-slate-500">Obtenir une estimation intelligente depuis MongoDB.</p>
        </Link>
      </div>
    </div>
  );
};

export default Dashboard;
