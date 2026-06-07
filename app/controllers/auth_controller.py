from flask import render_template, request, redirect, url_for, flash, session, current_app
from app.models import db, User
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.email_utils import send_welcome_email
import os
import secrets
import requests as http_requests

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
            return redirect(url_for('main.dashboard'))
        
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
            # Rediriger selon le rôle pour que le même formulaire permette aux admins/modérateurs
            if getattr(user, 'role', None) == 'admin':
                return redirect(url_for('admin.admin_users'))
            if getattr(user, 'role', None) == 'moderator':
                return redirect(url_for('moderation.moderation_dashboard'))
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

    # ── Google OAuth ──────────────────────────────────────────────────────────

    @staticmethod
    def google_login():
        """Redirige vers Google pour l'authentification."""
        client_id = os.getenv('GOOGLE_CLIENT_ID', '')
        if not client_id:
            flash("L'authentification Google n'est pas configurée.", 'error')
            return redirect(url_for('auth.login'))
        state = secrets.token_urlsafe(16)
        session['oauth_state'] = state
        # Utiliser GOOGLE_CALLBACK_URL si défini (Railway), sinon url_for
        callback_url = os.getenv('GOOGLE_CALLBACK_URL') or url_for('auth.google_callback', _external=True)
        google_auth_url = (
            "https://accounts.google.com/o/oauth2/v2/auth"
            f"?client_id={client_id}"
            f"&redirect_uri={callback_url}"
            "&response_type=code"
            "&scope=openid%20email%20profile"
            f"&state={state}"
        )
        return redirect(google_auth_url)

    @staticmethod
    def google_callback():
        """Reçoit le code Google et connecte/crée l'utilisateur."""
        if request.args.get('state') != session.pop('oauth_state', None):
            flash('Erreur de sécurité OAuth. Veuillez réessayer.', 'error')
            return redirect(url_for('auth.login'))

        code = request.args.get('code')
        if not code:
            flash("Connexion Google annulée.", 'warning')
            return redirect(url_for('auth.login'))

        client_id     = os.getenv('GOOGLE_CLIENT_ID', '')
        client_secret = os.getenv('GOOGLE_CLIENT_SECRET', '')
        # Utiliser la même URL que celle envoyée à Google dans google_login()
        callback_url  = os.getenv('GOOGLE_CALLBACK_URL') or url_for('auth.google_callback', _external=True)

        # Échanger le code contre un token
        token_resp = http_requests.post(
            'https://oauth2.googleapis.com/token',
            data={
                'code': code,
                'client_id': client_id,
                'client_secret': client_secret,
                'redirect_uri': callback_url,
                'grant_type': 'authorization_code',
            },
            timeout=10
        )
        token_data = token_resp.json()
        access_token = token_data.get('access_token')
        if not access_token:
            flash("Impossible d'obtenir le token Google. Réessayez.", 'error')
            return redirect(url_for('auth.login'))

        # Récupérer le profil Google
        profile_resp = http_requests.get(
            'https://www.googleapis.com/oauth2/v2/userinfo',
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=10
        )
        profile = profile_resp.json()
        google_email = profile.get('email', '').lower().strip()
        google_name  = profile.get('name', '').strip()
        google_id    = profile.get('id', '')

        if not google_email:
            flash("Impossible de récupérer l'email Google.", 'error')
            return redirect(url_for('auth.login'))

        # Chercher ou créer l'utilisateur
        user = User.query.filter_by(email=google_email).first()
        if not user:
            # Générer un username unique
            base_username = google_name.replace(' ', '').lower()[:20] or 'user'
            username = base_username
            suffix = 1
            while User.query.filter_by(username=username).first():
                username = f"{base_username}{suffix}"
                suffix += 1

            user = User(
                username=username,
                email=google_email,
                password=generate_password_hash(secrets.token_urlsafe(24)),
                onboarding_done=True,
            )
            db.session.add(user)
            db.session.commit()
            try:
                dashboard_url = url_for('main.dashboard', _external=True)
                send_welcome_email(user.email, user.username, dashboard_url=dashboard_url)
            except Exception:
                pass

        if user.is_blocked:
            flash('Votre compte est bloqué. Contactez un administrateur.', 'error')
            return redirect(url_for('auth.login'))

        login_user(user)
        flash(f'Bienvenue {user.username} !', 'success')
        return redirect(url_for('main.dashboard'))
