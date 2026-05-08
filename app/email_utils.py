import threading
import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import current_app

logger = logging.getLogger(__name__)

try:
	import resend as _resend_module
	RESEND_AVAILABLE = True
except ImportError:
	RESEND_AVAILABLE = False


def _configure_resend():
	"""Set resend.api_key and return True if a key is available."""
	if not RESEND_AVAILABLE:
		return False
	api_key = os.getenv('RESEND_API_KEY') or ''
	if not api_key:
		return False
	_resend_module.api_key = api_key
	return True


def _smtp_configured():
	"""Check if SMTP credentials are available."""
	return bool(os.getenv('MAIL_USERNAME') or os.getenv('SMTP_USER'))


def _send_email_smtp(recipient: str, subject: str, text_body: str, html_body: str = None, app=None):
	"""Send email via SMTP. `app` must be passed when called from a background thread."""
	if app is None:
		app = current_app._get_current_object()
	with app.app_context():
		try:
			server = (app.config.get('MAIL_SERVER') or '').strip()
			port = int(app.config.get('MAIL_PORT') or 587)
			username = (app.config.get('MAIL_USERNAME') or '').strip()
			password = (app.config.get('MAIL_PASSWORD') or '').strip()
			use_tls = app.config.get('MAIL_USE_TLS', True)
			sender = (app.config.get('MAIL_DEFAULT_SENDER') or username).strip()

			if not server or not username or not password:
				app.logger.warning('[SMTP] Configuration incomplète (MAIL_USERNAME / MAIL_PASSWORD / MAIL_SERVER manquants)')
				return

			msg = MIMEMultipart('alternative')
			msg['Subject'] = subject
			msg['From'] = sender
			msg['To'] = recipient
			msg.attach(MIMEText(text_body, 'plain', 'utf-8'))
			if html_body:
				msg.attach(MIMEText(html_body, 'html', 'utf-8'))

			app.logger.debug(f'[SMTP] Tentative | to={recipient} | server={server}:{port}')
			if port == 465:
				# SSL direct (port 465)
				with smtplib.SMTP_SSL(server, port, timeout=20) as smtp:
					smtp.login(username, password)
					smtp.sendmail(sender, recipient, msg.as_string())
			else:
				# STARTTLS (port 587)
				with smtplib.SMTP(server, port, timeout=20) as smtp:
					if use_tls:
						smtp.ehlo()
						smtp.starttls()
						smtp.ehlo()
					smtp.login(username, password)
					smtp.sendmail(sender, recipient, msg.as_string())
			app.logger.info(f'✅ Email envoyé via SMTP | to={recipient} | subject={subject}')
		except Exception as exc:
			app.logger.error(f'❌ ERREUR SMTP | to={recipient} | {type(exc).__name__}: {exc}', exc_info=True)


def _default_app_url(path='/dashboard'):
	app = current_app._get_current_object()
	base = (app.config.get('APP_BASE_URL') or 'https://web-production-skillrush.up.railway.app').rstrip('/')
	if not path.startswith('/'):
		path = '/' + path
	return f"{base}{path}"


def _send_email_resend(app, recipient: str, subject: str, text_body: str, html_body: str = None):
	"""Send email via Resend API v2 — runs in a background thread with the app object passed in."""
	with app.app_context():
		try:
			if not _configure_resend():
				if not RESEND_AVAILABLE:
					app.logger.warning('[RESEND] Package resend non disponible — tentative SMTP')
				else:
					app.logger.warning('[RESEND] RESEND_API_KEY absent — tentative SMTP')
				_send_email_smtp(recipient, subject, text_body, html_body, app=app)
				return

			sender_email = os.getenv('RESEND_FROM_EMAIL') or 'SkillRush <onboarding@resend.dev>'

			app.logger.debug(f'[RESEND] Tentative | to={recipient} | from={sender_email} | subject={subject}')

			email_data = {
				'from': sender_email,
				'to': [recipient],
				'subject': subject,
				'text': text_body,
			}
			if html_body:
				email_data['html'] = html_body

			result = _resend_module.Emails.send(email_data)
			email_id = result.get('id', 'unknown') if isinstance(result, dict) else getattr(result, 'id', 'unknown')
			app.logger.info(f'✅ Email ENVOYÉ via Resend | to={recipient} | subject={subject} | id={email_id}')

		except Exception as exc:
			app.logger.error(
				f'❌ ERREUR Resend | to={recipient} | subject={subject} | {type(exc).__name__}: {exc}',
				exc_info=True
			)


def _send_async(recipient: str, subject: str, text_body: str, html_body: str = None):
	"""Non-blocking email dispatch — captures app object in the calling thread."""
	app = current_app._get_current_object()
	t = threading.Thread(
		target=_send_email_resend,
		args=(app, recipient, subject, text_body, html_body),
		daemon=True,
	)
	t.start()


def send_email(recipient: str, subject: str, body: str):
	"""Legacy helper: send plain-text email asynchronously."""
	if not recipient:
		return False
	_send_async(recipient, subject, body)
	return True


