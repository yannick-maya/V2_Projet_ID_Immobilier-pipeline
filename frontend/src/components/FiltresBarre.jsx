const FiltresBarre = ({ filters, setFilters }) => (
  <div className="grid gap-3 rounded-2xl border border-slate-100 bg-white p-4 shadow-md md:grid-cols-5">
    <input
      className="input-modern"
      placeholder="Zone"
      value={filters.zone}
      onChange={(e) => setFilters({ ...filters, zone: e.target.value })}
    />
    <input
      className="input-modern"
      placeholder="Type bien"
      value={filters.type_bien}
      onChange={(e) => setFilters({ ...filters, type_bien: e.target.value })}
    />
    <select className="input-modern" value={filters.type_offre} onChange={(e) => setFilters({ ...filters, type_offre: e.target.value })}>
      <option value="">Type offre</option>
      <option value="VENTE">VENTE</option>
      <option value="LOCATION">LOCATION</option>
    </select>
    <input
      className="input-modern"
      placeholder="Prix min"
      type="number"
      value={filters.prix_min}
      onChange={(e) => setFilters({ ...filters, prix_min: e.target.value })}
    />
    <input
      className="input-modern"
      placeholder="Prix max"
      type="number"
      value={filters.prix_max}
      onChange={(e) => setFilters({ ...filters, prix_max: e.target.value })}
    />
  </div>
);

export default FiltresBarre;
