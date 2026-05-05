import os
from app import create_app


def _seed_default_users(app):
    """Crée les comptes par défaut si la base est vide."""
    from app.models import db, User
    from werkzeug.security import generate_password_hash

    with app.app_context():
        if User.query.first() is not None:
            return  # données déjà présentes

        admin = User(
            username='trainer',
            email='trainer@skillrush.com',
            password=generate_password_hash('password123'),
            role='admin',
            level=8,
            xp=5000,
            onboarding_done=True
        )
        moderator = User(
            username='moderator',
            email='moderator@skillrush.com',
            password=generate_password_hash('password123'),
            role='moderator',
            level=4,
            xp=1800,
            onboarding_done=True
        )
        demo = User(
            username='demo_user',
            email='demo@skillrush.com',
            password=generate_password_hash('password123'),
            role='user',
            level=5,
            xp=2500,
            onboarding_done=True
        )
        db.session.add_all([admin, moderator, demo])
        db.session.commit()


def main():
    config_name = os.getenv("FLASK_ENV", "production")
    app = create_app(config_name)
    _seed_default_users(app)
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)


if __name__ == "__main__":
    main()
