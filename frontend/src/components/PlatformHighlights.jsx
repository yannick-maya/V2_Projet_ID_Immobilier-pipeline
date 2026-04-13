import { Link } from "react-router-dom";

const defaultCards = [
  {
    icon: "Marche",
    title: "Explorer le marche",
    description:
      "Analysez les zones, les types de biens et les offres disponibles pour comprendre les niveaux de prix observes sur le marche togolais.",
    link: "/recherche",
    linkText: "Voir les annonces",
    color: "from-blue-500 to-blue-600",
  },
  {
    icon: "Indice",
    title: "Suivre l'indice",
    description:
      "Consultez l'evolution du prix au m2 dans le temps, par zone et par type de bien, avec des tendances hausse, baisse ou stabilite.",
    link: "/indice",
    linkText: "Voir l'indice",
    color: "from-green-500 to-green-600",
  },
  {
    icon: "OTR",
    title: "Comparer au referentiel",
    description:
      "Pour les terrains, la plateforme compare les prix de marche aux valeurs venales OTR afin d'identifier les biens sous ou surevalues.",
    link: "/indice",
    linkText: "Voir les ecarts",
    color: "from-emerald-500 to-emerald-600",
  },
  {
    icon: "Simulation",
    title: "Simuler un projet",
    description:
      "Estimez un prix de reference a partir de la zone, du type de bien, de la surface et des observations disponibles dans la base.",
    link: "/simulateur",
    linkText: "Lancer une simulation",
    color: "from-orange-500 to-orange-600",
  },
  {
    icon: "Sources",
    title: "Comparer les sources",
    description:
      "Mesurez les ecarts de prix et le volume d'annonces entre sources afin de juger la couverture et la coherence des donnees.",
    link: "/dashboard",
    linkText: "Voir le dashboard",
    color: "from-teal-500 to-teal-600",
  },
  {
    icon: "Compte",
    title: "Piloter vos usages",
    description:
      "Une fois connecte, vous retrouvez vos favoris, vos recherches et un tableau de bord personnalise pour suivre les zones utiles a votre projet.",
    link: "/profil",
    linkText: "Ouvrir mon profil",
    color: "from-indigo-500 to-indigo-600",
  },
];

const PlatformHighlights = ({
  cards = defaultCards,
  heading,
  subheading,
  showActions = true,
  footerAction = null,
}) => (
  <div className="space-y-8">
    {(heading || subheading) && (
      <div className="text-center">
        {heading && <h2 className="text-3xl font-bold text-gray-900">{heading}</h2>}
        {subheading && <p className="mt-2 text-lg text-gray-600">{subheading}</p>}
      </div>
    )}

    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      {cards.map((card) => (
        <div
          key={card.title}
          className="group relative overflow-hidden rounded-2xl bg-white shadow-lg transition-all duration-300 hover:shadow-2xl hover:-translate-y-1"
        >
          <div className={`absolute inset-0 bg-gradient-to-br ${card.color} opacity-0 group-hover:opacity-5 transition-opacity duration-300`} />

          <div className="relative p-6">
            <div className="mb-4 flex items-center space-x-4">
              <div className="rounded-full bg-slate-100 px-4 py-3 text-sm font-bold text-slate-700">{card.icon}</div>
              <div className={`h-12 w-1 bg-gradient-to-b ${card.color} rounded-full`} />
            </div>

            <h3 className="mb-3 text-xl font-bold text-gray-900">{card.title}</h3>
            <p className="mb-6 leading-relaxed text-gray-600">{card.description}</p>

            {showActions && card.link && (
              <Link
                to={card.link}
                className={`inline-flex items-center rounded-lg bg-gradient-to-r px-4 py-2 font-semibold text-white transition-all duration-300 hover:shadow-lg group-hover:scale-105 ${card.color}`}
              >
                {card.linkText}
                <svg className="ml-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </Link>
            )}
          </div>

          <div className="absolute -right-6 -top-6 h-24 w-24 rounded-full bg-gradient-to-br from-white/20 to-transparent blur-xl" />
          <div className="absolute -bottom-4 -left-4 h-16 w-16 rounded-full bg-gradient-to-tr from-white/10 to-transparent blur-lg" />
        </div>
      ))}
    </div>

    {footerAction}
  </div>
);

export default PlatformHighlights;
