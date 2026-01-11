#!/usr/bin/env python3
"""
Script para ejecutar la aplicación con MySQL local
"""

import os
import sys

# Configurar variables de entorno para MySQL local
os.environ['FLASK_ENV'] = 'development'
os.environ['SECRET_KEY'] = 'dev-secret-key-for-local-testing'
os.environ['DB_HOST'] = 'localhost'
os.environ['DB_PORT'] = '3306'
os.environ['DB_USER'] = 'root'
os.environ['DB_PASSWORD'] = input('Ingresa tu contraseña de MySQL root: ')
os.environ['DB_NAME'] = 'dbapp'

print("\n" + "="*50)
print("🔧 Configurando conexión a MySQL local...")
print("="*50)
print(f"Host: {os.environ['DB_HOST']}")
print(f"Puerto: {os.environ['DB_PORT']}")
print(f"Usuario: {os.environ['DB_USER']}")
print(f"Base de datos: {os.environ['DB_NAME']}")
print("="*50 + "\n")

# Importar y ejecutar la aplicación
from app import create_app

app = create_app()

print("\n" + "="*50)
print("🚀 Invagro - Sistema de Facturación (MySQL)")
print("="*50)
print(f"📍 Servidor: http://127.0.0.1:5000")
print(f"🔧 Modo: Desarrollo (MySQL)")
print(f"📊 Base de datos: {os.environ['DB_NAME']}")
print("\n💡 Credenciales:")
print("   Usuario: admin")
print("   Contraseña: invagro2024")
print("="*50)
print("\n⌨️  Presiona CTRL+C para detener el servidor\n")

app.run(host='127.0.0.1', port=5000, debug=True)
