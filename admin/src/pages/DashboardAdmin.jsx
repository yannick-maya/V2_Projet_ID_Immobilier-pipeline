import { useEffect, useState } from "react";
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, AreaChart, Area, ResponsiveContainer, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ComposedChart } from "recharts";
import api from "../services/api";

const DashboardAdmin = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/admin/stats").then((r) => {
      setStats(r.data);
      setLoading(false);
    }).catch(() => {
      setStats(null);
      setLoading(false);
    });
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const overview = stats?.overview || {};
  const kpis = overview.kpis || {};
  const sources = overview.sources || [];
  const typesBien = overview.types_bien || [];
  const tendances = overview.tendances || {};
  const timeSeriesData = Object.entries(stats?.statistiques_par_jour || {})
    .slice(-30)
    .map(([date, data]) => ({
      date: date.substring(5),
      annonces: data.count || 0,
      prix_moyen: Math.round(data.prix_moyen || 0)
    }));

  const statusData = Object.entries(stats?.nb_annonces_par_statut || {}).map(([name, value]) => ({
    name: name.charAt(0).toUpperCase() + name.slice(1),
    value
  }));

  const otrData = Object.entries(stats?.statistiques_otr || {}).map(([name, value]) => ({
    name: name.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
    value,
    color: name === 'sous-evalue' ? '#10B981' : name === 'sur-evalue' ? '#EF4444' : '#F59E0B'
  }));

  const COLORS = ["#065A82", "#1C7293", "#00B4D8", "#F59E0B", "#7CC6D9", "#0B3954"];

  const formatNumber = (value, options = {}) =>
    Number(value || 0).toLocaleString("fr-FR", { maximumFractionDigits: 0, ...options });

  const MetricCard = ({ title, value, subtitle, icon, color = "blue" }) => (
    <div className={`bg-white p-6 rounded-xl shadow-lg border-l-4 border-${color}-500 hover:shadow-xl transition-shadow duration-300`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-slate-600 font-semibold text-sm">{title}</p>
          <p className="text-3xl font-bold text-slate-900 mt-2">{value}</p>
          {subtitle && <p className="text-xs text-slate-500 mt-2">{subtitle}</p>}
        </div>
        <div className={`p-3 rounded-full bg-${color}-100`}>
          <span className="text-2xl">{icon}</span>
        </div>
      </div>
    </div>
  );

  const ChartCard = ({ title, subtitle, children, className = "" }) => (
    <div className={`bg-white p-6 rounded-xl shadow-lg ${className}`}>
      <div className="mb-4">
        <h3 className="text-lg font-bold text-slate-900">{title}</h3>
        {subtitle && <p className="text-sm text-slate-600 mt-1">{subtitle}</p>}
      </div>
      <div className="h-80">
        {children}
      </div>
    </div>
  );

  return (
    <div className="space-y-6 pb-6">
      {/* En-tête */}
      <div className="rounded-2xl bg-gradient-to-r from-slate-900 via-slate-800 to-slate-700 p-8 shadow-xl text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold">Tableau de bord administrateur</h1>
            <p className="mt-2 text-slate-300">Monitoring complet de la plateforme ID Immobilier</p>
          </div>
          <div className="text-right">
            <p className="text-2xl font-bold">{formatNumber(kpis.annonces || 0)}</p>
            <p className="text-sm text-slate-300">Annonces actives</p>
          </div>
        </div>
      </div>

      {/* KPIs Principaux */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <MetricCard
          title="Total Utilisateurs"
          value={formatNumber(stats?.nb_users || 0)}
          subtitle="Utilisateurs inscrits"
          icon="👥"
          color="blue"
        />
        <MetricCard
          title="Annonces Valides"
          value={formatNumber(stats?.nb_annonces_par_statut?.valide || 0)}
          subtitle="Annonces approuvées"
          icon="✅"
          color="green"
        />
        <MetricCard
          title="Prix Moyen / m²"
          value={`${formatNumber(kpis.prix_moyen_m2 || 0)} FCFA`}
          subtitle="Prix moyen du marché"
          icon="💰"
          color="amber"
        />
        <MetricCard
          title="Sources"
          value={formatNumber(kpis.sources || 0)}
          subtitle="Sources de données"
          icon="📊"
          color="purple"
        />
      </div>

      {/* Graphiques principaux */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Évolution temporelle */}
        <ChartCard
          title="Évolution des annonces (30 derniers jours)"
          subtitle="Nombre d'annonces et prix moyen par jour"
        >
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={timeSeriesData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="date" stroke="#64748b" fontSize={12} />
              <YAxis yAxisId="left" stroke="#64748b" fontSize={12} />
              <YAxis yAxisId="right" orientation="right" stroke="#64748b" fontSize={12} />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'white',
                  border: '1px solid #e2e8f0',
                  borderRadius: '8px',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                }}
                formatter={(value, name) => [
                  name === 'annonces' ? `${value} annonces` : `${formatNumber(value)} FCFA`,
                  name === 'annonces' ? 'Annonces' : 'Prix moyen'
                ]}
              />
              <Legend />
              <Bar yAxisId="left" dataKey="annonces" fill="#065A82" name="annonces" radius={[4, 4, 0, 0]} />
              <Line yAxisId="right" type="monotone" dataKey="prix_moyen" stroke="#F59E0B" strokeWidth={3} name="prix_moyen" />
            </ComposedChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* Répartition par sources */}
        <ChartCard
          title="Répartition par source de données"
          subtitle="Origine des annonces collectées"
        >
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={sources}
                cx="50%"
                cy="50%"
                outerRadius={100}
                dataKey="count"
                label={({ label, percent }) => `${label}: ${(percent * 100).toFixed(0)}%`}
                labelLine={false}
              >
                {sources.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => [`${value} annonces`, 'Nombre']} />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      {/* Graphiques secondaires */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Prix par zone */}
        <ChartCard
          title="Prix moyen par zone géographique"
          subtitle="Top 10 des zones les plus chères"
        >
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={overview.top_zones || []} layout="horizontal">
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis type="number" stroke="#64748b" fontSize={12} />
              <YAxis dataKey="label" type="category" stroke="#64748b" fontSize={10} width={120} />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'white',
                  border: '1px solid #e2e8f0',
                  borderRadius: '8px',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                }}
                formatter={(value) => [`${formatNumber(value)} FCFA/m²`, 'Prix moyen']}
              />
              <Bar dataKey="mean" fill="#065A82" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* Évaluation OTR */}
        <ChartCard
          title="Évaluation par rapport aux prix officiels"
          subtitle="Comparaison avec les valeurs vénale OTR"
        >
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={otrData}
                cx="50%"
                cy="50%"
                outerRadius={100}
                dataKey="value"
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                labelLine={false}
              >
                {otrData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => [`${value} annonces`, 'Nombre']} />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      {/* Tendances du marché */}
      <ChartCard
        title="Tendances du marché immobilier"
        subtitle="Évolution des prix par zone géographique"
        className="col-span-full"
      >
        <div className="grid gap-4 md:grid-cols-3">
          {["HAUSSE", "STABLE", "BAISSE"].map((key) => (
            <div key={key} className="bg-slate-50 p-6 rounded-xl border border-slate-200">
              <div className="flex items-center justify-between mb-4">
                <h4 className="text-lg font-semibold text-slate-900">{key}</h4>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  key === "HAUSSE" ? "bg-green-100 text-green-800" :
                  key === "STABLE" ? "bg-blue-100 text-blue-800" :
                  "bg-red-100 text-red-800"
                }`}>
                  {key === "HAUSSE" ? "📈" : key === "STABLE" ? "➡️" : "📉"}
                </span>
              </div>
              <p className="text-3xl font-bold text-slate-900 mb-2">
                {formatNumber(tendances[key]?.count || 0)}
              </p>
              <p className="text-sm text-slate-600 mb-4">Zones concernées</p>
              <div className="flex flex-wrap gap-2">
                {(tendances[key]?.zones || []).slice(0, 5).map((zone, index) => (
                  <span key={index} className="px-2 py-1 bg-white rounded-md text-xs text-slate-700 border border-slate-300">
                    {zone}
                  </span>
                ))}
                {(tendances[key]?.zones || []).length > 5 && (
                  <span className="px-2 py-1 bg-slate-200 rounded-md text-xs text-slate-600">
                    +{(tendances[key].zones.length - 5)} autres
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      </ChartCard>

      {/* Statut des annonces */}
      <ChartCard
        title="Statut des annonces"
        subtitle="Répartition par état de validation"
      >
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={statusData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
            <XAxis dataKey="name" stroke="#64748b" fontSize={12} />
            <YAxis stroke="#64748b" fontSize={12} />
            <Tooltip
              contentStyle={{
                backgroundColor: 'white',
                border: '1px solid #e2e8f0',
                borderRadius: '8px',
                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
              }}
              formatter={(value) => [`${value} annonces`, 'Nombre']}
            />
            <Bar dataKey="value" fill="#065A82" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>
    </div>
  );
};

export default DashboardAdmin;
