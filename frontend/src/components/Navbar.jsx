import { Link, NavLink } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const linkClass = ({ isActive }) =>
  `rounded-lg px-3 py-2 text-sm font-medium transition ${
    isActive ? "bg-[#065A82] text-white" : "text-slate-700 hover:bg-slate-100"
  }`;

const Navbar = () => {
  const { user, logout } = useAuth();
  return (
    <nav className="sticky top-0 z-50 border-b border-slate-200 bg-white/90 backdrop-blur">
      <div className="mx-auto flex max-w-[1380px] flex-col gap-3 px-3 py-3 md:flex-row md:items-center md:justify-between md:px-4">
        <Link to="/" className="text-lg font-extrabold text-[#065A82] md:text-xl">ID Immobilier</Link>
        <div className="flex flex-wrap items-center gap-2">
          <NavLink to="/" className={linkClass}>Accueil</NavLink>
          <NavLink to="/a-propos" className={linkClass}>A propos</NavLink>
          {user ? (
            <>
              <NavLink to="/recherche" className={linkClass}>Recherche</NavLink>
              <NavLink to="/indice" className={linkClass}>Indice</NavLink>
              <NavLink to="/simulateur" className={linkClass}>Simulateur</NavLink>
              <NavLink to="/dashboard" className={linkClass}>Dashboard</NavLink>
              <NavLink to="/favoris" className={linkClass}>Favoris</NavLink>
              <button onClick={logout} className="rounded-lg bg-[#F59E0B] px-3 py-2 text-sm font-semibold text-white hover:bg-[#D97706]">Déconnexion</button>
            </>
          ) : (
            <>
              <NavLink to="/login" className={linkClass}>Connexion</NavLink>
              <NavLink to="/register" className={linkClass}>Inscription</NavLink>
            </>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
