# Guide de Démarrage - ID Immobilier

## Configuration Initiale

### Prérequis
- Python 3.10+
- Node.js 16+
- MongoDB (local ou Atlas)
- Windows PowerShell ou Bash

### 1. Installation de l'environnement Python

```powershell
# Dans le dossier racine du projet
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Installer les dépendances
cd id_immobilier
pip install -r requirements.txt
```

### 2. Configuration des variables d'environnement

**Créer `.env` dans `id_immobilier/`:**

```env
# MongoDB
MONGO_URI=mongodb+srv://user:password@cluster.mongodb.net/?retryWrites=true&w=majority
MONGO_DB=id_immobilier

# Données de période
ID_IMMO_START_PERIOD=2025-10
ID_IMMO_END_PERIOD=2026-02

# JWT
SECRET_KEY=your-secret-key-here-change-this
ALGORITHM=HS256

# API Frontend
REACT_APP_API_URL=http://localhost:8000
```

### 3. Installation dépendances Frontend

```powershell
# Terminal séparé - Frontend
cd frontend
npm install

# Admin Dashboard
cd ../admin
npm install
```

## Démarrage du Projet

### Mode 1: Démarrage Complet via Script

```powershell
# À la racine du projet
.\\start_all.bat
```

### Mode 2: Démarrage Manuel

#### Terminal 1 - API Backend (Port 8000)
```powershell
cd id_immobilier
.\.venv\Scripts\Activate.ps1
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
```

#### Terminal 2 - Frontend (Port 3000)
```powershell
cd id_immobilier/frontend
npm start
```

#### Terminal 3 - Admin Dashboard (Port 3001)
```powershell
cd id_immobilier/admin
npm start
```

#### Terminal 4 - Pipeline de données (optionnel)
```powershell
cd id_immobilier
python pipeline/modeling_mongodb.py
```

## Tâches Principales

### Pipeline de Données

```powershell
cd id_immobilier

# 1. Nettoyage des données
python pipeline/cleaning_v2_pandas.py

# 2. Chargement OTR
python pipeline/load_otr.py

# 3. Modélisation MongoDB
python pipeline/modeling_mongodb.py

# 4. Indicateurs et statistiques
python pipeline/indicators.py

# 5. Mise à jour OTR
python pipeline/update_otr.py
```

### Test du Pipeline Complet

```powershell
python test_pipeline_local.py
```

## Accès à l'Application

- **Frontend Utilisateur**: http://localhost:3000
- **Admin Dashboard**: http://localhost:3001
- **API Swagger**: http://localhost:8000/docs
- **API ReDoc**: http://localhost:8000/redoc

## Accounts de Test

Créez des comptes ou utilisez:
- Email: `test@example.com`
- Mot de passe: `password123`

(Après création en base)

## Endpoints Principaux

### Public
- `GET /statistiques/options` - Zones, types de bien, périodes
- `GET /statistiques/overview` - Vue globale du marché
- `GET /statistiques/project` - Infos du projet
- `GET /annonces` - Liste des annonces avec filtres

### Utilisateur Authentifié
- `GET /auth/me` - Profil utilisateur
- `POST /favoris/{id}` - Ajouter aux favoris
- `GET /favoris` - Mes favoris
- `POST /scoring` - Simulateur de prix

### Admin (Token Admin requis)
- `GET /admin/stats` - Statistiques complètes
- `GET /admin/users` - Gestion utilisateurs
- `PUT /admin/users/{id}` - Modifier utilisateur
- `GET /admin/annonces` - Gestion annonces

## Troubleshooting

### API ne démarre pas
```
→ Vérifier MONGO_URI dans .env
→ Vérifier port 8000 disponible
→ Vérifier Python version (3.10+)
```

### Frontend ne se connecte pas à l'API
```
→ Vérifier REACT_APP_API_URL dans .env
→ Vérifier CORS dans api/main.py
→ Vérifier API en court d'exécution sur :8000
```

### Données manquantes dans les graphiques
```
→ Exécuter le pipeline: python pipeline/modeling_mongodb.py
→ Vérifier collection 'annonces' en base
→ Vérifier les champs: prix_m2, periode, year_month
```

### Erreur "model_dump"
```
→ Assurer Pydantic v2 installé
→ Relancer: pip install --upgrade pydantic
```

## Structure du Projet

```
id_immobilier/
├── api/
│   ├── routers/          # Endpoints FastAPI
│   ├── models/           # Modèles Pydantic
│   ├── auth/             # Authentification JWT
│   ├── main.py           # Entrée API
│   └── database.py       # Connexion MongoDB
├── frontend/             # React - Utilisateurs
├── admin/                # React - Tableau de bord admin
├── pipeline/             # ETL et traitement données
├── data/                 # Dossier données (raw, cleaned, gold)
└── notebooks/            # Exploration et expériences
```

## Documentation Complète

- **Architecture**: Voir `Documents/architecture_id_immobilier.html`
- **TDR Projet**: Voir `RAPPORT_PROJET_FINAL.md`
- **État du déploiement**: Voir `DEPLOIEMENT_PROJET_DETAILLE.md`

## Support

Pour questions ou problèmes:
1. Vérifier les logs des terminaux
2. Consulter le TDR pour les spécifications
3. Tester les endpoints via Swagger (/docs)

---

**Version**: 2.0.0 | **Mise à jour**: Avril 2026
