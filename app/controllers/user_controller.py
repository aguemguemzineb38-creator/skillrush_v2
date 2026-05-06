from flask import render_template, request, redirect, url_for, flash, jsonify, current_app
from app.models import db, User, UserProgress, UserMission, Mission, XPPurchase, Skill, Video, ContentUnlock
from flask_login import login_required, current_user
from datetime import datetime, timedelta, date
from functools import wraps
from app.email_utils import send_course_approved_email, send_course_rejected_email

# ── Décorateurs de rôle ──────────────────────────────────────────────────────

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Accès réservé aux administrateurs.', 'danger')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated

def moderator_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not (current_user.is_moderator or current_user.is_admin):
            flash('Accès réservé aux modérateurs/administrateurs.', 'danger')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated


def _build_ai_review(skill):
    """Construit un diagnostic explicable pour aider la modération."""
    name_len = len((skill.name or '').strip())
    desc_len = len((skill.description or '').strip())
    videos_count = len(skill.videos)
    has_pdf = bool(skill.course_pdf)

    score = 0
    reasons = []
    risks = []

    if name_len >= 8:
        score += 20
        reasons.append('Le titre est suffisamment précis et informatif.')
    else:
        score += 8
        risks.append('Le titre est trop court; il devrait mieux décrire le contenu.')

    if desc_len >= 120:
        score += 30
        reasons.append('La description est détaillée et contextualise bien le cours.')
    elif desc_len >= 60:
        score += 18
        reasons.append('La description est correcte mais peut être enrichie.')
    else:
        score += 6
        risks.append('La description est trop brève pour évaluer la qualité pédagogique.')

    if videos_count >= 2:
        score += 30
        reasons.append('Le cours contient plusieurs vidéos, ce qui favorise une progression par étapes.')
    elif videos_count == 1:
        score += 18
        reasons.append('Le cours contient une vidéo, mais un découpage en plusieurs parties serait préférable.')
    else:
        score += 4
        risks.append('Aucune vidéo détectée: le cours peut manquer de démonstration pratique.')

    if has_pdf:
        score += 20
        reasons.append('Un support PDF est disponible pour consolider l\'apprentissage.')
    else:
        score += 8
        risks.append('Aucun support PDF détecté: la révision hors vidéo est limitée.')

    recommendation = 'VALIDER' if score >= 70 else 'REVISION'
    return {
        'quality_score': min(score, 100),
        'recommendation': recommendation,
        'reasons': reasons,
        'risks': risks,
        'desc_len': desc_len,
        'videos_count': videos_count,
        'has_pdf': has_pdf,
    }

# ── XP packages disponibles à l'achat ────────────────────────────────────────
XP_PACKAGES = [
    {'id': 1, 'xp': 500,  'price': 4.99,  'label': 'Starter',   'icon': '⚡'},
    {'id': 2, 'xp': 1500, 'price': 9.99,  'label': 'Pro',       'icon': '🔥'},
    {'id': 3, 'xp': 4000, 'price': 19.99, 'label': 'Elite',     'icon': '💎'},
    {'id': 4, 'xp': 10000,'price': 39.99, 'label': 'Legendary', 'icon': '👑'},
]

