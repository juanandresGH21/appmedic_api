import os
# from dotenv import load_dotenv

# Cargar variables de entorno
# load_dotenv()
from pathlib import Path

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = Path(__file__).resolve().parent.parent

# Obtener el ambiente actual (por defecto 'local')
DJANGO_ENV = os.getenv('DJANGO_ENV', 'local')

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

SQLITE = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

POSTGRESQL = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', ''),
        'USER': os.getenv('DB_USER', ''),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', ''),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

if DJANGO_ENV != 'local':
    print(f"🗄️  PostgreSQL Config:")
    print(f"   DB_NAME: {os.getenv('DB_NAME', 'NOT SET')}")
    print(f"   DB_USER: {os.getenv('DB_USER', 'NOT SET')}")
    print(f"   DB_HOST: {os.getenv('DB_HOST', 'NOT SET')}")
    print(f"   DB_PORT: {os.getenv('DB_PORT', 'NOT SET')}")

# Seleccionar base de datos según el ambiente
if DJANGO_ENV == 'local':
    DATABASES = SQLITE
    print("Using SQLite database for local environment")
else:
    DATABASES = POSTGRESQL
    print("Using PostgreSQL database for production/testing environment")