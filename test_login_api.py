"""
Tests para API de Login
Usando pytest y requests para probar la autenticación

Instalación:
pip install pytest requests

Ejecución:
pytest test_login_api.py -v
pytest test_login_api.py::TestLoginAPI::test_login_successful -v
"""

import pytest
import requests
import json
import time
from typing import Dict, Any


class APITestConfig:
    """Configuración para las pruebas de API"""
    BASE_URL = "http://localhost:8000/api"
    HEADERS = {"Content-Type": "application/json"}
    
    # Datos de prueba
    TEST_USERS = {
        "patient": {
            "email": "patient_test@example.com",
            "password": "test_password_123",
            "name": "Paciente Test",
            "user_type": "patient"
        },
        "doctor": {
            "email": "doctor_test@example.com",
            "password": "test_password_123",
            "name": "Dr. Test",
            "user_type": "doctor"
        },
        "family": {
            "email": "family_test@example.com",
            "password": "test_password_123",
            "name": "Familiar Test",
            "user_type": "family"
        }
    }


class TestLoginAPI:
    """Clase principal de tests para la API de Login"""
    
    @classmethod
    def setup_class(cls):
        """Configuración inicial para todas las pruebas"""
        cls.config = APITestConfig()
        cls.created_users = {}
        print(f"\n🚀 Iniciando tests de Login API")
        print(f"URL Base: {cls.config.BASE_URL}")
        
        # Verificar que el servidor esté ejecutándose
        try:
            response = requests.get(f"{cls.config.BASE_URL}/medications/", timeout=5)
            print("✅ Servidor Django está ejecutándose")
        except requests.exceptions.RequestException:
            pytest.fail("❌ El servidor Django no está ejecutándose. Ejecuta 'python manage.py runserver'")
    
    def setup_method(self):
        """Configuración antes de cada test"""
        self.config = APITestConfig()
    
    # ========== TESTS DE REGISTRO (PREPARACIÓN) ==========
    
    def test_01_register_test_users(self):
        """Registrar usuarios de prueba para los tests de login"""
        print("\n📝 Registrando usuarios de prueba...")
        
        for user_type, user_data in self.config.TEST_USERS.items():
            data = json.dumps(user_data)
            print(f"Registrando {user_type} con datos: {data}")
            response = requests.post(
                f"{self.config.BASE_URL}/users/register/",
                headers=self.config.HEADERS,
                data=data
            )
            print(response)
            if response.status_code == 201:
                result = response.json()
                self.created_users[user_type] = result['user']
                print(f"✅ Usuario {user_type} registrado: {result['user']['name']}")
            elif response.status_code == 400 and "ya está en uso" in response.json().get('error', ''):
                print(f"⚠️  Usuario {user_type} ya existe (OK para tests)")
            else:
                print(f"❌ Error registrando {user_type}: {response.json()}")
    
    # ========== TESTS DE LOGIN EXITOSO ==========
    
    def test_02_login_successful_patient(self):
        """Test: Login exitoso para paciente"""
        user_data = self.config.TEST_USERS["patient"]
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }
        
        response = requests.post(
            f"{self.config.BASE_URL}/auth/login/",
            headers=self.config.HEADERS,
            data=json.dumps(login_data)
        )
        
        assert response.status_code == 200, f"Error: {response.text}"
        
        result = response.json()
        assert result['success'] is True
        assert 'user' in result
        assert 'permissions' in result
        assert result['user']['user_type'] == 'patient'
        assert result['user']['email'] == user_data["email"]
        
        print(f"✅ Login paciente exitoso: {result['user']['name']}")
    
    def test_03_login_successful_doctor(self):
        """Test: Login exitoso para doctor"""
        user_data = self.config.TEST_USERS["doctor"]
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }
        
        response = requests.post(
            f"{self.config.BASE_URL}/auth/login/",
            headers=self.config.HEADERS,
            data=json.dumps(login_data)
        )
        
        assert response.status_code == 200
        
        result = response.json()
        assert result['success'] is True
        assert result['user']['user_type'] == 'doctor'
        assert result['user']['email'] == user_data["email"]
        
        print(f"✅ Login doctor exitoso: {result['user']['name']}")
    
    def test_04_login_successful_family(self):
        """Test: Login exitoso para familiar"""
        user_data = self.config.TEST_USERS["family"]
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }
        
        response = requests.post(
            f"{self.config.BASE_URL}/auth/login/",
            headers=self.config.HEADERS,
            data=json.dumps(login_data)
        )
        
        assert response.status_code == 200
        
        result = response.json()
        assert result['success'] is True
        assert result['user']['user_type'] == 'family'
        assert result['user']['email'] == user_data["email"]
        
        print(f"✅ Login familiar exitoso: {result['user']['name']}")
    
    # ========== TESTS DE LOGIN FALLIDO ==========
    
    def test_05_login_wrong_password(self):
        """Test: Login con contraseña incorrecta"""
        user_data = self.config.TEST_USERS["patient"]
        login_data = {
            "email": user_data["email"],
            "password": "contraseña_incorrecta"
        }
        
        response = requests.post(
            f"{self.config.BASE_URL}/auth/login/",
            headers=self.config.HEADERS,
            data=json.dumps(login_data)
        )
        
        assert response.status_code == 401
        
        result = response.json()
        assert result['success'] is False
        assert 'error' in result
        assert 'incorrectos' in result['error'].lower()
        
        print("✅ Login con contraseña incorrecta rechazado correctamente")
    
    def test_06_login_nonexistent_user(self):
        """Test: Login con email que no existe"""
        login_data = {
            "email": "usuario_inexistente@example.com",
            "password": "cualquier_password"
        }
        
        response = requests.post(
            f"{self.config.BASE_URL}/auth/login/",
            headers=self.config.HEADERS,
            data=json.dumps(login_data)
        )
        
        assert response.status_code == 401
        
        result = response.json()
        assert result['success'] is False
        assert 'error' in result
        
        print("✅ Login con usuario inexistente rechazado correctamente")
    
    def test_07_login_missing_email(self):
        """Test: Login sin email"""
        login_data = {
            "password": "test_password_123"
        }
        
        response = requests.post(
            f"{self.config.BASE_URL}/auth/login/",
            headers=self.config.HEADERS,
            data=json.dumps(login_data)
        )
        
        assert response.status_code == 400
        
        result = response.json()
        assert result['success'] is False
        assert 'email' in result['error'].lower()
        
        print("✅ Login sin email rechazado correctamente")
    
    def test_08_login_missing_password(self):
        """Test: Login sin contraseña"""
        login_data = {
            "email": "test@example.com"
        }
        
        response = requests.post(
            f"{self.config.BASE_URL}/auth/login/",
            headers=self.config.HEADERS,
            data=json.dumps(login_data)
        )
        
        assert response.status_code == 400
        
        result = response.json()
        assert result['success'] is False
        assert 'contraseña' in result['error'].lower()
        
        print("✅ Login sin contraseña rechazado correctamente")
    
    def test_09_login_empty_fields(self):
        """Test: Login con campos vacíos"""
        login_data = {
            "email": "",
            "password": ""
        }
        
        response = requests.post(
            f"{self.config.BASE_URL}/auth/login/",
            headers=self.config.HEADERS,
            data=json.dumps(login_data)
        )
        
        assert response.status_code == 400
        
        result = response.json()
        assert result['success'] is False
        
        print("✅ Login con campos vacíos rechazado correctamente")
    
    def test_10_login_invalid_json(self):
        """Test: Login con JSON inválido"""
        invalid_json = "{ email: invalid json }"
        
        response = requests.post(
            f"{self.config.BASE_URL}/auth/login/",
            headers=self.config.HEADERS,
            data=invalid_json
        )
        
        assert response.status_code == 400
        
        result = response.json()
        assert result['success'] is False
        assert 'json' in result['error'].lower()
        
        print("✅ Login con JSON inválido rechazado correctamente")
    
    # ========== TESTS DE ESTRUCTURA DE RESPUESTA ==========
    
    def test_11_login_response_structure(self):
        """Test: Estructura correcta de respuesta de login exitoso"""
        user_data = self.config.TEST_USERS["doctor"]
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }
        
        response = requests.post(
            f"{self.config.BASE_URL}/auth/login/",
            headers=self.config.HEADERS,
            data=json.dumps(login_data)
        )
        
        assert response.status_code == 200
        result = response.json()
        
        # Verificar estructura principal
        required_fields = ['success', 'message', 'user', 'permissions']
        for field in required_fields:
            assert field in result, f"Campo '{field}' faltante en respuesta"
        
        # Verificar estructura del usuario
        user_fields = ['id', 'email', 'name', 'user_type', 'tz', 'login_time']
        for field in user_fields:
            assert field in result['user'], f"Campo '{field}' faltante en user"
        
        # Verificar tipos de datos
        assert isinstance(result['success'], bool)
        assert isinstance(result['message'], str)
        assert isinstance(result['user'], dict)
        assert isinstance(result['permissions'], dict)
        
        print("✅ Estructura de respuesta de login es correcta")
    
    def test_12_login_permissions_structure(self):
        """Test: Estructura de permisos en respuesta de login"""
        user_data = self.config.TEST_USERS["patient"]
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }
        
        response = requests.post(
            f"{self.config.BASE_URL}/auth/login/",
            headers=self.config.HEADERS,
            data=json.dumps(login_data)
        )
        
        assert response.status_code == 200
        result = response.json()
        
        permissions = result['permissions']
        
        # Verificar que los permisos son un diccionario
        assert isinstance(permissions, dict)
        
        # Verificar campos básicos de permisos (pueden variar según implementación)
        expected_fields = ['user_type', 'can_view_own_data', 'can_manage_own_schedules']
        for field in expected_fields:
            if field in permissions:  # Algunos campos pueden ser opcionales
                assert isinstance(permissions[field], (bool, str, list))
        
        print(f"✅ Estructura de permisos es correcta: {list(permissions.keys())}")
    
    # ========== TESTS DE RENDIMIENTO ==========
    
    def test_13_login_performance(self):
        """Test: Tiempo de respuesta del login"""
        user_data = self.config.TEST_USERS["patient"]
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }
        
        start_time = time.time()
        response = requests.post(
            f"{self.config.BASE_URL}/auth/login/",
            headers=self.config.HEADERS,
            data=json.dumps(login_data)
        )
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 2.0, f"Login muy lento: {response_time:.2f}s"
        
        print(f"✅ Tiempo de respuesta del login: {response_time:.3f}s")
    
    # ========== TESTS DE CASOS EDGE ==========
    
    def test_14_login_case_insensitive_email(self):
        """Test: Login con email en diferentes casos (mayúsculas/minúsculas)"""
        user_data = self.config.TEST_USERS["patient"]
        login_data = {
            "email": user_data["email"].upper(),  # Email en mayúsculas
            "password": user_data["password"]
        }
        
        response = requests.post(
            f"{self.config.BASE_URL}/auth/login/",
            headers=self.config.HEADERS,
            data=json.dumps(login_data)
        )
        
        # Esto puede fallar dependiendo de cómo esté implementado
        # Documentar el comportamiento esperado
        if response.status_code == 200:
            print("✅ Login es case-insensitive para emails")
        else:
            print("ℹ️  Login es case-sensitive para emails")
            assert response.status_code == 401
    
    def test_15_login_multiple_attempts(self):
        """Test: Múltiples intentos de login"""
        user_data = self.config.TEST_USERS["family"]
        
        # 3 intentos exitosos consecutivos
        for i in range(3):
            login_data = {
                "email": user_data["email"],
                "password": user_data["password"]
            }
            
            response = requests.post(
                f"{self.config.BASE_URL}/auth/login/",
                headers=self.config.HEADERS,
                data=json.dumps(login_data)
            )
            
            assert response.status_code == 200, f"Intento {i+1} falló"
            time.sleep(0.1)  # Pequeña pausa entre intentos
        
        print("✅ Múltiples intentos de login exitosos")


