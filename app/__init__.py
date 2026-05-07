from flask import Flask
from flask_login import LoginManager
from config import config
from app.models import db
import os

login_manager = LoginManager()

def create_app(config_name='development'):
    """Factory pour créer l'application Flask"""
    # Obtenir le chemin du répertoire app
    basedir = os.path.dirname(os.path.abspath(__file__))
    
    app = Flask(__name__, 
                template_folder=os.path.join(basedir, 'views'),
                static_folder=os.path.join(basedir, 'static'))
    app.config.from_object(config[config_name])
    
    # Initialiser les extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
    
    # Importer les modèles
    from app.models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Créer les tables
    with app.app_context():
        db.create_all()
    
    # Enregistrer les blueprints
    from app.routes import register_blueprints
    register_blueprints(app)

    # ── Onboarding gate : redirige les nouveaux utilisateurs ─────────────────
    from flask import request as flask_request, redirect as flask_redirect, url_for as flask_url_for
    from flask_login import current_user as _current_user

    # Préfixes/endpoints autorisés sans onboarding complété
    _ONBOARDING_ALLOWED_PREFIXES = ('/auth/', '/static/', '/onboarding/')
    _ONBOARDING_ALLOWED_ENDPOINTS = {'onboarding.step1', 'onboarding.step2', 'onboarding.step3',
                                     'main.dashboard',
                                     'auth.login', 'auth.logout', 'auth.register',
                                     'auth.admin_login', 'auth.moderator_login', 'static',
                                     'user.buy_xp', 'user.process_xp_purchase'}

    @app.before_request
    def enforce_onboarding():
        """Bloque l'accès au reste de l'app tant que l'onboarding n'est pas terminé."""
        if not _current_user.is_authenticated:
            return
        endpoint = flask_request.endpoint or ''
        path = flask_request.path
        # Admins et modérateurs sont exemptés
        if _current_user.role in ('admin', 'moderator'):
            return
        if _current_user.onboarding_rejected and not _current_user.onboarding_done:
            if endpoint in {'main.rejected_course', 'onboarding.step1', 'onboarding.step2', 'auth.logout', 'static'}:
                return
            return flask_redirect(flask_url_for('main.rejected_course'))
        if _current_user.onboarding_done:
            return
        # Autoriser les routes d'onboarding et d'auth
        if endpoint in _ONBOARDING_ALLOWED_ENDPOINTS:
            return
        for prefix in _ONBOARDING_ALLOWED_PREFIXES:
            if path.startswith(prefix):
                return
        # Nouveau flux: un onboarding simple (choix catégorie ou skip)
        return flask_redirect(flask_url_for('onboarding.step1'))

    return app
