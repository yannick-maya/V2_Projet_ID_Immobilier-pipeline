# Rapport Final - ID Immobilier

## Resume

ID Immobilier est une plateforme de donnees immobilieres articulee autour de 4 briques:

- pipeline data orchestre par Airflow
- stockage et analytics dans MongoDB
- API FastAPI
- interfaces React pour les utilisateurs et les administrateurs

Cette version finale integre:

- une modelisation geographique canonique avec collection `zones`
- une temporalite mensuelle et trimestrielle plus fiable avec `year_month`, `observation_month`, `observation_year`, `observation_quarter`
- des statistiques et indices recalcules sur cette nouvelle base
- un dashboard utilisateur recentre sur les prix au m2
- une interface admin avec page de connexion dediee
- une orchestration Airflow mise a jour
- un `docker-compose` complet pour les services principaux

## Architecture finale

### Data pipeline

1. `pipeline/ingestion.py`
2. `pipeline/cleaning_v2_spark.py`
3. `pipeline/modeling_mongodb.py`
4. `pipeline/migrate_mongodb_v2.py`
5. `pipeline/indicators.py`
6. `pipeline/index.py`

### Collections MongoDB

- `annonces`
- `zones`
- `statistiques`
- `indices`
- `users`

### Services applicatifs

- API: FastAPI
- Frontend user: React
- Admin: React
- Monitoring data: Airflow + Spark + Streamlit demo

## Modelisation de donnees

### Zones

Les annonces sont maintenant enrichies avec:

- `zone_id`
- `zone_slug`
- `zone_display`
- `geo.country`
- `geo.region`
- `geo.prefecture`
- `geo.city`
- `geo.district`

La collection `zones` sert de referentiel canonique.

### Temps

Les documents utilisent maintenant:

- `source_posted_at`
- `source_scraped_at`
- `observation_date`
- `observation_year`
- `observation_month`
- `observation_quarter`
- `year_month`
- `periode`

`periode` reste utile pour les vues trimestrielles, mais `year_month` devient la base temporelle principale.

## Orchestration Airflow

Le DAG `id_immobilier_pipeline` execute maintenant:

1. scraping ImmoAsk
2. ingestion
3. nettoyage des anciens exports
4. nettoyage Spark
5. modelisation MongoDB
6. migration MongoDB v2
7. calcul des statistiques
8. calcul de l indice

Fichier: [dag_immobilier.py](D:/PROJECTS/Projet_Immobilier/id_immobilier/dags/dag_immobilier.py)

## Docker Compose final

Le projet peut maintenant demarrer avec:

- `mongo`
- `spark`
- `spark-worker`
- `airflow`
- `api`
- `frontend`
- `admin`
- `streamlit`

Commande:

```powershell
docker-compose up -d --build
```

## URLs locales

- Frontend user: `http://localhost:3000`
- Admin: `http://localhost:3001`
- API: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- Airflow: `http://localhost:8081`
- Spark UI: `http://localhost:8082`
- Streamlit demo: `http://localhost:8501`
- MongoDB: `mongodb://localhost:27017`

## Acces admin

### Interface admin

Ouvrir:

`http://localhost:3001`

### Condition d acces

Le compte doit avoir `role = "admin"` dans MongoDB.

Si un utilisateur existe deja et doit devenir admin:

```powershell
@'
from dotenv import load_dotenv
from pymongo import MongoClient
import os
load_dotenv('.env')
client = MongoClient(os.getenv('MONGO_URI'))
db = client[os.getenv('MONGO_DB', 'id_immobilier')]
db['users'].update_one({'email': 'ton-email@example.com'}, {'$set': {'role': 'admin'}})
print('role admin applique')
client.close()
'@ | python -
```

Ensuite:

1. ouvrir `http://localhost:3001/login`
2. se connecter avec ce compte

## Verification recommandees

### Local sans Docker

```powershell
python -m uvicorn api.main:app --reload
cd frontend
npm start
cd ..\admin
npm start
```

### Recalcul data

```powershell
python pipeline\modeling_mongodb.py
python pipeline\migrate_mongodb_v2.py
python pipeline\indicators.py
python pipeline\index.py
```

## Etat actuel de la base apres migration

- annonces enrichies: 4879
- zones canoniques: 550
- statistiques recalcules avec `year_month`: 1034
- indices recalcules avec `year_month`: 932

## Points d attention restants

- beaucoup de donnees historiques n ont pas encore de vraie `date_annonce` source, donc la temporalite est parfois reconstituee depuis `created_at`
- les scrapers et le cleaning peuvent encore etre enrichis pour capter plus finement les dates de publication
- l admin UI est maintenant connectable, mais peut encore etre renforcee avec gestion de session plus poussee et audit trail

## Fichiers principaux modifies/ajoutes

- [docker-compose.yml](D:/PROJECTS/Projet_Immobilier/id_immobilier/docker-compose.yml)
- [Dockerfile.api](D:/PROJECTS/Projet_Immobilier/id_immobilier/Dockerfile.api)
- [Dockerfile.frontend](D:/PROJECTS/Projet_Immobilier/id_immobilier/Dockerfile.frontend)
- [Dockerfile.admin](D:/PROJECTS/Projet_Immobilier/id_immobilier/Dockerfile.admin)
- [Dockerfile.airflow](D:/PROJECTS/Projet_Immobilier/id_immobilier/Dockerfile.airflow)
- [dag_immobilier.py](D:/PROJECTS/Projet_Immobilier/id_immobilier/dags/dag_immobilier.py)
- [geo_temporal.py](D:/PROJECTS/Projet_Immobilier/id_immobilier/pipeline/geo_temporal.py)
- [migrate_mongodb_v2.py](D:/PROJECTS/Projet_Immobilier/id_immobilier/pipeline/migrate_mongodb_v2.py)
- [RAPPORT_PROJET_FINAL.md](D:/PROJECTS/Projet_Immobilier/id_immobilier/RAPPORT_PROJET_FINAL.md)
