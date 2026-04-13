const AnnonceCard = ({ annonce, onSave }) => (
  <div className="rounded-2xl border border-slate-100 bg-white p-5 shadow-md transition hover:-translate-y-0.5 hover:shadow-lg">
    <div className="mb-3 flex items-start justify-between gap-2">
      <h3 className="line-clamp-2 text-base font-bold text-[#0B3954]">{annonce.titre}</h3>
      <span className="rounded-full bg-[#F0F7FB] px-2 py-1 text-xs font-semibold text-[#065A82]">{annonce.type_offre}</span>
    </div>
    <p className="text-sm text-slate-600">{annonce.zone} · {annonce.type_bien}</p>
    <p className="mt-2 text-lg font-extrabold text-[#065A82]">{Number(annonce.prix_m2 || 0).toLocaleString()} FCFA/m²</p>
    <p className="text-sm text-slate-500">{annonce.surface_m2 ? `${Number(annonce.surface_m2).toLocaleString()} m²` : "Surface non renseignee"} · {annonce.source || "source inconnue"}</p>
    <div className="mt-4 grid gap-2">
      <Link to={`/annonce/${annonce.id}`} className="w-full rounded-xl border border-[#065A82] px-3 py-2 text-center text-sm font-semibold text-[#065A82] hover:bg-[#F0F7FB]">
        Voir le detail
      </Link>
      <button onClick={() => onSave?.(annonce.id)} className="w-full rounded-xl bg-[#065A82] px-3 py-2 text-sm font-semibold text-white hover:bg-[#054b6b]">
        Sauvegarder
      </button>
    </div>
  </div>
);

export default AnnonceCard;
import { Link } from "react-router-dom";
