# Application de Gestion de Projet - Mairie de Paris (Client Léger)

Application web Django pour la gestion de projets de la Mairie de Paris.

## Fonctionnalités

- Gestion des utilisateurs (création, modification, suppression)
- Gestion des projets (création, modification, suppression, suivi des statuts)
- Gestion des tâches (ajout, modification, suppression, attribution, suivi des statuts)
- Gestion des équipes (création, attribution des membres)
- Commentaires sur les projets et les tâches
- Tableau de bord avec informations récentes

## Prérequis

- Python 3.10+
- MySQL
- Pip (gestionnaire de paquets Python)

## Installation

1. Cloner le dépôt
```
git clone <url-du-repo>
cd client_leger
```

2. Créer et activer un environnement virtuel
```
python -m venv venv
source venv/Scripts/activate  # Windows
# ou
source venv/bin/activate      # Linux/Mac
```

3. Installer les dépendances
```
pip install -r requirements.txt
```

4. Créer la base de données MySQL
```sql
CREATE DATABASE mairie_paris_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

5. Configurer les paramètres de base de données dans `mairie_paris_project/settings.py`

6. Appliquer les migrations
```
python manage.py makemigrations
python manage.py migrate
```

7. Créer un superutilisateur
```
python manage.py createsuperuser
```

8. Lancer le serveur de développement
```
python manage.py runserver
```

9. Accéder à l'application via http://127.0.0.1:8000/

## Structure du projet

- `mairie_paris_project/` - Configuration principale du projet Django
- `project_management/` - Application principale de gestion de projet
  - `models.py` - Modèles de données
  - `views.py` - Vues et logique métier
  - `urls.py` - Configuration des URLs
  - `templates/` - Templates HTML pour le frontend
  - `static/` - Fichiers statiques (CSS, JS, images)

## Technologies utilisées

- Backend : Django
- Frontend : HTML, CSS, jQuery, Bootstrap
- Base de données : MySQL
- Authentification : Session

## Modèle de données

Le modèle de données comprend les tables suivantes :
- Users (utilisateurs)
- Teams (équipes)
- Projects (projets)
- Tasks (tâches)
- Comments (commentaires)
- Settings (paramètres)