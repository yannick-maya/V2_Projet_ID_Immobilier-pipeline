import { useEffect, useState } from "react";
import api from "../services/api";

const AnnoncesAdmin = () => {
  const [items, setItems] = useState([]);

  const load = () => api.get("/admin/annonces").then((r) => setItems(r.data.data || [])).catch(() => setItems([]));
  useEffect(() => { load(); }, []);

  const validate = async (id) => { await api.put(`/admin/annonces/${id}/valider`); load(); };
  const refuse = async (id) => { await api.put(`/admin/annonces/${id}/refuser`); load(); };

  return (
    <div className="bg-white p-4 rounded shadow">
      <h2 className="text-xl font-semibold mb-4">Gestion des annonces</h2>
      <table className="w-full text-sm">
        <thead><tr><th>Titre</th><th>Zone</th><th>Statut</th><th>Actions</th></tr></thead>
        <tbody>
          {items.map((a) => (
            <tr key={a.id}>
              <td>{a.titre}</td><td>{a.zone}</td><td>{a.statut || "valide"}</td>
              <td className="space-x-2">
                <button onClick={() => validate(a.id)} className="px-2 py-1 bg-emerald-600 text-white rounded">Valider</button>
                <button onClick={() => refuse(a.id)} className="px-2 py-1 bg-rose-600 text-white rounded">Refuser</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default AnnoncesAdmin;
