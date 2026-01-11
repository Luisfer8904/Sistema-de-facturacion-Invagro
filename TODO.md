# Sistema de Facturación Invagro - TODO List

## Fase 1: Estructura del Proyecto ✅
- [x] Crear estructura de carpetas
- [x] Crear requirements.txt
- [x] Crear .env.example
- [x] Crear .gitignore

## Fase 2: Configuración Base ✅
- [x] Crear config.py (configuración)
- [x] Crear app.py (aplicación principal)
- [x] Crear wsgi.py (para Gunicorn)

## Fase 3: Modelos de Base de Datos ✅
- [x] Crear models/__init__.py
- [x] Crear models/database.py con tablas:
  - [x] inva-usuarios
  - [x] inva-clientes
  - [x] inva-productos
  - [x] inva-facturas
  - [x] inva-detalle_facturas

## Fase 4: Rutas y Autenticación ✅
- [x] Crear routes/__init__.py
- [x] Crear routes/auth.py (login/logout)
- [x] Crear routes/dashboard.py

## Fase 5: Frontend - Templates ✅
- [x] Crear templates/base.html
- [x] Crear templates/login.html
- [x] Crear templates/dashboard.html

## Fase 6: Frontend - Estilos y Scripts ✅
- [x] Crear static/css/styles.css
- [x] Crear static/js/auth.js
- [x] Crear static/js/main.js
- [x] Organizar assets (logo, mascota, shampoo)

## Fase 7: Scripts de Deployment ✅
- [x] Crear scripts/init_db.py
- [x] Crear scripts/deploy.sh
- [x] Crear README.md con documentación completa

## Fase 8: Testing y Deployment 🔄
- [ ] Crear archivo .env local
- [ ] Probar localmente
- [ ] Deployment en AWS Lightsail
- [ ] Configurar SSL/HTTPS
- [ ] Configurar dominio (si aplica)

## Próximos Pasos Recomendados:
1. Crear archivo .env con credenciales de MySQL
2. Ejecutar script de inicialización: `python scripts/init_db.py`
3. Probar la aplicación localmente: `python app.py`
4. Subir código al servidor AWS Lightsail
5. Ejecutar script de deployment: `sudo ./scripts/deploy.sh`
