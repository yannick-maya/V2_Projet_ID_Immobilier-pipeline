from pydantic import BaseModel


class IndiceResponse(BaseModel):
    id: str | None = None
    zone: str
    type_bien: str
    periode: str
    indice_valeur: float
    tendance: str
    prix_moyen_m2: float | None = None
    nombre_annonces: int | None = None
