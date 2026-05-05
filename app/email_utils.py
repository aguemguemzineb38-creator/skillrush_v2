import smtplib
from email.message import EmailMessage
from flask import current_app


def send_email(recipient, subject, body):
    """Envoie un email SMTP si la config est fournie, sinon journalise l'événement."""
    if not recipient:
        return False

    mail_server = current_app.config.get('MAIL_SERVER')
    mail_port = current_app.config.get('MAIL_PORT')
    mail_username = current_app.config.get('MAIL_USERNAME')
    mail_password = current_app.config.get('MAIL_PASSWORD')
    mail_use_tls = current_app.config.get('MAIL_USE_TLS', True)
    mail_use_ssl = current_app.config.get('MAIL_USE_SSL', False)
    mail_sender = current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@skillrush.local')

    if not mail_server:
        current_app.logger.warning(
            'Email non envoye: config SMTP absente | to=%s | subject=%s', recipient, subject
        )
        return False

    message = EmailMessage()
    message['Subject'] = subject
    message['From'] = mail_sender
    message['To'] = recipient
    message.set_content(body)

    smtp_class = smtplib.SMTP_SSL if mail_use_ssl else smtplib.SMTP
    with smtp_class(mail_server, mail_port, timeout=20) as server:
        if mail_use_tls and not mail_use_ssl:
            server.starttls()
        if mail_username:
            server.login(mail_username, mail_password)
        server.send_message(message)

    return True
