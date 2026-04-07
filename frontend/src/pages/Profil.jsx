import { useAuth } from "../context/AuthContext";

const Profil = () => {
  const { user } = useAuth();
  return (
    <div className="space-y-4 rounded-2xl bg-white p-6 shadow-lg">
      <h2 className="text-2xl font-bold text-[#0B3954]">Mon profil</h2>
      <div className="grid gap-3 md:grid-cols-2">
        <div className="rounded-xl bg-slate-50 p-4"><p className="text-xs uppercase text-slate-500">Nom</p><p className="font-semibold">{user?.nom || "-"}</p></div>
        <div className="rounded-xl bg-slate-50 p-4"><p className="text-xs uppercase text-slate-500">Prenom</p><p className="font-semibold">{user?.prenom || "-"}</p></div>
        <div className="rounded-xl bg-slate-50 p-4"><p className="text-xs uppercase text-slate-500">Email</p><p className="font-semibold">{user?.email || "-"}</p></div>
        <div className="rounded-xl bg-slate-50 p-4"><p className="text-xs uppercase text-slate-500">Role</p><p className="font-semibold">{user?.role || "user"}</p></div>
      </div>
    </div>
  );
};

export default Profil;
