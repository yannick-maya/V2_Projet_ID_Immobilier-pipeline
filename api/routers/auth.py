from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr

from api.auth.jwt import create_access_token
from api.auth.middleware import get_current_user
from api.auth.password import hash_password, verify_password
from api.database import db
from api.models.user import UserCreate, UserUpdate
from api.utils import serialize_doc, utc_now_iso

router = APIRouter()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/register")
async def register(payload: UserCreate):
    email = payload.email.strip().lower()
    exists = await db["users"].find_one({"email": email})
    if exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email deja utilise")

    user = {
        "email": email,
        "nom": payload.nom.strip(),
        "prenom": payload.prenom.strip(),
        "hashed_password": hash_password(payload.password),
        "role": "user",
        "favoris": [],
        "blocked": False,
        "created_at": utc_now_iso(),
    }
    result = await db["users"].insert_one(user)
    created = await db["users"].find_one({"_id": result.inserted_id})
    created.pop("hashed_password", None)
    return serialize_doc(created)


@router.post("/login")
async def login(payload: LoginRequest):
    user = await db["users"].find_one({"email": payload.email.strip().lower()})
    if not user or not verify_password(payload.password, user.get("hashed_password", "")):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Identifiants invalides")
    if user.get("blocked"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Compte bloque")

    token = create_access_token({"sub": str(user["_id"]), "role": user.get("role", "user")})
    user.pop("hashed_password", None)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": serialize_doc(user),
    }


@router.get("/me")
async def me(user=Depends(get_current_user)):
    return user


@router.put("/me")
async def update_me(payload: UserUpdate, user=Depends(get_current_user)):
    update = {}
    if payload.nom is not None:
        update["nom"] = payload.nom.strip()
    if payload.prenom is not None:
        update["prenom"] = payload.prenom.strip()

    if update:
        await db["users"].update_one({"_id": ObjectId(user["id"])}, {"$set": update})

    refreshed = await db["users"].find_one({"email": user["email"]})
    refreshed.pop("hashed_password", None)
    return serialize_doc(refreshed)
