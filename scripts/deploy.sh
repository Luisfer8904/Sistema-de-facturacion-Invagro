#!/bin/bash

# Script de deployment para AWS Lightsail Ubuntu
# Sistema de Facturación Invagro

echo "================================================"
echo "🚀 Deployment - Sistema de Facturación Invagro"
echo "================================================"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Directorio de la aplicación
APP_DIR="/var/www/invagro"
APP_USER="www-data"

echo -e "\n${YELLOW}📦 Paso 1: Actualizando sistema...${NC}"
sudo apt update
sudo apt upgrade -y

echo -e "\n${YELLOW}📦 Paso 2: Instalando dependencias del sistema...${NC}"
sudo apt install -y python3 python3-pip python3-venv nginx supervisor git

echo -e "\n${YELLOW}📁 Paso 3: Creando directorio de la aplicación...${NC}"
sudo mkdir -p $APP_DIR
sudo chown -R $USER:$USER $APP_DIR

echo -e "\n${YELLOW}🐍 Paso 4: Creando entorno virtual Python...${NC}"
cd $APP_DIR
python3 -m venv venv
source venv/bin/activate

echo -e "\n${YELLOW}📚 Paso 5: Instalando dependencias Python...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

echo -e "\n${YELLOW}🔐 Paso 6: Configurando variables de entorno...${NC}"
if [ ! -f .env ]; then
    echo "Creando archivo .env..."
    cp .env.example .env
    echo -e "${RED}⚠️  IMPORTANTE: Edita el archivo .env con tus credenciales reales${NC}"
    echo "   nano $APP_DIR/.env"
fi

echo -e "\n${YELLOW}🗄️  Paso 7: Inicializando base de datos...${NC}"
python scripts/init_db.py

echo -e "\n${YELLOW}🌐 Paso 8: Configurando Nginx...${NC}"
sudo tee /etc/nginx/sites-available/invagro > /dev/null <<EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static {
        alias $APP_DIR/static;
        expires 30d;
    }

    client_max_body_size 10M;
}
EOF

# Habilitar sitio
sudo ln -sf /etc/nginx/sites-available/invagro /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Verificar configuración
sudo nginx -t

echo -e "\n${YELLOW}⚙️  Paso 9: Configurando Supervisor...${NC}"
sudo tee /etc/supervisor/conf.d/invagro.conf > /dev/null <<EOF
[program:invagro]
directory=$APP_DIR
command=$APP_DIR/venv/bin/gunicorn --workers 3 --timeout 120 --graceful-timeout 30 --bind 127.0.0.1:5000 wsgi:app
user=$APP_USER
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/log/invagro/error.log
stdout_logfile=/var/log/invagro/access.log
environment=FLASK_ENV="production"
EOF

# Crear directorio de logs
sudo mkdir -p /var/log/invagro
sudo chown -R $APP_USER:$APP_USER /var/log/invagro

echo -e "\n${YELLOW}🔄 Paso 10: Reiniciando servicios...${NC}"
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart invagro
sudo systemctl restart nginx

echo -e "\n${YELLOW}🔥 Paso 11: Configurando firewall...${NC}"
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw --force enable

echo -e "\n${GREEN}================================================${NC}"
echo -e "${GREEN}✅ Deployment completado exitosamente!${NC}"
echo -e "${GREEN}================================================${NC}"
echo -e "\n📋 Información del deployment:"
echo -e "   Directorio: $APP_DIR"
echo -e "   Usuario: $APP_USER"
echo -e "   Puerto: 80 (HTTP)"
echo -e "\n🌐 Accede a tu aplicación en:"
echo -e "   http://$(curl -s ifconfig.me)"
echo -e "\n📝 Comandos útiles:"
echo -e "   Ver logs: sudo tail -f /var/log/invagro/error.log"
echo -e "   Reiniciar app: sudo supervisorctl restart invagro"
echo -e "   Estado: sudo supervisorctl status invagro"
echo -e "\n${YELLOW}⚠️  No olvides:${NC}"
echo -e "   1. Configurar el archivo .env con tus credenciales"
echo -e "   2. Cambiar la contraseña del usuario admin"
echo -e "   3. Configurar SSL/HTTPS con Let's Encrypt (certbot)"
echo ""
