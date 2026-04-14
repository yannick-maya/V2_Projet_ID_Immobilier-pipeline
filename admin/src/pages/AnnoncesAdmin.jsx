import { useEffect, useState } from "react";
import api from "../services/api";

const AnnoncesAdmin = () => {
  const [items, setItems] = useState([]);

  const load = () => api.get("/admin/annonces").then((r) => setItems(r.data.data || [])).catch(() => setItems([]));
  useEffect(() => { load(); }, []);

  const validateAll = async () => {
    const pendingItems = items.filter(a => a.statut !== "valide");
    if (pendingItems.length === 0) {
      alert("Toutes les annonces sont déjà validées !");
      return;
    }

    if (!confirm(`Valider ${pendingItems.length} annonce(s) ?`)) return;

    try {
      for (const item of pendingItems) {
        await api.put(`/admin/annonces/${item.id}/valider`);
      }
      load();
      alert("Toutes les annonces ont été validées !");
    } catch (error) {
      alert("Erreur lors de la validation en masse");
    }
  };

  const inspect = (annonce) => {
    const details = `
Titre: ${annonce.titre}
Zone: ${annonce.zone}
Type: ${annonce.type_bien} - ${annonce.type_offre}
Prix: ${formatPrix(annonce.prix)}
Prix/m²: ${formatPrix(annonce.prix_m2)}
Surface: ${annonce.surface_m2 || 'N/A'} m²
Prix OTR: ${formatPrix(annonce.prix_otr)}
Écart OTR: ${annonce.difference_otr ? annonce.difference_otr.toFixed(1) + '%' : 'N/A'}
Statut OTR: ${annonce.statut_otr || 'N/A'}
Source: ${annonce.source}
Date: ${annonce.date_annonce || 'N/A'}
Description: ${annonce.description || 'N/A'}
    `.trim();

    alert(details);
  };

  const formatPrix = (prix) => {
    if (!prix) return "-";
    return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'XAF' }).format(prix);
  };

  const getStatutOtrBadge = (statut) => {
    if (!statut) return null;
    const colors = {
      "sous-evalue": "bg-blue-100 text-blue-800",
      "sur-evalue": "bg-red-100 text-red-800",
      "conforme": "bg-green-100 text-green-800"
    };
    return <span className={`px-2 py-1 rounded-full text-xs font-medium ${colors[statut] || "bg-gray-100 text-gray-800"}`}>{statut.replace("-", " ")}</span>;
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Gestion des annonces</h2>
        <button
          onClick={validateAll}
          className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors font-medium"
        >
          Valider tout ({items.filter(a => a.statut !== "valide").length})
        </button>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm border-collapse">
          <thead>
            <tr className="bg-gray-50">
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-48">Titre</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Zone</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type Bien</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Prix</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Prix OTR</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Différence OTR</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Statut OTR</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Statut</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {items.map((a) => (
              <tr key={a.id} className="hover:bg-gray-50">
                <td className="px-4 py-4 text-sm font-medium text-gray-900 max-w-xs">
                  <div className="truncate" title={a.titre}>
                    {a.titre}
                  </div>
                </td>
                <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500">{a.zone}</td>
                <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500">{a.type_bien}</td>
                <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900 font-semibold">{formatPrix(a.prix)}</td>
                <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500">{formatPrix(a.prix_otr)}</td>
                <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                  {a.difference_otr ? `${a.difference_otr.toFixed(1)}%` : "-"}
                </td>
                <td className="px-4 py-4 whitespace-nowrap">{getStatutOtrBadge(a.statut_otr)}</td>
                <td className="px-4 py-4 whitespace-nowrap">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    a.statut === "valide" ? "bg-green-100 text-green-800" :
                    a.statut === "rejete" ? "bg-red-100 text-red-800" :
                    "bg-yellow-100 text-yellow-800"
                  }`}>
                    {a.statut || "valide"}
                  </span>
                </td>
                <td className="px-4 py-4 whitespace-nowrap text-sm font-medium space-x-1">
                  <button
                    onClick={() => inspect(a)}
                    className="px-2 py-1 bg-blue-600 text-white rounded text-xs hover:bg-blue-700 transition-colors"
                    title="Inspecter les détails"
                  >
                    👁️
                  </button>
                  <button onClick={() => validate(a.id)} className="px-2 py-1 bg-emerald-600 text-white rounded text-xs hover:bg-emerald-700 transition-colors">✓</button>
                  <button onClick={() => refuse(a.id)} className="px-2 py-1 bg-rose-600 text-white rounded text-xs hover:bg-rose-700 transition-colors">✗</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default AnnoncesAdmin;
