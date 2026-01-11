#!/usr/bin/env python3
"""
Script para inicializar la base de datos
Crea las tablas y un usuario administrador por defecto
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from models import db
from models.database import Usuario, Cliente, Producto

def init_database():
    """Inicializar base de datos con datos de prueba"""
    
    app = create_app('development')
    
    with app.app_context():
        print("🔧 Creando tablas en la base de datos...")
        
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
        print("🎉 Base de datos inicializada correctamente")
        print("="*50)
        print("\n💡 Puedes iniciar la aplicación con:")
        print("   python app.py")
        print("\n")

if __name__ == '__main__':
    try:
        init_database()
    except Exception as e:
        print(f"\n❌ Error al inicializar la base de datos: {e}")
        sys.exit(1)
