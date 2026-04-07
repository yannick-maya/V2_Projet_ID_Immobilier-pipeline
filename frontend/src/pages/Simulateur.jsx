import { useMemo, useState } from "react";
import { scoringApi } from "../services/api";

const Simulateur = () => {
  const [form, setForm] = useState({ zone: "", type_bien: "", type_offre: "VENTE", surface_m2: "", pieces: "" });
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const canSubmit = useMemo(() => form.zone.trim() && form.type_bien.trim() && Number(form.surface_m2) > 0, [form]);

  const run = async () => {
    if (!canSubmit) {
      setError("Renseigne zone, type de bien et surface.");
      return;
    }
    setError("");
    setLoading(true);
    try {
      const payload = {
        zone: form.zone.trim(),
        type_bien: form.type_bien.trim(),
        type_offre: form.type_offre,
        surface_m2: Number(form.surface_m2),
        pieces: form.pieces ? Number(form.pieces) : 0,
      };
      const res = await scoringApi.predict(payload);
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Simulation indisponible (API /scoring). Relance le backend.");
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-5 rounded-2xl bg-white p-6 shadow-lg">
      <div>
        <h2 className="text-2xl font-bold text-[#0B3954]">Simulateur IA du prix</h2>
        <p className="text-sm text-slate-500">Calcul dynamique basé sur les données MongoDB et les indices.</p>
      </div>

      <div className="grid gap-3 md:grid-cols-5">
        <input className="input-modern" placeholder="Zone (Tokoin)" value={form.zone} onChange={(e) => setForm({ ...form, zone: e.target.value })} />
        <input className="input-modern" placeholder="Type bien (Villa)" value={form.type_bien} onChange={(e) => setForm({ ...form, type_bien: e.target.value })} />
        <select className="input-modern" value={form.type_offre} onChange={(e) => setForm({ ...form, type_offre: e.target.value })}>
          <option value="VENTE">VENTE</option>
          <option value="LOCATION">LOCATION</option>
        </select>
        <input className="input-modern" type="number" placeholder="Surface m2" value={form.surface_m2} onChange={(e) => setForm({ ...form, surface_m2: e.target.value })} />
        <input className="input-modern" type="number" placeholder="Pieces" value={form.pieces} onChange={(e) => setForm({ ...form, pieces: e.target.value })} />
      </div>

      <button className="btn-primary w-full md:w-auto" onClick={run} disabled={loading}>{loading ? "Calcul..." : "Estimer"}</button>

      {error && <p className="rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-700">{error}</p>}

      {result && (
        <div className="grid gap-4 md:grid-cols-2">
          <div className="card-kpi">
            <p className="kpi-label">Prix estime</p>
            <p className="kpi-value">{Number(result.prix_estime || 0).toLocaleString()} FCFA</p>
            <p className="mt-1 text-xs text-slate-500">
              Intervalle: {Number(result.intervalle_confiance?.[0] || 0).toLocaleString()} - {Number(result.intervalle_confiance?.[1] || 0).toLocaleString()} FCFA
            </p>
          </div>
          <div className="card-kpi">
            <p className="kpi-label">Indice zone</p>
            <p className="kpi-value">{result.indice_zone}</p>
            <p className="mt-1 text-xs text-slate-500">Indice valeur: {Number(result.indice_valeur || 100).toFixed(1)}</p>
          </div>
          <div className="rounded-xl bg-[#F0F7FB] p-4 md:col-span-2 text-sm text-slate-700">
            Base: {result.source_reference} · Observations: {result.observations} · Ref: {Number(result.prix_m2_reference || 0).toLocaleString()} FCFA/m²
          </div>
        </div>
      )}
    </div>
  );
};

export default Simulateur;
