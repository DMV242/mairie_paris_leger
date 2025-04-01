# API REST pour l'Application Mobile

Ce document explique comment configurer et utiliser l'API REST pour l'application mobile React Native.

## Configuration requise

Assurez-vous d'avoir installé toutes les dépendances requises :

```bash
pip install -r requirements.txt
```

## Endpoints API disponibles

L'API est accessible à l'URL `/api/` et fournit les endpoints suivants :

### Authentification

- **POST** `/api/login/` - Connexion avec matricule et mot de passe
  - Requête: `{"matricule": "string", "password": "string"}`
  - Réponse: `{"token": "string", "user": {...}}`

### Projets

- **GET** `/api/projects/` - Liste tous les projets
- **GET** `/api/projects/{id}/` - Détails d'un projet spécifique
- **GET** `/api/projects/?status=En cours` - Filtrer les projets par statut
- **GET** `/api/projects/?team=1` - Filtrer les projets par équipe
- **GET** `/api/projects/?search=terme` - Rechercher des projets

### Tâches

- **GET** `/api/tasks/` - Liste toutes les tâches
- **GET** `/api/tasks/{id}/` - Détails d'une tâche spécifique
- **GET** `/api/tasks/?project=1` - Filtrer les tâches par projet
- **GET** `/api/tasks/?status=En cours` - Filtrer les tâches par statut
- **GET** `/api/tasks/?priority=haute` - Filtrer les tâches par priorité
- **GET** `/api/tasks/?user=1` - Filtrer les tâches par utilisateur assigné
- **GET** `/api/tasks/?upcoming=true` - Tâches avec échéance dans les 7 prochains jours
- **GET** `/api/tasks/?overdue=true` - Tâches en retard (date d'échéance dépassée et non terminées)

### Équipes

- **GET** `/api/teams/` - Liste toutes les équipes
- **GET** `/api/teams/{id}/` - Détails d'une équipe spécifique avec ses membres

### Utilisateurs

- **GET** `/api/users/` - Liste tous les utilisateurs
- **GET** `/api/users/{id}/` - Détails d'un utilisateur spécifique
- **GET** `/api/profile/` - Profil de l'utilisateur connecté

### Commentaires

- **GET** `/api/comments/?project=1` - Commentaires d'un projet spécifique
- **GET** `/api/comments/?task=1` - Commentaires d'une tâche spécifique

## Authentification

L'API utilise l'authentification par token. Pour accéder aux endpoints protégés, vous devez inclure un en-tête `Authorization` dans vos requêtes :

```
Authorization: Bearer <token>
```

## Configuration pour l'application mobile

1. Assurez-vous que le serveur Django est en cours d'exécution
2. Dans le fichier `client_lourd/src/services/authService.js`, remplacez `YOUR_SERVER_IP` par l'adresse IP ou le nom de domaine de votre serveur
3. Assurez-vous que le port `8000` est ouvert et accessible depuis l'appareil mobile

## CORS

L'API est configurée pour accepter les requêtes de toutes les origines (`CORS_ALLOW_ALL_ORIGINS = True`). En production, il est recommandé de restreindre cette configuration à des origines spécifiques.

## Déploiement

Pour déployer cette API en production :

1. Modifiez `settings.py` pour désactiver `DEBUG` et configurer `ALLOWED_HOSTS`
2. Configurez un serveur WSGI comme Gunicorn
3. Utilisez un serveur web comme Nginx comme proxy
4. Configurez HTTPS avec Let's Encrypt pour sécuriser les communications