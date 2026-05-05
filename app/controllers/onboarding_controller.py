from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app.models import db, Skill, Video
from werkzeug.utils import secure_filename
import uuid
import os
import subprocess

# Extensions autorisées (whitelist sécurité)
_ALLOWED_VIDEO = {'mp4', 'avi', 'mov', 'mkv', 'webm'}
_ALLOWED_PDF = {'pdf'}

CHUNK_DURATION = 180  # 3 minutes in seconds


def _allowed(filename, allowed_set):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_set


def _save_upload(file, subdir):
    """Sauvegarde un fichier uploadé, retourne l'URL relative."""
    ext = secure_filename(file.filename).rsplit('.', 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    dest_dir = os.path.join(current_app.static_folder, 'uploads', subdir)
    os.makedirs(dest_dir, exist_ok=True)
    file.save(os.path.join(dest_dir, unique_name))
    return f"/static/uploads/{subdir}/{unique_name}"


def _get_ffmpeg():
    """Retourne le chemin ffmpeg (bundled via imageio_ffmpeg)."""
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return 'ffmpeg'


def _get_video_duration(video_path):
    """Retourne la durée en secondes d'une vidéo via ffprobe, ou 0 si indisponible."""
    import re
    ffmpeg_exe = _get_ffmpeg()
    try:
        result = subprocess.run(
            [ffmpeg_exe, '-i', video_path],
            capture_output=True, text=True, timeout=30
        )
        match = re.search(r'Duration:\s*(\d+):(\d+):(\d+)', result.stderr)
        if match:
            h, m, s = map(int, match.groups())
            return h * 3600 + m * 60 + s
    except Exception:
        pass
    return 0


def _split_video_into_chunks(video_path, dest_dir, base_name):
    """
    Coupe une vidéo en segments de CHUNK_DURATION secondes.
    Retourne une liste de (url_relative, duree_secondes) ou None si pas de coupe nécessaire.
    """
    duration = _get_video_duration(video_path)
    if duration == 0 or duration <= CHUNK_DURATION:
        return None  # Pas de découpage nécessaire

    ffmpeg_exe = _get_ffmpeg()
    chunks = []
    start = 0
    part = 1
    os.makedirs(dest_dir, exist_ok=True)

    while start < duration:
        chunk_secs = min(CHUNK_DURATION, duration - start)
        chunk_name = f"{base_name}_part{part}.mp4"
        chunk_path = os.path.join(dest_dir, chunk_name)
        try:
            subprocess.run(
                [ffmpeg_exe, '-y', '-i', video_path,
                 '-ss', str(start), '-t', str(CHUNK_DURATION),
                 '-c', 'copy', chunk_path],
                capture_output=True, timeout=120
            )
            if os.path.exists(chunk_path):
                chunks.append((f"/static/uploads/videos/{chunk_name}", int(chunk_secs)))
        except Exception:
            pass
        start += CHUNK_DURATION
        part += 1

    # Supprimer la vidéo originale si le découpage a réussi
    if chunks:
        try:
            os.remove(video_path)
        except Exception:
            pass
        return chunks
    return None  # Découpage échoué, garder l'original


def _count_pdf_pages(pdf_path):
    """Retourne le nombre de pages du PDF, ou 0 si impossible."""
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(pdf_path)
        return len(reader.pages)
    except Exception:
        return 0


def _static_url_to_abs_path(static_url):
    """Convertit /static/... en chemin absolu sous current_app.static_folder."""
    relative = static_url.replace('/static/', '', 1).lstrip('/').replace('/', os.sep)
    return os.path.abspath(os.path.join(current_app.static_folder, relative))


class OnboardingController:
    """Gère le flux d'onboarding en 3 étapes pour les nouveaux utilisateurs."""

    # ── Étape 1 : choix du rôle (Apprenant ou Formateur) ──────────────────
    @staticmethod
    @login_required
    def step1():
        if current_user.onboarding_done:
            return redirect(url_for('main.dashboard'))

        category_options = [
            {'value': 'Business', 'label': 'Business & Excel', 'icon': '📊'},
            {'value': 'Design',   'label': 'Design & Canva',   'icon': '🎨'},
            {'value': 'Programming', 'label': 'Digital Skills','icon': '💻'},
            {'value': 'Marketing','label': 'Marketing',        'icon': '📈'},
        ]

        if request.method == 'POST':
            role_choice = request.form.get('role_choice', '')

            # ── Chemin Apprenant ──────────────────────────────────────────
            if role_choice == 'apprenant':
                selected_category = request.form.get('category', '').strip()
                skipped = request.form.get('skip') == '1'

                if not selected_category and not skipped:
                    flash('Choisis une catégorie ou clique sur "Je ne sais pas encore".', 'warning')
                    return render_template('onboarding/step1.html', category_options=category_options)

                if selected_category:
                    current_user.competence = selected_category
                current_user.onboarding_done = True
                current_user.onboarding_rejected = False
                current_user.onboarding_skill_id = None
                db.session.commit()

                if selected_category:
                    return redirect(url_for('main.explore_skills', category=selected_category, onboarding='1'))
                return redirect(url_for('main.explore_skills', onboarding='1'))

            # ── Chemin Formateur ──────────────────────────────────────────
            elif role_choice == 'formateur':
                competence = request.form.get('competence', '').strip()
                if not competence:
                    flash('Merci de renseigner ta compétence principale.', 'error')
                    return render_template('onboarding/step1.html', category_options=category_options, show_formateur=True)
                current_user.competence = competence
                db.session.commit()
                return redirect(url_for('onboarding.step2'))

            # Aucun choix soumis (ne devrait pas arriver)
            return render_template('onboarding/step1.html', category_options=category_options)

        show_formateur = request.args.get('formateur') == '1'
        return render_template('onboarding/step1.html', category_options=category_options, show_formateur=show_formateur)

    # ── Étape 2 : créer le premier cours ─────────────────────────────────────
    @staticmethod
    @login_required
    def step2():
        if current_user.onboarding_done:
            return redirect(url_for('main.dashboard'))
        if not current_user.competence:
            return redirect(url_for('onboarding.step1'))

        categories = ['Excel', 'Canva', 'CV', 'Design', 'Programming', 'Business', 'Marketing', 'Autre']

        if request.method == 'POST':
            title       = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            category    = request.form.get('category', '').strip()
            difficulty  = request.form.get('difficulty', 'Beginner')
            video_title = request.form.get('video_title', '').strip()
            video_file  = request.files.get('video_file')
            pdf_file    = request.files.get('pdf_file')

            # ── Validation champs texte ──
            if not title or not description or not category:
                flash('Merci de remplir tous les champs obligatoires.', 'error')
                return render_template('onboarding/step2.html', categories=categories)

            has_video = bool(video_file and video_file.filename)
            has_pdf = bool(pdf_file and pdf_file.filename)

            # ── Au moins un support demandé : vidéo ou PDF ──
            if not has_video and not has_pdf:
                flash('Ajoute au moins un support : une vidéo ou un PDF.', 'error')
                return render_template('onboarding/step2.html', categories=categories)

            video_url = None
            if has_video:
                if not video_title:
                    flash('Ajoute un titre pour la video.', 'error')
                    return render_template('onboarding/step2.html', categories=categories)
                if not _allowed(video_file.filename, _ALLOWED_VIDEO):
                    flash('Format vidéo non supporté. Utilise MP4, MOV, AVI, MKV ou WEBM.', 'error')
                    return render_template('onboarding/step2.html', categories=categories)
                video_url = _save_upload(video_file, 'videos')

            # ── Sauvegarde PDF (optionnel) ──
            course_pdf_url = None
            pdf_pages = 0
            if pdf_file and pdf_file.filename != '':
                if not _allowed(pdf_file.filename, _ALLOWED_PDF):
                    flash('Seuls les fichiers PDF sont acceptés pour le support de cours.', 'error')
                    return render_template('onboarding/step2.html', categories=categories)
                course_pdf_url = _save_upload(pdf_file, 'pdfs')
                # Compter les pages du PDF
                pdf_abs = _static_url_to_abs_path(course_pdf_url)
                pdf_pages = _count_pdf_pages(pdf_abs)

            # ── Création du cours ──
            skill = Skill(
                name=title,
                description=description,
                category=category,
                difficulty=difficulty,
                is_approved=False,
                creator_id=current_user.id,
                course_pdf=course_pdf_url,
                pdf_total_pages=pdf_pages
            )
            db.session.add(skill)
            db.session.flush()

            if has_video:
                if not video_title:
                    video_title = 'Video du cours'

                # ── Découpage vidéo si > 3 min ──
                video_abs = _static_url_to_abs_path(video_url)
                dest_dir = os.path.join(current_app.static_folder, 'uploads', 'videos')
                base_name = uuid.uuid4().hex
                chunks = _split_video_into_chunks(video_abs, dest_dir, base_name)

                if chunks:
                    for idx, (chunk_url, chunk_duration) in enumerate(chunks):
                        v = Video(
                            title=f"{video_title} — Partie {idx + 1}",
                            description='',
                            video_url=chunk_url,
                            duration=chunk_duration,
                            is_free=(idx == 0),
                            xp_cost=100,
                            order=idx,
                            skill_id=skill.id
                        )
                        db.session.add(v)
                else:
                    # Vidéo courte ou découpage échoué → une seule entrée
                    duration_secs = _get_video_duration(video_abs)
                    v = Video(
                        title=video_title,
                        description='',
                        video_url=video_url,
                        duration=duration_secs,
                        is_free=True,
                        xp_cost=0,
                        order=0,
                        skill_id=skill.id
                    )
                    db.session.add(v)

            current_user.onboarding_rejected = False
            current_user.onboarding_skill_id = skill.id
            db.session.commit()

            return redirect(url_for('onboarding.step3'))

        return render_template('onboarding/step2.html', categories=categories)

    # ── Étape 3 : attente d'approbation ──────────────────────────────────────
    @staticmethod
    @login_required
    def step3():
        if current_user.onboarding_done:
            return redirect(url_for('main.dashboard'))
        if current_user.onboarding_rejected:
            flash('Votre cours a ete refuse. Consultez votre email puis revenez a l\'accueil.', 'warning')
            return redirect(url_for('main.rejected_course'))

        skill = None
        if current_user.onboarding_skill_id:
            skill = Skill.query.get(current_user.onboarding_skill_id)

        if skill and skill.is_approved:
            # L'équipe a approuvé pendant que l'utilisateur attendait
            current_user.onboarding_done = True
            current_user.xp += 100
            db.session.commit()
            flash('🎉 Ton cours a été approuvé ! Bienvenue dans SkillRush !', 'success')
            return redirect(url_for('main.dashboard'))

        return render_template('onboarding/step3.html', skill=skill)
