from flask import render_template, request, abort, redirect, url_for
from app.models import db, User, Skill, Video, Mission, UserProgress, UserMission, ContentUnlock
from flask_login import login_required, current_user
from datetime import date

class MainController:
    """Contrôleur principal pour les pages générales"""

    @staticmethod
    def _render_user_dashboard():
        """Construit un dashboard utilisateur simple et centré sur l'action."""
        # Gestion du streak journalier (concept Duolingo):
        # - première connexion: streak = 1
        # - connexion le lendemain: +1
        # - trou > 1 jour: reset à 1
        today = date.today()
        if current_user.streak_last_date is None:
            current_user.streak_count = 1
            current_user.streak_last_date = today
            db.session.commit()
        elif current_user.streak_last_date < today:
            delta_days = (today - current_user.streak_last_date).days
            if delta_days == 1:
                current_user.streak_count = (current_user.streak_count or 0) + 1
            else:
                current_user.streak_count = 1
            current_user.streak_last_date = today
            db.session.commit()

        recommended_skills = Skill.query.filter_by(is_approved=True).order_by(Skill.created_at.desc()).limit(6).all()
        uploaded_skills = Skill.query.filter_by(creator_id=current_user.id).order_by(Skill.created_at.desc()).limit(6).all()
        active_missions = UserMission.query.filter_by(
            user_id=current_user.id,
            is_completed=False
        ).limit(5).all()
        user_progress = UserProgress.query.filter_by(
            user_id=current_user.id
        ).all()

        total_skills_learning = len(user_progress)
        total_xp = current_user.xp
        daily_reward_claimed = bool(
            current_user.last_daily_reward and current_user.last_daily_reward.date() == today
        )

        # Missions du jour orientées usage réel
        daily_tasks = []
        daily_tasks.append({
            'title': 'Maintenir votre streak du jour',
            'description': 'Connectez-vous aujourd\'hui pour conserver votre série.',
            'status': 'done'
        })

        if active_missions:
            for um in active_missions[:3]:
                daily_tasks.append({
                    'title': um.mission.title,
                    'description': um.mission.description or 'Continuer cette mission.',
                    'status': 'in_progress',
                    'url': url_for('mission.mission_detail', mission_id=um.mission.id)
                })
        elif user_progress:
            for prog in user_progress[:3]:
                daily_tasks.append({
                    'title': f"Continuer {prog.skill.name}",
                    'description': f"Progression actuelle: {prog.progress_percentage}%",
                    'status': 'in_progress',
                    'url': url_for('main.skill_detail', skill_id=prog.skill_id)
                })

        if len(daily_tasks) < 3:
            daily_tasks.append({
                'title': 'Débloquer 1 nouvelle vidéo',
                'description': 'Objectif quotidien recommandé: progresser dans une compétence.',
                'status': 'todo',
                'url': url_for('main.explore_skills')
            })

        return render_template(
            'dashboard.html',
            recommended_skills=recommended_skills,
            uploaded_skills=uploaded_skills,
            daily_tasks=daily_tasks[:4],
            total_skills=total_skills_learning,
            total_xp=total_xp,
            daily_reward_claimed=daily_reward_claimed,
            streak_count=current_user.streak_count or 0,
            level=current_user.level
        )
    
    @staticmethod
    def dashboard():
        """Affiche le dashboard principal"""
        if current_user.is_authenticated:
            if getattr(current_user, 'onboarding_rejected', False) and not current_user.onboarding_done:
                return redirect(url_for('main.rejected_course'))
            return MainController._render_user_dashboard()
        return render_template('home.html')

    @staticmethod
    @login_required
    def rejected_course():
        """Page dédiée quand le cours d'onboarding a été refusé."""
        if not (getattr(current_user, 'onboarding_rejected', False) and not current_user.onboarding_done):
            return redirect(url_for('main.dashboard'))
        return render_template('onboarding/rejected.html')
    
    @staticmethod
    def explore_skills():
        """Explore les compétences disponibles"""
        page = request.args.get('page', 1, type=int)
        category = request.args.get('category', '', type=str)
        search = request.args.get('search', '', type=str)
        onboarding = request.args.get('onboarding', '', type=str)
        
        query = Skill.query.filter_by(is_approved=True)
        
        if search:
            query = query.filter(Skill.name.ilike(f'%{search}%') | 
                                Skill.description.ilike(f'%{search}%'))
        
        if category:
            query = query.filter_by(category=category)
        
        skills = query.paginate(page=page, per_page=12)
        categories = ['Excel', 'Canva', 'CV', 'Design', 'Programming', 'Business']

        trending_skills = Skill.query.filter_by(is_approved=True).order_by(Skill.views.desc(), Skill.created_at.desc()).limit(6).all()

        recommended_query = Skill.query.filter_by(is_approved=True)
        if current_user.is_authenticated and getattr(current_user, 'competence', ''):
            recommended_query = recommended_query.filter(
                Skill.category.ilike(f"%{current_user.competence}%") |
                Skill.name.ilike(f"%{current_user.competence}%")
            )
        recommended_skills = recommended_query.order_by(Skill.created_at.desc()).limit(6).all()
        if not recommended_skills:
            recommended_skills = trending_skills[:6]

        top_encg_skills = Skill.query.filter_by(is_approved=True).order_by(Skill.rating.desc(), Skill.views.desc()).limit(6).all()
        
        return render_template('explore_skills.html',
            skills=skills,
            categories=categories,
            current_category=category,
            search_query=search,
            trending_skills=trending_skills,
            recommended_skills=recommended_skills,
            top_encg_skills=top_encg_skills,
            from_onboarding=(onboarding == '1'))
    
    @staticmethod
    def skill_detail(skill_id):
        """Affiche les détails d'une compétence"""
        skill = Skill.query.get_or_404(skill_id)
        
        if not skill.is_approved:
            can_access_unapproved = (
                current_user.is_authenticated and
                (current_user.id == skill.creator_id or current_user.is_moderator)
            )
            if not can_access_unapproved:
                abort(404)

        videos = Video.query.filter_by(skill_id=skill_id).order_by(Video.order, Video.id).all()
        missions = Mission.query.filter_by(skill_id=skill_id).all()
        
        # Vérifier la progression utilisateur
        user_progress = None
        unlocked_video_ids = set()
        pdf_fully_unlocked = False

        if current_user.is_authenticated:
            user_progress = UserProgress.query.filter_by(
                user_id=current_user.id,
                skill_id=skill_id
            ).first()
            # Construire le set des vidéos débloquées
            video_unlocks = ContentUnlock.query.filter_by(
                user_id=current_user.id, skill_id=skill_id, content_type='video'
            ).all()
            unlocked_video_ids = {int(u.content_ref) for u in video_unlocks}
            pdf_unlock = ContentUnlock.query.filter_by(
                user_id=current_user.id, skill_id=skill_id, content_type='pdf_full'
            ).first()
            pdf_fully_unlocked = pdf_unlock is not None

        # Première vidéo toujours accessible
        first_video_id = videos[0].id if videos else None

        FREE_PDF_PAGES = 5
        pdf_cost = max(100, ((skill.pdf_total_pages or 0) - FREE_PDF_PAGES) * 100) if skill.course_pdf else 0

        return render_template('skill_detail.html',
            skill=skill,
            videos=videos,
            missions=missions,
            user_progress=user_progress,
            unlocked_video_ids=unlocked_video_ids,
            first_video_id=first_video_id,
            pdf_fully_unlocked=pdf_fully_unlocked,
            pdf_cost=pdf_cost,
            FREE_PDF_PAGES=FREE_PDF_PAGES,
            VIDEO_XP_COST=100)
    
    @staticmethod
    def leaderboard():
        """Le classement est désactivé dans cette version produit."""
        return redirect(url_for('main.dashboard'))
    
    @staticmethod
    def user_profile(user_id):
        """Affiche le profil d'un utilisateur"""
        user = User.query.get_or_404(user_id)
        skills_created = Skill.query.filter_by(creator_id=user_id).all()
        missions_completed = UserMission.query.filter_by(
            user_id=user_id,
            is_completed=True
        ).all()
        
        return render_template('user/profile.html',
            profile_user=user,
            skills_created=skills_created,
            missions_completed=missions_completed,
            missions_count=len(missions_completed))

    @staticmethod
    @login_required
    def user_space():
        """Interface dediee a l'utilisateur"""
        return MainController._render_user_dashboard()

    @staticmethod
    @login_required
    def admin_space():
        """Interface dediee a l'administrateur"""
        if not current_user.is_admin:
            abort(403)
        return render_template('admin/space.html')

    @staticmethod
    @login_required
    def moderation_space():
        """Interface dediee a l'equipe de moderation"""
        if not (current_user.is_moderator or current_user.is_admin):
            abort(403)
        return render_template('moderation/space.html')


