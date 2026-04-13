import { useEffect, useState } from "react";
import PlatformHighlights from "../components/PlatformHighlights";
import { statsApi } from "../services/api";

const About = () => {
  const [project, setProject] = useState(null);
  const [overview, setOverview] = useState(null);

  useEffect(() => {
    statsApi.project().then((res) => setProject(res.data)).catch(() => setProject(null));
    statsApi.overview().then((res) => setOverview(res.data)).catch(() => setOverview(null));
  }, []);

  const functionalityCards = (project?.functionalites || []).map((item, index) => ({
    icon: ["", "", "", "", ""][index % 5],
    title: item.charAt(0).toUpperCase() + item.slice(1),
    description: item,
    color: ["from-blue-500 to-blue-600", "from-green-500 to-green-600", "from-orange-500 to-orange-600", "from-teal-500 to-teal-600", "from-indigo-500 to-indigo-600"][index % 5],
  }));

  const analysisFeatures = [
    { icon: "", title: "Analyses Géographiques", description: "Segmentation par zone administrative avec indicateurs détaillés (prix moyen, médiane, tendances, volume)." },
    { icon: "", title: "Analyses Temporelles", description: "Suivi mensuel et trimestriel du marché pour identifier les tendances d'évolution des prix." },
    { icon: "", title: "Comparaison de Sources", description: "Analyse comparative des données par source pour valider la cohérence et couvrir les lacunes." },
    { icon: "", title: "Calcul du Prix/m²", description: "Calcul standardisé avec contrôle des valeurs extrêmes pour des comparaisons fiables." },
  ];

  const indexFeatures = [
    { icon: " ", title: "Suivi d'Evolution", description: "Indice calculé mensuellement et trimestriellement pour suivre les mouvements du marché." },
    { icon: "", title: "Segmentation", description: "Indice par type de bien et par zone pour une analyse granulaire des marchés spécifiques." },
    { icon: "", title: "Détection de Tendances", description: "Identifie les zones en hausse, stabilité ou baisse pour mieux anticiper les opportunités." },
    { icon: "", title: "Évaluation OTR", description: "Compare les prix de marché aux valeurs vénales officielles pour identifier les anomalies." },
  ];

  return (
    <div className="space-y-6">
      {/* Hero Section */}
      <section className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-[#0B3954] via-[#146C8D] to-[#00B4D8] px-6 py-16 text-white shadow-xl md:px-10">
        <div className="absolute -right-20 -top-20 h-40 w-40 rounded-full bg-white/10 blur-3xl" />
        <div className="absolute -bottom-10 left-10 h-32 w-32 rounded-full bg-[#F59E0B]/10 blur-2xl" />
        <div className="relative max-w-4xl space-y-6">
          <span className="inline-flex rounded-full bg-white/15 px-4 py-1 text-sm font-medium backdrop-blur-sm border border-white/20">
             Plateforme d'analyse immobilière
          </span>
          <h1 className="text-5xl font-black leading-tight">{project?.title || "ID Immobilier"}</h1>
          <p className="max-w-3xl text-lg text-white/90">
            {project?.description ||
              "Une plateforme pour suivre les prix au m², comparer les zones, les sources de données et l'évolution du marché immobilier togolais."}
          </p>
        </div>
      </section>

      {/* KPIs Section */}
      <section className="grid gap-4 md:grid-cols-4">
        <div className="card-kpi">
          <p className="kpi-label">Zones analysées</p>
          <p className="kpi-value">{overview?.kpis?.zones || 0}</p>
        </div>
        <div className="card-kpi">
          <p className="kpi-label">Annonces exploitées</p>
          <p className="kpi-value">{overview?.kpis?.annonces || 0}</p>
        </div>
        <div className="card-kpi">
          <p className="kpi-label">Prix moyen / m²</p>
          <p className="kpi-value text-sm">{Number(overview?.kpis?.prix_moyen_m2 || 0).toLocaleString("fr-FR")}</p>
          <p className="text-xs text-slate-500 mt-1">FCFA</p>
        </div>
        <div className="card-kpi">
          <p className="kpi-label">Sources comparées</p>
          <p className="kpi-value">{overview?.kpis?.sources || 0}</p>
        </div>
      </section>

      {/* Mission Section */}
      <section className="rounded-2xl bg-white p-8 shadow-lg">
        <h2 className="text-3xl font-bold text-[#0B3954]">Notre mission</h2>
        <p className="mt-4 text-slate-700 text-lg leading-relaxed">
          Rendre l'information immobilière plus transparente et intelligente en centralisant les données multi-sources, 
          en produisant des indicateurs fiables basés sur le prix au m², et en permettant une comparaison objective 
          entre les marchés, les sources et les prix officiels.
        </p>
      </section>

      {/* Analysis Features */}
      <section className="space-y-4">
        <h2 className="text-3xl font-bold text-[#0B3954]">Analyses métier</h2>
        <div className="grid gap-4 md:grid-cols-2">
          {analysisFeatures.map((feature, idx) => (
            <div key={idx} className="rounded-xl bg-white p-6 shadow-lg hover:shadow-xl transition-shadow border-l-4 border-[#00B4D8]">
              <div className="flex items-start gap-4">
                <span className="text-3xl">{feature.icon}</span>
                <div>
                  <h3 className="font-bold text-[#0B3954]">{feature.title}</h3>
                  <p className="text-sm text-slate-600 mt-2">{feature.description}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Indice Features */}
      <section className="space-y-4">
        <h2 className="text-3xl font-bold text-[#0B3954]">Indice immobilier ID</h2>
        <p className="text-slate-700">Un indicateur synthétique permettant de suivre, comparer et anticiper les mouvements du marché immobilier.</p>
        <div className="grid gap-4 md:grid-cols-2">
          {indexFeatures.map((feature, idx) => (
            <div key={idx} className="rounded-xl bg-gradient-to-br from-amber-50 to-orange-50 p-6 shadow-lg hover:shadow-xl transition-shadow border-l-4 border-[#F59E0B]">
              <div className="flex items-start gap-4">
                <span className="text-3xl">{feature.icon}</span>
                <div>
                  <h3 className="font-bold text-[#0B3954]">{feature.title}</h3>
                  <p className="text-sm text-slate-600 mt-2">{feature.description}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* MVP Section */}
      <section className="rounded-2xl bg-gradient-to-br from-slate-50 to-white p-8 shadow-lg border border-slate-200">
        <h2 className="text-2xl font-bold text-[#0B3954] mb-4">Parcours utilisateur (MVP)</h2>
        <div className="grid gap-3 md:grid-cols-2">
          {(project?.mvp || [
            "Sélectionner une zone",
            "Visualiser le prix au m²",
            "Consulter l'indice immobilier",
            "Comparer plusieurs zones"
          ]).map((item, idx) => (
            <div key={idx} className="flex items-start gap-3">
              <span className="text-xl font-bold text-[#00B4D8] mt-1">{idx + 1}.</span>
              <p className="text-slate-700">{item.charAt(0).toUpperCase() + item.slice(1)}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Features Display */}
      <PlatformHighlights
        heading="Fonctionnalités de la plateforme"
        subheading="Les modules ci-dessous structurent l'expérience utilisateur et les analyses métier."
        cards={functionalityCards}
        showActions={false}
      />
    </div>
  );
};

export default About;
