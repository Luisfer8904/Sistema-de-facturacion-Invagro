# Sistema de Facturacion Invagro

Proyecto base para un sistema web de facturacion con backend en Python (Flask) y frontend en HTML, CSS y JavaScript. Esta base esta lista para escalar con autenticacion, clientes y facturacion.

## Tecnologias

- Python 3
- Flask
- python-dotenv
- HTML5, CSS3, JavaScript

## Instalacion

1. Crear y activar un entorno virtual.
2. Instalar dependencias.

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Copiar variables de entorno.

```bash
cp .env.example .env
```

## Ejecutar backend

```bash
cd backend
python app.py
```

El backend quedara disponible en `http://127.0.0.1:5000/`.

## Despliegue en Ubuntu Server

1. Clonar o copiar el proyecto a `/var/www/` y asegurar permisos.

```
/var/www/Sistema-de-facturacion-Invagro/
```

2. Crear y activar el entorno virtual.

```bash
cd /var/www/Sistema-de-facturacion-Invagro/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Configurar variables de entorno (por ejemplo en un archivo `.env` solo para desarrollo).

4. Ejecutar Gunicorn.

```bash
cd /var/www/Sistema-de-facturacion-Invagro/backend
gunicorn --workers 3 --bind 0.0.0.0:8000 wsgi:app
```

Este comando deja la app lista para Nginx y systemd.

### Variables requeridas en /etc/invagro.env

Estas variables deben existir en el servidor y cargarse con systemd usando `EnvironmentFile=/etc/invagro.env`:

```env
FLASK_ENV=production
SECRET_KEY=tu-clave-segura
DB_HOST=tu-host-mysql
DB_PORT=3306
DB_USER=tu-usuario
DB_PASS=tu-password
DB_NAME=invagro
```

## Estructura del proyecto

```
Sistema-de-facturacion-Invagro/
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── requirements.txt
│   ├── .env.example
│   └── routes/
│       └── __init__.py
├── frontend/
│   ├── index.html
│   ├── css/
│   │   └── styles.css
│   └── js/
│       └── app.js
├── .gitignore
└── README.md
```
