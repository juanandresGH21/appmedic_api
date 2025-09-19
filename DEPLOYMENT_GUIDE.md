# 🚀 Guía de Despliegue - API Django en VM

**Guía completa para montar la API AppMedic en una máquina virtual con PostgreSQL, Nginx y Git**

---

## 📋 Índice

1. [Preparación inicial del servidor](#1-preparación-inicial-del-servidor)
2. [Instalar Python y dependencias](#2-instalar-python-y-dependencias)
3. [Instalar y configurar PostgreSQL](#3-instalar-y-configurar-postgresql)
4. [Instalar y configurar Nginx](#4-instalar-y-configurar-nginx)
5. [Configurar estructura de directorios](#5-configurar-estructura-de-directorios)
6. [Clonar y configurar el proyecto](#6-clonar-y-configurar-el-proyecto)
7. [Instalar dependencias del proyecto](#7-instalar-dependencias-del-proyecto)
8. [Configurar variables de entorno](#8-configurar-variables-de-entorno)
9. [Configurar Django para producción](#9-configurar-django-para-producción)
10. [Migrar base de datos](#10-migrar-base-de-datos)
11. [Configurar Gunicorn](#11-configurar-gunicorn)
12. [Configurar Nginx](#12-configurar-nginx)
13. [Configurar SSL con Let's Encrypt](#13-configurar-ssl-con-lets-encrypt)
14. [Configurar Firewall](#14-configurar-firewall)
15. [Scripts de monitoreo y mantenimiento](#15-scripts-de-monitoreo-y-mantenimiento)
16. [Verificar instalación](#16-verificar-instalación)
17. [Comandos útiles para mantenimiento](#17-comandos-útiles-para-mantenimiento)

---

## 🖥️ 1. Preparación inicial del servidor

### Actualizar el sistema:

```bash
sudo apt update && sudo apt upgrade -y
```

### Instalar dependencias básicas:

```bash
sudo apt install -y curl wget git vim software-properties-common apt-transport-https ca-certificates gnupg lsb-release
```

---

## 🐍 2. Instalar Python y dependencias

```bash
# Instalar Python 3.10+ y pip
sudo apt install -y python3 python3-pip python3-venv python3-dev

# Verificar versión
python3 --version
```

---

## 🗄️ 3. Instalar y configurar PostgreSQL

### Instalar PostgreSQL:

```bash
sudo apt install -y postgresql postgresql-contrib libpq-dev
```

### Configurar PostgreSQL:

```bash
# Cambiar a usuario postgres
sudo -u postgres psql
```

Dentro de PostgreSQL ejecutar:

```sql
CREATE DATABASE appmedic_db;
CREATE USER appmedic_user WITH PASSWORD '';
GRANT ALL PRIVILEGES ON DATABASE appmedic_db TO appmedic_user;
ALTER USER appmedic_user CREATEDB;
ALTER USER postgres WITH PASSWORD '';


-- Otorgar permisos completos sobre el esquema public
GRANT ALL PRIVILEGES ON SCHEMA public TO appmedic_user;

-- Otorgar permisos para crear tablas
GRANT CREATE ON SCHEMA public TO appmedic_user;

-- Otorgar permisos sobre todas las tablas existentes y futuras
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO appmedic_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO appmedic_user;

-- Establecer permisos por defecto para objetos futuros
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO appmedic_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO appmedic_user;

-- Hacer al usuario propietario del esquema (recomendado)
ALTER SCHEMA public OWNER TO appmedic_user;
\q
```

### Configurar acceso remoto (opcional):

```bash
# Editar configuración
sudo vim /etc/postgresql/14/main/postgresql.conf
```

Cambiar la línea:
```
listen_addresses = 'localhost'
```
Por:
```
listen_addresses = '*'
```

Editar autenticación:

```bash
sudo vim /etc/postgresql/14/main/pg_hba.conf
```

Agregar línea:
```
host    all             all             0.0.0.0/0               md5
```

Reiniciar PostgreSQL:

```bash
sudo systemctl restart postgresql
sudo systemctl enable postgresql
```

---

## 🌐 4. Instalar y configurar Nginx

```bash
# Instalar Nginx
sudo apt install -y nginx

# Habilitar Nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Verificar estado
sudo systemctl status nginx
```

---

## 📁 5. Configurar estructura de directorios

```bash
# Crear usuario para la aplicación
sudo adduser appmedic

# Cambiar a usuario appmedic
sudo su - appmedic

# Crear directorios
mkdir -p ~/apps/appmedic_api
cd ~/apps/appmedic_api
```

---

## 📥 6. Clonar y configurar el proyecto

```bash
# Clonar repositorio
git clone https://github.com/juanandresGH21/appmedic_api.git .

# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate

# Actualizar pip
pip install --upgrade pip
```

---

## 📦 7. Instalar dependencias del proyecto

```bash
# Instalar dependencias básicas
pip install django djangorestframework python-dateutil psycopg2-binary gunicorn python-dotenv django-cors-headers PyJWT

# Si tienes requirements.txt:
pip install -r requirements.txt
```

---

## ⚙️ 8. Configurar variables de entorno

```bash
# Crear archivo .env
vim .env
```

**Contenido del archivo `.env`:**

```env
DJANGO_ENV=production
DEBUG=False
SECRET_KEY=tu_secret_key_muy_seguro_aqui_cambia_esto
ALLOWED_HOSTS=tu_dominio.com,tu_ip_servidor

# Base de datos
DB_NAME=appmedic_db
DB_USER=appmedic_user
DB_PASSWORD=tu_password_seguro
DB_HOST=localhost
DB_PORT=5432

# Auth0 (si usas)
AUTH0_DOMAIN=tu_dominio.auth0.com
AUTH0_CLIENT_ID=tu_client_id
AUTH0_CLIENT_SECRET=tu_client_secret
```

---

## 🔧 9. Configurar Django para producción

### Actualizar `config/settings.py`:

```python
# Al final de config/settings.py
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración de producción
if os.getenv('DJANGO_ENV') == 'production':
    DEBUG = False
    ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')
    
    # Configuración de base de datos PostgreSQL
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME'),
            'USER': os.getenv('DB_USER'),
            'PASSWORD': os.getenv('DB_PASSWORD'),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '5432'),
        }
    }
    
    # Configuración de archivos estáticos
    STATIC_URL = '/static/'
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    
    # Configuración de medios
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
    
    # Configuración de seguridad
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    
    # CORS para producción
    CORS_ALLOWED_ORIGINS = [
        "https://tu_dominio_frontend.com",
        "http://localhost:3000",  # Para desarrollo
    ]
```

---

## 🗃️ 10. Migrar base de datos

```bash
# Hacer migraciones
python manage.py makemigrations
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Recopilar archivos estáticos
python manage.py collectstatic --noinput
```

---

## 🔥 11. Configurar Gunicorn

### Crear archivo de configuración:

```bash
vim ~/apps/appmedic_api/gunicorn.conf.py
```

**Contenido:**

```python
# gunicorn.conf.py
bind = "127.0.0.1:8000"
workers = 3
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
user = "appmedic"
group = "appmedic"
```

### Crear servicio systemd:

```bash
sudo vim /etc/systemd/system/appmedic.service
```

**Contenido:**

```ini
[Unit]
Description=AppMedic Django Application
After=network.target

[Service]
User=appmedic
Group=appmedic
WorkingDirectory=/home/appmedic/apps/appmedic_api
Environment="PATH=/home/appmedic/apps/appmedic_api/venv/bin"
ExecStart=/home/appmedic/apps/appmedic_api/venv/bin/gunicorn --config gunicorn.conf.py config.wsgi:application
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### Habilitar servicio:

```bash
sudo systemctl daemon-reload
sudo systemctl start appmedic
sudo systemctl enable appmedic
sudo systemctl status appmedic
```

---

## 🌐 12. Configurar Nginx

### Crear configuración del sitio:

```bash
sudo vim /etc/nginx/sites-available/appmedic
```

**Contenido:**

```nginx
server {
    listen 80;
    server_name tu_dominio.com tu_ip_servidor;

    client_max_body_size 100M;

    # Archivos estáticos
    location /static/ {
        alias /home/appmedic/apps/appmedic_api/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Archivos de medios
    location /media/ {
        alias /home/appmedic/apps/appmedic_api/media/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Proxy a Django
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }

    # Configuración de CORS para API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Headers CORS
        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization,User-ID' always;
        
        if ($request_method = 'OPTIONS') {
            add_header 'Access-Control-Allow-Origin' '*';
            add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS';
            add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization,User-ID';
            add_header 'Access-Control-Max-Age' 1728000;
            add_header 'Content-Type' 'text/plain; charset=utf-8';
            add_header 'Content-Length' 0;
            return 204;
        }
    }
}
```

### Habilitar sitio:

```bash
# Crear enlace simbólico
sudo ln -s /etc/nginx/sites-available/appmedic /etc/nginx/sites-enabled/

# Eliminar sitio por defecto
sudo rm /etc/nginx/sites-enabled/default

# Verificar configuración
sudo nginx -t

# Reiniciar Nginx
sudo systemctl restart nginx
```

---

## 🔒 13. Configurar SSL con Let's Encrypt (Opcional)

```bash
# Instalar Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtener certificado SSL
sudo certbot --nginx -d tu_dominio.com

# Verificar renovación automática
sudo systemctl status certbot.timer
```

---

## 🔥 14. Configurar Firewall

```bash
# Habilitar UFW
sudo ufw enable

# Permitir SSH
sudo ufw allow ssh

# Permitir HTTP y HTTPS
sudo ufw allow 'Nginx Full'

# Permitir PostgreSQL (solo si necesitas acceso externo)
# sudo ufw allow 5432

# Verificar estado
sudo ufw status
```

---

## 📊 15. Scripts de monitoreo y mantenimiento

### Script de backup:

```bash
vim ~/backup_db.sh
```

**Contenido:**

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/appmedic/backups"
mkdir -p $BACKUP_DIR

# Backup de base de datos
PGPASSWORD='tu_password_seguro' pg_dump -U appmedic_user -h localhost appmedic_db > $BACKUP_DIR/appmedic_db_$DATE.sql

# Mantener solo últimos 7 backups
find $BACKUP_DIR -name "appmedic_db_*.sql" -mtime +7 -delete

echo "Backup completado: appmedic_db_$DATE.sql"
```

```bash
chmod +x ~/backup_db.sh

# Agregar a crontab (backup diario a las 2 AM)
crontab -e
# Agregar línea:
0 2 * * * /home/appmedic/backup_db.sh
```

### Script de actualización:

```bash
vim ~/update_app.sh
```

**Contenido:**

```bash
#!/bin/bash
cd ~/apps/appmedic_api

echo "🔄 Actualizando código..."
git pull origin production

echo "🐍 Activando entorno virtual..."
source venv/bin/activate

echo "📦 Instalando dependencias..."
pip install -r requirements.txt

echo "🗃️ Aplicando migraciones..."
python manage.py migrate

echo "📁 Recopilando archivos estáticos..."
python manage.py collectstatic --noinput

echo "🔄 Reiniciando servicio..."
sudo systemctl restart appmedic

echo "✅ Actualización completada"
```

```bash
chmod +x ~/update_app.sh
```

---

## 🧪 16. Verificar instalación

### Verificar servicios:

```bash
# Verificar servicios
sudo systemctl status postgresql
sudo systemctl status nginx
sudo systemctl status appmedic
```

### Verificar logs:

```bash
# Ver logs de la aplicación
sudo journalctl -u appmedic -f

# Ver logs de Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Probar API:

```bash
# Probar endpoint básico
curl http://tu_ip_servidor/api/

# Probar con headers
curl -H "Content-Type: application/json" http://tu_ip_servidor/api/v2/users/
```

---

## 📋 17. Comandos útiles para mantenimiento

### Actualizar código:

```bash
cd ~/apps/appmedic_api
git pull origin production
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart appmedic
```

### Ver logs en tiempo real:

```bash
# Logs de la aplicación
sudo journalctl -u appmedic -f

# Logs de Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Logs de PostgreSQL
sudo tail -f /var/log/postgresql/postgresql-14-main.log
```

### Reiniciar servicios:

```bash
# Reiniciar aplicación
sudo systemctl restart appmedic

# Reiniciar Nginx
sudo systemctl restart nginx

# Reiniciar PostgreSQL
sudo systemctl restart postgresql

# Reiniciar todos
sudo systemctl restart appmedic nginx postgresql
```

### Comandos de Django útiles:

```bash
cd ~/apps/appmedic_api
source venv/bin/activate

# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Shell de Django
python manage.py shell

# Ejecutar tests
python manage.py test

# Recopilar archivos estáticos
python manage.py collectstatic
```

### Monitoreo de recursos:

```bash
# Ver uso de memoria
free -h

# Ver uso de disco
df -h

# Ver procesos
ps aux | grep python
ps aux | grep nginx
ps aux | grep postgres

# Ver conexiones de red
netstat -tulpn | grep :8000
netstat -tulpn | grep :80
netstat -tulpn | grep :5432
```

---

## 🎉 ¡Instalación Completada!

Tu API de Django AppMedic ahora está ejecutándose en:

- **HTTP**: `http://tu_ip_servidor`
- **HTTPS**: `https://tu_dominio.com` (si configuraste SSL)

### URLs importantes:

- **API Base**: `http://tu_ip_servidor/api/v2/`
- **Admin Django**: `http://tu_ip_servidor/admin/`
- **Auth0 Login**: `http://tu_ip_servidor/auth/login/`
- **Admin Users/Schedules**: `http://tu_ip_servidor/api/v2/admin/all-users-schedules/`

### Headers requeridos para algunas APIs:

```bash
# Para endpoints que requieren autenticación
-H "User-ID: {user_id}"

# Para Auth0
-H "Authorization: Bearer {token}"
```

### Ejemplo de prueba completa:

```bash
# Probar endpoint público
curl http://tu_ip_servidor/auth/public/

# Probar endpoint con Auth0 (requiere token válido)
curl -H "Authorization: Bearer tu_token_auth0" http://tu_ip_servidor/auth/private/

# Probar API principal
curl -H "User-ID: 1" http://tu_ip_servidor/api/v2/admin/all-users-schedules/
```

---

## 🆘 Solución de problemas comunes

### La aplicación no inicia:

```bash
# Ver logs detallados
sudo journalctl -u appmedic -n 50

# Verificar configuración de Gunicorn
/home/appmedic/apps/appmedic_api/venv/bin/gunicorn --check-config config.wsgi:application
```

### Error de base de datos:

```bash
# Verificar conexión a PostgreSQL
sudo -u postgres psql -c "SELECT version();"

# Verificar usuario y base de datos
sudo -u postgres psql -c "\l" | grep appmedic
sudo -u postgres psql -c "\du" | grep appmedic
```

### Error 502 Bad Gateway:

```bash
# Verificar que Gunicorn esté corriendo en puerto 8000
netstat -tulpn | grep :8000

# Verificar configuración de Nginx
sudo nginx -t
```

### Problemas de permisos:

```bash
# Corregir permisos de archivos
sudo chown -R appmedic:appmedic /home/appmedic/apps/appmedic_api/
sudo chmod -R 755 /home/appmedic/apps/appmedic_api/
```

---

**¡Tu API AppMedic está lista para producción!** 🚀