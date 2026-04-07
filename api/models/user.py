from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    nom: str
    prenom: str


class UserUpdate(BaseModel):
    nom: str | None = None
    prenom: str | None = None


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    nom: str
    prenom: str
    role: str
    created_at: str


class UserInDB(UserResponse):
    hashed_password: str
