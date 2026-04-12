# Guide de Test du Pipeline Immobilier en Local

Ce guide explique comment tester le pipeline complet en local avant le déploiement.

## Prérequis

- Python 3.10+
- MongoDB local ou distant
- Variables d'environnement configurées (.env)

## Étapes du Pipeline

### 1. Nettoyage des Données
```bash
python pipeline/cleaning_v2_pandas.py
```
- Nettoie et standardise les données scrapées
- Génère `data/cleaned_v2/annonces_clean.csv`

### 2. Chargement des Données OTR
```bash
python pipeline/load_otr.py
```
- Charge `data/raw/valeursvenales.csv` dans MongoDB collection `valeurs_venales`
- Prépare les données de référence pour comparaison prix

### 3. Modélisation MongoDB
```bash
python pipeline/modeling_mongodb.py
```
- Insère les annonces nettoyées dans MongoDB
- Ajoute automatiquement la comparaison OTR pour les terrains

### 4. Mise à Jour OTR des Annonces Existantes
```bash
python pipeline/update_otr.py
```
- Met à jour les annonces Terrain existantes avec les champs OTR

### 5. Calcul des Indicateurs
```bash
python pipeline/indicators.py
```
- Calcule les statistiques par zone/type bien

### 6. Indexation
```bash
python pipeline/index.py
```
- Crée les index pour optimisation recherche

### 7. Migration MongoDB v2
```bash
python pipeline/migrate_mongodb_v2.py
```
- Enrichit les annonces avec champs géographiques et temporels

## Test Automatique Complet

Pour exécuter toutes les étapes automatiquement :

```bash
python test_pipeline_local.py
```

Ce script :
- Vérifie les prérequis
- Exécute toutes les étapes séquentiellement
- Teste l'API
- Fournit un résumé des résultats

## Vérification des Résultats

### Dans MongoDB
```javascript
// Vérifier les annonces avec OTR
db.annonces.find({type_bien: "Terrain", prix_otr: {$exists: true}}).limit(5)

// Vérifier les données OTR
db.valeurs_venales.find().limit(5)

// Vérifier les statistiques
db.statistiques.find().limit(5)
```

### Test API
```bash
# Démarrer l'API
python run_api.py

# Tester les endpoints
curl http://localhost:8000/health
curl http://localhost:8000/admin/annonces | jq '.data[0]'
```

### Test Frontend Admin
```bash
cd admin
npm install
npm start
```
- Se connecter à l'admin
- Vérifier l'affichage des colonnes OTR pour les terrains

## Dépannage

### Erreur MongoDB Connection
- Vérifier `MONGO_URI` dans `.env`
- S'assurer que MongoDB est démarré

### Erreur Fichiers Manquants
- Vérifier que `data/raw/valeursvenales.csv` existe
- Vérifier que les données scrapées sont présentes

### Erreur API
- Vérifier que le port 8000 est libre
- Vérifier les logs de l'API

## Métriques de Succès

- ✅ Données OTR chargées (354 lignes)
- ✅ Annonces insérées avec comparaison OTR
- ✅ API répond correctement
- ✅ Frontend affiche les colonnes OTR
- ✅ DAG Airflow mis à jour avec nouvelles tâches