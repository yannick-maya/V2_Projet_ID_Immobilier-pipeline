import { useEffect, useMemo, useState } from "react";
import AnnonceCard from "../components/AnnonceCard";
import FiltresBarre from "../components/FiltresBarre";
import MapView from "../components/MapView";
import { annoncesApi, favorisApi, statsApi } from "../services/api";

const Recherche = () => {
  const [filters, setFilters] = useState({ zone: "", type_bien: "", type_offre: "", prix_min: "", prix_max: "", page: 1, limit: 20 });
  const [data, setData] = useState({ total: 0, data: [] });
  const [loading, setLoading] = useState(false);
  const [options, setOptions] = useState({ zones: [], types_bien: [], types_offre: [] });

  const load = async () => {
    setLoading(true);
    try {
      const res = await annoncesApi.list(filters);
      setData(res.data);
    } catch {
      setData({ total: 0, data: [] });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [filters.page]);

  useEffect(() => {
    statsApi.options().then((res) => setOptions(res.data)).catch(() => setOptions({ zones: [], types_bien: [], types_offre: [] }));
  }, []);

  const save = (id) => favorisApi.add(id).catch(() => null);
  const showMap = useMemo(() => Boolean(filters.zone && filters.zone.trim()), [filters.zone]);

  return (
    <div className="space-y-5">
      <div className="rounded-2xl bg-white p-5 shadow-lg">
        <h2 className="text-2xl font-bold text-[#0B3954]">Recherche avancée</h2>
        <p className="mt-1 text-sm text-slate-500">Filtre par zone, type de bien, offre et prix. Les suggestions viennent maintenant de toute la base.</p>
      </div>

      <FiltresBarre filters={{ ...filters, options }} setFilters={setFilters} />
      <div className="flex flex-wrap items-center justify-between gap-3">
        <button
          className="btn-primary"
          onClick={() => {
            if (filters.page === 1) {
              load();
              return;
            }
            setFilters((current) => ({ ...current, page: 1 }));
          }}
        >
          {loading ? "Recherche..." : "Appliquer les filtres"}
        </button>
        <p className="text-sm text-slate-600"><strong>{data.total}</strong> résultats</p>
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        {data.data.map((annonce) => <AnnonceCard key={annonce.id} annonce={annonce} onSave={save} />)}
      </div>

      {showMap && (
        <section className="rounded-2xl bg-white p-6 shadow-lg">
          <h3 className="text-xl font-bold text-[#0B3954]">Carte de la zone recherchée</h3>
          <p className="mb-4 mt-1 text-sm text-slate-500">Zone: {filters.zone}</p>
          <MapView points={data.data.map((a) => ({ ...a, lat: a.localisation?.coordinates?.[1], lon: a.localisation?.coordinates?.[0] }))} />
        </section>
      )}

      <div className="flex gap-2">
        <button className="rounded-lg border border-slate-300 px-3 py-1 hover:bg-slate-50" onClick={() => setFilters({ ...filters, page: Math.max(1, filters.page - 1) })}>Précédent</button>
        <button className="rounded-lg border border-slate-300 px-3 py-1 hover:bg-slate-50" onClick={() => setFilters({ ...filters, page: filters.page + 1 })}>Suivant</button>
      </div>
    </div>
  );
};

export default Recherche;
