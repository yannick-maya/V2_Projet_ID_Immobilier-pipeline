import { Link } from "react-router-dom";
import { useNavigate } from "react-router-dom";

const Navbar = () => {
  const navigate = useNavigate();
  const isLogged = localStorage.getItem("admin_role") === "admin";

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("admin_role");
    localStorage.removeItem("admin_user_email");
    navigate("/login");
  };

  return (
    <nav className="flex flex-wrap items-center gap-4 bg-slate-900 px-4 py-3 text-white md:px-6">
      <Link to="/" className="font-bold">Admin ID Immobilier</Link>
      {isLogged && (
        <>
          <Link to="/">Dashboard</Link>
          <Link to="/annonces">Annonces</Link>
          <Link to="/users">Utilisateurs</Link>
          <Link to="/okr">OKR</Link>
          <Link to="/pipeline">Pipeline</Link>
          <button className="rounded bg-white/10 px-3 py-1 text-sm" onClick={logout}>Deconnexion</button>
        </>
      )}
    </nav>
  );
};

export default Navbar;
