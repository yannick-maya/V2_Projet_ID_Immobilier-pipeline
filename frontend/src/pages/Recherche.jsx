import { useEffect, useMemo, useState } from "react";
import AnnonceCard from "../components/AnnonceCard";
import FiltresBarre from "../components/FiltresBarre";
import MapView from "../components/MapView";
import { annoncesApi, favorisApi, statsApi } from "../services/api";

const Recherche = () => {
  const [filters, setFilters] = useState({ q: "", zone: "", type_bien: "", type_offre: "", prix_min: "", prix_max: "", page: 1, limit: 20 });
  const [data, setData] = useState({ total: 0, data: [] });
  const [loading, setLoading] = useState(false);
  const [options, setOptions] = useState({ zones: [], types_bien: [], types_offre: [] });

  const load = async () => {
    setLoading(true);
    try {
      const params = {
        q: filters.q || undefined,
        zone: filters.zone || undefined,
        type_bien: filters.type_bien || undefined,
        type_offre: filters.type_offre || undefined,
        prix_min: filters.prix_min ? Number(filters.prix_min) : undefined,
        prix_max: filters.prix_max ? Number(filters.prix_max) : undefined,
        page: filters.page,
        limit: filters.limit,
      };
      // Nettoyer les undefined
      Object.keys(params).forEach(key => params[key] === undefined && delete params[key]);
      const res = await annoncesApi.list(params);
      setData(res.data || { total: 0, data: [] });
    } catch (err) {
      console.error("Erreur recherche:", err);
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
  const mapPoints = useMemo(
    () =>
      data.data
        .map((a) => ({ ...a, lat: a.localisation?.coordinates?.[1], lon: a.localisation?.coordinates?.[0] }))
        .filter((point) => Number.isFinite(point.lat) && Number.isFinite(point.lon)),
    [data.data]
  );
  const showMap = useMemo(() => Boolean(filters.zone && filters.zone.trim() && mapPoints.length), [filters.zone, mapPoints.length]);

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
        <p className="text-sm text-slate-600"><strong>{data.total}</strong> resultats</p>
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        {data.data.map((annonce) => <AnnonceCard key={annonce.id} annonce={annonce} onSave={save} />)}
      </div>

      {!loading && data.data.length === 0 && (
        <div className="rounded-2xl bg-white p-6 text-sm text-slate-600 shadow-lg">
          Aucun resultat pour ces filtres. Essaie d'alleger la zone, le type de bien ou le budget.
        </div>
      )}

      {showMap && (
        <section className="rounded-2xl bg-white p-6 shadow-lg">
          <h3 className="text-xl font-bold text-[#0B3954]">Carte de la zone recherchée</h3>
          <p className="mb-4 mt-1 text-sm text-slate-500">Zone: {filters.zone}</p>
          <MapView points={mapPoints} />
        </section>
      )}

      {!showMap && filters.zone && (
        <div className="rounded-2xl bg-slate-50 p-4 text-sm text-slate-500">
          La carte n'est pas affichee pour cette recherche car aucune annonce geolocalisee n'a ete trouvee dans cette zone.
        </div>
      )}

      <div className="flex gap-2">
        <button className="rounded-lg border border-slate-300 px-3 py-1 hover:bg-slate-50" onClick={() => setFilters({ ...filters, page: Math.max(1, filters.page - 1) })}>Précédent</button>
        <button className="rounded-lg border border-slate-300 px-3 py-1 hover:bg-slate-50" onClick={() => setFilters({ ...filters, page: filters.page + 1 })}>Suivant</button>
      </div>
    </div>
  );
};

export default Recherche;
