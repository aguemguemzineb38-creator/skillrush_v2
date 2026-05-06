import smtplib
import threading
from email.message import EmailMessage
from flask import current_app


# ---------------------------------------------------------------------------
# Low-level SMTP sender (plain text + optional HTML alternative)
# ---------------------------------------------------------------------------

def _smtp_send(app, recipient, subject, text_body, html_body=None):
    """Runs inside a background thread; uses app context."""
    with app.app_context():
        mail_server   = app.config.get('MAIL_SERVER')
        mail_port     = int(app.config.get('MAIL_PORT', 587))
        mail_username = app.config.get('MAIL_USERNAME')
        mail_password = app.config.get('MAIL_PASSWORD')
        mail_use_tls  = app.config.get('MAIL_USE_TLS', True)
        mail_use_ssl  = app.config.get('MAIL_USE_SSL', False)
        mail_sender   = app.config.get('MAIL_DEFAULT_SENDER', 'SkillRush <noreply@skillrush.app>')

        if not mail_server:
            app.logger.warning('Email non envoyé: MAIL_SERVER absent | to=%s', recipient)
            return

        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From']    = mail_sender
        msg['To']      = recipient
        msg.set_content(text_body)   # plain-text fallback

        if html_body:
            msg.add_alternative(html_body, subtype='html')

        try:
            smtp_cls = smtplib.SMTP_SSL if mail_use_ssl else smtplib.SMTP
            with smtp_cls(mail_server, mail_port, timeout=20) as server:
                if mail_use_tls and not mail_use_ssl:
                    server.starttls()
                if mail_username:
                    server.login(mail_username, mail_password)
                server.send_message(msg)
            app.logger.info('Email envoyé | to=%s | subject=%s', recipient, subject)
        except Exception as exc:
            app.logger.exception('Erreur envoi email | to=%s | %s', recipient, exc)


def _send_async(recipient, subject, text_body, html_body=None):
    """Non-blocking email dispatch via a daemon thread."""
    app = current_app._get_current_object()
    t = threading.Thread(
        target=_smtp_send,
        args=(app, recipient, subject, text_body, html_body),
        daemon=True,
    )
    t.start()


# ---------------------------------------------------------------------------
# Legacy helper (plain text, kept for backward-compatibility)
# ---------------------------------------------------------------------------

def send_email(recipient, subject, body):
    """Envoie un email texte brut (non-bloquant)."""
    if not recipient:
        return False
    _send_async(recipient, subject, body)
    return True


# ---------------------------------------------------------------------------
# SkillRush HTML email helpers
# ---------------------------------------------------------------------------

_BASE_STYLE = """
  body{margin:0;padding:0;background:#f0f4ff;font-family:'Segoe UI',Arial,sans-serif;}
  .wrap{max-width:600px;margin:32px auto;background:#fff;border-radius:16px;
        overflow:hidden;box-shadow:0 4px 24px rgba(15,95,255,.10);}
  .hero{background:linear-gradient(130deg,#0f5fff 0%,#00b4d8 45%,#20bf55 100%);
        padding:40px 32px 32px;text-align:center;color:#fff;}
  .hero h1{margin:0 0 8px;font-size:26px;font-weight:800;letter-spacing:-.5px;}
  .hero p{margin:0;font-size:15px;opacity:.9;}
  .body{padding:32px;}
  .body h2{margin:0 0 12px;color:#182235;font-size:20px;}
  .body p{margin:0 0 16px;color:#3d4f6e;line-height:1.6;font-size:15px;}
  .feature{display:flex;align-items:flex-start;margin-bottom:14px;}
  .feature .icon{font-size:22px;width:36px;flex-shrink:0;}
  .feature .text{color:#3d4f6e;font-size:14px;line-height:1.5;}
  .feature .text strong{color:#182235;}
  .cta{text-align:center;margin:28px 0 8px;}
  .btn{display:inline-block;padding:14px 36px;background:linear-gradient(130deg,#0f5fff,#20bf55);
       color:#fff!important;text-decoration:none;border-radius:50px;font-weight:700;
       font-size:15px;letter-spacing:.3px;}
  .divider{border:none;border-top:1px solid #e8edf5;margin:24px 0;}
  .footer{text-align:center;padding:20px 32px 28px;font-size:12px;color:#8899aa;}
  .badge{display:inline-block;background:#fff3;border-radius:20px;padding:4px 14px;
         font-size:13px;font-weight:700;margin-bottom:8px;}
"""


