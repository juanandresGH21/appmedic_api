"""
Ejemplos de uso de las APIs REST para gestionar schedules y medicamentos
Usar con herramientas como curl, Postman, o requests de Python
"""

import requests
import json
from datetime import date, timedelta

# Configuración base
BASE_URL = "http://localhost:8000/api"
HEADERS = {"Content-Type": "application/json"}

# Datos de ejemplo que necesitas crear primero
EXAMPLE_DATA = {
    "patient_id": 1,  # Cambiar por ID real del paciente
    "doctor_id": 2,   # Cambiar por ID real del doctor
    "family_id": 3,   # Cambiar por ID real del familiar
    "medication_id": 1  # Cambiar por ID real del medicamento
}

def print_response(response, operation):
    """Imprimir respuesta de la API de forma formateada"""
    print(f"\n--- {operation} ---")
    print(f"Status Code: {response.status_code}")
    if response.content:
        try:
            print(f"Response: {json.dumps(response.json(), indent=2, default=str)}")
        except:
            print(f"Response: {response.text}")
    else:
        print("Response: (empty)")

def register_users():
    """Ejemplos de registro de usuarios"""
    print("=== 1. REGISTRO DE USUARIOS ===")
    
    # Registrar paciente
    patient_data = {
        "user_type": "patient",
        "email": "paciente_api@example.com",
        "password": "password123",
        "name": "Juan API Test"
    }
    response = requests.post(f"{BASE_URL}/register/", 
                           json=patient_data, headers=HEADERS)
    print_response(response, "Registro de Paciente")
    
    # Registrar doctor
    doctor_data = {
        "user_type": "doctor",
        "email": "doctor_api@example.com",
        "password": "password123",
        "name": "Dr. Ana API Test"
    }
    response = requests.post(f"{BASE_URL}/register/", 
                           json=doctor_data, headers=HEADERS)
    print_response(response, "Registro de Doctor")
    
    # Registrar familiar
    family_data = {
        "user_type": "family",
        "email": "family_api@example.com",
        "password": "password123",
        "name": "María API Test (Esposa)"
    }
    response = requests.post(f"{BASE_URL}/register/", 
                           json=family_data, headers=HEADERS)
    print_response(response, "Registro de Familiar")

def manage_caregivers():
    """Ejemplos de gestión de cuidadores"""
    print("\n=== 2. GESTIÓN DE CUIDADORES ===")
    
    # Asignar doctor a paciente
    doctor_assignment = {
        "doctor_user_id": EXAMPLE_DATA["doctor_id"],
        "patient_user_id": EXAMPLE_DATA["patient_id"],
        "specialty": "Medicina General"
    }
    response = requests.post(f"{BASE_URL}/assign-doctor/", 
                           json=doctor_assignment, headers=HEADERS)
    print_response(response, "Asignación de Doctor")
    
    # Asignar familiar a paciente
    family_assignment = {
        "family_user_id": EXAMPLE_DATA["family_id"],
        "patient_user_id": EXAMPLE_DATA["patient_id"],
        "relationship_type": "spouse",
        "can_manage_medications": True,
        "emergency_contact": True
    }
    response = requests.post(f"{BASE_URL}/assign-family/", 
                           json=family_assignment, headers=HEADERS)
    print_response(response, "Asignación de Familiar")
    
    # Remover doctor
    doctor_removal = {
        "doctor_user_id": EXAMPLE_DATA["doctor_id"],
        "patient_user_id": EXAMPLE_DATA["patient_id"]
    }
    response = requests.delete(f"{BASE_URL}/remove-caregiver/", 
                             json=doctor_removal, headers=HEADERS)
    print_response(response, "Remoción de Doctor")

def manage_medications():
    """Ejemplos de gestión de medicamentos"""
    print("\n=== 3. GESTIÓN DE MEDICAMENTOS ===")
    
    # Crear medicamento
    medication_data = {
        "name": "Aspirina API Test",
        "form": "tablet",
        "created_by": EXAMPLE_DATA["doctor_id"]
    }
    response = requests.post(f"{BASE_URL}/medications/", 
                           json=medication_data, headers=HEADERS)
    print_response(response, "Creación de Medicamento")
    
    # Listar medicamentos
    response = requests.get(f"{BASE_URL}/medications/")
    print_response(response, "Lista de Medicamentos")
    
    # Actualizar medicamento (ID de ejemplo: 1)
    medication_update = {
        "name": "Aspirina Actualizada",
        "form": "capsule"
    }
    response = requests.put(f"{BASE_URL}/medications/1/", 
                          json=medication_update, headers=HEADERS)
    print_response(response, "Actualización de Medicamento")
    
    # Eliminar medicamento
    response = requests.delete(f"{BASE_URL}/medications/1/")
    print_response(response, "Eliminación de Medicamento")

