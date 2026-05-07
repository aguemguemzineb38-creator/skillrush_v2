import os
from dotenv import load_dotenv

load_dotenv()



def _mail_server():
    username = os.getenv('MAIL_USERNAME', '').strip().lower()
    explicit = os.getenv('MAIL_SERVER', '').strip()
    if explicit:
        return explicit
    if username.endswith('@gmail.com'):
        return 'smtp.gmail.com'
    return ''


def _mail_default_sender():
    explicit = os.getenv('MAIL_DEFAULT_SENDER', '').strip()
    username = os.getenv('MAIL_USERNAME', '').strip()
    if explicit:
        return explicit
    if username:
        return f'SkillRush <{username}>'
    return 'SkillRush <noreply@skillrush.local>'

def _database_url():
    """Return a SQLAlchemy-compatible database URL."""
    url = os.getenv('DATABASE_URL', 'sqlite:///skillrush.db')
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
    MAIL_PORT = int(os.getenv('MAIL_PORT', '587'))
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'false').lower() == 'true'
    MAIL_DEFAULT_SENDER = _mail_default_sender()
    
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
