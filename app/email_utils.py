import smtplib
import threading
import logging
from email.message import EmailMessage
from email.utils import formataddr, parseaddr

from flask import current_app

logger = logging.getLogger(__name__)


def _default_app_url(path='/dashboard'):
	app = current_app._get_current_object()
	base = (app.config.get('APP_BASE_URL') or 'https://web-production-skillrush.up.railway.app').rstrip('/')
	if not path.startswith('/'):
		path = '/' + path
	return f"{base}{path}"


def _resolve_sender(mail_sender, mail_username, mail_server):
	"""Build a sender compatible with SMTP providers (notably Gmail)."""
	sender_name, sender_addr = parseaddr(mail_sender or '')
	_, smtp_addr = parseaddr(mail_username or '')
	smtp_addr = smtp_addr or (mail_username or '').strip()
	server = (mail_server or '').lower()

	if not sender_addr:
		if smtp_addr:
			return formataddr(('SkillRush', smtp_addr)), None
		return 'SkillRush <no-reply@skillrush.app>', None

	# Gmail often rejects a From address that differs from the authenticated account.
	if 'gmail' in server and smtp_addr and sender_addr.lower() != smtp_addr.lower():
		display = sender_name or 'SkillRush'
		effective_sender = formataddr((display, smtp_addr))
		reply_to = formataddr((display, sender_addr))
		return effective_sender, reply_to

	return mail_sender, None


def _smtp_send(app, recipient, subject, text_body, html_body=None):
	"""Runs inside a background thread; uses app context."""
	with app.app_context():
		mail_server = app.config.get('MAIL_SERVER')
		mail_port = int(app.config.get('MAIL_PORT', 587))
		mail_username = app.config.get('MAIL_USERNAME')
		mail_password = app.config.get('MAIL_PASSWORD')
		mail_use_tls = app.config.get('MAIL_USE_TLS', True)
		mail_use_ssl = app.config.get('MAIL_USE_SSL', False)
		mail_sender = app.config.get('MAIL_DEFAULT_SENDER', 'SkillRush <no-reply@skillrush.app>')

		if not recipient:
			app.logger.warning('Email non envoyé: destinataire absent')
			return

		if not mail_server:
			app.logger.warning('Email non envoyé: MAIL_SERVER absent | to=%s', recipient)
			return

		if mail_username and not mail_password:
			app.logger.warning('Email non envoyé: MAIL_PASSWORD/SMTP_PASS absent | to=%s', recipient)
			return

		effective_sender, reply_to = _resolve_sender(mail_sender, mail_username, mail_server)

		msg = EmailMessage()
		msg['Subject'] = subject
		msg['From'] = effective_sender
		msg['To'] = recipient
		if reply_to:
			msg['Reply-To'] = reply_to
		msg.set_content(text_body)

		if html_body:
			msg.add_alternative(html_body, subtype='html')

		try:
			app.logger.debug(f'[EMAIL] Tentative d\'envoi à {recipient} | Serveur={mail_server}:{mail_port} | TLS={mail_use_tls} | SSL={mail_use_ssl}')
			smtp_cls = smtplib.SMTP_SSL if mail_use_ssl else smtplib.SMTP
			with smtp_cls(mail_server, mail_port, timeout=20) as server:
				server.ehlo()
				if mail_use_tls and not mail_use_ssl:
					app.logger.debug(f'[EMAIL] Activation de STARTTLS')
					server.starttls()
					server.ehlo()
				if mail_username:
					app.logger.debug(f'[EMAIL] Login avec {mail_username}')
					server.login(mail_username, mail_password)
				app.logger.debug(f'[EMAIL] Envoi du message')
				server.send_message(msg)
			app.logger.info(f'✅ Email ENVOYÉ | to={recipient} | subject={subject}')
		except Exception as exc:
			app.logger.error(f'❌ ERREUR EMAIL | to={recipient} | subject={subject} | Exception: {type(exc).__name__}: {exc}', exc_info=True)