def manage_schedules():
    """Ejemplos de gestión de schedules"""
    print("\n=== 4. GESTIÓN DE SCHEDULES ===")
    
    # Crear schedule
    schedule_data = {
        "user_id": EXAMPLE_DATA["patient_id"],
        "medication_id": EXAMPLE_DATA["medication_id"],
        "start_date": str(date.today()),
        "end_date": str(date.today() + timedelta(days=30)),
        "pattern": "daily_8am",
        "dose_amount": "100mg",
        "created_by_user_id": EXAMPLE_DATA["doctor_id"]
    }
    response = requests.post(f"{BASE_URL}/schedules/", 
                           json=schedule_data, headers=HEADERS)
    print_response(response, "Creación de Schedule")
    
    # Listar schedules del paciente
    response = requests.get(f"{BASE_URL}/schedules/?patient_id={EXAMPLE_DATA['patient_id']}")
    print_response(response, "Lista de Schedules del Paciente")
    
    # Actualizar schedule (ID de ejemplo: 1)
    schedule_update = {
        "dose_amount": "150mg",
        "pattern": "daily_12pm",
        "user_id": EXAMPLE_DATA["doctor_id"]
    }
    response = requests.put(f"{BASE_URL}/schedules/1/", 
                          json=schedule_update, headers=HEADERS)
    print_response(response, "Actualización de Schedule")
    
    # Obtener detalles de un schedule específico
    response = requests.get(f"{BASE_URL}/schedules/1/")
    print_response(response, "Detalles de Schedule")
    
    # Eliminar schedule
    delete_data = {
        "user_id": EXAMPLE_DATA["doctor_id"]
    }
    response = requests.delete(f"{BASE_URL}/schedules/1/", 
                             json=delete_data, headers=HEADERS)
    print_response(response, "Eliminación de Schedule")

def demonstrate_error_cases():
    """Ejemplos de casos de error y validaciones"""
    print("\n=== 5. CASOS DE ERROR Y VALIDACIONES ===")
    
    # Intentar crear schedule sin permisos
    unauthorized_schedule = {
        "user_id": EXAMPLE_DATA["patient_id"],
        "medication_id": EXAMPLE_DATA["medication_id"],
        "start_date": str(date.today()),
        "pattern": "daily",
        "dose_amount": "100mg",
        "created_by_user_id": 999  # Usuario inexistente
    }
    response = requests.post(f"{BASE_URL}/schedules/", 
                           json=unauthorized_schedule, headers=HEADERS)
    print_response(response, "Schedule sin Permisos (Error Esperado)")
    
    # Intentar actualizar schedule inexistente
    response = requests.put(f"{BASE_URL}/schedules/999/", 
                          json={"dose_amount": "200mg", "user_id": EXAMPLE_DATA["doctor_id"]}, 
                          headers=HEADERS)
    print_response(response, "Actualizar Schedule Inexistente (Error Esperado)")
    
    # Intentar eliminar schedule sin permisos
    response = requests.delete(f"{BASE_URL}/schedules/1/", 
                             json={"user_id": 999}, 
                             headers=HEADERS)
    print_response(response, "Eliminar Schedule sin Permisos (Error Esperado)")

# Ejemplos de uso con curl (comentados para referencia)
CURL_EXAMPLES = """
# EJEMPLOS CON CURL

# 1. Registrar paciente
curl -X POST http://localhost:8000/api/register/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "user_type": "patient",
    "email": "paciente_curl@example.com",
    "password": "password123",
    "name": "Juan Curl Test"
  }'

# 2. Asignar doctor a paciente
curl -X POST http://localhost:8000/api/assign-doctor/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "doctor_user_id": 2,
    "patient_user_id": 1,
    "specialty": "Medicina General"
  }'

# 3. Crear medicamento
curl -X POST http://localhost:8000/api/medications/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "name": "Aspirina Curl",
    "form": "tablet",
    "created_by": 2
  }'

# 4. Crear schedule
curl -X POST http://localhost:8000/api/schedules/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "user_id": 1,
    "medication_id": 1,
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "pattern": "daily_8am",
    "dose_amount": "100mg",
    "created_by_user_id": 2
  }'

# 5. Listar schedules del paciente
curl -X GET "http://localhost:8000/api/schedules/?patient_id=1"

# 6. Actualizar schedule
curl -X PUT http://localhost:8000/api/schedules/1/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "dose_amount": "150mg",
    "pattern": "daily_12pm",
    "user_id": 2
  }'

# 7. Eliminar schedule
curl -X DELETE http://localhost:8000/api/schedules/1/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "user_id": 2
  }'

# 8. Remover cuidador
curl -X DELETE http://localhost:8000/api/remove-caregiver/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "doctor_user_id": 2,
    "patient_user_id": 1
  }'
"""

def main():
    """Función principal para ejecutar ejemplos"""
    print("EJEMPLOS DE APIs REST PARA GESTIÓN DE SCHEDULES")
    print("=" * 60)
    print("NOTA: Asegúrate de que el servidor Django esté ejecutándose en localhost:8000")
    print("NOTA: Actualiza los IDs en EXAMPLE_DATA con valores reales de tu base de datos")
    print()
    
    try:
        # Ejecutar ejemplos (comentado para evitar errores sin servidor)
        # register_users()
        # manage_caregivers()
        # manage_medications()
        # manage_schedules()
        # demonstrate_error_cases()
        
        print("Para ejecutar los ejemplos reales:")
        print("1. Inicia el servidor Django: python manage.py runserver")
        print("2. Actualiza los IDs en EXAMPLE_DATA")
        print("3. Descomenta las llamadas a las funciones en main()")
        print("4. Ejecuta: python api_rest_examples.py")
        
        print(CURL_EXAMPLES)
        
    except Exception as e:
        print(f"Error: {e}")
        print("Asegúrate de que el servidor Django esté ejecutándose")

if __name__ == "__main__":
    main()
