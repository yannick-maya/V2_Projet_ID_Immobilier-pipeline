# README de Test - ID Immobilier v2.0

Ce document permet de tester **tout le projet**, du pipeline MongoDB jusqu'aux apps web.

## 1) Prérequis

- Python 3.10
- Docker + Docker Compose
- Node.js 18+
- MongoDB Atlas (ou Mongo local)

## 2) Variables d'environnement

Copier le template:

```bash
cp .env.example .env
```

Renseigner au minimum dans `.env`:

- `MONGO_URI`
- `MONGO_DB`
- `JWT_SECRET`
- `JWT_ALGORITHM`
- `JWT_EXPIRE_MINUTES`

## 3) Installation backend

```bash
pip install -r requirements.txt
```

## 4) Tests Chantier 1 (MongoDB pipeline)

### 4.1 Démarrer les services

```bash
docker-compose up -d
```

Vérifier:

```bash
docker ps
```

Services attendus: `id_mongo`, `id_immobilier_airflow`, `id_immobilier_streamlit`, `id_immobilier_spark`, `id_immobilier_spark_worker`.

### 4.2 Ingestion

```bash
python pipeline/ingestion.py
```

Attendu: fichiers CSV dans `data/raw/` avec colonnes `annee`, `trimestre`, `periode`.

### 4.3 Cleaning PySpark

```bash
python pipeline/cleaning_pyspark_v2.py
```

Attendu: données nettoyées dans `data/cleaned_v2/annonces`.

### 4.4 Modeling MongoDB

```bash
python pipeline/modeling_mongodb.py
```

Attendu:

- logs `Inserees` et `Mises a jour`
- collection `annonces` alimentée
- index créés: `zone`, `type_bien`, `periode`, `localisation (2dsphere)`

### 4.5 Indicateurs

```bash
python pipeline/indicators.py
```

Attendu: collection `statistiques` alimentée.

### 4.6 Indice

```bash
python pipeline/index.py
```

Attendu: collection `indices` alimentée, avec `tendance` = `HAUSSE|STABLE|BAISSE`.

### 4.7 Dashboard Streamlit

```bash
streamlit run dashboard/dashboard.py
```

Attendu:

- chargement depuis MongoDB
- filtre `Periode` disponible en sidebar

### 4.8 Correction des périodes

```bash
python pipeline/fix_periodes.py
```

Attendu: périodes "2026-Q2" remplacées par dates aléatoires entre novembre 2025 et février 2026.

### 4.9 Migration MongoDB v2

```bash
python pipeline/migrate_mongodb_v2.py
```

Attendu:

- données nettoyées migrées vers MongoDB
- collections `annonces` et `venales` alimentées
- périodes corrigées dans la base

### 4.10 Intégration données OTR

```bash
python pipeline/integrate_otr.py
```

Attendu:

- annonces enrichies avec `prix_otr`, `difference_otr`, `statut_otr`
- statistiques d'écarts affichées
- données prêtes pour les comparaisons marché vs OTR

### 4.11 Tests des nouveaux endpoints

```bash
# Tester les endpoints périodiques
curl "http://localhost:8000/periodique/comparaison?zone=adidogome"
curl "http://localhost:8000/periodique/evolution"
curl "http://localhost:8000/periodique/annonces?periode=2025-11"
```

Attendu: données JSON avec comparaisons OTR et évolutions temporelles.

## 5) Tests Chantier 3 (API FastAPI)

Lancer l'API:

```bash
uvicorn api.main:app --reload
```

Ouvrir:

- http://localhost:8000/docs

Checklist:

- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`
- `PUT /auth/me`
- `GET /annonces` (filtres + pagination)
- `GET /annonces/search?q=...`
- `POST /annonces` (token requis)
- `GET /statistiques`
- `GET /indice`
- `GET /indice/tendances`
- `GET/POST/DELETE /favoris`
- `GET /admin/*` avec compte admin

## 6) Tests Chantier 4 (Frontend utilisateur)

```bash
cd frontend
npm install
npm start
```

URL: http://localhost:3000

Pages à valider:

- Accueil
- Connexion / Inscription
- Recherche (filtres + pagination)
- Détail bien
- Favoris
- Indice
- Simulateur
- Profil

## 7) Tests Chantier 5 (Back-office admin)

```bash
cd admin
npm install
npm start
```

URL: http://localhost:3001 (ou port proposé automatiquement)

Pages à valider:

- Dashboard KPI
- Gestion annonces (valider/refuser)
- Gestion utilisateurs (rôle, blocage)
- OKR (graphiques Recharts)
- Monitoring pipeline

## 8) Déploiement (Chantier 6)

### 8.1 Render API

- `render.yaml` fourni
- Build: `pip install -r requirements.txt`
- Start: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
- Variables env à configurer dans Render

### 8.2 Vercel Front/Admin

- `frontend/vercel.json` et `admin/vercel.json` fournis
- Ajouter `REACT_APP_API_URL` vers l'URL Render

### 8.3 CI/CD GitHub Actions

Workflow: `.github/workflows/deploy.yml`

- Sur push `main`: tests de syntaxe
- Puis trigger hook Render via secret `RENDER_DEPLOY_HOOK`

## 9) Commandes de diagnostic rapide

```bash
python -m py_compile api/main.py
python -m py_compile pipeline/modeling_mongodb.py
python -m py_compile pipeline/index.py
```

## 10) Collections MongoDB attendues

- `annonces`
- `zones`
- `statistiques`
- `indices`
- `valeurs_venales`
- `users`

Si une collection manque, rejouer les scripts pipeline correspondants.