def _send_async(recipient, subject, text_body, html_body=None):
	"""Non-blocking email dispatch via a daemon thread."""
	app = current_app._get_current_object()
	t = threading.Thread(
		target=_smtp_send,
		args=(app, recipient, subject, text_body, html_body),
		daemon=True,
	)
	t.start()


def send_email(recipient, subject, body):
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
	  <div class="feature"><div class="icon">XP</div><div class="text"><strong>Systeme XP &amp; Niveaux</strong><br>Gagne des points d'experience a chaque video regardee et monte en niveau.</div></div>
	  <div class="feature"><div class="icon">Streak</div><div class="text"><strong>Streak quotidien</strong><br>Reviens chaque jour pour maintenir ta serie et debloquer des bonus.</div></div>
	  <div class="feature"><div class="icon">Video</div><div class="text"><strong>Mini-videos de competences</strong><br>Des cours courts et cibles sur Excel, Canva, Python, Marketing et plus.</div></div>
	  <div class="feature"><div class="icon">Mission</div><div class="text"><strong>Missions &amp; Quiz</strong><br>Releve des defis, valide tes acquis et remporte des recompenses.</div></div>
	  <hr class="divider">
	  <div class="cta"><a class="btn" href="{dashboard_url}">Commencer maintenant</a></div>"""

	_send_async(email, subject, text_body, _html_wrap(hero, body))


def send_course_approved_email(email: str, username: str, course_name: str, course_url: str = None):
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
	  <div class="badge" style="background:rgba(32,191,85,.25)">Cours approuve</div>
	  <h1>Felicitations !</h1>
	  <p>Votre cours a passe la moderation avec succes.</p>"""

	body = f"""
	  <h2>Bonjour {username}</h2>
	  <p>Votre cours <strong>{course_name}</strong> a ete approuve. Il est maintenant visible pour tous les apprenants.</p>
	  <hr class="divider">
	  <div class="cta"><a class="btn" href="{course_url}">Voir mon cours</a></div>"""

	_send_async(email, subject, text_body, _html_wrap(hero, body))


def send_course_rejected_email(email: str, username: str, course_name: str, reason: str = None, edit_url: str = None):
	subject = "❌ Votre cours nécessite des modifications — SkillRush"
	edit_url = edit_url or _default_app_url('/skill/my-skills')
	reason_html = (
		f'<p style="background:#fff5f5;border-left:4px solid #e53e3e;padding:12px 16px;'
		f'border-radius:6px;color:#742a2a;"><strong>Motif :</strong> {reason}</p>'
	) if reason else ""
	reason_text = f"\nMotif du refus : {reason}\n" if reason else ""

	text_body = (
		f"Bonjour {username},\n\n"
		f"Votre cours '{course_name}' n'a pas passe la validation de moderation.{reason_text}\n"
		"Ne vous decouragez pas ! Vous pouvez corriger votre contenu et le soumettre a nouveau.\n\n"
		f"Modifier votre cours : {edit_url}\n\n"
		"L'equipe SkillRush"
	)

	hero = """
	  <div class="logo">SkillRush</div>
	  <div class="badge" style="background:rgba(229,62,62,.25)">Modifications requises</div>
	  <h1>Votre cours necessite des ajustements</h1>
	  <p>Notre equipe a examine votre soumission.</p>"""

	body = f"""
	  <h2>Bonjour {username}</h2>
	  <p>Votre cours <strong>{course_name}</strong> n'a pas pu etre valide en l'etat.</p>
	  {reason_html}
	  <p>Vous pouvez corriger votre contenu puis le resoumettre.</p>
	  <hr class="divider">
	  <div class="cta"><a class="btn" style="background:linear-gradient(130deg,#e53e3e,#ff6b35)" href="{edit_url}">Modifier mon cours</a></div>"""

	_send_async(email, subject, text_body, _html_wrap(hero, body))
