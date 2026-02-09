import os
from datetime import timedelta
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Config:
    """Configuración base"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # SQLAlchemy configuration para SQLite local
    SQLALCHEMY_DATABASE_URI = 'sqlite:///invagro_local.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True
    
    # Sesion y recordar cuenta
    REMEMBER_COOKIE_DURATION = timedelta(days=7)
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_SECURE = False
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_REFRESH_EACH_REQUEST = False
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # Aplicación
    APP_NAME = os.environ.get('APP_NAME', 'Invagro - Sistema de Facturación')
    APP_HOST = '127.0.0.1'
    APP_PORT = 5000


class DevelopmentConfig(Config):
    """Configuración para desarrollo local"""
    DEBUG = True
    SQLALCHEMY_ECHO = True


# Configuración por defecto
config = {
    'development': DevelopmentConfig,
    'default': DevelopmentConfig
}
