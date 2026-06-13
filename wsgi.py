import os
from app import create_app, db
from app.models import User, Skill, Video, Mission

app = create_app(os.getenv('FLASK_ENV', 'production'))

with app.app_context():
    db.create_all()

    # Only creates hardcoded users if database is truly empty
    # Otherwise, uses the 100+ seeded users already in the database
    if User.query.count() == 0:
        from werkzeug.security import generate_password_hash

        # ── Comptes système ──────────────────────────────────────────────────
        admin = User(username='admin', email='admin@skillrush.com',
                     password=generate_password_hash('Admin1234!'), role='admin',
                     level=10, xp=9999, onboarding_done=True,
                     bio='Administrateur SkillRush')
        moderator = User(username='moderator', email='moderator@skillrush.com',
                         password=generate_password_hash('Moderator1234!'), role='moderator',
                         level=5, xp=3000, onboarding_done=True,
                         bio='Équipe modération SkillRush')
        demo = User(username='demo', email='demo@skillrush.com',
                    password=generate_password_hash('Demo1234!'), role='user',
                    level=3, xp=850, onboarding_done=True,
                    bio='Étudiant ENCG Marrakech')

        # ── Formateurs réalistes ENCG ────────────────────────────────────────
        karim = User(username='Karim_Benali', email='karim.benali@encg.ma',
                     password=generate_password_hash('Karim1234!'), role='user',
                     level=8, xp=4200, onboarding_done=True,
                     competence='Business',
                     bio='Étudiant S6 ENCG Marrakech | Passionné Excel & Finance')
        sara = User(username='Sara_Moussaoui', email='sara.moussaoui@encg.ma',
                    password=generate_password_hash('Sara1234!'), role='user',
                    level=7, xp=3800, onboarding_done=True,
                    competence='Design',
                    bio='Étudiante S5 ENCG | Créatrice de contenu Canva & Design')
        youssef = User(username='Youssef_Tahiri', email='youssef.tahiri@encg.ma',
                       password=generate_password_hash('Youssef1234!'), role='user',
                       level=9, xp=5100, onboarding_done=True,
                       competence='Marketing',
                       bio='Alumni ENCG 2024 | Marketing Digital & Réseaux sociaux')
        imane = User(username='Imane_Chraibi', email='imane.chraibi@encg.ma',
                     password=generate_password_hash('Imane1234!'), role='user',
                     level=6, xp=2900, onboarding_done=True,
                     competence='Programming',
                     bio='Étudiante S4 ENCG | Python & Data Analysis')
        mehdi = User(username='Mehdi_Alaoui', email='mehdi.alaoui@encg.ma',
                     password=generate_password_hash('Mehdi1234!'), role='user',
                     level=7, xp=3500, onboarding_done=True,
                     competence='Business',
                     bio='Étudiant S6 ENCG | Entrepreneuriat & Business Plan')

        db.session.add_all([admin, moderator, demo, karim, sara, youssef, imane, mehdi])
        db.session.flush()  # obtenir les IDs

        # ── Cours & Vidéos ───────────────────────────────────────────────────
        courses = [
            # ── Excel ──────────────────────────────────────────────────────
            {
                'skill': Skill(name='Excel Avancé pour la Finance',
                               description='Maîtrisez Excel pour les analyses financières : tableaux croisés dynamiques, formules avancées, dashboards. Cours conçu pour les étudiants ENCG.',
                               category='Business', difficulty='Intermediate',
                               rating=4.8, views=312, is_approved=True, creator_id=karim.id),
                'videos': [
                    Video(title='Introduction & Interface Excel', description='Présentation de l\'interface, raccourcis essentiels et navigation rapide.', video_url='https://www.youtube.com/embed/rwbho0CgEAI', duration=720, is_free=True, xp_cost=0, order=0),
                    Video(title='Formules RECHERCHEV & INDEX/EQUIV', description='Maîtriser les formules de recherche indispensables en entreprise.', video_url='https://www.youtube.com/embed/M5oxK7TbRRQ', duration=860, is_free=False, xp_cost=100, order=1),
                    Video(title='Tableaux Croisés Dynamiques', description='Créer des TCD puissants pour analyser vos données en quelques clics.', video_url='https://www.youtube.com/embed/qu-AK0Hv0b4', duration=940, is_free=False, xp_cost=100, order=2),
                    Video(title='Dashboard Financier Complet', description='Construire un tableau de bord interactif avec graphiques dynamiques.', video_url='https://www.youtube.com/embed/K74_FNnlIF8', duration=1080, is_free=False, xp_cost=100, order=3),
                ],
                'missions': [
                    Mission(title='Crée ton premier TCD', description='Télécharge le fichier exercice et crée un tableau croisé dynamique.', objective='Créer un TCD sur un jeu de données de ventes', reward_xp=150, difficulty='Easy'),
                    Mission(title='Dashboard en 30 min', description='Reproduis le dashboard vu en cours sur tes propres données.', objective='Créer un dashboard avec 3 graphiques liés', reward_xp=300, difficulty='Medium'),
                ]
            },
            # ── Canva ───────────────────────────────────────────────────────
            {
                'skill': Skill(name='Canva Pro : Design sans être graphiste',
                               description='Créez des présentations, posts Instagram, CV et affiches professionnelles avec Canva. Zéro compétence technique requise.',
                               category='Design', difficulty='Beginner',
                               rating=4.9, views=487, is_approved=True, creator_id=sara.id),
                'videos': [
                    Video(title='Prise en main de Canva', description='Interface, templates gratuits et outils de base pour démarrer rapidement.', video_url='https://www.youtube.com/embed/qRpMF_5FKAM', duration=650, is_free=True, xp_cost=0, order=0),
                    Video(title='Créer une présentation pro', description='Design d\'un PowerPoint moderne pour tes exposés ENCG.', video_url='https://www.youtube.com/embed/AHsGGr70Xzk', duration=780, is_free=False, xp_cost=100, order=1),
                    Video(title='CV visuel qui se démarque', description='Crée un CV graphique qui attire l\'attention des recruteurs.', video_url='https://www.youtube.com/embed/FDMtEPmcVhg', duration=720, is_free=False, xp_cost=100, order=2),
                ],
                'missions': [
                    Mission(title='Refais ton CV avec Canva', description='Utilise un template Canva pour redesigner ton CV actuel.', objective='CV exporté en PDF avec photo et couleurs cohérentes', reward_xp=200, difficulty='Easy'),
                ]
            },
            # ── Marketing ──────────────────────────────────────────────────
            {
                'skill': Skill(name='Marketing Digital & Réseaux Sociaux',
                               description='Stratégie de contenu, publicité Meta, analytics et personal branding. Tout ce qu\'un étudiant ENCG doit savoir pour travailler en marketing.',
                               category='Marketing', difficulty='Intermediate',
                               rating=4.7, views=263, is_approved=True, creator_id=youssef.id),
                'videos': [
                    Video(title='Fondamentaux du Marketing Digital', description='Les 4P à l\'ère numérique, funnel de conversion et KPIs essentiels.', video_url='https://www.youtube.com/embed/bixR-KIJKYM', duration=900, is_free=True, xp_cost=0, order=0),
                    Video(title='Créer une stratégie de contenu', description='Plan éditorial, calendrier de publication et choix des plateformes.', video_url='https://www.youtube.com/embed/TM6B_g1FU_w', duration=840, is_free=False, xp_cost=100, order=1),
                    Video(title='Publicité Meta (Facebook & Instagram)', description='Créer et optimiser des campagnes publicitaires avec petit budget.', video_url='https://www.youtube.com/embed/6VPqO-8FMiI', duration=1020, is_free=False, xp_cost=100, order=2),
                ],
                'missions': [
                    Mission(title='Analyse un compte Instagram', description='Choisis une marque marocaine et analyse sa stratégie de contenu.', objective='Rapport de 1 page avec forces/faiblesses et recommandations', reward_xp=250, difficulty='Medium'),
                ]
            },
            # ── Python ─────────────────────────────────────────────────────
            {
                'skill': Skill(name='Python pour l\'Analyse de Données',
                               description='Apprenez Python avec pandas et matplotlib pour analyser des données business. Parfait pour les étudiants ENCG en Finance ou Contrôle de gestion.',
                               category='Programming', difficulty='Intermediate',
                               rating=4.6, views=198, is_approved=True, creator_id=imane.id),
                'videos': [
                    Video(title='Python en 30 min — Les bases', description='Variables, listes, boucles et fonctions. Tout ce qu\'il faut pour commencer.', video_url='https://www.youtube.com/embed/8DvywoWv6fI', duration=1800, is_free=True, xp_cost=0, order=0),
                    Video(title='Pandas pour analyser des données Excel', description='Importer, filtrer et agréger des données avec pandas.', video_url='https://www.youtube.com/embed/vmEHCJofslg', duration=1200, is_free=False, xp_cost=100, order=1),
                    Video(title='Visualisation avec Matplotlib', description='Graphiques en barres, courbes et camemberts en Python.', video_url='https://www.youtube.com/embed/3Xc3CA655Y4', duration=960, is_free=False, xp_cost=100, order=2),
                ],
                'missions': [
                    Mission(title='Analyse un dataset CSV', description='Télécharge un dataset de ventes et calcule le CA par région avec pandas.', objective='Script Python qui affiche un graphique de résultats', reward_xp=350, difficulty='Hard'),
                ]
            },
            # ── Business Plan ──────────────────────────────────────────────
            {
                'skill': Skill(name='Créer un Business Plan Solide',
                               description='De l\'idée au business model : étude de marché, analyse financière, pitch deck. Cours pratique orienté projets de fin d\'études ENCG.',
                               category='Business', difficulty='Advanced',
                               rating=4.9, views=175, is_approved=True, creator_id=mehdi.id),
                'videos': [
                    Video(title='Canvas Business Model expliqué', description='Les 9 blocs du Business Model Canvas avec exemples concrets.', video_url='https://www.youtube.com/embed/QoAOzMTLP5s', duration=780, is_free=True, xp_cost=0, order=0),
                    Video(title='Étude de marché : méthode ENCG', description='Comment réaliser une étude de marché rigoureuse en 5 étapes.', video_url='https://www.youtube.com/embed/YZQM3C4D5RI', duration=920, is_free=False, xp_cost=100, order=1),
                    Video(title='Prévisions financières & Rentabilité', description='Compte de résultat prévisionnel, seuil de rentabilité, cash flow.', video_url='https://www.youtube.com/embed/1Q37yqWKNc8', duration=1100, is_free=False, xp_cost=100, order=2),
                ],
                'missions': [
                    Mission(title='Remplis ton Business Model Canvas', description='Complète les 9 blocs pour ton projet ou une startup de ton choix.', objective='Canvas complet avec justification de chaque bloc', reward_xp=300, difficulty='Medium'),
                    Mission(title='Pitch de 3 minutes', description='Prépare et enregistre un pitch de ton projet en moins de 3 minutes.', objective='Vidéo de pitch ou slides + notes', reward_xp=400, difficulty='Hard'),
                ]
            },
            # ── CV & Entretien ─────────────────────────────────────────────
            {
                'skill': Skill(name='CV & Entretien d\'embauche',
                               description='Optimise ton CV, ta lettre de motivation et prépare-toi aux entretiens. Conseils issus de recruteurs marocains et multinationales.',
                               category='Business', difficulty='Beginner',
                               rating=4.8, views=401, is_approved=True, creator_id=karim.id),
                'videos': [
                    Video(title='Les 7 erreurs fatales sur un CV', description='Les erreurs qui font rejeter un CV en moins de 10 secondes.', video_url='https://www.youtube.com/embed/7s2UtCW-b8s', duration=600, is_free=True, xp_cost=0, order=0),
                    Video(title='Rédiger une lettre de motivation percutante', description='Structure, ton et formules à utiliser pour convaincre le recruteur.', video_url='https://www.youtube.com/embed/p2xhT7CKWiI', duration=720, is_free=False, xp_cost=100, order=1),
                    Video(title='Simuler un entretien RH', description='Les 10 questions les plus posées et comment y répondre avec confiance.', video_url='https://www.youtube.com/embed/HG68Ymazo18', duration=840, is_free=False, xp_cost=100, order=2),
                ],
                'missions': [
                    Mission(title='Améliore ton CV en 24h', description='Applique les conseils du cours pour retravailler ton CV actuel.', objective='CV corrigé et soumis pour feedback', reward_xp=200, difficulty='Easy'),
                ]
            },
            # ── Négociation ─────────────────────────────────────────────────
            {
                'skill': Skill(name='Négociation Commerciale',
                               description='Techniques de négociation utilisées en entreprise : BATNA, ancrage, concessions. Apprenez à négocier salaire, contrats et partenariats.',
                               category='Business', difficulty='Intermediate',
                               rating=4.5, views=142, is_approved=True, creator_id=youssef.id),
                'videos': [
                    Video(title='Les principes de la négociation', description='Win-win, BATNA et préparation d\'une négociation efficace.', video_url='https://www.youtube.com/embed/MFxGHMJsOmc', duration=780, is_free=True, xp_cost=0, order=0),
                    Video(title='Techniques d\'ancrage et concessions', description='Comment utiliser le premier chiffre pour influencer toute la négociation.', video_url='https://www.youtube.com/embed/yLnSbC8xnN4', duration=860, is_free=False, xp_cost=100, order=1),
                ],
                'missions': [
                    Mission(title='Jeu de rôle : Négocie ton stage', description='Simulez une négociation de salaire de stage avec un camarade.', objective='Résumé de la négociation avec ce que tu as obtenu', reward_xp=250, difficulty='Medium'),
                ]
            },
        ]

        for course in courses:
            skill_obj = course['skill']
            db.session.add(skill_obj)
            db.session.flush()
            for v in course['videos']:
                v.skill_id = skill_obj.id
                db.session.add(v)
            for m in course['missions']:
                m.skill_id = skill_obj.id
                db.session.add(m)

        db.session.commit()
