# 🔧 Guide de Troubleshooting - Problèmes de Connexion

## 🔍 Ce que nous avons découvert

✅ **MongoDB**: Fonctionne correctement  
✅ **Utilisateurs**: 3 utilisateurs existants dans la BD

```
- yannickmadjiadoum23@gmail.com (admin) ✓ Actif
- yannickmadjiadoum@gmail.com (admin) ✓ Actif
- nickson@gmail.com (user) ✓ Actif
```

❌ **Problème identifié**: L'API FastAPI n'est probablement pas en cours d'exécution

---

## 📋 Checklist de Vérification

### 1️⃣ L'API est-elle lancée ?

```bash
# Terminal 1 - Lancer l'API
cd d:\PROJECTS\Projet_Immobilier\id_immobilier
python -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

✅ Vous devez voir:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 2️⃣ Le Frontend pointe-t-il vers la bonne API ?

**Frontend utilisateur** (`frontend/.env`):
```
REACT_APP_API_URL=http://localhost:8000
```

**Admin** (`admin/.env`):
```
REACT_APP_API_URL=http://localhost:8000
```

Si les fichiers `.env` n'existent pas dans `frontend/` et `admin/`, créez-les !

### 3️⃣ Testez la Connexion Manuelle

Ouvrez **Postman** ou **VS Code REST Client** et testez:

```http
POST http://localhost:8000/auth/login
Content-Type: application/json

{
  "email": "yannickmadjiadoum23@gmail.com",
  "password": "[VOTRE_MOT_DE_PASSE]"
}
```

### 4️⃣ Lancez le Frontend

```bash
# Terminal 2 - Frontend utilisateur (port 3000)
cd d:\PROJECTS\Projet_Immobilier\id_immobilier\frontend
npm start
```

```bash
# Terminal 3 - Admin interface (port 3001)
cd d:\PROJECTS\Projet_Immobilier\id_immobilier\admin
REACT_APP_API_URL=http://localhost:8000 npm start
```

---

## 🚨 Problèmes Courants et Solutions

### ❌ "Identifiants invalides" ou "Connexion échouée"

**Causes possibles:**
1. L'API n'est pas lancée → Lancez-la (voir étape 1)
2. Mauvais identifiants → Vérifiez l'email/mot de passe
3.  L'utilisateur est bloqué → Vérifiez `blocked: false` dans MongoDB
4. Le mot de passe a été changé → Créer un nouvel utilisateur

**Solution:**
```bash
# Vérifier l'utilisateur dans MongoDB
python

from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import os
from dotenv import load_dotenv

async def check():
    load_dotenv()
    client = AsyncIOMotorClient(os.getenv("MONGO_URI"))
    db = client["id_immobilier"]
    user = await db["users"].find_one({"email": "yannickmadjiadoum23@gmail.com"})
    print(f"Email: {user.get('email')}")
    print(f"Blocked: {user.get('blocked')}")
    print(f"Role: {user.get('role')}")
    await client.close()

asyncio.run(check())
```

### ❌ "Cannot GET /admin" ou "Cannot GET /dashboard"

**Cause:** Vercel/serveur ne sert pas les routes correctement

**Solution:** Vérifiez que `vercel.json` redirige tout vers `index.html`:
```json
{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static-build",
      "config": { "distDir": "build" }
    }
  ],
  "routes": [
    { "src": "/(.*)", "dest": "/index.html" }
  ]
}
```

### ❌ "CORS error" ou "XMLHttpRequest blocked"

**Cause:** L'API bloque les requêtes du frontend

**Solution:** Vérifiez `api/main.py`:
```python
cors_origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000,http://127.0.0.1:3001",
)
```

---

## 🎯 Scénario Complet de Test

### Terminal 1 - API Backend (Port 8000)
```bash
cd d:\PROJECTS\Projet_Immobilier\id_immobilier
python -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

### Terminal 2 - Frontend User (Port 3000)
```bash
cd d:\PROJECTS\Projet_Immobilier\id_immobilier\frontend
npm install  # Si premiere fois
npm start
```

### Terminal 3 - Admin (Port 3001)
```bash
cd d:\PROJECTS\Projet_Immobilier\id_immobilier\admin
npm install  # Si premiere fois
REACT_APP_API_URL=http://localhost:8000 npm start
```

### Testez dans le Navigateur

🌐 **Frontend User**: http://localhost:3000  
🌐 **Admin Panel**: http://localhost:3001  
🌐 **API Docs**: http://localhost:8000/docs

---

## 📡 Vérification API avec cURL

```bash
# Test endpoint sante
curl http://localhost:8000/

# Test login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"yannickmadjiadoum23@gmail.com","password":"TON_MOT_DE_PASSE"}'
```

---

## 📝 Notes importantes

- ✅ Utilisateurs existent: Pas besoin de créer de compte
- ⚠️ L'API **doit** être lancée en premier
- ⚠️ Les variables `.env` doivent être présentes dans `frontend/` et `admin/`
- ⚠️ Utilisez des **URLs locales** (`localhost:8000`), pas des URLs distantes en dev
- 🔄 Si rien ne marche: Vérifiez les logs de chaque terminal pour les erreurs

---

## 🆘 Si vous êtes bloqué

Partagez les logs d'erreur de:
1. Terminal de l'API (port 8000)
2. Console du navigateur (F12)
3. Terminal npm du frontend/admin