class UserController:

    # ── Profil ────────────────────────────────────────────────────────────────

    @staticmethod
    def profile(user_id):
        user = User.query.get_or_404(user_id)

        created_skills = user.skills_created
        completed_missions = UserMission.query.filter_by(user_id=user_id, is_completed=True).count()
        learned_skills = UserProgress.query.filter_by(user_id=user_id, is_completed=True).count()
        return render_template('user/profile.html',
            profile_user=user,
            created_skills=created_skills,
            completed_missions=completed_missions,
            learned_skills=learned_skills)

    @staticmethod
    @login_required
    def edit_profile():
        if request.method == 'POST':
            username = request.form.get('username')
            email = request.form.get('email')
            bio = request.form.get('bio')
            if username != current_user.username and User.query.filter_by(username=username).first():
                flash("Ce nom d'utilisateur est déjà pris", 'error')
                return render_template('user/edit_profile.html')
            if email != current_user.email and User.query.filter_by(email=email).first():
                flash("Cet email est déjà utilisé", 'error')
                return render_template('user/edit_profile.html')
            current_user.username = username
            current_user.email = email
            current_user.bio = bio
            db.session.commit()
            flash('Profil mis à jour!', 'success')
            return redirect(url_for('user.profile', user_id=current_user.id))
        return render_template('user/edit_profile.html')

    # ── Progression ───────────────────────────────────────────────────────────

    @staticmethod
    @login_required
    def my_progress():
        user_progress = UserProgress.query.filter_by(user_id=current_user.id).all()
        total_skills = len(user_progress)
        completed_skills = sum(1 for p in user_progress if p.is_completed)
        avg_progress = sum(p.progress_percentage for p in user_progress) / total_skills if total_skills else 0
        return render_template('user/my_progress.html',
            user_progress=user_progress,
            total_skills=total_skills,
            completed_skills=completed_skills,
            avg_progress=avg_progress)

    # ── Achat XP ──────────────────────────────────────────────────────────────

    @staticmethod
    @login_required
    def buy_xp():
        """Page d'achat de XP — simulation carte bancaire (Stripe-ready)"""
        return render_template('user/buy_xp.html', packages=XP_PACKAGES)

    @staticmethod
    @login_required
    def process_xp_purchase():
        """Traitement de l'achat (simulation — à remplacer par Stripe Checkout)"""
        package_id = request.form.get('package_id', type=int)
        # Carte (simulation — non vérifiée en prod)
        card_number = request.form.get('card_number', '').replace(' ', '')
        card_expiry = request.form.get('card_expiry', '')
        card_cvv = request.form.get('card_cvv', '')

        package = next((p for p in XP_PACKAGES if p['id'] == package_id), None)
        if not package:
            flash('Offre invalide.', 'danger')
            return redirect(url_for('user.buy_xp'))

        # Validation basique (simulation)
        if len(card_number) < 12 or not card_expiry or len(card_cvv) < 3:
            flash('Informations de carte invalides.', 'danger')
            return redirect(url_for('user.buy_xp'))

        # Enregistrer l'achat
        purchase = XPPurchase(
            user_id=current_user.id,
            xp_amount=package['xp'],
            price_eur=package['price'],
            status='completed',
            completed_at=datetime.utcnow()
        )
        db.session.add(purchase)

        # Créditer l'XP
        current_user.xp += package['xp']
        while current_user.xp >= current_user.level * 1000:
            current_user.level += 1

        db.session.commit()
        flash(f"✅ Achat réussi ! +{package['xp']} XP crédités sur votre compte.", 'success')
        return redirect(url_for('user.profile', user_id=current_user.id))

    # ── Récompense quotidienne ─────────────────────────────────────────────────

    @staticmethod
    @login_required
    def daily_reward():
        now = datetime.utcnow()
        today = date.today()
        if current_user.last_daily_reward and current_user.last_daily_reward.date() == today:
            return jsonify({'error': 'Récompense déjà récupérée aujourd\'hui.', 'already_claimed': True}), 429

        daily_xp = 100
        current_user.xp += daily_xp
        current_user.last_daily_reward = now

        level_up = False
        while current_user.xp >= current_user.level * 1000:
            current_user.level += 1
            level_up = True

        db.session.commit()
        return jsonify({
            'message': 'Récompense quotidienne reçue !',
            'xp': daily_xp,
            'total_xp': current_user.xp,
            'level_up': level_up,
            'new_level': current_user.level if level_up else None
        })

    # ── Admin : gestion utilisateurs ─────────────────────────────────────────

    @staticmethod
    @login_required
    @admin_required
    def admin_users():
        q = request.args.get('q', '', type=str).strip()
        query = User.query
        if q:
            ilike_q = f"%{q}%"
            query = query.filter(
                User.username.ilike(ilike_q) | User.email.ilike(ilike_q)
            )
        users = query.order_by(User.created_at.desc()).all()
        return render_template('admin/users.html', users=users, q=q)

    @staticmethod
    @login_required
    @admin_required
    def delete_user(user_id):
        user = User.query.get_or_404(user_id)
        if user.id == current_user.id:
            flash('Suppression de votre propre compte impossible.', 'danger')
            return redirect(url_for('admin.admin_users'))
        if user.is_admin:
            flash('Suppression d\'un compte administrateur interdite.', 'danger')
            return redirect(url_for('admin.admin_users'))
        username = user.username
        # Delete skills created by user (and their videos via cascade)
        for skill in Skill.query.filter_by(creator_id=user.id).all():
            for video in Video.query.filter_by(skill_id=skill.id).all():
                db.session.delete(video)
            db.session.delete(skill)
        db.session.flush()
        # Delete other user-related records
        UserMission.query.filter_by(user_id=user.id).delete()
        UserProgress.query.filter_by(user_id=user.id).delete()
        ContentUnlock.query.filter_by(user_id=user.id).delete()
        XPPurchase.query.filter_by(user_id=user.id).delete()
        db.session.delete(user)
        db.session.commit()
        flash(f'Profil {username} supprimé.', 'success')
        return redirect(url_for('admin.admin_users'))

    @staticmethod
    @login_required
    @admin_required
    def admin_stats():
        total_users = User.query.count()
        from app.models import Skill
        total_skills = Skill.query.count()
        total_purchases = XPPurchase.query.filter_by(status='completed').count()
        revenue = db.session.query(db.func.sum(XPPurchase.price_eur)).filter_by(status='completed').scalar() or 0
        return render_template('admin/stats.html',
            total_users=total_users,
            total_skills=total_skills,
            total_purchases=total_purchases,
            revenue=revenue)

    @staticmethod
    @login_required
    @admin_required
    def block_user(user_id):
        user = User.query.get_or_404(user_id)
        if user.is_admin:
            flash("Impossible de bloquer un administrateur.", 'danger')
            return redirect(url_for('user.admin_users'))
        user.is_blocked = not user.is_blocked
        db.session.commit()
        action = 'bloqué' if user.is_blocked else 'débloqué'
        flash(f"Utilisateur {user.username} {action}.", 'success')
        return redirect(url_for('user.admin_users'))

    @staticmethod
    @login_required
    @admin_required
    def change_role(user_id):
        user = User.query.get_or_404(user_id)
        new_role = request.form.get('role')
        if new_role not in ('user', 'moderator', 'admin'):
            flash('Rôle invalide.', 'danger')
            return redirect(url_for('user.admin_users'))
        user.role = new_role
        db.session.commit()
        flash(f"Rôle de {user.username} changé en {new_role}.", 'success')
        return redirect(url_for('user.admin_users'))

    # ── Modération : contenu ──────────────────────────────────────────────────

    @staticmethod
    @login_required
    @moderator_required
    def moderation_dashboard():
        from app.models import Skill
        flagged_skills = Skill.query.filter_by(is_flagged=True).all()
        pending_skills = Skill.query.filter_by(is_approved=False).all()
        return render_template('moderation/dashboard.html',
            flagged_skills=flagged_skills,
            pending_skills=pending_skills)

    @staticmethod
    @login_required
    @moderator_required
    def approve_skill(skill_id):
        from app.models import Skill, User
        skill = Skill.query.get_or_404(skill_id)
        ai = _build_ai_review(skill)
        moderator_reason = (request.form.get('reason') or '').strip()
        skill.is_approved = True
        skill.is_flagged = False

        # Débloquer l'onboarding si ce cours est le cours d'onboarding du créateur
        creator = User.query.get(skill.creator_id)
        if creator and not creator.onboarding_done and creator.onboarding_skill_id == skill.id:
            creator.onboarding_done = True
            creator.onboarding_rejected = False
            creator.xp += 100

        db.session.commit()

        if creator:
            try:
                from flask import url_for
                course_url = url_for('skill.skill_detail', skill_id=skill.id, _external=True)
            except Exception:
                course_url = None
            try:
                send_course_approved_email(
                    creator.email,
                    creator.username,
                    skill.name,
                    course_url,
                )
            except Exception as exc:
                current_app.logger.exception('Erreur envoi email acceptation: %s', exc)

        flash(f'Compétence "{skill.name}" approuvée.', 'success')
        return redirect(url_for('moderation.moderation_dashboard'))

    @staticmethod
    @login_required
    @moderator_required
    def reject_skill(skill_id):
        from app.models import Skill, User
        skill = Skill.query.get_or_404(skill_id)
        ai = _build_ai_review(skill)
        moderator_reason = (request.form.get('reason') or '').strip()
        skill.is_approved = False
        skill.is_flagged = False

        creator = User.query.get(skill.creator_id)
        if creator and creator.onboarding_skill_id == skill.id:
            creator.onboarding_done = False
            creator.onboarding_rejected = True
            creator.onboarding_skill_id = None

        db.session.commit()

        if creator:
            try:
                from flask import url_for
                edit_url = url_for('skill.my_skills', _external=True)
            except Exception:
                edit_url = None
            try:
                send_course_rejected_email(
                    creator.email,
                    creator.username,
                    skill.name,
                    moderator_reason or None,
                    edit_url,
                )
            except Exception as exc:
                current_app.logger.exception('Erreur envoi email refus: %s', exc)

        flash(f'Compétence "{skill.name}" refusée.', 'warning')
        return redirect(url_for('moderation.moderation_dashboard'))

    @staticmethod
    @login_required
    @moderator_required
    def delete_skill(skill_id):
        from app.models import Skill
        skill = Skill.query.get_or_404(skill_id)
        skill_name = skill.name
        db.session.delete(skill)
        db.session.commit()
        flash(f'Contenu "{skill_name}" supprime.', 'success')
        return redirect(url_for('moderation.moderation_dashboard'))

    @staticmethod
    @login_required
    @moderator_required
    def ai_review_skill(skill_id):
        from app.models import Skill
        skill = Skill.query.get_or_404(skill_id)
        ai = _build_ai_review(skill)

        return render_template(
            'moderation/ai_review.html',
            skill=skill,
            quality_score=ai['quality_score'],
            recommendation=ai['recommendation'],
            has_videos=ai['videos_count'] > 0,
            videos_count=ai['videos_count'],
            has_pdf=ai['has_pdf'],
            desc_len=ai['desc_len'],
            reasons=ai['reasons'],
            risks=ai['risks']
        )

    @staticmethod
    @login_required
    def flag_skill(skill_id):
        from app.models import Skill
        skill = Skill.query.get_or_404(skill_id)
        skill.is_flagged = True
        db.session.commit()
        flash('Contenu signalé à la modération.', 'info')
        return redirect(url_for('main.skill_detail', skill_id=skill_id))
