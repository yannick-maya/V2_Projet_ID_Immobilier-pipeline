# Guide de Deploiement Detaille - ID Immobilier

Ce document decrit toutes les etapes de deploiement de la plateforme:
- Pipeline data + MongoDB Atlas
- API FastAPI
- Frontend utilisateur React
- Back-office admin React
- CI/CD GitHub Actions

## 1. Prerequis

- GitHub repo a jour
- Python 3.10+
- Node.js 18+
- Docker (pour tests locaux)
- Comptes:
  - MongoDB Atlas
  - Render
  - Vercel

## 2. MongoDB Atlas (Production Data Layer)

### 2.1 Creer le cluster
1. Se connecter a MongoDB Atlas.
2. Creer un cluster M0 (free tier).
3. Region proche (ex: Europe/Ouest Afrique selon latence).

### 2.2 Creer l'utilisateur DB
1. Database Access > Add New Database User.
2. Username: `yann` (ou autre).
3. Password: mot de passe fort.
4. Role: `readWriteAnyDatabase` (ou `readWrite` sur `id_immobilier`).

### 2.3 Ouvrir l'acces reseau
1. Network Access > Add IP Address.
2. Pour test rapide: `0.0.0.0/0`.
3. En production: restreindre aux IP des services deployes.

### 2.4 Recuperer l'URI
1. Connect > Drivers > Python.
2. Copier l'URI Atlas.
3. Remplacer `<db_password>` par le vrai mot de passe.

Exemple:
`mongodb+srv://yann:MON_MDP@cluster-v2-id-immobilie.78dw9xv.mongodb.net/?retryWrites=true&w=majority&appName=cluster-v2-id-immobilier`

## 3. Configuration des variables d'environnement

## 3.1 Backend `.env`
Dans la racine du projet:

```env
MONGO_URI=...
MONGO_DB=id_immobilier
JWT_SECRET=...
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,https://ton-frontend.vercel.app,https://ton-admin.vercel.app
```

## 3.2 Frontend `.env`
Dans `frontend/.env`:

```env
REACT_APP_API_URL=https://ton-api.onrender.com
```

## 3.3 Admin `.env`
Dans `admin/.env`:

```env
REACT_APP_API_URL=https://ton-api.onrender.com
```

## 4. Validation locale complete

### 4.1 Installer dependances
```bash
pip install -r requirements.txt
cd frontend && npm install
cd ../admin && npm install
```

### 4.2 Verifier Mongo
```bash
python test_mongo.py
```

### 4.3 Charger les donnees
```bash
python pipeline/ingestion.py
python pipeline/cleaning_V2.py
python pipeline/modeling_mongodb.py
python pipeline/indicators.py
python pipeline/index.py
```

### 4.4 Lancer API
```bash
uvicorn api.main:app --reload
```
Docs: `http://localhost:8000/docs`

### 4.5 Lancer apps React
```bash
cd frontend && npm start
cd admin && npm start
```

## 5. Deploiement API sur Render

### 5.1 Service
1. Render > New > Web Service.
2. Connecter le repo GitHub.
3. Root directory: racine du projet.

### 5.2 Build/Start
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`

### 5.3 Variables Render
Ajouter:
- `MONGO_URI`
- `MONGO_DB=id_immobilier`
- `JWT_SECRET`
- `JWT_ALGORITHM=HS256`
- `JWT_EXPIRE_MINUTES=1440`
- `CORS_ORIGINS=https://ton-frontend.vercel.app,https://ton-admin.vercel.app`

### 5.4 Test API deployee
- `GET /` doit retourner status `ok`
- `GET /docs` accessible
- `POST /auth/register` fonctionnel

## 6. Deploiement Frontend sur Vercel

1. Vercel > Add New Project.
2. Selectionner le repo.
3. Root: `frontend`.
4. Build command: `npm run build`.
5. Output: `build`.
6. Env var: `REACT_APP_API_URL=https://ton-api.onrender.com`.
7. Deploy.

## 7. Deploiement Admin sur Vercel

1. Add New Project.
2. Root: `admin`.
3. Build command: `npm run build`.
4. Output: `build`.
5. Env var: `REACT_APP_API_URL=https://ton-api.onrender.com`.
6. Deploy.

## 8. CORS en production

Dans backend (`CORS_ORIGINS`):
- URL Vercel frontend
- URL Vercel admin
- optionnellement localhost pour debug

Exemple:
`CORS_ORIGINS=https://id-immo-frontend.vercel.app,https://id-immo-admin.vercel.app`

## 9. CI/CD GitHub Actions

Workflow present: `.github/workflows/deploy.yml`

Fonctionnement:
1. Push sur `main`.
2. Job `test` (compilation syntaxique Python).
3. Job `deploy-render` (hook Render via secret `RENDER_DEPLOY_HOOK`).

### 9.1 Secret GitHub a ajouter
- `RENDER_DEPLOY_HOOK` = URL de deploy hook Render.

## 10. Checklist post-deploiement

- API Render repond sur `/` et `/docs`
- Frontend peut:
  - s'inscrire
  - se connecter
  - lire annonces/stats/indices
  - lancer simulateur
- Admin peut:
  - lire users
  - moderer annonces
- Les collections MongoDB se remplissent:
  - `annonces`
  - `statistiques`
  - `indices`
  - `users`

## 11. Pannes frequentes et correctifs

### 11.1 `bad auth : authentication failed`
- verifier user/password Atlas
- verifier URL encode du mot de passe
- verifier `MONGO_URI`

### 11.2 CORS bloque dans navigateur
- ajouter domaines exacts dans `CORS_ORIGINS`
- redployer API

### 11.3 Simulateur ne repond pas
- verifier endpoint `POST /scoring`
- verifier que l'API redemarre avec la nouvelle version

### 11.4 Frontend n'a pas les donnees
- verifier `REACT_APP_API_URL`
- verifier que l'API est accessible publiquement
- verifier que `pipeline/modeling_mongodb.py` a bien insere des annonces

---

En cas de doute, refaire d'abord la validation locale complete (section 4), puis deployer.


# lien render: 
https://projet-id-immobilier-pipeline.onrender.com

# lien admin 
https://admin-id-immobilier-pipeline.vercel.app

# lien dashbord 
https://dashbordadmin-id-immobilier-pipelin.vercel.app/login

# lien streamlit
