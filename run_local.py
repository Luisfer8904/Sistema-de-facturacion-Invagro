#!/usr/bin/env python3
"""
Script para ejecutar la aplicación localmente con SQLite
"""

import os
import sys
from flask import Flask
from config_local import config
from models import db, login_manager
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from models.database import Usuario, Cliente, Producto


def create_local_app():
    """Crear aplicación Flask para desarrollo local"""
    
    app = Flask(__name__)
    app.config.from_object(config['development'])
    
    # Inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)
    
    # Registrar blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    
    return app


def init_local_database(app):
    """Inicializar base de datos local con datos de prueba"""
    
    with app.app_context():
        print("\n" + "="*50)
        print("🔧 Inicializando base de datos local (SQLite)...")
        print("="*50)
        
        # Crear todas las tablas
        db.create_all()
        print("✅ Tablas creadas exitosamente")
        
        # Verificar si ya existe el usuario admin
        admin = Usuario.query.filter_by(username='admin').first()
        
        if not admin:
            print("\n👤 Creando usuario administrador...")
            
            # Crear usuario admin
            admin = Usuario(
                username='admin',
                nombre_completo='Administrador Invagro',
                email='admin@invagro.com',
                rol='admin',
                activo=True
            )
            admin.set_password('invagro2024')
            
            db.session.add(admin)
            db.session.commit()
            
            print("✅ Usuario administrador creado")
            print("\n📋 Credenciales de acceso:")
            print("   Usuario: admin")
            print("   Contraseña: invagro2024")
        else:
            print("\n⚠️  El usuario administrador ya existe")
        
        # Crear algunos productos de ejemplo
        if Producto.query.count() == 0:
            print("\n📦 Creando productos de ejemplo...")
            
            productos = [
                Producto(
                    codigo='SHMP001',
                    nombre='Shampoo Antipulgas Premium',
                    categoria='shampoo',
                    precio=45.00,
                    stock=50,
                    descripcion='Shampoo antipulgas de alta calidad para perros',
                    activo=True
                ),
                Producto(
                    codigo='SHMP002',
                    nombre='Shampoo Hipoalergénico',
                    categoria='shampoo',
                    precio=38.00,
                    stock=30,
                    descripcion='Shampoo especial para pieles sensibles',
                    activo=True
                ),
                Producto(
                    codigo='VET001',
                    nombre='Vitaminas Caninas',
                    categoria='veterinario',
                    precio=65.00,
                    stock=40,
                    descripcion='Suplemento vitamínico completo',
                    activo=True
                ),
                Producto(
                    codigo='VET002',
                    nombre='Desparasitante Interno',
                    categoria='veterinario',
                    precio=55.00,
                    stock=60,
                    descripcion='Desparasitante de amplio espectro',
                    activo=True
                ),
            ]
            
            for producto in productos:
                db.session.add(producto)
            
            db.session.commit()
            print(f"✅ {len(productos)} productos creados")
        
        # Crear algunos clientes de ejemplo
        if Cliente.query.count() == 0:
            print("\n👥 Creando clientes de ejemplo...")
            
            clientes = [
                Cliente(
                    nombre='Veterinaria San Francisco',
                    ruc_dni='20123456789',
                    direccion='Av. Principal 123, Lima',
                    telefono='01-2345678',
                    email='ventas@vetsanfrancisco.com'
                ),
                Cliente(
                    nombre='Pet Shop Los Cachorros',
                    ruc_dni='20987654321',
                    direccion='Jr. Los Perros 456, Lima',
                    telefono='01-8765432',
                    email='info@loscachorros.com'
                ),
                Cliente(
                    nombre='Juan Pérez García',
                    ruc_dni='12345678',
                    direccion='Calle Las Flores 789, Lima',
                    telefono='987654321',
                    email='juan.perez@email.com'
                ),
            ]
            
            for cliente in clientes:
                db.session.add(cliente)
            
            db.session.commit()
            print(f"✅ {len(clientes)} clientes creados")
        
        print("\n" + "="*50)
        print("🎉 Base de datos local inicializada correctamente")
        print("="*50)


if __name__ == '__main__':
    app = create_local_app()
    
    # Inicializar base de datos si no existe
    if not os.path.exists('invagro_local.db'):
        init_local_database(app)
    
    print("\n" + "="*50)
    print("🚀 Invagro - Sistema de Facturación (LOCAL)")
    print("="*50)
    print(f"📍 Servidor: http://127.0.0.1:5000")
    print(f"🔧 Modo: Desarrollo (SQLite)")
    print(f"📊 Base de datos: invagro_local.db")
    print("\n💡 Credenciales:")
    print("   Usuario: admin")
    print("   Contraseña: invagro2024")
    print("="*50)
    print("\n⌨️  Presiona CTRL+C para detener el servidor\n")
    
    app.run(host='127.0.0.1', port=5000, debug=True)
