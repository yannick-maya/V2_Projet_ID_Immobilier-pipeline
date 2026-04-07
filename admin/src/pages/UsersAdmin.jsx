import { useEffect, useState } from "react";
import api from "../services/api";

const UsersAdmin = () => {
  const [users, setUsers] = useState([]);

  const load = () => api.get("/admin/users").then((r) => setUsers(r.data.data || [])).catch(() => setUsers([]));
  useEffect(() => { load(); }, []);

  const toggleRole = async (u) => {
    const role = u.role === "admin" ? "user" : "admin";
    await api.put(`/admin/users/${u.id}`, { role });
    load();
  };

  const toggleBlocked = async (u) => {
    await api.put(`/admin/users/${u.id}`, { blocked: !u.blocked });
    load();
  };

  return (
    <div className="bg-white p-4 rounded shadow">
      <h2 className="text-xl font-semibold mb-4">Gestion des utilisateurs</h2>
      <table className="w-full text-sm">
        <thead><tr><th>Email</th><th>Role</th><th>Bloqué</th><th>Actions</th></tr></thead>
        <tbody>
          {users.map((u) => (
            <tr key={u.id}>
              <td>{u.email}</td><td>{u.role}</td><td>{String(!!u.blocked)}</td>
              <td className="space-x-2">
                <button onClick={() => toggleRole(u)} className="px-2 py-1 bg-indigo-600 text-white rounded">Changer rôle</button>
                <button onClick={() => toggleBlocked(u)} className="px-2 py-1 bg-amber-600 text-white rounded">Bloquer/Débloquer</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default UsersAdmin;
