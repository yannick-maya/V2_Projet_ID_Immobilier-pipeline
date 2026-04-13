import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { indiceApi } from "../services/api";

const Indice = () => {
  const [indices, setIndices] = useState([]);
  const [tendances, setTendances] = useState(null);
  const [zoneFilter, setZoneFilter] = useState("Toutes");
  const [typeFilter, setTypeFilter] = useState("Tous");
  const [periodeFilter, setPeriodeFilter] = useState("Toutes");

  useEffect(() => {
    indiceApi.list().then((r) => setIndices(r.data.data || [])).catch(() => setIndices([]));
    indiceApi.tendances().then((r) => setTendances(r.data)).catch(() => setTendances(null));
  }, []);

  const zones = useMemo(() => ["Toutes", ...new Set(indices.map((i) => i.zone).filter(Boolean))], [indices]);
  const types = useMemo(() => ["Tous", ...new Set(indices.map((i) => i.type_bien).filter(Boolean))], [indices]);
  const periodes = useMemo(() => ["Toutes", ...new Set(indices.map((i) => i.periode).filter(Boolean))], [indices]);

  const filtered = useMemo(() => {
    return indices.filter((i) => {
      if (zoneFilter !== "Toutes" && i.zone !== zoneFilter) return false;
      if (typeFilter !== "Tous" && i.type_bien !== typeFilter) return false;
      if (periodeFilter !== "Toutes" && i.periode !== periodeFilter) return false;
      return true;
    });
  }, [indices, zoneFilter, typeFilter, periodeFilter]);

  return (
    <div className="space-y-5">
      <div className="rounded-2xl bg-white p-5 shadow-lg">
        <h2 className="text-2xl font-bold text-[#0B3954]">Indice immobilier par zone</h2>
        <p className="text-sm text-slate-500">Suivi des tendances de prix  depuis la base de données des donnees sourcées et etudiées .</p>
      </div>

      {tendances && (
        <div className="grid gap-4 md:grid-cols-3">
          <Link to="/indice/tendance/HAUSSE" className="card-kpi hover:shadow-lg"><p className="kpi-label">Hausse</p><p className="kpi-value">{tendances.HAUSSE?.count || 0}</p></Link>
          <Link to="/indice/tendance/STABLE" className="card-kpi hover:shadow-lg"><p className="kpi-label">Stable</p><p className="kpi-value">{tendances.STABLE?.count || 0}</p></Link>
          <Link to="/indice/tendance/BAISSE" className="card-kpi hover:shadow-lg"><p className="kpi-label">Baisse</p><p className="kpi-value">{tendances.BAISSE?.count || 0}</p></Link>
        </div>
      )}

      <div className="rounded-2xl bg-white p-5 shadow-lg">
        <div className="mb-4 grid gap-3 md:grid-cols-3">
          <select className="input-modern" value={zoneFilter} onChange={(e) => setZoneFilter(e.target.value)}>
            {zones.map((z) => <option key={z}>{z}</option>)}
          </select>
          <select className="input-modern" value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)}>
            {types.map((t) => <option key={t}>{t}</option>)}
          </select>
          <select className="input-modern" value={periodeFilter} onChange={(e) => setPeriodeFilter(e.target.value)}>
            {periodes.map((p) => <option key={p}>{p}</option>)}
          </select>
        </div>

        <div className="space-y-3 md:hidden">
          {filtered.map((i) => (
            <div key={i.id} className="rounded-xl border border-slate-100 bg-slate-50 p-4">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="font-semibold text-slate-800">{i.zone}</p>
                  <p className="text-sm text-slate-500">{i.type_bien}</p>
                </div>
                <span className={`rounded-full px-2 py-1 text-xs font-semibold ${
                  i.tendance === "HAUSSE" ? "bg-red-100 text-red-700" : i.tendance === "BAISSE" ? "bg-emerald-100 text-emerald-700" : "bg-amber-100 text-amber-700"
                }`}>{i.tendance}</span>
              </div>
              <div className="mt-3 flex items-center justify-between text-sm text-slate-600">
                <span>{i.year_month || i.periode}</span>
                <span className="font-bold text-[#0B3954]">{Number(i.indice_valeur || 0).toFixed(1)}</span>
              </div>
            </div>
          ))}
        </div>

        <div className="hidden overflow-auto md:block">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b">
                <th className="px-2 py-2 text-left">Zone</th>
                <th className="px-2 py-2 text-left">Type bien</th>
                <th className="px-2 py-2 text-left">Periode</th>
                <th className="px-2 py-2 text-left">Indice</th>
                <th className="px-2 py-2 text-left">Tendance</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((i) => (
                <tr key={i.id} className="border-b last:border-0">
                  <td className="px-2 py-2">{i.zone}</td>
                  <td className="px-2 py-2">{i.type_bien}</td>
                  <td className="px-2 py-2">{i.year_month || i.periode}</td>
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
