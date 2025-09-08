# Tests para Login API

Este directorio contiene varios archivos para probar la funcionalidad de login de la API.

## 📁 Archivos de Testing

### 🧪 Tests Automatizados

#### `test_login_simple.py` - Tests Básicos (Recomendado)
- **Descripción**: Tests usando unittest nativo de Python
- **Dependencias**: Solo `requests` (ya instalado)
- **Ejecución**: `python test_login_simple.py`
- **Características**:
  - ✅ No requiere instalaciones adicionales
  - ✅ Tests completos de login (exitoso/fallido)
  - ✅ Validación de estructura de respuesta
  - ✅ Tests de rendimiento
  - ✅ Reporte detallado de resultados

#### `test_login_api.py` - Tests Avanzados (Opcional)
- **Descripción**: Tests usando pytest (framework más avanzado)
- **Dependencias**: `pytest`, `requests`
- **Instalación**: `pip install -r requirements_test.txt`
- **Ejecución**: `pytest test_login_api.py -v`
- **Características**:
  - ✅ Framework de testing más potente
  - ✅ Mejores reportes y fixtures
  - ✅ Tests parametrizados
  - ✅ Cobertura de código

### 🎮 Tests Manuales

#### `manual_login_test.py` - Tester Interactivo
- **Descripción**: Script interactivo para probar login manualmente
- **Ejecución**: `python manual_login_test.py`
- **Características**:
  - 🎯 Modo interactivo para ingresar credenciales
  - 🧪 Tests predefinidos automatizados
  - 📊 Reporte detallado de respuestas
  - ⏱️ Medición de tiempos de respuesta

### ⚙️ Configuración

#### `setup_tests.bat` - Script de Configuración (Windows)
- **Descripción**: Instala dependencias automáticamente
- **Ejecución**: Doble clic o `setup_tests.bat`

#### `requirements_test.txt` - Dependencias de Testing
- **Descripción**: Lista de paquetes para tests avanzados
- **Instalación**: `pip install -r requirements_test.txt`

#### `pytest.ini` - Configuración de Pytest
- **Descripción**: Configuración para pytest
- **Uso**: Automático cuando ejecutas pytest

## 🚀 Cómo Usar

### Opción 1: Tests Rápidos (Recomendado)

```bash
# 1. Instalar dependencias básicas
pip install requests

# 2. Iniciar servidor Django
python manage.py runserver

# 3. En otra terminal, ejecutar tests
python test_login_simple.py
```

### Opción 2: Tests Avanzados

```bash
# 1. Instalar dependencias completas
pip install -r requirements_test.txt

# 2. Iniciar servidor Django
python manage.py runserver

# 3. En otra terminal, ejecutar tests con pytest
pytest test_login_api.py -v
```

### Opción 3: Tests Manuales/Interactivos

```bash
# 1. Iniciar servidor Django
python manage.py runserver

# 2. En otra terminal, ejecutar tester manual
python manual_login_test.py
```

## 📋 Tests Incluidos

### ✅ Tests de Login Exitoso
- Login de paciente
- Login de doctor  
- Login de familiar
- Verificación de estructura de respuesta
- Validación de permisos

### ❌ Tests de Login Fallido
- Contraseña incorrecta
- Usuario inexistente
- Campos faltantes (email/password)
- Campos vacíos
- JSON inválido

### 🔍 Tests de Validación
- Estructura de respuesta JSON
- Campos requeridos en respuesta
- Tipos de datos correctos
- Información de permisos

### ⚡ Tests de Rendimiento
- Tiempo de respuesta del login
- Múltiples intentos consecutivos

### 🎯 Tests de Casos Edge
- Emails en mayúsculas/minúsculas
- Caracteres especiales
- Longitud de campos

## 📊 Salida de Ejemplo

```
🧪 EJECUTANDO TESTS DE LOGIN API
============================================================

🔐 Test: Login exitoso paciente
✅ Login paciente exitoso: Paciente UnitTest

🔐 Test: Login exitoso doctor  
✅ Login doctor exitoso: Dr. UnitTest

🔐 Test: Login con contraseña incorrecta
✅ Login con contraseña incorrecta rechazado correctamente

============================================================
RESUMEN DE TESTS
============================================================
Tests ejecutados: 10
Tests exitosos: 10
Tests fallidos: 0
Errores: 0

Tasa de éxito: 100.0%
🎉 ¡TODOS LOS TESTS PASARON!
```

## 🔧 Troubleshooting

### Servidor no responde
```bash
❌ Error conectando al servidor: Connection refused
```
**Solución**: Verifica que Django esté ejecutándose en `localhost:8000`

### Dependencias faltantes
```bash
❌ Error: requests no está instalado
```
**Solución**: `pip install requests`

### Tests fallan por datos
```bash
❌ Error registrando usuario: Email ya está en uso
```
**Solución**: Los tests manejan esto automáticamente, es normal.

### JSON de respuesta inválido
```bash
❌ Error decodificando JSON
```
**Solución**: Verifica que el endpoint `/auth/login/` esté configurado correctamente.

## 📚 Próximos Pasos

1. **Autenticación JWT**: Agregar tests para tokens
2. **Tests de Sesión**: Validar persistencia de sesión  
3. **Tests de Seguridad**: Rate limiting, brute force
4. **Tests de Integración**: Login + operaciones posteriores
5. **Tests de Carga**: Performance con múltiples usuarios

## 🤝 Contribuir

Para agregar nuevos tests:

1. **Tests simples**: Agregar métodos a `TestLoginAPI` en `test_login_simple.py`
2. **Tests avanzados**: Agregar a `test_login_api.py` con pytest
3. **Tests manuales**: Extender `manual_login_test.py`

### Convenciones
- Nombres de test: `test_XX_descripcion_del_test`
- Mensajes informativos con emojis
- Asserts claros con mensajes de error
- Cleanup automático de datos de prueba
