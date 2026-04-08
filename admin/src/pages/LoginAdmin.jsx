import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

const LoginAdmin = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const onSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const response = await api.post("/auth/login", { email, password });
      const token = response.data?.access_token;
      const user = response.data?.user;

      if (!token || user?.role !== "admin") {
        setError("Ce compte n'a pas les droits admin.");
        localStorage.removeItem("token");
        localStorage.removeItem("admin_role");
        setLoading(false);
        return;
      }

      localStorage.setItem("token", token);
      localStorage.setItem("admin_role", user.role);
      localStorage.setItem("admin_user_email", user.email || "");
      navigate("/", { replace: true });
    } catch (err) {
      setError(err.response?.data?.detail || "Connexion admin impossible.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-md rounded-2xl bg-white p-6 shadow-lg">
      <h1 className="text-2xl font-bold text-slate-900">Connexion admin</h1>
      <p className="mt-1 text-sm text-slate-500">Utilise un compte ayant le role `admin` dans MongoDB.</p>

      <form className="mt-5 space-y-4" onSubmit={onSubmit}>
        <input className="w-full rounded-xl border border-slate-200 px-3 py-2" type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
        <input className="w-full rounded-xl border border-slate-200 px-3 py-2" type="password" placeholder="Mot de passe" value={password} onChange={(e) => setPassword(e.target.value)} />
        {error && <p className="rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-700">{error}</p>}
        <button className="w-full rounded-xl bg-slate-900 px-4 py-2 font-semibold text-white" disabled={loading} type="submit">
          {loading ? "Connexion..." : "Se connecter"}
        </button>
      </form>
    </div>
  );
};

export default LoginAdmin;
