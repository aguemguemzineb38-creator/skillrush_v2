import os
from app import create_app, db
from app.models import User, Skill, Video, Mission, UserMission, UserProgress

if __name__ == '__main__':
    app = create_app(os.getenv('FLASK_ENV', 'development'))
    
    with app.app_context():
        # Créer les tables
        db.create_all()
        
        # Ajouter des données de test
        if User.query.first() is None:
            from werkzeug.security import generate_password_hash
            # Créer des utilisateurs de test
            user1 = User(
                username='demo_user',
                email='demo@skillrush.com',
                password=generate_password_hash('password123'),
                level=5,
                xp=2500
            )
            
            user2 = User(
                username='trainer',
                email='trainer@skillrush.com',
                password=generate_password_hash('password123'),
                role='admin',
                level=8,
                xp=5000
            )

            user3 = User(
                username='moderator',
                email='moderator@skillrush.com',
                password=generate_password_hash('password123'),
                role='moderator',
                level=4,
                xp=1800
            )
            
            db.session.add(user1)
            db.session.add(user2)
            db.session.add(user3)
            db.session.commit()
            
            # Créer des compétences de test
            skill1 = Skill(
                name='Excel Avancé',
                description='Apprenez les fonctions avancées d\'Excel',
                category='Excel',
                difficulty='Intermediate',
                rating=4.5,
                creator_id=user2.id
            )
            
            skill2 = Skill(
                name='Canva pour Débutants',
                description='Créer des designs magnifiques avec Canva',
                category='Canva',
                difficulty='Beginner',
                rating=4.8,
                creator_id=user2.id
            )
            
            db.session.add(skill1)
            db.session.add(skill2)
            db.session.commit()
            
            # Créer des vidéos de test
            video1 = Video(
                title='Introduction à Excel',
                description='Les bases d\'Excel expliquées simplement',
                duration=120,
                video_url='https://www.youtube.com/embed/dQw4w9WgXcQ',
                is_free=True,
                skill_id=skill1.id
            )
            
            video2 = Video(
                title='Formules avancées',
                description='Apprenez les formules complexes',
                duration=180,
                video_url='https://www.youtube.com/embed/dQw4w9WgXcQ',
                is_free=False,
                skill_id=skill1.id
            )
            
            db.session.add(video1)
            db.session.add(video2)
            db.session.commit()
            
            # Créer des missions de test
            mission1 = Mission(
                title='Créer un tableau de budget',
                description='Créez un tableau de budget mensuel',
                objective='Utiliser les formules SUM et AVERAGE',
                reward_xp=100,
                difficulty='Medium',
                skill_id=skill1.id
            )
            
            db.session.add(mission1)
            db.session.commit()
            
            print("✓ Données de test créées avec succès")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
