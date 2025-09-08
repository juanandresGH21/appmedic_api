@echo off
echo 🧪 CONFIGURANDO ENTORNO DE TESTING PARA LOGIN API
echo ===================================================

echo.
echo 📦 Instalando dependencias básicas...
pip install requests

echo.
echo 🔧 Verificando instalación de Django...
python -c "import django; print(f'Django {django.get_version()} instalado')" 2>nul || (
    echo ❌ Django no encontrado. Instalando...
    pip install django djangorestframework
)

echo.
echo 📋 Dependencias instaladas:
pip list | findstr -i "requests django"

echo.
echo ✅ Configuración completada!
echo.
echo 🚀 Para ejecutar los tests:
echo    1. Inicia el servidor: python manage.py runserver
echo    2. En otra terminal: python test_login_simple.py
echo.
echo 📚 Para tests avanzados con pytest:
echo    pip install -r requirements_test.txt
echo    pytest test_login_api.py -v
echo.

pause
