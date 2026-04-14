import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const UserWelcomeCards = () => {
  const { user } = useAuth();

  const cards = [
    {
      icon: "",
      title: "Explorez le Marché",
      description: "Découvrez les tendances immobilières par zone et type de bien. Nos analyses sont basées sur des données réelles du marché togolais.",
      link: "/recherche",
      linkText: "Voir les annonces",
      color: "from-blue-500 to-blue-600"
    },
    {
      icon: "",
      title: "Analysez les Prix",
      description: "Comprenez les prix au m² par quartier. Nous comparons les offres du marché avec les valeurs officielles pour une transparence totale.",
      link: "/indice",
      linkText: "Voir les indices",
      color: "from-green-500 to-green-600"
    },
    {
      icon: "",
      title: "Vos Favoris",
      description: "Sauvegardez et suivez les biens qui vous intéressent. Recevez des notifications sur les évolutions de prix.",
      link: "/favoris",
      linkText: "Mes favoris",
      color: "from-purple-500 to-purple-600"
    },
    {
      icon: "",
      title: "Simulez votre Projet",
      description: "Calculez vos mensualités, estimez les frais annexes et planifiez votre investissement immobilier.",
      link: "/simulateur",
      linkText: "Simuler",
      color: "from-orange-500 to-orange-600"
    },
    {
      icon: "",
      title: "Tendances du Marché",
      description: "Suivez l'évolution des prix immobiliers dans le temps. Identifiez les meilleures opportunités d'achat ou de vente.",
      link: "/indice-tendance",
      linkText: "Voir les tendances",
      color: "from-teal-500 to-teal-600"
    },
    {
      icon: "",
      title: "Votre Profil",
      description: "Gérez vos informations personnelles, vos préférences de recherche et l'historique de vos consultations.",
      link: "/profil",
      linkText: "Mon profil",
      color: "from-indigo-500 to-indigo-600"
    }
  ];

  return (
    <div className="space-y-8">
      {/* Message de bienvenue personnalisé */}
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">
          Bienvenue, {user?.email?.split('@')[0]} ! 
        </h2>
        <p className="text-lg text-gray-600">
          Découvrez les outils puissants d'ID Immobilier pour votre projet immobilier
        </p>
      </div>

      {/* Cards explicatives */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {cards.map((card, index) => (
          <div
            key={index}
            className="group relative overflow-hidden rounded-2xl bg-white shadow-lg transition-all duration-300 hover:shadow-2xl hover:-translate-y-1"
          >
            {/* Background gradient */}
            <div className={`absolute inset-0 bg-gradient-to-br ${card.color} opacity-0 group-hover:opacity-5 transition-opacity duration-300`} />

            {/* Content */}
            <div className="relative p-6">
              <div className="flex items-center space-x-4 mb-4">
                <div className="text-4xl">{card.icon}</div>
                <div className={`h-12 w-1 bg-gradient-to-b ${card.color} rounded-full`} />
              </div>

              <h3 className="text-xl font-bold text-gray-900 mb-3">
                {card.title}
              </h3>

              <p className="text-gray-600 mb-6 leading-relaxed">
                {card.description}
              </p>

              <Link
                to={card.link}
                className={`inline-flex items-center px-4 py-2 bg-gradient-to-r ${card.color} text-white font-semibold rounded-lg hover:shadow-lg transition-all duration-300 group-hover:scale-105`}
              >
                {card.linkText}
                <svg className="ml-2 w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </Link>
            </div>

            {/* Decorative elements */}
            <div className="absolute -top-6 -right-6 w-24 h-24 bg-gradient-to-br from-white/20 to-transparent rounded-full blur-xl" />
            <div className="absolute -bottom-4 -left-4 w-16 h-16 bg-gradient-to-tr from-white/10 to-transparent rounded-full blur-lg" />
          </div>
        ))}
      </div>

      {/* Section informative sur les données OTR */}
      <div className="mt-12 rounded-2xl bg-gradient-to-r from-emerald-50 to-teal-50 border border-emerald-200 p-8">
        <div className="flex items-start space-x-4">
          <div className="flex-shrink-0">
            <div className="w-12 h-12 bg-emerald-100 rounded-full flex items-center justify-center">
              <svg className="w-6 h-6 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
          <div>
            <h3 className="text-xl font-bold text-emerald-900 mb-2">
              Transparence des Prix Garantie
            </h3>
            <p className="text-emerald-800 mb-4">
              Pour les terrains, nous comparons systématiquement les prix du marché avec les valeurs officielles
              de l'Office Togolais des Recettes (OTR). Vous savez toujours si un bien est sous-évalué,
              sur-évalué ou conforme aux standards officiels.
            </p>
            <div className="flex flex-wrap gap-3">
              <div className="flex items-center space-x-2 text-sm text-emerald-700">
                <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                <span>Sous-évalué (&lt; -10%)</span>
              </div>
              <div className="flex items-center space-x-2 text-sm text-emerald-700">
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                <span>Conforme (-10% à +10%)</span>
              </div>
              <div className="flex items-center space-x-2 text-sm text-emerald-700">
                <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                <span>Sur-évalué (&gt; +10%)</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Call to action */}
      <div className="text-center py-8">
        <Link
          to="/recherche"
          className="inline-flex items-center px-8 py-4 bg-gradient-to-r from-[#065A82] to-[#1C7293] text-white font-bold text-lg rounded-xl hover:shadow-2xl hover:scale-105 transition-all duration-300"
        >
          Commencer mon exploration immobilière
          <svg className="ml-3 w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
          </svg>
        </Link>
      </div>
    </div>
  );
};

export default UserWelcomeCards;