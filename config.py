import os
from datetime import timedelta
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Config:
    """Configuración base"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Configuración de la base de datos MySQL
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '3306')
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_NAME = os.environ.get('DB_NAME', 'invagro')
    
    # SQLAlchemy configuration
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # Flask-Login
    REMEMBER_COOKIE_DURATION = 3600  # 1 hora
    SESSION_COOKIE_SECURE = False  # Cambiar a True en producción con HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)
    
    # Aplicación
    APP_NAME = os.environ.get('APP_NAME', 'Invagro - Sistema de Facturación')
    APP_HOST = os.environ.get('APP_HOST', '0.0.0.0')
    APP_PORT = int(os.environ.get('APP_PORT', 5000))


class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True  # Requiere HTTPS
    SQLALCHEMY_ECHO = False


# Diccionario de configuraciones
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
