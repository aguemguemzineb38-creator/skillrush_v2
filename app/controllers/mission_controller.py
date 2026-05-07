from flask import render_template, request, redirect, url_for, flash, jsonify
from app.models import db, Mission, UserMission, Skill, MissionQuizQuestion, UserMissionQuizAttempt
from flask_login import login_required, current_user
from datetime import datetime

class MissionController:
    """Contrôleur pour la gestion des missions"""

    @staticmethod
    def _grant_mission_xp_and_complete(user_mission, mission):
        """Marque la mission complétée et crédite l'XP associé."""
        user_mission.is_completed = True
        user_mission.completed_at = datetime.utcnow()
        current_user.xp += mission.reward_xp

        leveled_up_to = None
        while current_user.xp >= current_user.level * 1000:
            current_user.level += 1
            leveled_up_to = current_user.level

        return leveled_up_to
    
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
        quiz_count = MissionQuizQuestion.query.filter_by(mission_id=mission_id).count()
        
        # Vérifier si l'utilisateur a commencé cette mission
        user_mission = None
        latest_attempt = None
        if current_user.is_authenticated:
            user_mission = UserMission.query.filter_by(
                user_id=current_user.id,
                mission_id=mission_id
            ).first()
            latest_attempt = UserMissionQuizAttempt.query.filter_by(
                user_id=current_user.id,
                mission_id=mission_id
            ).order_by(UserMissionQuizAttempt.attempted_at.desc()).first()
        
        return render_template('mission/mission_detail.html',
            mission=mission,
            user_mission=user_mission,
            quiz_count=quiz_count,
            latest_attempt=latest_attempt)
    
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
            flash('Mission commencée !', 'success')
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

        quiz_count = MissionQuizQuestion.query.filter_by(mission_id=mission_id).count()
        if quiz_count > 0:
            flash('Passez le quiz (minimum 5/10) pour valider la mission et récupérer les XP.', 'info')
            return redirect(url_for('mission.take_quiz', mission_id=mission_id))
        
        leveled_up_to = MissionController._grant_mission_xp_and_complete(user_mission, mission)
        
        db.session.commit()

        if leveled_up_to:
            flash(f'Félicitations ! Vous êtes passé au niveau {leveled_up_to} !', 'success')
        
        flash(f'Bravo ! Vous avez reçu +{mission.reward_xp} XP !', 'success')
        return redirect(url_for('user.my_progress'))

    @staticmethod
    @login_required
    def take_quiz(mission_id):
        """Quiz de mission: score minimum 5/10 pour débloquer l'XP."""
        mission = Mission.query.get_or_404(mission_id)
        questions = MissionQuizQuestion.query.filter_by(mission_id=mission_id).order_by(MissionQuizQuestion.id).all()

        user_mission = UserMission.query.filter_by(
            user_id=current_user.id,
            mission_id=mission_id
        ).first()

        if not user_mission:
            flash('Commencez la mission avant de passer le quiz.', 'warning')
            return redirect(url_for('mission.mission_detail', mission_id=mission_id))

        if user_mission.is_completed:
            flash('Mission déjà complétée.', 'info')
            return redirect(url_for('mission.mission_detail', mission_id=mission_id))

        if not questions:
            leveled_up_to = MissionController._grant_mission_xp_and_complete(user_mission, mission)
            db.session.commit()
            if leveled_up_to:
                flash(f'Félicitations ! Vous êtes passé au niveau {leveled_up_to} !', 'success')
            flash(f'Quiz indisponible : mission validée automatiquement (+{mission.reward_xp} XP).', 'success')
            return redirect(url_for('user.my_progress'))

        if request.method == 'POST':
            total = len(questions)
            correct = 0

            for question in questions:
                answer = (request.form.get(f'q_{question.id}') or '').strip().upper()
                if answer == question.correct_option:
                    correct += 1

            score_10 = round((correct / total) * 10, 1)
            passed = score_10 >= 5.0

            attempt = UserMissionQuizAttempt(
                user_id=current_user.id,
                mission_id=mission_id,
                score_10=score_10,
                passed=passed,
            )
            db.session.add(attempt)

            if passed:
                leveled_up_to = MissionController._grant_mission_xp_and_complete(user_mission, mission)
                db.session.commit()
                if leveled_up_to:
                    flash(f'Félicitations ! Vous êtes passé au niveau {leveled_up_to} !', 'success')
                flash(f'Quiz validé ({score_10}/10). Mission complétée : +{mission.reward_xp} XP.', 'success')
                return redirect(url_for('user.my_progress'))

            db.session.commit()
            flash(f'Score insuffisant ({score_10}/10). Il faut au moins 5/10 pour récupérer les XP.', 'warning')

        latest_attempt = UserMissionQuizAttempt.query.filter_by(
            user_id=current_user.id,
            mission_id=mission_id
        ).order_by(UserMissionQuizAttempt.attempted_at.desc()).first()

        return render_template(
            'mission/take_quiz.html',
            mission=mission,
            questions=questions,
            latest_attempt=latest_attempt
        )
    
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

            question_texts = request.form.getlist('quiz_question[]')
            option_as = request.form.getlist('quiz_option_a[]')
            option_bs = request.form.getlist('quiz_option_b[]')
            option_cs = request.form.getlist('quiz_option_c[]')
            option_ds = request.form.getlist('quiz_option_d[]')
            correct_options = request.form.getlist('quiz_correct[]')
            
            if not title or not description:
                flash('Veuillez remplir tous les champs obligatoires', 'error')
                return render_template('mission/create_mission.html', skill=skill)

            quiz_rows = []
            total_rows = max(
                len(question_texts), len(option_as), len(option_bs),
                len(option_cs), len(option_ds), len(correct_options)
            )

            for i in range(total_rows):
                q = (question_texts[i] if i < len(question_texts) else '').strip()
                a = (option_as[i] if i < len(option_as) else '').strip()
                b = (option_bs[i] if i < len(option_bs) else '').strip()
                c = (option_cs[i] if i < len(option_cs) else '').strip()
                d = (option_ds[i] if i < len(option_ds) else '').strip()
                correct = (correct_options[i] if i < len(correct_options) else '').strip().upper()

                filled = any([q, a, b, c, d])
                if not filled:
                    continue

                if not (q and a and b and c and d and correct in {'A', 'B', 'C', 'D'}):
                    flash(f'Quiz: la question {i + 1} est incomplète.', 'error')
                    return render_template('mission/create_mission.html', skill=skill)

                quiz_rows.append((q, a, b, c, d, correct))

            if not quiz_rows:
                flash('Ajoutez au moins 1 question de quiz pour cette mission.', 'error')
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
            db.session.flush()

            for q, a, b, c, d, correct in quiz_rows:
                db.session.add(MissionQuizQuestion(
                    mission_id=mission.id,
                    question_text=q,
                    option_a=a,
                    option_b=b,
                    option_c=c,
                    option_d=d,
                    correct_option=correct,
                ))

            db.session.commit()
            
            flash(f'Mission créée avec succès ! ({len(quiz_rows)} question(s) de quiz)', 'success')
            return redirect(url_for('main.skill_detail', skill_id=skill_id))
        
        return render_template('mission/create_mission.html', skill=skill)
