import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import MapView from "../components/MapView";
import { annoncesApi, favorisApi, statsApi } from "../services/api";

const BienDetail = () => {
  const { id } = useParams();
  const [annonce, setAnnonce] = useState(null);
  const [stats, setStats] = useState([]);

  useEffect(() => {
    annoncesApi.get(id).then((r) => setAnnonce(r.data)).catch(() => setAnnonce(null));
    statsApi.list().then((r) => setStats(r.data.data || [])).catch(() => setStats([]));
  }, [id]);

  if (!annonce) return <div className="rounded-2xl bg-white p-6 shadow-lg">Chargement...</div>;

  const zoneStats = stats.find((s) => s.zone === annonce.zone && s.type_bien === annonce.type_bien);

  return (
    <div className="space-y-6 rounded-2xl bg-white p-6 shadow-lg">
      <div>
        <h1 className="text-2xl font-bold text-[#0B3954]">{annonce.titre}</h1>
        <p className="mt-1 text-slate-600">{annonce.type_bien} · {annonce.type_offre} · {annonce.zone}</p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <div className="card-kpi"><p className="kpi-label">Prix</p><p className="kpi-value">{Number(annonce.prix || 0).toLocaleString()} FCFA</p></div>
        <div className="card-kpi"><p className="kpi-label">Prix/m²</p><p className="kpi-value">{Number(annonce.prix_m2 || 0).toLocaleString()} FCFA</p></div>
        <div className="card-kpi"><p className="kpi-label">Référence zone</p><p className="kpi-value">{Number(zoneStats?.prix_moyen_m2 || 0).toLocaleString()} FCFA</p></div>
      </div>

      <button className="btn-primary w-full md:w-auto" onClick={() => favorisApi.add(id)}>Ajouter aux favoris</button>

      <MapView points={[{ ...annonce, lat: annonce.localisation?.coordinates?.[1], lon: annonce.localisation?.coordinates?.[0] }]} />
    </div>
  );
};

export default BienDetail;
