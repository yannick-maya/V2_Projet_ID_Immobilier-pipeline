import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, ResponsiveContainer, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from "recharts";
import MarketOverview from "../components/MarketOverview";
import { useAuth } from "../context/AuthContext";
import { favorisApi, statsApi } from "../services/api";

const Dashboard = () => {
  const { user } = useAuth();
  const [favorisCount, setFavorisCount] = useState(0);
  const [overview, setOverview] = useState(null);
  const [chartData, setChartData] = useState([]);
  const [typeData, setTypeData] = useState([]);

  useEffect(() => {
    favorisApi.list().then((r) => setFavorisCount((r.data.data || []).length)).catch(() => setFavorisCount(0));
    statsApi.overview().then((r) => {
      setOverview(r.data);
      
      // Préparer les données pour les graphiques
      if (r.data?.par_zone) {
        const zones = Object.entries(r.data.par_zone)
          .slice(0, 8)
          .map(([zone, data]) => ({
            zone: zone.substring(0, 15),
            price: Math.round(data.prix_moyen || 0),
            count: data.count || 0
          }));
        setChartData(zones);
      }

      if (r.data?.par_type) {
        const types = Object.entries(r.data.par_type).map(([type, data]) => ({
          name: type,
          value: data.count || 0,
          price: Math.round(data.prix_moyen || 0)
        }));
        setTypeData(types);
      }
    }).catch(() => setOverview(null));
  }, []);

  const COLORS = ["#0B3954", "#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A", "#98D8C8", "#F7DC6F", "#BB8FCE"];

  return (
    <div className="space-y-6">
      {/* En-tête */}
      <div className="rounded-2xl bg-gradient-to-r from-[#0B3954] to-[#1e5f74] p-6 shadow-lg text-white">
        <h2 className="text-3xl font-bold">Bonjour {user?.prenom}</h2>
        <p className="mt-1 text-slate-200">Analyse complète du marché immobilier au Togo</p>
      </div>

      {/* KPIs */}
      <div className="grid gap-4 md:grid-cols-4">
        <div className="card-kpi bg-gradient-to-br from-blue-50 to-blue-100 border-l-4 border-blue-500">
          <p className="kpi-label text-blue-600">Annonces</p>
          <p className="kpi-value text-blue-900">{overview?.total_annonces || 0}</p>
          <p className="text-xs text-blue-500 mt-1">+12% ce mois</p>
        </div>
        <div className="card-kpi bg-gradient-to-br from-green-50 to-green-100 border-l-4 border-green-500">
          <p className="kpi-label text-green-600">Prix moyen</p>
          <p className="kpi-value text-green-900">${overview?.prix_moyen_global || 0}</p>
          <p className="text-xs text-green-500 mt-1">Par m²</p>
        </div>
        <div className="card-kpi bg-gradient-to-br from-purple-50 to-purple-100 border-l-4 border-purple-500">
          <p className="kpi-label text-purple-600">Favoris</p>
          <p className="kpi-value text-purple-900">{favorisCount}</p>
          <p className="text-xs text-purple-500 mt-1">Enregistrés</p>
        </div>
        <div className="card-kpi bg-gradient-to-br from-orange-50 to-orange-100 border-l-4 border-orange-500">
          <p className="kpi-label text-orange-600">Zone hotteste</p>
          <p className="kpi-value text-orange-900 text-lg">{overview?.zone_plus_active?.substring(0, 12)}</p>
          <p className="text-xs text-orange-500 mt-1">Activité max</p>
        </div>
      </div>

      {/* Graphiques */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Graphique prix par zone */}
        <div className="bg-white p-6 rounded-2xl shadow-lg">
          <h3 className="text-lg font-bold text-[#0B3954] mb-4"> Prix moyens par zone</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="zone" angle={-45} textAnchor="end" height={100} />
              <YAxis />
              <Tooltip formatter={(value) => `$${value}`} />
              <Bar dataKey="price" fill="#0B3954" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Distribution par type */}
        <div className="bg-white p-6 rounded-2xl shadow-lg">
          <h3 className="text-lg font-bold text-[#0B3954] mb-4"> Distribution par type</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie data={typeData} cx="50%" cy="50%" labelLine={false} label={({ name, value }) => `${name}: ${value}`} outerRadius={80} fill="#8884d8" dataKey="value">
                {typeData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => `${value} annonces`} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Overview du marché */}
      {overview && <MarketOverview overview={overview} isAuthenticated />}

      {/* Actions rapides */}
      <div className="grid gap-4 md:grid-cols-2">
        <Link to="/recherche" className="group rounded-2xl bg-white p-6 shadow-lg hover:shadow-xl transition-all border-l-4 border-[#0B3954]">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-bold text-[#0B3954] group-hover:text-blue-600">🔍 Recherche avancée</h3>
              <p className="mt-1 text-sm text-slate-500">Filtrer par zone, type et budget</p>
            </div>
            <span className="text-2xl">→</span>
          </div>
        </Link>
        <Link to="/simulateur" className="group rounded-2xl bg-white p-6 shadow-lg hover:shadow-xl transition-all border-l-4 border-green-500">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-bold text-[#0B3954] group-hover:text-green-600">💰 Simulateur de prix</h3>
              <p className="mt-1 text-sm text-slate-500">Estimer le prix d'un bien immobilier</p>
            </div>
            <span className="text-2xl">→</span>
          </div>
        </Link>
      </div>
    </div>
  );
};

export default Dashboard;
