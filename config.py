import os
from dotenv import load_dotenv

load_dotenv()



def _mail_server():
    username = (os.getenv('MAIL_USERNAME') or os.getenv('SMTP_USER') or '').strip().lower()
    explicit = (os.getenv('MAIL_SERVER') or os.getenv('SMTP_HOST') or '').strip()
    if explicit:
        return explicit
    if username.endswith('@gmail.com'):
        return 'smtp.gmail.com'
    return ''


def _mail_default_sender():
    explicit = (os.getenv('MAIL_DEFAULT_SENDER') or os.getenv('SMTP_FROM') or '').strip()
    username = (os.getenv('MAIL_USERNAME') or os.getenv('SMTP_USER') or '').strip()
    if explicit:
        return explicit
    # Use the brand sender requested by product, even if SMTP auth uses another account.
    return 'SkillRush <no-reply@skillrush.app>'


def _mail_port():
    return int(os.getenv('MAIL_PORT') or os.getenv('SMTP_PORT') or '587')


def _mail_username():
    return os.getenv('MAIL_USERNAME') or os.getenv('SMTP_USER') or ''


def _mail_password():
    return os.getenv('MAIL_PASSWORD') or os.getenv('SMTP_PASS') or ''


def _app_base_url():
    return (os.getenv('APP_BASE_URL') or 'https://web-production-skillrush.up.railway.app').rstrip('/')

def _database_url():
    """Return a SQLAlchemy-compatible database URL."""
    url = os.getenv('DATABASE_URL')
    if not url:
        pg_host = os.getenv('PGHOST')
        pg_port = os.getenv('PGPORT') or '5432'
        pg_user = os.getenv('PGUSER')
        pg_password = os.getenv('PGPASSWORD')
        pg_db = os.getenv('PGDATABASE')

        if pg_host and pg_user and pg_password and pg_db:
            url = f'postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}'

    if not url:
        url = 'sqlite:///skillrush.db'

    # Some platforms provide postgres:// which SQLAlchemy expects as postgresql://
    if url.startswith('postgres://'):
        url = url.replace('postgres://', 'postgresql://', 1)
    return url

class Config:
    """Configuration de base"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = _database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Limite upload : 500 Mo (vidéos)
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024
    MAIL_SERVER = _mail_server()
    MAIL_PORT = _mail_port()
    MAIL_USERNAME = _mail_username()
    MAIL_PASSWORD = _mail_password()
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'false').lower() == 'true'
    MAIL_DEFAULT_SENDER = _mail_default_sender()
    APP_BASE_URL = _app_base_url()
    
class DevelopmentConfig(Config):
    """Configuration pour le développement"""
    DEBUG = True
    TESTING = False

class TestingConfig(Config):
    """Configuration pour les tests"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

class ProductionConfig(Config):
    """Configuration pour la production"""
    DEBUG = False
    TESTING = False

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