def _html_wrap(hero_html: str, body_html: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="fr">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<style>{_BASE_STYLE}</style></head>
<body>
<div class="wrap">
  <div class="hero">{hero_html}</div>
  <div class="body">{body_html}</div>
  <div class="footer">
    © 2026 SkillRush — Tous droits réservés.<br>
    <span style="color:#aab">La plateforme de compétences professionnelles pour étudiants ENCG</span>
  </div>
</div>
</body></html>"""


# ── Welcome ─────────────────────────────────────────────────────────────────

def send_welcome_email(email: str, username: str):
    subject = "Bienvenue sur SkillRush 🎉 — Commence ton parcours !"

    text_body = (
        f"Bonjour {username},\n\n"
        "Bienvenue sur SkillRush !\n\n"
        "Tu peux maintenant :\n"
        "  ⚡ Gagner des XP et monter de niveau\n"
        "  🔥 Maintenir un streak quotidien\n"
        "  🎥 Regarder des mini-vidéos de compétences\n"
        "  🎯 Relever des Missions et gagner des récompenses\n\n"
        "Connecte-toi dès maintenant sur SkillRush et commence ton parcours.\n\n"
        "L'équipe SkillRush"
    )

    hero = """
      <div class="badge">🎓 Plateforme ENCG</div>
      <h1>Bienvenue sur SkillRush !</h1>
      <p>Ta carrière commence ici.</p>"""

    body = f"""
      <h2>Salut {username} 👋</h2>
      <p>On est ravis de t'avoir parmi nous ! Ton compte est actif et tu peux dès maintenant explorer des centaines de compétences professionnelles.</p>
      <div class="feature"><div class="icon">⚡</div><div class="text"><strong>Système XP &amp; Niveaux</strong><br>Gagne des points d'expérience à chaque vidéo regardée et monte en niveau.</div></div>
      <div class="feature"><div class="icon">🔥</div><div class="text"><strong>Streak quotidien</strong><br>Reviens chaque jour pour maintenir ta série et débloquer des bonus.</div></div>
      <div class="feature"><div class="icon">🎥</div><div class="text"><strong>Mini-vidéos de compétences</strong><br>Des cours courts et ciblés sur Excel, Canva, Python, Marketing et bien plus.</div></div>
      <div class="feature"><div class="icon">🎯</div><div class="text"><strong>Missions &amp; Quiz</strong><br>Relève des défis, valide tes acquis et remporte des récompenses.</div></div>
      <hr class="divider">
      <div class="cta"><a class="btn" href="https://web-production-0337.up.railway.app/dashboard">Commencer maintenant →</a></div>"""

    _send_async(email, subject, text_body, _html_wrap(hero, body))


# ── Course approved ──────────────────────────────────────────────────────────

def send_course_approved_email(email: str, username: str, course_name: str,
                                course_url: str = None):
    subject = "✅ Votre cours a été approuvé — SkillRush"
    course_url = course_url or "https://web-production-0337.up.railway.app/dashboard"

    text_body = (
        f"Bonjour {username},\n\n"
        f"Félicitations ! Votre cours « {course_name} » a été validé par notre équipe de modération.\n"
        "Il est désormais visible pour tous les apprenants SkillRush.\n\n"
        f"Lien vers votre cours : {course_url}\n\n"
        "Merci pour votre contribution !\nL'équipe SkillRush"
    )

    hero = """
      <div class="badge" style="background:rgba(32,191,85,.25)">✅ Cours approuvé</div>
      <h1>Félicitations !</h1>
      <p>Votre cours a passé la modération avec succès.</p>"""

    body = f"""
      <h2>Bonjour {username} 🎉</h2>
      <p>Votre cours <strong>« {course_name} »</strong> a été <strong style="color:#20bf55">officiellement validé</strong> par notre équipe de modération.</p>
      <p>Il est maintenant <strong>visible pour tous les apprenants</strong> de la plateforme SkillRush. Les étudiants peuvent dès à présent le regarder, gagner des XP et laisser des évaluations.</p>
      <p style="background:#f0fff6;border-left:4px solid #20bf55;padding:12px 16px;border-radius:6px;color:#1a7a40;">
        💡 <strong>Conseil :</strong> Partagez le lien de votre cours avec vos étudiants pour maximiser votre impact !
      </p>
      <hr class="divider">
      <div class="cta"><a class="btn" href="{course_url}">Voir mon cours →</a></div>"""

    _send_async(email, subject, text_body, _html_wrap(hero, body))


# ── Course rejected ──────────────────────────────────────────────────────────

def send_course_rejected_email(email: str, username: str, course_name: str,
                                reason: str = None, edit_url: str = None):
    subject = "❌ Votre cours nécessite des modifications — SkillRush"
    edit_url = edit_url or "https://web-production-0337.up.railway.app/dashboard"
    reason_html = (
        f'<p style="background:#fff5f5;border-left:4px solid #e53e3e;padding:12px 16px;'
        f'border-radius:6px;color:#742a2a;"><strong>Motif :</strong> {reason}</p>'
    ) if reason else ""
    reason_text = f"\nMotif du refus : {reason}\n" if reason else ""

    text_body = (
        f"Bonjour {username},\n\n"
        f"Votre cours « {course_name} » n'a pas passé la validation de modération.{reason_text}\n"
        "Ne vous découragez pas ! Vous pouvez corriger votre contenu et le soumettre à nouveau.\n\n"
        f"Modifier votre cours : {edit_url}\n\n"
        "L'équipe SkillRush"
    )

    hero = """
      <div class="badge" style="background:rgba(229,62,62,.25)">❌ Modifications requises</div>
      <h1>Votre cours nécessite<br>des ajustements</h1>
      <p>Notre équipe a examiné votre soumission.</p>"""

    body = f"""
      <h2>Bonjour {username},</h2>
      <p>Après examen attentif, votre cours <strong>« {course_name} »</strong> n'a pas pu être validé en l'état par notre équipe de modération.</p>
      {reason_html}
      <p>Ce refus n'est <strong>pas définitif</strong> — vous pouvez tout à fait corriger votre contenu et le resoumettre. Nous sommes là pour vous aider à publier le meilleur contenu possible.</p>
      <p style="background:#fffbf0;border-left:4px solid #ffb703;padding:12px 16px;border-radius:6px;color:#7a5a00;">
        💪 <strong>Encouragement :</strong> De nombreux créateurs SkillRush ont dû affiner leur cours avant validation. Chaque itération améliore la qualité !
      </p>
      <hr class="divider">
      <div class="cta"><a class="btn" style="background:linear-gradient(130deg,#e53e3e,#ff6b35)" href="{edit_url}">Modifier mon cours →</a></div>"""

    _send_async(email, subject, text_body, _html_wrap(hero, body))
