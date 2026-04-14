# Configuration GitHub Actions - ID Immobilier

## Secrets Nécessaires

### Pour le déploiement API (Render)
- `RENDER_DEPLOY_HOOK_API`: Webhook URL fourni par Render pour déclencher le déploiement automatique de l'API

### Pour le déploiement Frontend et Admin (Vercel)
- `VERCEL_TOKEN`: Token d'authentification Vercel (généré dans les paramètres Vercel)
- `VERCEL_ORG_ID`: ID de l'organisation Vercel
- `VERCEL_PROJECT_ID_FRONTEND`: ID du projet frontend sur Vercel
- `VERCEL_PROJECT_ID_ADMIN`: ID du projet admin sur Vercel

### Pour la base de données
- `MONGODB_URL`: URL de connexion MongoDB (avec credentials)

### Pour les notifications
- `SLACK_WEBHOOK`: Webhook URL Slack pour les notifications de déploiement

## Configuration des Secrets

1. Aller dans les paramètres du repository GitHub
2. Sélectionner "Secrets and variables" > "Actions"
3. Ajouter chaque secret avec son nom exact et sa valeur

## Variables d'Environnement Nécessaires

### Pour l'API (Render)
```
MONGODB_URL=mongodb://...
JWT_SECRET_KEY=votre-cle-secrete-jwt
```

### Pour le Frontend (Vercel)
```
REACT_APP_API_BASE_URL=https://votre-api-render.com
```

### Pour l'Admin (Vercel)
```
REACT_APP_API_BASE_URL=https://votre-api-render.com
```

## Déclenchement du Pipeline

Le pipeline se déclenche automatiquement sur :
- Push sur les branches `main` ou `master`
- Pull requests vers ces branches

## Jobs du Pipeline

1. **test**: Tests unitaires et validation du code
2. **deploy-api**: Construction et déploiement de l'API sur Render
3. **deploy-frontend**: Construction et déploiement du frontend sur Vercel
4. **deploy-admin**: Construction et déploiement de l'admin sur Vercel
5. **update-database**: Mise à jour de la base de données avec les nouvelles données
6. **notify**: Notification Slack du résultat du déploiement

## Monitoring

- Les déploiements sont automatiquement notifiés sur Slack
- Les métriques de couverture de code sont envoyées à Codecov
- Les images Docker sont stockées sur GitHub Container Registry