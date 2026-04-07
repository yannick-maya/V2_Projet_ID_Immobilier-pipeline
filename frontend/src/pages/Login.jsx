import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { authApi } from "../services/api";

const Login = () => {
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth();

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const res = await authApi.login({ email: form.email.trim().toLowerCase(), password: form.password });
      login(res.data.access_token, res.data.user);
      navigate("/dashboard");
    } catch (err) {
      setError(err.response?.data?.detail || "Connexion echouee");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-md rounded-2xl border border-slate-100 bg-white p-6 shadow-lg">
      <h2 className="text-2xl font-bold text-[#0B3954]">Connexion</h2>
      <p className="mt-1 text-sm text-slate-500">Accede a ton espace personnel.</p>
      <form className="mt-5 space-y-3" onSubmit={submit}>
        <input className="input-modern" type="email" required placeholder="Email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
        <input className="input-modern" type="password" required placeholder="Mot de passe" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
        {error && <p className="rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-700">{error}</p>}
        <button className="btn-primary w-full" disabled={loading}>{loading ? "Connexion..." : "Se connecter"}</button>
      </form>
    </div>
  );
};

export default Login;
