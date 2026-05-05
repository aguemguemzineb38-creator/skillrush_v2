from flask import render_template, request, redirect, url_for, flash, jsonify
from app.models import db, Mission, UserMission, Skill
from flask_login import login_required, current_user
from datetime import datetime

class MissionController:
    """Contrôleur pour la gestion des missions"""
    
    @staticmethod
    def missions_list():
        """Lister toutes les missions"""
        page = request.args.get('page', 1, type=int)
        difficulty = request.args.get('difficulty', '', type=str)
        
        query = Mission.query
        
        if difficulty:
            query = query.filter_by(difficulty=difficulty)
        
        missions = query.paginate(page=page, per_page=12)
        difficulties = ['Easy', 'Medium', 'Hard', 'Expert']
        
        return render_template('mission/missions_list.html',
            missions=missions,
            difficulties=difficulties,
            current_difficulty=difficulty)
    
    @staticmethod
    def mission_detail(mission_id):
        """Afficher les détails d'une mission"""
        mission = Mission.query.get_or_404(mission_id)
        
        # Vérifier si l'utilisateur a commencé cette mission
        user_mission = None
        if current_user.is_authenticated:
            user_mission = UserMission.query.filter_by(
                user_id=current_user.id,
                mission_id=mission_id
            ).first()
        
        return render_template('mission/mission_detail.html',
            mission=mission,
            user_mission=user_mission)
    
    @staticmethod
    @login_required
    def start_mission(mission_id):
        """Commencer une mission"""
        mission = Mission.query.get_or_404(mission_id)
        
        # Vérifier si l'utilisateur a déjà commencé cette mission
        user_mission = UserMission.query.filter_by(
            user_id=current_user.id,
            mission_id=mission_id
        ).first()
        
        if not user_mission:
            user_mission = UserMission(
                user_id=current_user.id,
                mission_id=mission_id
            )
            db.session.add(user_mission)
            db.session.commit()
            flash('Mission commencée!', 'success')
        else:
            flash('Vous avez déjà commencé cette mission', 'info')
        
        return redirect(url_for('mission.mission_detail', mission_id=mission_id))
    
    @staticmethod
    @login_required
    def complete_mission(mission_id):
        """Compléter une mission"""
        mission = Mission.query.get_or_404(mission_id)
        
        user_mission = UserMission.query.filter_by(
            user_id=current_user.id,
            mission_id=mission_id
        ).first()
        
        if not user_mission:
            flash('Vous n\'avez pas commencé cette mission', 'error')
            return redirect(url_for('mission.mission_detail', mission_id=mission_id))
        
        if user_mission.is_completed:
            flash('Vous avez déjà complété cette mission', 'info')
            return redirect(url_for('mission.mission_detail', mission_id=mission_id))
        
        # Marquer comme complétée
        user_mission.is_completed = True
        user_mission.completed_at = datetime.utcnow()
        
        # Ajouter les récompenses
        current_user.xp += mission.reward_xp
        
        # Vérifier la montée de niveau
        while current_user.xp >= current_user.level * 1000:
            current_user.level += 1
            flash(f'Félicitations! Vous êtes passé niveau {current_user.level}!', 'success')
        
        db.session.commit()
        
        flash(f'Bravo! Vous avez reçu +{mission.reward_xp} XP!', 'success')
        return redirect(url_for('user.my_progress'))
    
    @staticmethod
    @login_required
    def my_missions():
        """Afficher mes missions"""
        active_missions = UserMission.query.filter_by(
            user_id=current_user.id,
            is_completed=False
        ).all()
        
        completed_missions = UserMission.query.filter_by(
            user_id=current_user.id,
            is_completed=True
        ).all()
        
        return render_template('mission/my_missions.html',
            active_missions=active_missions,
            completed_missions=completed_missions)
    
    @staticmethod
    @login_required
    def create_mission(skill_id):
        """Créer une mission pour une compétence"""
        skill = Skill.query.get_or_404(skill_id)
        
        # Vérifier que l'utilisateur est le créateur de la compétence
        if skill.creator_id != current_user.id:
            flash('Vous n\'avez pas la permission d\'effectuer cette action', 'error')
            return redirect(url_for('main.skill_detail', skill_id=skill_id))
        
        if request.method == 'POST':
            title = request.form.get('title')
            description = request.form.get('description')
            objective = request.form.get('objective')
            reward_xp = request.form.get('reward_xp', 50, type=int)
            difficulty = request.form.get('difficulty', 'Easy')
            
            if not title or not description:
                flash('Veuillez remplir tous les champs obligatoires', 'error')
                return render_template('mission/create_mission.html', skill=skill)
            
            mission = Mission(
                title=title,
                description=description,
                objective=objective,
                reward_xp=reward_xp,
                difficulty=difficulty,
                skill_id=skill_id
            )
            
            db.session.add(mission)
            db.session.commit()
            
            flash('Mission créée avec succès!', 'success')
            return redirect(url_for('main.skill_detail', skill_id=skill_id))
        
        return render_template('mission/create_mission.html', skill=skill)
