import { useEffect, useState } from "react";
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, ResponsiveContainer, BarChart, Bar, XAxis, YAxis } from "recharts";
import api from "../services/api";

const OkrAdmin = () => {
  const [data, setData] = useState(null);

  useEffect(() => {
    api.get("/admin/okr").then((r) => setData(r.data)).catch(() => setData(null));
  }, []);

  return (
    <div className="grid lg:grid-cols-2 gap-4">
      <div className="bg-white p-4 rounded shadow h-80">
        <h3 className="font-semibold mb-2">Radar maturité digitale</h3>
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={data?.okr || []}><PolarGrid /><PolarAngleAxis dataKey="label" /><Radar dataKey="value" stroke="#0f766e" fill="#0f766e" fillOpacity={0.5} /></RadarChart>
        </ResponsiveContainer>
      </div>
      <div className="bg-white p-4 rounded shadow h-80">
        <h3 className="font-semibold mb-2">Progression OKR</h3>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data?.okr || []}><XAxis dataKey="label" /><YAxis /><Bar dataKey="value" fill="#f97316" /></BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default OkrAdmin;
