"""
WSGI entry point para producción con Gunicorn
Uso: gunicorn --bind 0.0.0.0:5000 wsgi:app
"""
from app import create_app

app = create_app('production')

if __name__ == "__main__":
    app.run()
