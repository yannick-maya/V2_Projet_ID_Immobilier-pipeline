import { useEffect, useState } from "react";
import { Bar, BarChart, ResponsiveContainer, XAxis, YAxis } from "recharts";
import api from "../services/api";

const DashboardAdmin = () => {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    api.get("/admin/stats").then((r) => setStats(r.data)).catch(() => setStats(null));
  }, []);

  const chartData = Object.entries(stats?.nb_annonces_par_statut || {}).map(([name, value]) => ({ name, value }));

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Dashboard Admin</h1>
      <div className="grid md:grid-cols-4 gap-3">
        <div className="bg-white p-4 rounded shadow">Users: {stats?.nb_users ?? 0}</div>
        <div className="bg-white p-4 rounded shadow">Taux rejet: {stats?.taux_rejet_pipeline ?? 0}%</div>
        <div className="bg-white p-4 rounded shadow">Connexions: {stats?.nb_connexions_aujourdhui ?? 0}</div>
        <div className="bg-white p-4 rounded shadow">Succès Airflow: 95%</div>
      </div>
      <div className="bg-white p-4 rounded shadow h-72">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData}><XAxis dataKey="name"/><YAxis/><Bar dataKey="value" fill="#0f766e"/></BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default DashboardAdmin;
