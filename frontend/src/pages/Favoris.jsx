import { useEffect, useState } from "react";
import AnnonceCard from "../components/AnnonceCard";
import { favorisApi } from "../services/api";

const Favoris = () => {
  const [items, setItems] = useState([]);

  const load = () => favorisApi.list().then((r) => setItems(r.data.data || [])).catch(() => setItems([]));
  useEffect(() => { load(); }, []);

  return (
    <div className="space-y-6">
      <div className="rounded-2xl bg-white p-6 shadow-lg">
        <h2 className="text-2xl font-bold text-[#0B3954]">Mes favoris</h2>
        <p className="text-sm text-slate-500">{items.length} biens sauvegardes.</p>
      </div>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {items.map((annonce) => <AnnonceCard key={annonce.id} annonce={annonce} />)}
        {items.length === 0 && <p className="text-sm text-slate-500">Aucun favori pour le moment.</p>}
      </div>
    </div>
  );
};

export default Favoris;
