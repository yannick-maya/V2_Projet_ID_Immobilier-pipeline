from pydantic import BaseModel


class Localisation(BaseModel):
    type: str
    coordinates: list[float]


class AnnonceCreate(BaseModel):
    titre: str
    prix: float
    prix_m2: float | None = None
    surface_m2: float | None = None
    type_bien: str
    type_offre: str
    zone: str
    source: str = "user"
    periode: str | None = None
    annee: int | None = None
    trimestre: int | None = None
    date_annonce: str | None = None
    description: str | None = None
    localisation: Localisation | None = None


class AnnonceResponse(AnnonceCreate):
    id: str
    statut: str = "valide"
    created_at: str | None = None
