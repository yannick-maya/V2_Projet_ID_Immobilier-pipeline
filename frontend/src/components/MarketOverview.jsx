const formatNumber = (value, options = {}) =>
  Number(value || 0).toLocaleString("fr-FR", { maximumFractionDigits: 0, ...options });

const palette = ["#065A82", "#1C7293", "#00B4D8", "#F59E0B", "#7CC6D9", "#0B3954"];

const MetricCard = ({ label, value, note }) => (
  <div className="card-kpi">
    <p className="kpi-label">{label}</p>
    <p className="kpi-value">{value}</p>
    {note && <p className="mt-2 text-xs text-slate-500">{note}</p>}
  </div>
);

const ChartCard = ({ title, subtitle, children, className = "" }) => (
  <section className={`rounded-2xl border border-slate-100 bg-white p-4 md:p-5 shadow-md ${className}`}>
    <div className="rounded-xl bg-[#146C8D] px-4 py-3 text-white">
      <h3 className="text-base font-bold md:text-lg">{title}</h3>
      {subtitle && <p className="mt-1 text-xs text-white/80">{subtitle}</p>}
    </div>
    <div className="mt-4">{children}</div>
  </section>
);

const HorizontalDualBars = ({ rows }) => {
  const maxValue = Math.max(...rows.flatMap((row) => [row.mean, row.median]), 1);
  return (
    <div className="space-y-4">
      {rows.map((row) => (
        <div key={row.label} className="grid gap-2 md:grid-cols-[150px_1fr] md:items-center">
          <div>
            <p className="text-sm font-semibold text-slate-800">{row.label}</p>
            <p className="text-xs text-slate-500">{row.count} annonces</p>
          </div>
          <div className="space-y-2">
            <div>
              <div className="mb-1 flex items-center justify-between text-xs text-slate-500">
                <span>Prix moyen</span>
                <span>{formatNumber(row.mean)} FCFA/m²</span>
              </div>
              <div className="h-3 overflow-hidden rounded-full bg-slate-100">
                <div className="h-full rounded-full bg-[#065A82]" style={{ width: `${(row.mean / maxValue) * 100}%` }} />
              </div>
            </div>
            <div>
              <div className="mb-1 flex items-center justify-between text-xs text-slate-500">
                <span>Prix médian</span>
                <span>{formatNumber(row.median)} FCFA/m²</span>
              </div>
              <div className="h-3 overflow-hidden rounded-full bg-slate-100">
                <div className="h-full rounded-full bg-[#55C5DE]" style={{ width: `${(row.median / maxValue) * 100}%` }} />
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

const DonutChart = ({ rows }) => {
  const total = rows.reduce((sum, row) => sum + row.count, 0) || 1;
  let cursor = 0;
  const gradient = rows
    .map((row, index) => {
      const start = (cursor / total) * 100;
      cursor += row.count;
      const end = (cursor / total) * 100;
      return `${palette[index % palette.length]} ${start}% ${end}%`;
    })
    .join(", ");

  return (
    <div className="grid gap-5 lg:grid-cols-[220px_1fr] lg:items-center">
      <div className="mx-auto flex h-36 w-36 items-center justify-center rounded-full md:h-44 md:w-44" style={{ background: `conic-gradient(${gradient || "#cbd5e1 0 100%"})` }}>
        <div className="flex h-24 w-24 flex-col items-center justify-center rounded-full bg-white text-center shadow-inner">
          <span className="text-xs uppercase tracking-wide text-slate-500">Sources</span>
          <span className="text-xl font-black text-[#0B3954]">{formatNumber(total)}</span>
        </div>
      </div>
      <div className="space-y-3">
        {rows.map((row, index) => {
          const share = (row.count / total) * 100;
          return (
            <div key={row.label} className="flex items-center justify-between gap-3 rounded-xl border border-slate-100 px-3 py-2">
              <div className="flex items-center gap-3">
                <span className="h-3 w-3 rounded-full" style={{ backgroundColor: palette[index % palette.length] }} />
                <span className="text-sm font-medium text-slate-700">{row.label}</span>
              </div>
              <span className="text-sm font-semibold text-slate-600">{share.toFixed(1)}%</span>
            </div>
          );
        })}
      </div>
    </div>
  );
};

const VerticalBars = ({ rows }) => {
  const maxValue = Math.max(...rows.map((row) => row.mean), 1);
  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {rows.map((row, index) => (
        <div key={row.label} className="rounded-xl border border-slate-100 bg-slate-50 p-4">
          <div className="flex h-40 items-end">
            <div
              className="w-full rounded-t-xl"
              style={{
                height: `${Math.max(14, (row.mean / maxValue) * 100)}%`,
                background: palette[index % palette.length],
              }}
            />
          </div>
          <p className="mt-3 text-sm font-semibold text-slate-800">{row.label}</p>
          <p className="text-lg font-extrabold text-[#0B3954]">{formatNumber(row.mean)} FCFA/m²</p>
          <p className="text-xs text-slate-500">Médiane {formatNumber(row.median)} · {row.count} annonces</p>
        </div>
      ))}
    </div>
  );
};

const TrendsPanel = ({ tendances }) => (
  <div className="grid gap-3 md:grid-cols-3">
    {["HAUSSE", "STABLE", "BAISSE"].map((key) => (
      <div key={key} className="rounded-xl border border-slate-100 bg-slate-50 p-4">
        <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{key}</p>
        <p className="mt-2 text-2xl font-black text-[#0B3954]">{formatNumber(tendances?.[key]?.count || 0)}</p>
        <p className="mt-1 text-xs text-slate-500">Zones distinctes</p>
      </div>
    ))}
  </div>
);

const MarketOverview = ({ overview, compact = false, isAuthenticated = false }) => {
  const topZones = overview?.top_zones || [];
  const sources = overview?.sources || [];
  const propertyTypes = overview?.types_bien || [];
  const tendances = overview?.tendances || null;
  const temporalite = overview?.temporalite || {};
  const kpis = overview?.kpis || {};

  return (
    <div className="space-y-5">
      <section className={`grid gap-4 ${compact ? "sm:grid-cols-2 xl:grid-cols-4" : "sm:grid-cols-2 xl:grid-cols-5"}`}>
        <MetricCard label="Prix moyen / m²" value={`${formatNumber(kpis.prix_moyen_m2)} FCFA`} note="moyenne robuste hors extrêmes" />
        <MetricCard label="Prix médian / m²" value={`${formatNumber(kpis.prix_median_m2)} FCFA`} note="référence de marché plus stable" />
        <MetricCard label="Zones analysées" value={formatNumber(kpis.zones)} />
        <MetricCard label="Annonces" value={formatNumber(kpis.annonces)} />
        {!compact && <MetricCard label="Sources" value={formatNumber(kpis.sources)} />}
      </section>

      <div className="rounded-2xl border border-amber-100 bg-amber-50 px-4 py-3 text-sm text-amber-900">
        Temporalité des données: {temporalite.periodes?.length ? temporalite.periodes.join(", ") : "non fiabilisée"}.
        {temporalite.periodes_invalides ? ` ${formatNumber(temporalite.periodes_invalides)} enregistrements ont une période invalide.` : ""}
      </div>

      <div className={`grid gap-5 ${compact ? "xl:grid-cols-1" : "xl:grid-cols-[1.6fr_1fr]"}`}>
        <ChartCard title="Prix moyen et médian au m² par zone" subtitle="Calculé sur le prix/m² de chaque bien, avec filtrage des valeurs extrêmes">
          {topZones.length ? <HorizontalDualBars rows={topZones} /> : <p className="text-sm text-slate-500">Aucune zone exploitable pour le moment.</p>}
        </ChartCard>

        <div className="space-y-5">
          {!compact && (
            <ChartCard title="Répartition par type de bien">
              {propertyTypes.length ? <DonutChart rows={propertyTypes.map(pt => ({ label: pt.label, count: pt.count }))} /> : <p className="text-sm text-slate-500">Aucune donnée disponible.</p>}
            </ChartCard>
          )}

          {isAuthenticated && (
            <ChartCard title="Synthèse des tendances">
              <TrendsPanel tendances={tendances} />
            </ChartCard>
          )}
        </div>
      </div>

      {isAuthenticated && !compact && (
        <ChartCard title="Prix moyen au m² par type de bien">
          {propertyTypes.length ? <VerticalBars rows={propertyTypes.slice(0, 5)} /> : <p className="text-sm text-slate-500">Pas assez de données pour comparer les types.</p>}
        </ChartCard>
      )}
    </div>
  );
};

export default MarketOverview;
