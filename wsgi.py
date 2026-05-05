import os
from app import create_app, db
from app.models import User

app = create_app(os.getenv('FLASK_ENV', 'production'))

with app.app_context():
    db.create_all()

    # Créer les comptes par défaut si la base est vide
    if User.query.first() is None:
        from werkzeug.security import generate_password_hash

        users = [
            User(username='admin',     email='admin@skillrush.com',
                 password=generate_password_hash('Admin1234!'),    role='admin',
                 level=10, xp=9999, onboarding_done=True),
            User(username='moderator', email='moderator@skillrush.com',
                 password=generate_password_hash('Moderator1234!'), role='moderator',
                 level=5,  xp=3000, onboarding_done=True),
            User(username='demo',      email='demo@skillrush.com',
                 password=generate_password_hash('Demo1234!'),      role='user',
                 level=1,  xp=100,  onboarding_done=True),
        ]
        db.session.add_all(users)
        db.session.commit()
