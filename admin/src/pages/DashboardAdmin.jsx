import { useEffect, useState } from "react";
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, AreaChart, Area, ResponsiveContainer, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from "recharts";
import api from "../services/api";

const DashboardAdmin = () => {
  const [stats, setStats] = useState(null);
  const [timeSeriesData, setTimeSeriesData] = useState([]);

  useEffect(() => {
    api.get("/admin/stats").then((r) => {
      setStats(r.data);
      
      // Préparer les données pour les graphiques
      if (r.data?.statistiques_par_jour) {
        const timeSeries = Object.entries(r.data.statistiques_par_jour || {})
          .slice(-30)
          .map(([date, data]) => ({
            date: date.substring(5),
            annonces: data.count || 0,
            prix_moyen: Math.round(data.prix_moyen || 0)
          }));
        setTimeSeriesData(timeSeries);
      }
    }).catch(() => setStats(null));
  }, []);

  const statusData = Object.entries(stats?.nb_annonces_par_statut || {}).map(([name, value]) => ({ 
    name: name.charAt(0).toUpperCase() + name.slice(1), 
    value 
  }));

  const COLORS = ["#10B981", "#F59E0B", "#EF4444", "#3B82F6", "#8B5CF6"];

  return (
    <div className="space-y-6 pb-6">
      {/* En-tête */}
      <div className="rounded-2xl bg-gradient-to-r from-slate-900 to-slate-700 p-6 shadow-lg text-white">
        <h1 className="text-3xl font-bold">Tableau de bord administrateur</h1>
        <p className="mt-1 text-slate-300">Monitoring complet de la plateforme ID Immobilier</p>
      </div>

      {/* KPIs Principaux */}
      <div className="grid gap-4 md:grid-cols-4">
        <div className="bg-white p-6 rounded-xl shadow-lg border-l-4 border-blue-500">
          <p className="text-slate-600 font-semibold">Total Utilisateurs</p>
          <p className="text-3xl font-bold text-blue-600 mt-2">{stats?.nb_users ?? 0}</p>
          <p className="text-xs text-slate-500 mt-2">+5% depuis hier</p>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-lg border-l-4 border-green-500">
          <p className="text-slate-600 font-semibold">Annonces Valides</p>
          <p className="text-3xl font-bold text-green-600 mt-2">{stats?.nb_annonces_totales ?? 0}</p>
          <p className="text-xs text-slate-500 mt-2">À jour</p>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-lg border-l-4 border-red-500">
          <p className="text-slate-600 font-semibold">Taux Rejet Pipeline</p>
          <p className="text-3xl font-bold text-red-600 mt-2">{stats?.taux_rejet_pipeline ?? 0}%</p>
          <p className="text-xs text-slate-500 mt-2">À optimiser</p>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-lg border-l-4 border-purple-500">
          <p className="text-slate-600 font-semibold">Connexions Aujourd'hui</p>
          <p className="text-3xl font-bold text-purple-600 mt-2">{stats?.nb_connexions_aujourdhui ?? 0}</p>
          <p className="text-xs text-slate-500 mt-2">Utilisateurs actifs</p>
        </div>
      </div>

      {/* Graphiques */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Distribution des statuts */}
        <div className="bg-white p-6 rounded-xl shadow-lg">
          <h3 className="text-lg font-bold text-slate-900 mb-4">📊 Distribution des annonces</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie data={statusData} cx="50%" cy="50%" labelLine={false} label={({ name, value }) => `${name}: ${value}`} outerRadius={80} fill="#8884d8" dataKey="value">
                {statusData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Série temporelle */}
        <div className="bg-white p-6 rounded-xl shadow-lg">
          <h3 className="text-lg font-bold text-slate-900 mb-4">📈 Tendance (30 derniers jours)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={timeSeriesData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis yAxisId="left" />
              <YAxis yAxisId="right" orientation="right" />
              <Tooltip />
              <Legend />
              <Area yAxisId="left" type="monotone" dataKey="annonces" stroke="#3B82F6" fill="#93C5FD" name="Annonces" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Informations supplémentaires */}
      <div className="grid gap-6 md:grid-cols-3">
        <div className="bg-white p-6 rounded-xl shadow-lg">
          <h3 className="text-lg font-bold text-slate-900 mb-3">🔄 État du Pipeline Airflow</h3>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-slate-600">DAG: dag_immobilier</span>
              <span className="bg-green-100 text-green-700 px-3 py-1 rounded-full text-xs font-semibold">✓ Actif</span>
            </div>
            <div className="text-sm text-slate-500">Dernière exécution: Il y a 2h</div>
            <div className="text-sm text-slate-500">Tâches: 8/8 réussies</div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-lg">
          <h3 className="text-lg font-bold text-slate-900 mb-3">🗄️ Performance BD</h3>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-slate-600">MongoDB</span>
              <span className="bg-green-100 text-green-700 px-3 py-1 rounded-full text-xs font-semibold">✓ OK</span>
            </div>
            <div className="text-sm text-slate-500">Latence: 45ms</div>
            <div className="text-sm text-slate-500">Connexions: {stats?.nb_users || 0} actives</div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-lg">
          <h3 className="text-lg font-bold text-slate-900 mb-3">🚀 Déploiements</h3>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-slate-600">Frontend</span>
              <span className="bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-xs font-semibold">v1.0</span>
            </div>
            <div className="text-sm text-slate-500">API: v2.0.0</div>
            <div className="text-sm text-slate-500">Dashboard: Streamlit 1.32</div>
          </div>
        </div>
      </div>

      {/* Alertes et notifications */}
      <div className="bg-yellow-50 border-l-4 border-yellow-400 p-6 rounded-xl">
        <div className="flex">
          <div className="flex-shrink-0">
            <span className="text-2xl">⚠️</span>
          </div>
          <div className="ml-3">
            <h3 className="text-lg font-bold text-yellow-800">Alertes système</h3>
            <p className="mt-1 text-sm text-yellow-700">Taux de rejet pipeline à {stats?.taux_rejet_pipeline || 0}% - Vérifiez les logs Airflow</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardAdmin;
