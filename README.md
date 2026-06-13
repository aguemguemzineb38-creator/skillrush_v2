# 🚀 SkillRush - Application d'Apprentissage Gamifiée

SkillRush est une plateforme d'apprentissage moderne et interactive qui combine la gamification avec le partage de compétences. Conçue pour les étudiants et jeunes diplômés au Maroc et au-delà.

## 📋 Table des matières

- [Architecture](#architecture)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Fonctionnalités](#fonctionnalités)
- [Structure du projet](#structure-du-projet)
- [Technologies](#technologies)
- [Données de test](#données-de-test)

## 🏗️ Architecture

SkillRush suit l'architecture **MVC (Model-View-Controller)** :

```
skillrush_app/
├── app/
│   ├── models/              # Modèles de données (ORM SQLAlchemy)
│   │   ├── models.py        # User, Skill, Video, Mission, etc.
│   │   └── __init__.py
│   ├── controllers/         # Logique métier
│   │   ├── main_controller.py
│   │   ├── auth_controller.py
│   │   ├── skill_controller.py
│   │   ├── user_controller.py
│   │   ├── mission_controller.py
│   │   └── __init__.py
│   ├── views/              # Templates HTML (Jinja2)
│   │   ├── base.html
│   │   ├── home.html
│   │   ├── dashboard.html
│   │   ├── auth/
│   │   ├── skill/
│   │   ├── user/
│   │   └── mission/
│   ├── static/             # Ressources statiques
│   │   ├── css/style.css
│   │   ├── js/main.js
│   │   └── images/
│   ├── routes.py           # Définition des routes (Blueprints)
│   └── __init__.py         # Initialisation Flask
├── config.py               # Configuration (dev, test, prod)
├── run.py                  # Point d'entrée
├── requirements.txt        # Dépendances
└── .env                    # Variables d'environnement
```

## 📦 Installation

### Prérequis

- Python 3.8+
- pip ou conda
- Git

### Étapes

1. **Cloner le repository**
   ```bash
   cd skillrush_app
   ```

2. **Créer un environnement virtuel**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Sur Windows: venv\Scripts\activate
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurer les variables d'environnement**
   ```bash
   # Éditer le fichier .env avec vos paramètres
   cat .env
   ```

5. **Lancer l'application**
   ```bash
   python run.py
   ```

6. **Accéder à l'application**
   ```
   http://localhost:5000
   ```

## 🎮 Utilisation

### Inscription et Connexion

1. Cliquez sur "Inscription" ou "S'inscrire"
2. Remplissez le formulaire avec vos données
3. Connectez-vous avec vos identifiants

### Découvrir des compétences

1. Allez dans "Découvrir" pour voir toutes les compétences
2. Utilisez la recherche et les filtres par catégorie
3. Cliquez sur une compétence pour voir les détails

### Apprendre

1. Regardez les vidéos d'apprentissage gratuites
2. Progressez à travers le contenu
3. Complétez les missions pour gagner des récompenses
4. Notez la compétence pour gagner des coins

### Créer et partager

1. Allez dans "Publier un cours"
2. Créez une nouvelle compétence
3. Ajoutez des vidéos et des missions
4. Partagez avec la communauté

## ✨ Fonctionnalités

### Système de Gamification

- **Niveaux** : Progressez et débloquez des achievements
- **Coins** : Gagnez des récompenses pour vos activités
- **XP** : Accumulez de l'expérience pour monter de niveau
- **Missions** : Complétez des défis pour gagner des récompenses

### Gestion des compétences

- **Recherche** : Trouvez facilement les compétences
- **Catégories** : Excel, Canva, CV, Design, Programming, etc.
- **Mini-vidéos** : Contenu court et engageant (1-2 minutes)
- **Notation** : Évaluez les compétences et les formateurs

### Progression utilisateur

- **Suivi** : Suivez votre progression en temps réel
- **Statistiques** : Consultez vos statistiques
- **Profil** : Personnalisez votre profil utilisateur
- **Classement** : Voyez où vous vous situez

### Système de missions

- **Missions variées** : Easy, Medium, Hard, Expert
- **Récompenses** : Coins et XP
- **Suivi** : Suivez vos missions en cours et complétées

## 🗂️ Structure du projet détaillée

### Models (models/models.py)

```python
User          # Utilisateur avec gamification
Skill         # Compétence créée par un utilisateur
Video         # Vidéo d'apprentissage
Mission       # Mission/défi lié à une compétence
UserMission   # Suivre les missions de l'utilisateur
UserProgress  # Suivre la progression d'un utilisateur
```

### Controllers

- **main_controller.py** : Dashboard, exploration, classement
- **auth_controller.py** : Inscription, connexion, déconnexion
- **skill_controller.py** : CRUD des compétences et vidéos
- **user_controller.py** : Gestion du profil et progression
- **mission_controller.py** : Gestion des missions

### Routes

Les routes sont organisées par blueprint :

- `/` - Dashboard
- `/auth/` - Authentification
- `/skill/` - Compétences
- `/user/` - Utilisateurs
- `/mission/` - Missions

## 🛠️ Technologies

### Backend

- **Flask** : Framework web Python
- **SQLAlchemy** : ORM pour la base de données
- **Flask-Login** : Gestion de l'authentification
- **SQLite** : Base de données (par défaut)

### Frontend

- **Bootstrap 5** : Framework CSS
- **HTML5** : Structure
- **CSS3** : Styles personnalisés
- **JavaScript** : Interactions et animations
- **Font Awesome** : Icônes

### Architecture

- **MVC** : Séparation des responsabilités
- **REST API** : Endpoints pour les opérations
- **Jinja2** : Moteur de template

## 📊 Données de test

L'application crée automatiquement des données de test au premier démarrage :

### Utilisateurs
- `demo_user` / `password123` (Niveau 5, 500 coins)
- `trainer` / `password123` (Niveau 8, 1000 coins)

### Compétences
- Excel Avancé (Intermediate)
- Canva pour Débutants (Beginner)

### Vidéos
- Introduction à Excel (gratuite)
- Formules avancées (premium)

### Missions
- Créer un tableau de budget

## 🚀 Prochaines étapes

### Améliorations futures

- [ ] Système d'authentification social (Google, GitHub)
- [ ] Notifications en temps réel
- [ ] Système de recommandation (IA)
- [ ] Certification des utilisateurs
- [ ] App mobile (React Native)
- [ ] Live streaming des cours
- [ ] Système de badges
- [ ] Intégration de paiement
- [ ] Analytics et rapports
- [ ] Support multilingue

## 📝 Notes de développement

### Configuration en développement

```bash
FLASK_ENV=development
DEBUG=True
```

### Configuration en production

```bash
FLASK_ENV=production
DEBUG=False
SECRET_KEY=<strong-secret-key>
DATABASE_URL=<postgresql-url>
```

> Railway prend aussi en charge `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD` et `PGDATABASE`.
>
> Pour seed la base Railway depuis le dépôt :
>
> ```bash
> railway run psql -f railway_db_seed.sql
> ```
>
> Si vous utilisez le binaire local Railway :
>
> ```powershell
> .\railway-cli\railway.exe run psql -f railway_db_seed.sql
> ```

### Créer la base de données

```bash
python
>>> from app import create_app, db
>>> app = create_app()
>>> with app.app_context():
...     db.create_all()
```

## 🤝 Contribution

Les contributions sont bienvenues! Consultez CONTRIBUTING.md pour plus de détails.

## 📄 Licence

Ce projet est sous licence MIT.

## 👥 Auteur

**SkillRush Team** - Plateforme d'apprentissage gamifiée

---

**Faites connaître SkillRush à votre communauté! 🚀**
