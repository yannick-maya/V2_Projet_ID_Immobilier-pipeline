import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { authApi } from "../services/api";

const extractError = (err) => {
  if (err?.message === "Network Error" || !err?.response) {
    return "API inaccessible. Vérifie que uvicorn tourne sur http://localhost:8000";
  }
  const detail = err?.response?.data?.detail;
  if (Array.isArray(detail)) {
    return detail.map((d) => d.msg).join(" | ");
  }
  return detail || "Inscription échouée";
};

const Register = () => {
  const [form, setForm] = useState({ nom: "", prenom: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await authApi.register({
        nom: form.nom.trim(),
        prenom: form.prenom.trim(),
        email: form.email.trim().toLowerCase(),
        password: form.password,
      });
      navigate("/login");
    } catch (err) {
      setError(extractError(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-md rounded-2xl border border-slate-100 bg-white p-6 shadow-lg">
      <h2 className="text-2xl font-bold text-[#0B3954]">Créer un compte</h2>
      <p className="mt-1 text-sm text-slate-500">Accède à tes favoris, alertes et simulations.</p>
      <form className="mt-5 space-y-3" onSubmit={submit}>
        <input className="input-modern" placeholder="Nom" required value={form.nom} onChange={(e) => setForm({ ...form, nom: e.target.value })} />
        <input className="input-modern" placeholder="Prénom" required value={form.prenom} onChange={(e) => setForm({ ...form, prenom: e.target.value })} />
        <input className="input-modern" type="email" placeholder="email@exemple.com" required value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
        <input className="input-modern" type="password" minLength={6} placeholder="Mot de passe (6+ caractères)" required value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
        {error && <p className="rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-700">{error}</p>}
        <button disabled={loading} className="btn-primary w-full disabled:opacity-60">
          {loading ? "Création..." : "Créer un compte"}
        </button>
      </form>
    </div>
  );
};

export default Register;
