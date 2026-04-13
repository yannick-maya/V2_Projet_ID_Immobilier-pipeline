const FiltresBarre = ({ filters, setFilters }) => (
  <>
    <div className="grid gap-3 rounded-2xl border border-slate-100 bg-white p-4 shadow-md md:grid-cols-6">
      <input
        className="input-modern"
        placeholder="Mot-cle"
        value={filters.q || ""}
        onChange={(e) => setFilters((current) => ({ ...current, q: e.target.value, page: 1 }))}
      />
      <input
        className="input-modern"
        placeholder="Zone"
        list="zones-options"
        value={filters.zone}
        onChange={(e) => setFilters((current) => ({ ...current, zone: e.target.value, page: 1 }))}
      />
      <input
        className="input-modern"
        placeholder="Type bien"
        list="types-options"
        value={filters.type_bien}
        onChange={(e) => setFilters((current) => ({ ...current, type_bien: e.target.value, page: 1 }))}
      />
      <select className="input-modern" value={filters.type_offre} onChange={(e) => setFilters((current) => ({ ...current, type_offre: e.target.value, page: 1 }))}>
        <option value="">Type offre</option>
        <option value="VENTE">VENTE</option>
        <option value="LOCATION">LOCATION</option>
      </select>
      <input
        className="input-modern"
        placeholder="Prix min"
        type="number"
        value={filters.prix_min}
        onChange={(e) => setFilters((current) => ({ ...current, prix_min: e.target.value, page: 1 }))}
      />
      <input
        className="input-modern"
        placeholder="Prix max"
        type="number"
        value={filters.prix_max}
        onChange={(e) => setFilters((current) => ({ ...current, prix_max: e.target.value, page: 1 }))}
      />
    </div>
    <datalist id="zones-options">
      {(filters.options?.zones || []).map((zone) => <option key={zone} value={zone} />)}
    </datalist>
    <datalist id="types-options">
      {(filters.options?.types_bien || []).map((type) => <option key={type} value={type} />)}
    </datalist>
  </>
);

export default FiltresBarre;