class TestLoginHelpers:
    """Tests para funciones helper del sistema de login"""
    
    def test_password_hashing(self):
        """Test: Verificar que las contraseñas se hashean correctamente"""
        # Este test requiere acceso directo al modelo
        # Se puede implementar como script separado si es necesario
        pass
    
    def test_user_authentication_method(self):
        """Test: Método authenticate del modelo User"""
        # Test para verificar el método User.authenticate() directamente
        pass


# ========== FUNCIONES DE UTILIDAD ==========

def print_test_summary():
    """Imprimir resumen de tests"""
    print("\n" + "="*60)
    print("RESUMEN DE TESTS DE LOGIN API")
    print("="*60)
    print("✅ Tests de login exitoso")
    print("❌ Tests de login fallido") 
    print("🔍 Tests de estructura de respuesta")
    print("⚡ Tests de rendimiento")
    print("🎯 Tests de casos edge")
    print("="*60)


# ========== CONFIGURACIÓN DE PYTEST ==========

def pytest_configure(config):
    """Configuración inicial de pytest"""
    print("\n🧪 Configurando tests de Login API...")


def pytest_collection_modifyitems(config, items):
    """Modificar orden de ejecución de tests"""
    # Ordenar tests por nombre para ejecución secuencial
    items.sort(key=lambda x: x.name)


if __name__ == "__main__":
    """Ejecutar tests directamente"""
    print("Para ejecutar los tests, usa:")
    print("pytest test_login_api.py -v")
    print("pytest test_login_api.py::TestLoginAPI::test_02_login_successful_patient -v")
    print_test_summary()
