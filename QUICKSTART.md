# 📖 Guide de Démarrage - SkillRush

## ⚡ Démarrage rapide (5 minutes)

### 1. Installer Python 3.8+
- Télécharger depuis [python.org](https://www.python.org)
- Vérifier l'installation : `python --version`

### 2. Configurer l'environnement
```bash
# Aller dans le dossier du projet
cd skillrush_app

# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement virtuel
# Sur Windows:
venv\Scripts\activate
# Sur Mac/Linux:
source venv/bin/activate
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Lancer l'application
```bash
python run.py
```

### 5. Accéder à l'application
Ouvrir votre navigateur et aller à : **http://localhost:5000**

## 🔐 Comptes de test

Utilisez ces identifiants pour tester :

| Username | Password | Rôle | Niveau |
|----------|----------|------|--------|
| demo_user | password123 | Apprenant | 5 |
| trainer | password123 | Formateur | 8 |

## 📱 Parcours utilisateur

### Pour les apprenants :
1. S'inscrire ou se connecter
2. Aller dans "Découvrir" pour trouver une compétence
3. Regarder une vidéo gratuite
4. Compléter une mission pour gagner des récompenses
5. Consulter votre profil pour suivre votre progression

### Pour les formateurs :
1. Se connecter
2. Cliquer sur "Publier un cours"
3. Créer une nouvelle compétence
4. Ajouter des vidéos d'apprentissage
5. Créer des missions pour les apprenants

## 🎮 Système de gamification

### Niveaux
- Commence au niveau 1
- Monte de niveau tous les 1000 XP
- Débloquez des achievements

### Coins
- Gagnez 50 coins par jour
- 50 coins pour noter une compétence
- 100-500 coins pour compléter une mission

### XP
- 25 XP par jour
- 10-50 XP par vidéo regardée
- 50-500 XP par mission complétée

### Missions
- **Easy** : 100 coins, 50 XP
- **Medium** : 200 coins, 100 XP
- **Hard** : 350 coins, 200 XP
- **Expert** : 500 coins, 300 XP

## 📊 Données de test

Les données suivantes sont créées automatiquement :

### Compétences
- Excel Avancé (Intermediate)
- Canva pour Débutants (Beginner)

### Vidéos
- Introduction à Excel (gratuite)
- Formules avancées (premium)

### Missions
- Créer un tableau de budget

## 🐛 Dépannage

### Erreur : "No module named flask"
```bash
pip install -r requirements.txt
```

### Erreur : Port 5000 déjà utilisé
```bash
# Sur Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Sur Mac/Linux:
lsof -ti:5000 | xargs kill -9
```

### Base de données corrompue
```bash
# Supprimer la base de données
rm skillrush.db

# Relancer l'application
python run.py
```

## 🔧 Configuration avancée

### Changer le port
Éditer `run.py` et modifier :
```python
app.run(debug=True, host='0.0.0.0', port=8000)
```

### Utiliser PostgreSQL
Éditer `.env` :
```
DATABASE_URL=postgresql://user:password@localhost/skillrush
```

### Mode production
```bash
# Éditer .env
FLASK_ENV=production
DEBUG=False

# Utiliser un serveur WSGI
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 run:app
```

## 📚 Documentation complète

Voir [README.md](README.md) pour la documentation complète.

## 🆘 Besoin d'aide?

- Consultez le [README.md](README.md)
- Vérifiez les logs dans le terminal
- Reportez les bugs sur GitHub Issues

---

**Prêt à commencer ? Lancez `python run.py` ! 🚀**
