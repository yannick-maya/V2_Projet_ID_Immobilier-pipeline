import { useEffect, useMemo, useState } from "react";
import { scoringApi, statsApi } from "../services/api";

const Simulateur = () => {
  const [form, setForm] = useState({ zone: "", type_bien: "", type_offre: "VENTE", surface_m2: "", pieces: "" });
  const [result, setResult] = useState(null);
  const [marketSnapshot, setMarketSnapshot] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [zones, setZones] = useState([]);
  const [types, setTypes] = useState([]);

  useEffect(() => {
    statsApi.options().then((r) => {
      setZones(r.data.zones || []);
      setTypes(r.data.types_bien || []);
    }).catch(() => {
      setZones([]);
      setTypes([]);
    });
  }, []);

  useEffect(() => {
    if (!form.zone.trim() || !form.type_bien.trim()) {
      setMarketSnapshot(null);
      return;
    }

    statsApi
      .overview({ zone: form.zone.trim(), type_bien: form.type_bien.trim(), type_offre: form.type_offre })
      .then((res) => setMarketSnapshot(res.data))
      .catch(() => setMarketSnapshot(null));
  }, [form.zone, form.type_bien, form.type_offre]);

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
    <div className="space-y-5 rounded-2xl bg-white p-5 shadow-lg">
      <div>
        <h2 className="text-2xl font-bold text-[#0B3954]">Simulateur du prix de reference</h2>
        <p className="text-sm text-slate-500">
          Estimation a partir des donnees observees dans la zone, du type de bien, de la surface, des tendances et des distributions de prix.
        </p>
      </div>

      <div className="grid gap-3 md:grid-cols-5">
        <input className="input-modern" list="simulateur-zones" placeholder="Selectionner une zone" value={form.zone} onChange={(e) => setForm({ ...form, zone: e.target.value })} />
        <input className="input-modern" list="simulateur-types" placeholder="Type de bien" value={form.type_bien} onChange={(e) => setForm({ ...form, type_bien: e.target.value })} />
        <select className="input-modern" value={form.type_offre} onChange={(e) => setForm({ ...form, type_offre: e.target.value })}>
          <option value="VENTE">VENTE</option>
          <option value="LOCATION">LOCATION</option>
        </select>
        <input className="input-modern" type="number" placeholder="Surface m2" value={form.surface_m2} onChange={(e) => setForm({ ...form, surface_m2: e.target.value })} />
        <input className="input-modern" type="number" placeholder="Pieces" value={form.pieces} onChange={(e) => setForm({ ...form, pieces: e.target.value })} />
      </div>
      <datalist id="simulateur-zones">
        {zones.map((z) => <option key={z} value={z} />)}
      </datalist>
      <datalist id="simulateur-types">
        {types.map((t) => <option key={t} value={t} />)}
      </datalist>

      <button className="btn-primary w-full md:w-auto" onClick={run} disabled={loading}>{loading ? "Calcul..." : "Estimer"}</button>

      {error && <p className="rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-700">{error}</p>}

      {marketSnapshot && (
        <div className="grid gap-4 md:grid-cols-3">
          <div className="card-kpi">
            <p className="kpi-label">Prix moyen / m²</p>
            <p className="kpi-value">{Number(marketSnapshot.kpis?.prix_moyen_m2 || 0).toLocaleString("fr-FR")} FCFA</p>
          </div>
          <div className="card-kpi">
            <p className="kpi-label">Prix median / m²</p>
            <p className="kpi-value">{Number(marketSnapshot.kpis?.prix_median_m2 || 0).toLocaleString("fr-FR")} FCFA</p>
          </div>
          <div className="card-kpi">
            <p className="kpi-label">Sources comparees</p>
            <p className="kpi-value">{marketSnapshot.kpis?.sources || 0}</p>
          </div>
        </div>
      )}

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
          <div className="card-kpi">
            <p className="kpi-label">Prix de reference / m²</p>
            <p className="kpi-value">{Number(result.prix_m2_reference || 0).toLocaleString("fr-FR")} FCFA</p>
            <p className="mt-1 text-xs text-slate-500">Source: {result.source_reference}</p>
          </div>
          <div className="card-kpi">
            <p className="kpi-label">Observations utilisees</p>
            <p className="kpi-value">{result.observations || 0}</p>
            <p className="mt-1 text-xs text-slate-500">Base de calcul locale, zone ou globale selon disponibilite</p>
          </div>
          <div className="rounded-xl bg-[#F0F7FB] p-4 md:col-span-2 text-sm text-slate-700">
            Le simulateur combine la reference statistique disponible avec la surface et le nombre de pieces. Utilise cette estimation comme base de discussion et non comme prix contractuel final.
          </div>
        </div>
      )}
    </div>
  );
};

export default Simulateur;