_BASE_STYLE = """
  body{margin:0;padding:0;background:#f0f4ff;font-family:'Segoe UI',Arial,sans-serif;}
  .wrap{max-width:600px;margin:32px auto;background:#fff;border-radius:16px;
		overflow:hidden;box-shadow:0 4px 24px rgba(15,95,255,.10);}
  .hero{background:linear-gradient(130deg,#0f5fff 0%,#00b4d8 45%,#20bf55 100%);
		padding:40px 32px 32px;text-align:center;color:#fff;}
  .hero h1{margin:0 0 8px;font-size:26px;font-weight:800;letter-spacing:-.5px;}
  .hero p{margin:0;font-size:15px;opacity:.9;}
  .logo{display:inline-flex;align-items:center;gap:8px;background:rgba(255,255,255,.16);
		border:1px solid rgba(255,255,255,.28);border-radius:999px;padding:8px 14px;
		font-weight:800;font-size:13px;margin-bottom:12px;}
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


def send_welcome_email(email: str, username: str, dashboard_url: str = None):
	"""Send welcome email to new user."""
	subject = "Bienvenue sur SkillRush 🎉 — Commence ton parcours !"
	dashboard_url = dashboard_url or _default_app_url('/dashboard')

	text_body = (
		f"Bonjour {username},\n\n"
		"Bienvenue sur SkillRush !\n\n"
		"Tu peux maintenant :\n"
		"  - Gagner des XP et monter de niveau\n"
		"  - Maintenir un streak quotidien\n"
		"  - Regarder des mini-videos de competences\n"
		"  - Relever des missions et gagner des recompenses\n\n"
		"Connecte-toi des maintenant sur SkillRush et commence ton parcours.\n\n"
		"L'equipe SkillRush"
	)

	hero = """
	  <div class="logo">SkillRush</div>
	  <div class="badge">Plateforme ENCG</div>
	  <h1>Bienvenue sur SkillRush !</h1>
	  <p>Ta carriere commence ici.</p>"""

	body = f"""
	  <h2>Salut {username}</h2>
	  <p>On est ravis de t'avoir parmi nous ! Ton compte est actif et tu peux des maintenant explorer des centaines de competences professionnelles.</p>
	  <div class="feature"><div class="icon">⭐</div><div class="text"><strong>Systeme XP &amp; Niveaux</strong><br>Gagne des points d'experience a chaque video regardee et monte en niveau.</div></div>
	  <div class="feature"><div class="icon">🔥</div><div class="text"><strong>Streak quotidien</strong><br>Reviens chaque jour pour maintenir ta serie et debloquer des bonus.</div></div>
	  <div class="feature"><div class="icon">📺</div><div class="text"><strong>Mini-videos de competences</strong><br>Des cours courts et cibles sur Excel, Canva, Python, Marketing et plus.</div></div>
	  <div class="feature"><div class="icon">🎯</div><div class="text"><strong>Missions &amp; Quiz</strong><br>Releve des defis, valide tes acquis et remporte des recompenses.</div></div>
	  <hr class="divider">
	  <div class="cta"><a class="btn" href="{dashboard_url}">Commencer maintenant</a></div>"""

	_send_async(email, subject, text_body, _html_wrap(hero, body))


def send_course_approved_email(email: str, username: str, course_name: str, course_url: str = None):
	"""Send course approval email to creator."""
	subject = "✅ Votre cours a été approuvé — SkillRush"
	course_url = course_url or _default_app_url('/dashboard')

	text_body = (
		f"Bonjour {username},\n\n"
		f"Felicitations ! Votre cours '{course_name}' a ete valide par notre equipe de moderation.\n"
		"Il est desormais visible pour tous les apprenants SkillRush.\n\n"
		f"Lien vers votre cours : {course_url}\n\n"
		"Merci pour votre contribution !\nL'equipe SkillRush"
	)

	hero = """
	  <div class="logo">SkillRush</div>
	  <h1>✅ Cours approuvé !</h1>
	  <p>Votre contenu est maintenant en direct.</p>"""

	body = f"""
	  <h2>Bravo {username} !</h2>
	  <p>Votre cours <strong>"{course_name}"</strong> a été approuvé par notre équipe de modération.</p>
	  <p>Il est maintenant visible pour tous les utilisateurs SkillRush. Vos apprenants peuvent commencer à regarder votre contenu !</p>
	  <div class="cta"><a class="btn" href="{course_url}">Voir votre cours</a></div>
	  <hr class="divider">
	  <p style="font-size:13px;color:#666;">Merci de contribuer à la communauté SkillRush ! 🙏</p>"""

	_send_async(email, subject, text_body, _html_wrap(hero, body))


def send_course_rejected_email(email: str, username: str, course_name: str, reason: str = None, edit_url: str = None):
	"""Send course rejection email to creator."""
	subject = "📝 Votre cours nécessite des modifications — SkillRush"
	edit_url = edit_url or _default_app_url('/skill/my-skills')

	reason_text = f"\n\nMotif du refus :\n{reason}" if reason else ""
	
	text_body = (
		f"Bonjour {username},\n\n"
		f"Votre cours '{course_name}' n'a pas pu etre approuve par notre equipe de moderation.\n"
		f"{reason_text}\n\n"
		"Vous pouvez modifier votre cours et soumettre une nouvelle version.\n"
		f"Lien pour editer : {edit_url}\n\n"
		"L'equipe SkillRush"
	)

	hero = """
	  <div class="logo">SkillRush</div>
	  <h1>📝 Modifications requises</h1>
	  <p>Nous avons besoin de quelques ajustements.</p>"""

	reason_html = f"<p style='background:#fff9e6;padding:16px;border-radius:8px;border-left:4px solid #ff9800;'><strong>Motif :</strong><br>{reason}</p>" if reason else ""

	body = f"""
	  <h2>Bonjour {username}</h2>
	  <p>Merci d'avoir créé le cours <strong>"{course_name}"</strong>. Notre équipe l'a examiné et nous suggérons quelques modifications pour mieux correspondre à nos standards.</p>
	  {reason_html}
	  <p>Vous pouvez modifier votre cours et soumettre une nouvelle version pour approbation.</p>
	  <div class="cta"><a class="btn" href="{edit_url}">Modifier mon cours</a></div>"""

	_send_async(email, subject, text_body, _html_wrap(hero, body))
