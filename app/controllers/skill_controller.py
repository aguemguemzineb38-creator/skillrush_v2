from flask import request, jsonify, render_template, flash, redirect, url_for, send_file, abort, current_app
from app.models import db, Skill, Video, UserProgress, ContentUnlock
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime, date
import os
import uuid


def _static_url_to_abs_path(static_url):
    """Convertit /static/... en chemin absolu sous current_app.static_folder."""
    relative = static_url.replace('/static/', '', 1).lstrip('/').replace('/', os.sep)
    return os.path.abspath(os.path.join(current_app.static_folder, relative))

class SkillController:
    """Contrôleur pour la gestion des compétences"""
    
    @staticmethod
    @login_required
    def create_skill():
        """Créer une nouvelle compétence"""
        if request.method == 'POST':
            title = request.form.get('title')
            description = request.form.get('description')
            category = request.form.get('category')
            difficulty = request.form.get('difficulty', 'Beginner')
            
            if not title or not description or not category:
                flash('Veuillez remplir tous les champs obligatoires', 'error')
                return render_template('skill/create_skill.html')
            
            skill = Skill(
                name=title,
                description=description,
                category=category,
                difficulty=difficulty,
                is_approved=False,
                creator_id=current_user.id
            )
            
            db.session.add(skill)
            db.session.commit()
            
            flash('Competence creee! Elle sera visible apres validation.', 'success')
            return redirect(url_for('skill.add_video', skill_id=skill.id))
        
        return render_template('skill/create_skill.html')
    
    @staticmethod
    @login_required
    def add_video(skill_id):
        """Ajouter une vidéo à une compétence (upload local + découpage auto en segments)"""
        skill = Skill.query.get_or_404(skill_id)

        # Vérifier que l'utilisateur est le créateur
        if skill.creator_id != current_user.id:
            flash('Vous n\'avez pas la permission d\'effectuer cette action', 'error')
            return redirect(url_for('main.skill_detail', skill_id=skill_id))

        if request.method == 'POST':
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '')
            video_file = request.files.get('video_file')
            pdf_file   = request.files.get('pdf_file')

            has_video = bool(video_file and video_file.filename)
            has_pdf   = bool(pdf_file and pdf_file.filename)

            if not title or (not has_video and not has_pdf):
                flash('Veuillez remplir le titre et fournir au moins une vidéo ou un PDF.', 'error')
                videos = Video.query.filter_by(skill_id=skill_id).order_by(Video.order).all()
                return render_template('skill/add_video.html', skill=skill, videos=videos)

            # ── Sauvegarde PDF ─────────────────────────────────────────────
            if has_pdf:
                pdf_ext = os.path.splitext(secure_filename(pdf_file.filename))[1].lower()
                if pdf_ext != '.pdf':
                    flash('Seuls les fichiers PDF sont acceptés.', 'error')
                    videos = Video.query.filter_by(skill_id=skill_id).order_by(Video.order).all()
                    return render_template('skill/add_video.html', skill=skill, videos=videos)
                pdf_folder = os.path.join(current_app.static_folder, 'uploads', 'pdfs')
                os.makedirs(pdf_folder, exist_ok=True)
                pdf_filename = f'skill_{skill_id}_{uuid.uuid4().hex}.pdf'
                pdf_path = os.path.join(pdf_folder, pdf_filename)
                pdf_file.save(pdf_path)
                try:
                    from PyPDF2 import PdfReader
                    pdf_pages = len(PdfReader(pdf_path).pages)
                except Exception:
                    pdf_pages = 0
                skill.course_pdf = f'/static/uploads/pdfs/{pdf_filename}'
                skill.pdf_total_pages = pdf_pages
                db.session.commit()
                if not has_video:
                    flash(f'PDF ajouté avec succès ({pdf_pages} pages) !', 'success')
                    return redirect(url_for('skill.add_video', skill_id=skill_id))

            upload_folder = os.path.join(current_app.static_folder, 'uploads', 'videos')
            os.makedirs(upload_folder, exist_ok=True)

            ext = os.path.splitext(video_file.filename)[1].lower() or '.mp4'
            temp_filename = f'skill_{skill_id}_temp_{int(datetime.utcnow().timestamp())}{ext}'
            temp_path = os.path.join(upload_folder, temp_filename)
            video_file.save(temp_path)

            try:
                from moviepy import VideoFileClip

                clip = VideoFileClip(temp_path)
                total_duration = clip.duration  # secondes
                segment_seconds = 150  # 2 min 30 s par segment

                existing_count = Video.query.filter_by(skill_id=skill_id).count()

                seg_num = 1
                start = 0.0
                created_titles = []

                while start < total_duration:
                    end = min(start + segment_seconds, total_duration)
                    ts = int(datetime.utcnow().timestamp())
                    seg_filename = f'skill_{skill_id}_seg_{existing_count + seg_num}_{ts}.mp4'
                    seg_path = os.path.join(upload_folder, seg_filename)

                    sub = clip.subclipped(start, end)
                    sub.write_videofile(seg_path, logger=None, codec='libx264', audio_codec='aac')
                    sub.close()

                    if total_duration > segment_seconds:
                        seg_title = f'{title} — Partie {existing_count + seg_num}'
                    else:
                        seg_title = title

                    # Premier segment global gratuit, le reste premium
                    is_free = (existing_count + seg_num == 1)

                    video = Video(
                        title=seg_title,
                        description=description if seg_num == 1 else '',
                        video_url=f'/static/uploads/videos/{seg_filename}',
                        duration=int(end - start),
                        is_free=is_free,
                        order=existing_count + seg_num,
                        skill_id=skill_id
                    )
                    db.session.add(video)
                    created_titles.append(seg_title)

                    start = end
                    seg_num += 1

                clip.close()
                db.session.commit()
                os.remove(temp_path)

                flash(f'{len(created_titles)} segment(s) créé(s) avec succès !', 'success')

            except Exception as e:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                flash(f'Erreur lors du traitement vidéo : {e}', 'error')

            return redirect(url_for('skill.add_video', skill_id=skill_id))

        videos = Video.query.filter_by(skill_id=skill_id).order_by(Video.order).all()
        return render_template('skill/add_video.html', skill=skill, videos=videos)
    
    @staticmethod
    @login_required
    def watch_video(skill_id, video_id):
        """Regarder une vidéo et enregistrer la progression"""
        skill = Skill.query.get_or_404(skill_id)
        video = Video.query.get_or_404(video_id)
        
        # Enregistrer la progression
        progress = UserProgress.query.filter_by(
            user_id=current_user.id,
            skill_id=skill_id
        ).first()
        
        if not progress:
            progress = UserProgress(
                user_id=current_user.id,
                skill_id=skill_id
            )
            db.session.add(progress)

        # Legacy rows may contain NULL values despite model defaults.
        progress.videos_watched = (progress.videos_watched or 0) + 1
        progress.last_accessed = datetime.utcnow()
        
        # Calculer le pourcentage
        total_videos = Video.query.filter_by(skill_id=skill_id).count()
        if total_videos > 0:
            progress.progress_percentage = int((progress.videos_watched / total_videos) * 100)
        
        db.session.commit()
        
        return render_template('skill/watch_video.html',
            skill=skill,
            video=video,
            progress=progress)
    
    @staticmethod
    @login_required
    def rate_skill(skill_id):
        """Noter une compétence"""
        if request.method == 'POST':
            data = request.get_json()
            rating = data.get('rating')
            
            if not 1 <= rating <= 5:
                return jsonify({'error': 'Note invalide'}), 400
            
            progress = UserProgress.query.filter_by(
                user_id=current_user.id,
                skill_id=skill_id
            ).first()
            
            if not progress:
                return jsonify({'error': 'Vous n\'avez pas accès à cette compétence'}), 403
            
            progress.rating = rating
            db.session.commit()
            
            # Donner des récompenses
            current_user.xp += 25
            db.session.commit()
            
            return jsonify({
                'message': 'Merci pour votre évaluation!',
                'xp_earned': 25
            })
        
        return jsonify({'error': 'Méthode non autorisée'}), 405
    
    @staticmethod
    @login_required
    def my_skills():
        """Afficher mes compétences (comme créateur)"""
        skills = Skill.query.filter_by(creator_id=current_user.id).all()
        return render_template('skill/my_skills.html', skills=skills)

    @staticmethod
    @login_required
    def edit_skill(skill_id):
        """Modifier le titre/description d'une compétence"""
        skill = Skill.query.get_or_404(skill_id)
        if skill.creator_id != current_user.id:
            flash('Action non autorisée.', 'error')
            return redirect(url_for('skill.my_skills'))

        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            category = request.form.get('category', '').strip()
            difficulty = request.form.get('difficulty', skill.difficulty)

            if not name or not description or not category:
                flash('Veuillez remplir tous les champs.', 'error')
                return render_template('skill/edit_skill.html', skill=skill)

            skill.name = name
            skill.description = description
            skill.category = category
            skill.difficulty = difficulty
            db.session.commit()
            flash('Cours modifié avec succès.', 'success')
            return redirect(url_for('skill.my_skills'))

        return render_template('skill/edit_skill.html', skill=skill)

    @staticmethod
    @login_required
    def delete_skill(skill_id):
        """Supprimer un cours (creator only)"""
        skill = Skill.query.get_or_404(skill_id)
        if skill.creator_id != current_user.id:
            flash('Action non autorisée.', 'error')
            return redirect(url_for('skill.my_skills'))

        # Supprimer les fichiers vidéo uploadés
        for video in Video.query.filter_by(skill_id=skill_id).all():
            if video.video_url and video.video_url.startswith('/static/'):
                abs_path = _static_url_to_abs_path(video.video_url)
                if os.path.exists(abs_path):
                    os.remove(abs_path)

        db.session.delete(skill)
        db.session.commit()
        flash(f'Cours "{skill.name}" supprimé.', 'success')
        return redirect(url_for('skill.my_skills'))

    # ─── Unlock vidéo ──────────────────────────────────────────────────────────
    @staticmethod
    @login_required
    def unlock_video(skill_id, video_id):
        """Déverouille une vidéo en dépensant 100 XP."""
        VIDEO_XP_COST = 100
        DAILY_MISSION_BONUS = 50

        skill = Skill.query.get_or_404(skill_id)
        video = Video.query.get_or_404(video_id)

        if video.skill_id != skill_id:
            return jsonify({'error': 'Vidéo introuvable pour cette compétence.'}), 404

        # Vérifier si déjà débloqué
        already = ContentUnlock.query.filter_by(
            user_id=current_user.id, skill_id=skill_id,
            content_type='video', content_ref=str(video_id)
        ).first()
        if already:
            return jsonify({'already_unlocked': True})

        # Première vidéo (order=0) est gratuite
        first_video = Video.query.filter_by(skill_id=skill_id).order_by(Video.order, Video.id).first()
        if first_video and first_video.id == video_id:
            return jsonify({'already_unlocked': True, 'message': 'Première vidéo gratuite'})

        if current_user.xp < VIDEO_XP_COST:
            return jsonify({'error': f'XP insuffisant. Il te faut {VIDEO_XP_COST} XP.',
                            'xp_needed': VIDEO_XP_COST, 'xp_current': current_user.xp}), 400

        # Déduire XP
        current_user.xp -= VIDEO_XP_COST
        unlock = ContentUnlock(
            user_id=current_user.id, skill_id=skill_id,
            content_type='video', content_ref=str(video_id)
        )
        db.session.add(unlock)

        # Mission journalière: première vidéo débloquée aujourd'hui → bonus XP
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        daily_count = ContentUnlock.query.filter(
            ContentUnlock.user_id == current_user.id,
            ContentUnlock.content_type == 'video',
            ContentUnlock.unlocked_at >= today_start
        ).count()

        daily_bonus = 0
        if daily_count == 0:
            current_user.xp += DAILY_MISSION_BONUS
            daily_bonus = DAILY_MISSION_BONUS

        db.session.commit()
        return jsonify({
            'success': True,
            'xp_spent': VIDEO_XP_COST,
            'xp_remaining': current_user.xp,
            'daily_mission_completed': daily_count == 0,
            'daily_bonus': daily_bonus
        })

    # ─── Unlock PDF complet ────────────────────────────────────────────────────
    @staticmethod
    @login_required
    def unlock_pdf_full(skill_id):
        """Déverouille l'accès complet au PDF (pages 6+)."""
        FREE_PAGES = 5

        skill = Skill.query.get_or_404(skill_id)
        if not skill.course_pdf:
            return jsonify({'error': 'Pas de PDF pour cette compétence.'}), 404

        total = skill.pdf_total_pages or 0
        if total <= FREE_PAGES:
            return jsonify({'already_unlocked': True, 'message': 'PDF entièrement gratuit.'})

        already = ContentUnlock.query.filter_by(
            user_id=current_user.id, skill_id=skill_id, content_type='pdf_full'
        ).first()
        if already:
            return jsonify({'already_unlocked': True})

        xp_cost = max(100, (total - FREE_PAGES) * 100)
        if current_user.xp < xp_cost:
            return jsonify({'error': f'XP insuffisant. Il te faut {xp_cost} XP.',
                            'xp_needed': xp_cost, 'xp_current': current_user.xp}), 400

        current_user.xp -= xp_cost
        unlock = ContentUnlock(
            user_id=current_user.id, skill_id=skill_id,
            content_type='pdf_full', content_ref='full'
        )
        db.session.add(unlock)
        db.session.commit()
        return jsonify({'success': True, 'xp_spent': xp_cost, 'xp_remaining': current_user.xp})

    # ─── Servir PDF (restreint ou complet) ────────────────────────────────────
    @staticmethod
    @login_required
    def serve_skill_pdf(skill_id):
        """Sert le PDF: 5 premières pages libres, le reste après unlock."""
        import io
        try:
            from PyPDF2 import PdfReader, PdfWriter
        except ImportError:
            # Si PyPDF2 absent, servir le PDF brut
            skill = Skill.query.get_or_404(skill_id)
            if not skill.course_pdf:
                abort(404)
            pdf_path = _static_url_to_abs_path(skill.course_pdf)
            return send_file(os.path.abspath(pdf_path), mimetype='application/pdf')

        FREE_PAGES = 5
        skill = Skill.query.get_or_404(skill_id)
        if not skill.course_pdf:
            abort(404)

        pdf_path = _static_url_to_abs_path(skill.course_pdf)
        if not os.path.exists(pdf_path):
            abort(404)

        reader = PdfReader(pdf_path)
        total = len(reader.pages)

        # Mettre à jour le total si nécessaire
        if skill.pdf_total_pages != total:
            skill.pdf_total_pages = total
            db.session.commit()

        unlocked = ContentUnlock.query.filter_by(
            user_id=current_user.id, skill_id=skill_id, content_type='pdf_full'
        ).first()

        if unlocked or total <= FREE_PAGES:
            return send_file(pdf_path, mimetype='application/pdf',
                             download_name=f"{skill.name}.pdf")

        # Aperçu: 5 premières pages uniquement
        writer = PdfWriter()
        for i in range(min(FREE_PAGES, total)):
            writer.add_page(reader.pages[i])
        buf = io.BytesIO()
        writer.write(buf)
        buf.seek(0)
        return send_file(buf, mimetype='application/pdf',
                         download_name=f"{skill.name}_apercu.pdf")
