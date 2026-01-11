# 🐾 Sistema de Facturación Invagro

Sistema de facturación web para **Invagro (Inversiones Agroindustriales)** - Especialistas en productos veterinarios y shampoo para perros.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)
![MySQL](https://img.shields.io/badge/MySQL-8.0-orange.svg)

## 📋 Características

- ✅ Sistema de autenticación seguro
- ✅ Dashboard interactivo con estadísticas
- ✅ Gestión de clientes
- ✅ Gestión de productos (veterinarios y shampoo)
- ✅ Sistema de facturación
- ✅ Reportes y análisis
- ✅ Diseño responsive (móvil y desktop)
- ✅ Base de datos MySQL con prefijo "inva-"

## 🛠️ Tecnologías

**Backend:**
- Python 3.8+
- Flask 3.0
- Flask-SQLAlchemy
- Flask-Login
- PyMySQL
- Gunicorn (producción)

**Frontend:**
- HTML5 + Jinja2
- CSS3 + Bootstrap 5
- JavaScript (Vanilla)
- Font Awesome

**Base de Datos:**
- MySQL 8.0
- Tablas con prefijo "inva-"

**Servidor:**
- Ubuntu 22.04 LTS
- Nginx (reverse proxy)
- Supervisor (gestión de procesos)

## 📁 Estructura del Proyecto

```
Sistema de facturacion/
├── app.py                  # Aplicación Flask principal
├── config.py              # Configuración
├── wsgi.py                # Entry point para Gunicorn
├── requirements.txt       # Dependencias Python
├── .env.example          # Plantilla de variables de entorno
├── models/
│   ├── __init__.py
│   └── database.py       # Modelos de BD (inva-*)
├── routes/
│   ├── __init__.py
│   ├── auth.py          # Autenticación
│   └── dashboard.py     # Dashboard
├── static/
│   ├── css/
│   │   └── styles.css
│   ├── js/
│   │   ├── auth.js
│   │   └── main.js
│   └── assets/
│       ├── logo.jpg
│       ├── mascota.jpeg
│       └── shampoo.jpeg
├── templates/
│   ├── base.html
│   ├── login.html
│   └── dashboard.html
└── scripts/
    ├── init_db.py       # Inicializar BD
    └── deploy.sh        # Script de deployment
```

## 🚀 Instalación Local

### 1. Clonar el repositorio

```bash
cd "Sistema de facturacion"
```

### 2. Crear entorno virtual

```bash
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
cp .env.example .env
nano .env  # Editar con tus credenciales
```

Variables importantes:
```env
FLASK_ENV=development
SECRET_KEY=tu-clave-secreta
DB_HOST=tu-host-mysql
DB_PORT=3306
DB_USER=tu-usuario
DB_PASSWORD=tu-password
DB_NAME=invagro
```

### 5. Inicializar base de datos

```bash
python scripts/init_db.py
```

### 6. Ejecutar la aplicación

```bash
python app.py
```

La aplicación estará disponible en: `http://localhost:5000`

## 🔐 Credenciales por Defecto

```
Usuario: admin
Contraseña: invagro2024
```

**⚠️ IMPORTANTE:** Cambia estas credenciales en producción.

## 🗄️ Estructura de Base de Datos

Todas las tablas usan el prefijo `inva-`:

### inva-usuarios
- Gestión de usuarios del sistema
- Roles: admin, vendedor, contador

### inva-clientes
- Información de clientes
- RUC/DNI, contacto, dirección

### inva-productos
- Catálogo de productos
- Categorías: veterinario, shampoo

### inva-facturas
- Registro de facturas
- Estados: pendiente, pagada, anulada

### inva-detalle_facturas
- Detalles de cada factura
- Productos, cantidades, precios

## 🌐 Deployment en AWS Lightsail

### Requisitos
- Instancia Ubuntu 22.04 LTS
- Base de datos MySQL en AWS RDS
- Acceso SSH al servidor

### Pasos de Deployment

1. **Conectar al servidor:**
```bash
ssh ubuntu@tu-ip-servidor
```

2. **Clonar/subir el proyecto:**
```bash
cd /var/www
sudo git clone tu-repositorio invagro
# O usar SCP/SFTP para subir archivos
```

3. **Ejecutar script de deployment:**
```bash
cd /var/www/invagro
chmod +x scripts/deploy.sh
sudo ./scripts/deploy.sh
```

4. **Configurar variables de entorno:**
```bash
sudo nano /var/www/invagro/.env
```

5. **Reiniciar servicios:**
```bash
sudo supervisorctl restart invagro
sudo systemctl restart nginx
```

### Configuración SSL (Opcional pero Recomendado)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d tu-dominio.com
```

## 📝 Comandos Útiles

### Desarrollo Local
```bash
# Activar entorno virtual
source venv/bin/activate

# Ejecutar en modo desarrollo
python app.py

# Ejecutar con Gunicorn
gunicorn --bind 0.0.0.0:5000 wsgi:app
```

### Producción (Servidor)
```bash
# Ver logs de la aplicación
sudo tail -f /var/log/invagro/error.log
sudo tail -f /var/log/invagro/access.log

# Estado de la aplicación
sudo supervisorctl status invagro

# Reiniciar aplicación
sudo supervisorctl restart invagro

# Reiniciar Nginx
sudo systemctl restart nginx

# Ver logs de Nginx
sudo tail -f /var/log/nginx/error.log
```

## 🔧 Configuración de Nginx

Archivo: `/etc/nginx/sites-available/invagro`

```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static {
        alias /var/www/invagro/static;
        expires 30d;
    }
}
```

## 🐛 Troubleshooting

### Error de conexión a MySQL
```bash
# Verificar conectividad
mysql -h tu-host -P 3306 -u tu-usuario -p

# Verificar variables de entorno
cat .env
```

### Aplicación no inicia
```bash
# Ver logs
sudo supervisorctl tail invagro stderr

# Verificar permisos
sudo chown -R www-data:www-data /var/www/invagro
```

### Error 502 Bad Gateway
```bash
# Verificar que Gunicorn esté corriendo
sudo supervisorctl status invagro

# Reiniciar servicios
sudo supervisorctl restart invagro
sudo systemctl restart nginx
```

## 📚 Documentación Adicional

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Bootstrap 5 Documentation](https://getbootstrap.com/docs/5.3/)
- [Nginx Documentation](https://nginx.org/en/docs/)

## 🤝 Soporte

Para soporte técnico o consultas:
- Email: admin@invagro.com
- Teléfono: [Tu teléfono]

## 📄 Licencia

© 2024 Invagro - Inversiones Agroindustriales. Todos los derechos reservados.

---

**Desarrollado con ❤️ para Invagro** 🐾
