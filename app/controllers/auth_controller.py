from flask import render_template, request, redirect, url_for, flash
from app.models import db, User
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.email_utils import send_welcome_email

class AuthController:
    """Contrôleur d'authentification"""

    @staticmethod
    def _role_login(required_role, page_title, success_endpoint):
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')

            if not username or not password:
                flash('Veuillez remplir tous les champs', 'error')
                return render_template('auth/role_login.html', page_title=page_title)

            user = User.query.filter_by(username=username).first()

            if not user or not check_password_hash(user.password, password):
                flash('Nom d\'utilisateur ou mot de passe incorrect', 'error')
                return render_template('auth/role_login.html', page_title=page_title)

            if user.is_blocked:
                flash('Votre compte est bloqué. Contactez un administrateur.', 'error')
                return render_template('auth/role_login.html', page_title=page_title)

            if user.role != required_role:
                flash('Accès refusé : rôle non autorisé pour cet espace.', 'error')
                return render_template('auth/role_login.html', page_title=page_title)

            login_user(user)
            flash(f'Bienvenue {user.username} !', 'success')
            return redirect(url_for(success_endpoint))

        return render_template('auth/role_login.html', page_title=page_title)
    
    @staticmethod
    def register():
        """Page d'inscription"""
        if request.method == 'POST':
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            
            # Validation
            if not username or not email or not password:
                flash('Veuillez remplir tous les champs', 'error')
                return render_template('auth/register.html')
            
            if password != confirm_password:
                flash('Les mots de passe ne correspondent pas', 'error')
                return render_template('auth/register.html')
            
            # Vérifier si l'utilisateur existe
            if User.query.filter_by(username=username).first():
                flash('Ce nom d\'utilisateur existe déjà', 'error')
                return render_template('auth/register.html')
            
            if User.query.filter_by(email=email).first():
                flash('Cet email est déjà utilisé', 'error')
                return render_template('auth/register.html')
            
            # Créer l'utilisateur
            user = User(
                username=username,
                email=email,
                password=generate_password_hash(password)
            )
            
            db.session.add(user)
            db.session.commit()

            # Email de bienvenue HTML
            try:
                dashboard_url = url_for('main.dashboard', _external=True)
                send_welcome_email(user.email, user.username, dashboard_url=dashboard_url)
            except Exception as e:
                from flask import current_app
                current_app.logger.error(f'[AUTH] Erreur envoi email bienvenue pour {user.username}: {e}', exc_info=True)

            login_user(user)
            return redirect(url_for('onboarding.step1'))
        
        return render_template('auth/register.html')
    
    @staticmethod
    def login():
        """Page de connexion"""
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            if not username or not password:
                flash('Veuillez remplir tous les champs', 'error')
                return render_template('auth/login.html')
            
            user = User.query.filter_by(username=username).first()
            
            if not user or not check_password_hash(user.password, password):
                flash('Nom d\'utilisateur ou mot de passe incorrect', 'error')
                return render_template('auth/login.html')
            
            if user.is_blocked:
                flash('Votre compte est bloqué. Contactez un administrateur.', 'error')
                return render_template('auth/login.html')
            
            login_user(user)
            if getattr(user, 'onboarding_rejected', False) and not user.onboarding_done:
                flash('Votre cours a été refusé. Consultez votre email puis revenez à l\'accueil pour préparer une nouvelle soumission.', 'warning')
                return redirect(url_for('main.rejected_course'))
            flash(f'Bienvenue {user.username} !', 'success')
            return redirect(url_for('main.dashboard'))
        
        return render_template('auth/login.html')

    @staticmethod
    def admin_login():
        """Connexion réservée aux administrateurs"""
        return AuthController._role_login(
            required_role='admin',
            page_title='Connexion Administrateur',
            success_endpoint='admin.admin_users'
        )

    @staticmethod
    def moderator_login():
        """Connexion réservée à l'équipe de modération"""
        return AuthController._role_login(
            required_role='moderator',
            page_title='Connexion Équipe de modération',
            success_endpoint='moderation.moderation_dashboard'
        )
    
    @staticmethod
    @login_required
    def logout():
        """Déconnexion"""
        logout_user()
        flash('Vous avez été déconnecté', 'info')
        return redirect(url_for('main.dashboard'))
