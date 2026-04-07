import { useEffect, useMemo, useState } from "react";
import { indiceApi } from "../services/api";

const Indice = () => {
  const [indices, setIndices] = useState([]);
  const [tendances, setTendances] = useState(null);
  const [zoneFilter, setZoneFilter] = useState("Toutes");

  useEffect(() => {
    indiceApi.list().then((r) => setIndices(r.data.data || [])).catch(() => setIndices([]));
    indiceApi.tendances().then((r) => setTendances(r.data)).catch(() => setTendances(null));
  }, []);

  const zones = useMemo(() => ["Toutes", ...new Set(indices.map((i) => i.zone).filter(Boolean))], [indices]);
  const filtered = useMemo(() => (zoneFilter === "Toutes" ? indices : indices.filter((i) => i.zone === zoneFilter)), [indices, zoneFilter]);

  return (
    <div className="space-y-6">
      <div className="rounded-2xl bg-white p-6 shadow-lg">
        <h2 className="text-2xl font-bold text-[#0B3954]">Indice immobilier par zone</h2>
        <p className="text-sm text-slate-500">Suivi des tendances de prix (HAUSSE/STABLE/BAISSE) depuis MongoDB.</p>
      </div>

      {tendances && (
        <div className="grid gap-4 md:grid-cols-3">
          <div className="card-kpi"><p className="kpi-label">Hausse</p><p className="kpi-value">{tendances.HAUSSE?.count || 0}</p></div>
          <div className="card-kpi"><p className="kpi-label">Stable</p><p className="kpi-value">{tendances.STABLE?.count || 0}</p></div>
          <div className="card-kpi"><p className="kpi-label">Baisse</p><p className="kpi-value">{tendances.BAISSE?.count || 0}</p></div>
        </div>
      )}

      <div className="rounded-2xl bg-white p-6 shadow-lg">
        <div className="mb-4 flex items-center justify-between gap-3">
          <h3 className="text-lg font-bold text-[#0B3954]">Détail des indices</h3>
          <select className="input-modern w-56" value={zoneFilter} onChange={(e) => setZoneFilter(e.target.value)}>
            {zones.map((z) => <option key={z}>{z}</option>)}
          </select>
        </div>
        <div className="overflow-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b">
                <th className="px-2 py-2 text-left">Zone</th>
                <th className="px-2 py-2 text-left">Type bien</th>
                <th className="px-2 py-2 text-left">Période</th>
                <th className="px-2 py-2 text-left">Indice</th>
                <th className="px-2 py-2 text-left">Tendance</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((i) => (
                <tr key={i.id} className="border-b last:border-0">
                  <td className="px-2 py-2">{i.zone}</td>
                  <td className="px-2 py-2">{i.type_bien}</td>
                  <td className="px-2 py-2">{i.periode}</td>
                  <td className="px-2 py-2 font-semibold">{Number(i.indice_valeur || 0).toFixed(1)}</td>
                  <td className="px-2 py-2">
                    <span className={`rounded-full px-2 py-1 text-xs font-semibold ${
                      i.tendance === "HAUSSE" ? "bg-red-100 text-red-700" : i.tendance === "BAISSE" ? "bg-emerald-100 text-emerald-700" : "bg-amber-100 text-amber-700"
                    }`}>{i.tendance}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Indice;
