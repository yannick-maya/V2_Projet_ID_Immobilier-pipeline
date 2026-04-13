import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, ResponsiveContainer, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ComposedChart } from "recharts";
import MarketOverview from "../components/MarketOverview";
import { useAuth } from "../context/AuthContext";
import { favorisApi, statsApi } from "../services/api";

const Dashboard = () => {
  const { user } = useAuth();
  const [favorisCount, setFavorisCount] = useState(0);
  const [overview, setOverview] = useState(null);
  const [chartData, setChartData] = useState([]);
  const [typeData, setTypeData] = useState([]);
  const [timelineData, setTimelineData] = useState([]);
  const [terrainOtrData, setTerrainOtrData] = useState([]);

  useEffect(() => {
    favorisApi.list().then((r) => setFavorisCount((r.data?.data || []).length)).catch(() => setFavorisCount(0));
    statsApi.overview().then((r) => {
      const data = r.data || {};
      setOverview(data);

      // Graphique prix par zone
      const zones = (data?.comparaison_zones || []).slice(0, 8).map((item) => ({
        zone: item.label || "Zone",
        price: Math.round(item.mean || 0),
        count: item.count || 0,
      }));
      setChartData(zones && zones.length > 0 ? zones : []);

      // Graphique sources
      const sources = (data?.comparaison_sources || []).map((item) => ({
        name: item.label || "Source",
        value: item.count || 0,
        price: Math.round(item.prix_moyen_m2 || 0),
      }));
      setTypeData(sources && sources.length > 0 ? sources : []);

      // Timeline temporelle
      const timeline = (data?.timeline || []).map((item) => ({
        periode: item.periode || "Période",
        prix_moyen_m2: Math.round(item.prix_moyen_m2 || 0),
        prix_median_m2: Math.round(item.prix_median_m2 || 0),
        volume: item.volume || 0,
      }));
      setTimelineData(timeline && timeline.length > 0 ? timeline : []);

      const terrainOtr = (data?.terrain_otr_points || []).map((item, index) => ({
        label: item.zone || `Terrain ${index + 1}`,
        marketPrice: Math.round(item.prix || 0),
        otrPrice: Math.round(item.prix_otr || 0),
        diff: Math.round(item.difference_pct || 0),
      }));
      setTerrainOtrData(terrainOtr && terrainOtr.length > 0 ? terrainOtr : []);
    }).catch((err) => {
      console.error("Erreur lors du chargement des statistiques:", err);
      setOverview(null);
    });
  }, []);

  const COLORS = ["#0B3954", "#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A", "#98D8C8", "#F7DC6F", "#BB8FCE"];

  return (
    <div className="space-y-6">
      {/* En-tête */}
      <div className="rounded-2xl bg-gradient-to-r from-[#0B3954] to-[#1e5f74] p-6 shadow-lg text-white">
        <h2 className="text-3xl font-bold">Bonjour {user?.prenom}</h2>
        <p className="mt-1 text-slate-200">Analyse complète du marché immobilier au Togo</p>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <div className="card-kpi">
          <p className="kpi-label">Annonces</p>
          <p className="kpi-value">{overview?.kpis?.annonces || 0}</p>
        </div>
        <div className="card-kpi">
          <p className="kpi-label">Prix moyen / m²</p>
          <p className="kpi-value">{Number(overview?.kpis?.prix_moyen_m2 || 0).toLocaleString("fr-FR")} FCFA</p>
        </div>
        <div className="card-kpi">
          <p className="kpi-label">Favoris</p>
          <p className="kpi-value">{favorisCount}</p>
        </div>
        <div className="card-kpi">
          <p className="kpi-label">Sources</p>
          <p className="kpi-value">{overview?.kpis?.sources || 0}</p>
        </div>
      </div>

      {overview && <MarketOverview overview={overview} isAuthenticated />}

      {/* Actions rapides */}
      <div className="grid gap-4 md:grid-cols-2">
        <Link to="/recherche" className="group rounded-2xl bg-white p-6 shadow-lg hover:shadow-xl transition-all border-l-4 border-[#0B3954]">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-bold text-[#0B3954] group-hover:text-blue-600">Recherche avancée</h3>
              <p className="mt-1 text-sm text-slate-500">Filtrer par zone, type et budget</p>
            </div>
            <span className="text-2xl">→</span>
          </div>
        </Link>
        <Link to="/simulateur" className="group rounded-2xl bg-white p-6 shadow-lg hover:shadow-xl transition-all border-l-4 border-green-500">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-bold text-[#0B3954] group-hover:text-green-600">Simulateur de prix</h3>
              <p className="mt-1 text-sm text-slate-500">Estimer le prix d'un bien immobilier</p>
            </div>
            <span className="text-2xl">→</span>
          </div>
        </Link>
      </div>

      <section className="space-y-4">
        <div>
          <h3 className="text-xl font-bold text-[#0B3954]">Graphiques de synthese</h3>
          <p className="text-sm text-slate-500">Les graphiques sont places en bas du dashboard pour garder les informations essentielles et l'analyse en premier.</p>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          <div className="rounded-2xl bg-white p-6 shadow-lg">
            <h3 className="mb-4 text-lg font-bold text-[#0B3954]">Prix moyens par zone</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="zone" angle={-35} textAnchor="end" height={80} />
                <YAxis />
                <Tooltip formatter={(value) => `${Number(value || 0).toLocaleString("fr-FR")} FCFA/m²`} />
                <Bar dataKey="price" fill="#0B3954" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="rounded-2xl bg-white p-6 shadow-lg">
            <h3 className="mb-4 text-lg font-bold text-[#0B3954]">Repartition des sources</h3>
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

        <div className="rounded-2xl bg-white p-6 shadow-lg">
          <h3 className="mb-4 text-lg font-bold text-[#0B3954]">Evolution temporelle du prix au m²</h3>
          <ResponsiveContainer width="100%" height={320}>
            <LineChart data={timelineData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="periode" />
              <YAxis />
              <Tooltip formatter={(value) => `${Number(value || 0).toLocaleString("fr-FR")} FCFA/m²`} />
              <Legend />
              <Line type="monotone" dataKey="prix_moyen_m2" stroke="#0B3954" strokeWidth={3} name="Prix moyen / m²" />
              <Line type="monotone" dataKey="prix_median_m2" stroke="#F59E0B" strokeWidth={2} name="Prix median / m²" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="rounded-2xl bg-white p-6 shadow-lg">
          <h3 className="mb-4 text-lg font-bold text-[#0B3954]">Comparaison terrains : marché vs valeur vénale</h3>
          {terrainOtrData.length > 0 ? (
            <ResponsiveContainer width="100%" height={320}>
              <ComposedChart data={terrainOtrData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="label" angle={-30} textAnchor="end" height={80} />
                <YAxis />
                <Tooltip formatter={(value, name) => {
                  if (name === 'diff') return [`${value}%`, 'Ecart (%)'];
                  return [`${Number(value || 0).toLocaleString('fr-FR')} FCFA`, name === 'marketPrice' ? 'Prix marché' : 'Prix OTR'];
                }} />
                <Legend />
                <Bar dataKey="marketPrice" fill="#0B3954" name="Prix marché" radius={[8, 8, 0, 0]} />
                <Bar dataKey="otrPrice" fill="#F59E0B" name="Valeur vénale OTR" radius={[8, 8, 0, 0]} />
                <Line type="monotone" dataKey="diff" stroke="#EF4444" strokeWidth={3} name="Ecart (%)" />
              </ComposedChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-sm text-slate-500">Données OTR terrain non disponibles pour le moment.</p>
          )}
        </div>
      </section>
    </div>
  );
};

export default Dashboard;
