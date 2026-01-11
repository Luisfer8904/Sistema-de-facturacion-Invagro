# 🚀 Guía de Deployment - Sistema de Facturación Invagro

## ✅ Estado del Proyecto

El sistema ha sido completamente desarrollado y está listo para deployment. Todos los componentes están implementados:

### Componentes Completados:
- ✅ Backend Flask con Python
- ✅ Modelos de base de datos con prefijo "inva-"
- ✅ Sistema de autenticación (login/logout)
- ✅ Dashboard interactivo
- ✅ Frontend responsive con Bootstrap 5
- ✅ Scripts de deployment
- ✅ Documentación completa

## 📋 Pasos para Deployment en AWS Lightsail

### 1. Verificar Credenciales de Base de Datos

Primero, verifica que puedes conectarte a tu base de datos MySQL desde tu máquina local:

```bash
mysql -h ls-2bfaa22cfdc7ff048e57bf0cc7680cde22b2bb84.cmpokeawm2j7.us-east-1.rds.amazonaws.com -P 3306 -u dbluis -p
```

Si no puedes conectarte, verifica:
- ✅ La contraseña es correcta
- ✅ Tu IP está en la lista blanca de AWS RDS
- ✅ El security group permite conexiones desde tu IP

### 2. Actualizar Archivo .env

Edita el archivo `.env` con las credenciales correctas:

```bash
nano .env
```

Actualiza la contraseña de la base de datos:
```env
DB_PASSWORD=tu-password-real-aqui
```

### 3. Probar Localmente (Opcional)

Si quieres probar localmente primero:

```bash
# Activar entorno virtual
source venv/bin/activate

# Inicializar base de datos
python scripts/init_db.py

# Ejecutar aplicación
python app.py
```

Accede a: `http://localhost:5000`

Credenciales:
- Usuario: `admin`
- Contraseña: `invagro2024`

### 4. Subir Código al Servidor AWS Lightsail

#### Opción A: Usando Git (Recomendado)

```bash
# En tu máquina local
git init
git add .
git commit -m "Sistema de facturación Invagro v1.0"
git remote add origin tu-repositorio-git
git push -u origin main

# En el servidor
ssh ubuntu@tu-ip-servidor
cd /var/www
sudo git clone tu-repositorio invagro
```

#### Opción B: Usando SCP

```bash
# Desde tu máquina local
cd "Sistema de facturacion"
scp -r * ubuntu@tu-ip-servidor:/tmp/invagro/

# En el servidor
ssh ubuntu@tu-ip-servidor
sudo mkdir -p /var/www/invagro
sudo mv /tmp/invagro/* /var/www/invagro/
```

### 5. Ejecutar Script de Deployment

```bash
# Conectar al servidor
ssh ubuntu@tu-ip-servidor

# Ir al directorio
cd /var/www/invagro

# Hacer ejecutable el script
chmod +x scripts/deploy.sh

# Ejecutar deployment
sudo ./scripts/deploy.sh
```

El script automáticamente:
- ✅ Instala todas las dependencias del sistema
- ✅ Crea entorno virtual Python
- ✅ Instala dependencias Python
- ✅ Configura Nginx
- ✅ Configura Supervisor
- ✅ Inicializa la base de datos
- ✅ Inicia la aplicación

### 6. Configurar Variables de Entorno en Producción

```bash
sudo nano /var/www/invagro/.env
```

Actualiza con valores de producción:
```env
FLASK_ENV=production
SECRET_KEY=genera-una-clave-secreta-muy-larga-y-aleatoria
DB_PASSWORD=tu-password-real
```

Genera una clave secreta segura:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 7. Reiniciar Servicios

```bash
sudo supervisorctl restart invagro
sudo systemctl restart nginx
```

### 8. Verificar que Todo Funciona

```bash
# Ver logs
sudo tail -f /var/log/invagro/error.log

# Verificar estado
sudo supervisorctl status invagro
```

Accede a tu aplicación:
```
http://tu-ip-servidor
```

## 🔒 Configurar SSL/HTTPS (Recomendado)

### Opción 1: Con Dominio (Let's Encrypt)

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx

# Obtener certificado
sudo certbot --nginx -d tu-dominio.com

