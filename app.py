import os
from flask import Flask
from config import config
from models import db, login_manager
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp


def create_app(config_name=None):
    """Factory para crear la aplicación Flask"""
    
    # Determinar el entorno
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Crear aplicación
    app = Flask(__name__)
    
    # Cargar configuración
    app.config.from_object(config[config_name])
    
    # Inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)
    
    # Registrar blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    
    # Crear tablas si no existen
    with app.app_context():
        db.create_all()
    
    return app


if __name__ == '__main__':
    app = create_app()
    
    # Obtener configuración del host y puerto
    host = app.config.get('APP_HOST', '0.0.0.0')
    port = app.config.get('APP_PORT', 5000)
    debug = app.config.get('DEBUG', True)
    
    print(f"\n{'='*50}")
    print(f"🚀 Invagro - Sistema de Facturación")
    print(f"{'='*50}")
    print(f"📍 Servidor: http://{host}:{port}")
    print(f"🔧 Modo: {'Desarrollo' if debug else 'Producción'}")
    print(f"{'='*50}\n")
    
    app.run(host=host, port=port, debug=debug)
