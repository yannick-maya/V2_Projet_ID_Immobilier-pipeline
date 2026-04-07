import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { indiceApi } from "../services/api";

const normalizeTrend = (value) => {
  const upper = (value || "").toUpperCase();
  if ([ "HAUSSE", "STABLE", "BAISSE" ].includes(upper)) return upper;
  return "STABLE";
};

const IndiceTendance = () => {
  const { tendance } = useParams();
  const trend = normalizeTrend(tendance);
  const [rows, setRows] = useState([]);
  const [zone, setZone] = useState("Toutes");
  const [typeBien, setTypeBien] = useState("Tous");
  const [periode, setPeriode] = useState("Toutes");

  useEffect(() => {
    indiceApi.list({ tendance: trend }).then((r) => setRows(r.data.data || [])).catch(() => setRows([]));
  }, [trend]);

  const zones = useMemo(() => ["Toutes", ...new Set(rows.map((r) => r.zone).filter(Boolean))], [rows]);
  const types = useMemo(() => ["Tous", ...new Set(rows.map((r) => r.type_bien).filter(Boolean))], [rows]);
  const periodes = useMemo(() => ["Toutes", ...new Set(rows.map((r) => r.periode).filter(Boolean))], [rows]);

  const filtered = useMemo(() => {
    return rows.filter((r) => {
      if (zone !== "Toutes" && r.zone !== zone) return false;
      if (typeBien !== "Tous" && r.type_bien !== typeBien) return false;
      if (periode !== "Toutes" && r.periode !== periode) return false;
      return true;
    });
  }, [rows, zone, typeBien, periode]);

  return (
    <div className="space-y-6">
      <div className="rounded-2xl bg-white p-6 shadow-lg">
        <h2 className="text-2xl font-bold text-[#0B3954]">Zones en {trend}</h2>
        <p className="text-sm text-slate-500">{filtered.length} enregistrements apres filtres.</p>
        <Link to="/indice" className="mt-3 inline-block text-sm font-semibold text-[#065A82] hover:underline">← Retour a la page indice</Link>
      </div>

      <div className="grid gap-3 rounded-2xl bg-white p-4 shadow-lg md:grid-cols-3">
        <select className="input-modern" value={zone} onChange={(e) => setZone(e.target.value)}>
          {zones.map((z) => <option key={z}>{z}</option>)}
        </select>
        <select className="input-modern" value={typeBien} onChange={(e) => setTypeBien(e.target.value)}>
          {types.map((t) => <option key={t}>{t}</option>)}
        </select>
        <select className="input-modern" value={periode} onChange={(e) => setPeriode(e.target.value)}>
          {periodes.map((p) => <option key={p}>{p}</option>)}
        </select>
      </div>

      <div className="rounded-2xl bg-white p-6 shadow-lg overflow-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b">
              <th className="px-2 py-2 text-left">Zone</th>
              <th className="px-2 py-2 text-left">Type bien</th>
              <th className="px-2 py-2 text-left">Periode</th>
              <th className="px-2 py-2 text-left">Indice</th>
              <th className="px-2 py-2 text-left">Nb annonces</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((r) => (
              <tr key={r.id} className="border-b last:border-0">
                <td className="px-2 py-2">{r.zone}</td>
                <td className="px-2 py-2">{r.type_bien}</td>
                <td className="px-2 py-2">{r.periode}</td>
                <td className="px-2 py-2 font-semibold">{Number(r.indice_valeur || 0).toFixed(1)}</td>
                <td className="px-2 py-2">{r.nombre_annonces || 0}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default IndiceTendance;