# Renovación automática
sudo certbot renew --dry-run
```

### Opción 2: Sin Dominio (Certificado Auto-firmado)

```bash
# Generar certificado
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/invagro.key \
  -out /etc/ssl/certs/invagro.crt

# Actualizar configuración de Nginx
sudo nano /etc/nginx/sites-available/invagro
```

Agregar:
```nginx
server {
    listen 443 ssl;
    ssl_certificate /etc/ssl/certs/invagro.crt;
    ssl_certificate_key /etc/ssl/private/invagro.key;
    # ... resto de configuración
}
```

## 🔧 Comandos Útiles

### Gestión de la Aplicación

```bash
# Ver logs en tiempo real
sudo tail -f /var/log/invagro/error.log
sudo tail -f /var/log/invagro/access.log

# Estado de la aplicación
sudo supervisorctl status invagro

# Reiniciar aplicación
sudo supervisorctl restart invagro

# Detener aplicación
sudo supervisorctl stop invagro

# Iniciar aplicación
sudo supervisorctl start invagro
```

### Gestión de Nginx

```bash
# Verificar configuración
sudo nginx -t

# Reiniciar Nginx
sudo systemctl restart nginx

# Ver logs de Nginx
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### Base de Datos

```bash
# Conectar a MySQL
mysql -h tu-host -P 3306 -u dbluis -p invagro

# Ver tablas
SHOW TABLES;

# Ver usuarios
SELECT * FROM `inva-usuarios`;
```

## 🐛 Troubleshooting

### Error: No se puede conectar a la base de datos

**Solución:**
1. Verifica las credenciales en `.env`
2. Verifica que tu servidor esté en la lista blanca de AWS RDS
3. Verifica el security group de RDS

```bash
# Probar conexión
mysql -h tu-host -P 3306 -u dbluis -p
```

### Error: 502 Bad Gateway

**Solución:**
```bash
# Verificar que Gunicorn esté corriendo
sudo supervisorctl status invagro

# Ver logs
sudo tail -f /var/log/invagro/error.log

# Reiniciar
sudo supervisorctl restart invagro
```

### Error: Permission Denied

**Solución:**
```bash
# Ajustar permisos
sudo chown -R www-data:www-data /var/www/invagro
sudo chmod -R 755 /var/www/invagro
```

### Error: ModuleNotFoundError

**Solución:**
```bash
# Reinstalar dependencias
cd /var/www/invagro
source venv/bin/activate
pip install -r requirements.txt
```

## 📊 Monitoreo

### Logs Importantes

```bash
# Logs de la aplicación
/var/log/invagro/error.log
/var/log/invagro/access.log

# Logs de Nginx
/var/log/nginx/error.log
/var/log/nginx/access.log

# Logs de Supervisor
/var/log/supervisor/supervisord.log
```

### Verificar Recursos

```bash
# Uso de CPU y memoria
htop

# Espacio en disco
df -h

# Procesos de Python
ps aux | grep python
```

## 🔐 Seguridad

### Checklist de Seguridad

- [ ] Cambiar contraseña del usuario admin
- [ ] Configurar HTTPS/SSL
- [ ] Actualizar SECRET_KEY en producción
- [ ] Configurar firewall (UFW)
- [ ] Mantener sistema actualizado
- [ ] Hacer backups regulares de la BD
- [ ] Limitar acceso SSH
- [ ] Configurar fail2ban

### Cambiar Contraseña Admin

```python
# Conectar a Python shell
cd /var/www/invagro
source venv/bin/activate
python

# En Python:
from app import create_app
from models import db
from models.database import Usuario

app = create_app('production')
with app.app_context():
    admin = Usuario.query.filter_by(username='admin').first()
    admin.set_password('nueva-password-segura')
    db.session.commit()
    print("Contraseña actualizada!")
```

## 📞 Soporte

Si encuentras problemas:

1. Revisa los logs: `sudo tail -f /var/log/invagro/error.log`
2. Verifica el estado: `sudo supervisorctl status invagro`
3. Consulta la documentación en README.md
4. Contacta al equipo de desarrollo

---

**¡Éxito con tu deployment!** 🎉
