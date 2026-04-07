import { Link } from "react-router-dom";

const Navbar = () => (
  <nav className="bg-slate-900 text-white px-6 py-3 flex gap-4">
    <Link to="/">Dashboard</Link>
    <Link to="/annonces">Annonces</Link>
    <Link to="/users">Utilisateurs</Link>
    <Link to="/okr">OKR</Link>
    <Link to="/pipeline">Pipeline</Link>
  </nav>
);

export default Navbar;
