"""
Ejemplos de uso de las APIs para gestionar asignaciones de cuidadores
"""

import requests
import json

# Configuración base
BASE_URL = "http://localhost:8000/api"

def example_api_calls():
    """Ejemplos de llamadas a la API para gestión de cuidadores"""
    
    print("=== EJEMPLOS DE GESTIÓN DE CUIDADORES ===\n")
    
    # 1. Crear usuarios de ejemplo
    print("1. Creando usuarios de ejemplo...")
    response = requests.post(f"{BASE_URL}/demo/create-sample-users/")
    if response.status_code == 200:
        users_data = response.json()
        print(f"✓ Usuarios creados: {users_data['message']}")
        
        patient_id = users_data['users']['patient']['id']
        doctor_id = users_data['users']['doctor']['id']
        family_id = users_data['users']['family']['id']
        
        print(f"  - Paciente ID: {patient_id}")
        print(f"  - Doctor ID: {doctor_id}")
        print(f"  - Familiar ID: {family_id}")
    else:
        print(f"✗ Error creando usuarios: {response.text}")
        return
    
    # 2. Listar relaciones del paciente
    print(f"\n2. Listando relaciones del paciente...")
    response = requests.get(
        f"{BASE_URL}/patient/{patient_id}/relations/",
        headers={'User-ID': doctor_id}
    )
    if response.status_code == 200:
        relations_data = response.json()
        print("✓ Relaciones obtenidas:")
        print(f"  - Familiares: {len(relations_data['relations']['family_members'])}")
        print(f"  - Doctores: {len(relations_data['relations']['doctors'])}")
        
        for family in relations_data['relations']['family_members']:
            print(f"    * Familiar: {family['caregiver']['name']} ({family['relationship_type']})")
        
        for doctor in relations_data['relations']['doctors']:
            print(f"    * Doctor: {doctor['caregiver']['name']} ({doctor['specialty']})")
    else:
        print(f"✗ Error obteniendo relaciones: {response.text}")
    
    # 3. Crear un familiar adicional y asignarlo
    print(f"\n3. Creando y asignando familiar adicional...")
    
    # Crear nuevo familiar
    new_family_data = {
        "user_type": "family",
        "email": "hermano@example.com",
        "password": "password123",
        "name": "Pedro Pérez"
    }
    
    response = requests.post(
        f"{BASE_URL}/users/register/",
        headers={'Content-Type': 'application/json'},
        data=json.dumps(new_family_data)
    )
    
    if response.status_code == 201:
        new_family = response.json()['user']
        new_family_id = new_family['id']
        print(f"✓ Nuevo familiar creado: {new_family['name']} (ID: {new_family_id})")
        
        # Asignar al paciente
        assign_data = {
            "caregiver_type": "family",
            "caregiver_id": new_family_id,
            "patient_id": patient_id,
            "relationship_type": "sibling",
            "can_manage_medications": False,
            "emergency_contact": False
        }
        
        response = requests.post(
            f"{BASE_URL}/assign-caregiver/",
            headers={
                'Content-Type': 'application/json',
                'User-ID': doctor_id
            },
            data=json.dumps(assign_data)
        )
        
        if response.status_code == 200:
            print(f"✓ Familiar asignado exitosamente")
        else:
            print(f"✗ Error asignando familiar: {response.text}")
    else:
        print(f"✗ Error creando familiar: {response.text}")
        new_family_id = None
    
    # 4. Listar relaciones actualizadas
    print(f"\n4. Listando relaciones actualizadas...")
    response = requests.get(
        f"{BASE_URL}/patient/{patient_id}/relations/",
        headers={'User-ID': doctor_id}
    )
    if response.status_code == 200:
        relations_data = response.json()
        print("✓ Relaciones actualizadas:")
        print(f"  - Familiares: {len(relations_data['relations']['family_members'])}")
        print(f"  - Doctores: {len(relations_data['relations']['doctors'])}")
        
        for family in relations_data['relations']['family_members']:
            print(f"    * {family['caregiver']['name']} ({family['relationship_type']}) - Puede gestionar medicamentos: {family['can_manage_medications']}")
    
    # 5. Remover el familiar recién creado
    if new_family_id:
        print(f"\n5. Removiendo familiar recién creado...")
        
        remove_data = {
            "caregiver_type": "family",
            "caregiver_id": new_family_id,
            "patient_id": patient_id
        }
        
        response = requests.delete(
            f"{BASE_URL}/remove-caregiver/",
            headers={
                'Content-Type': 'application/json',
                'User-ID': doctor_id
            },
            data=json.dumps(remove_data)
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Familiar removido exitosamente:")
            print(f"  - Nombre: {result['relation_info']['caregiver_name']}")
            print(f"  - Relación: {result['relation_info']['relationship_type']}")
            print(f"  - Era contacto de emergencia: {result['relation_info']['was_emergency_contact']}")
        else:
            print(f"✗ Error removiendo familiar: {response.text}")
    
    # 6. Verificar relaciones finales
    print(f"\n6. Verificando relaciones finales...")
    response = requests.get(
        f"{BASE_URL}/patient/{patient_id}/relations/",
        headers={'User-ID': doctor_id}
    )
    if response.status_code == 200:
        relations_data = response.json()
        print("✓ Relaciones finales:")
        print(f"  - Familiares: {len(relations_data['relations']['family_members'])}")
        print(f"  - Doctores: {len(relations_data['relations']['doctors'])}")
    
    # 7. Intentar remover al único doctor (debería fallar)
    print(f"\n7. Intentando remover al único doctor (debería fallar)...")
    
    remove_doctor_data = {
        "caregiver_type": "doctor",
        "caregiver_id": doctor_id,
        "patient_id": patient_id
    }
    
    response = requests.delete(
        f"{BASE_URL}/remove-caregiver/",
        headers={
            'Content-Type': 'application/json',
            'User-ID': doctor_id
        },
        data=json.dumps(remove_doctor_data)
    )
    
    if response.status_code == 400:
        error_data = response.json()
        print(f"✓ Error esperado: {error_data['error']}")
    else:
        print(f"✗ Se esperaba un error pero la operación fue: {response.status_code}")


def example_permission_scenarios():
    """Ejemplos de diferentes escenarios de permisos"""
    
    print("\n=== ESCENARIOS DE PERMISOS ===\n")
    
    # Crear usuarios para los ejemplos
    users = {}
    
    # Crear paciente
    patient_data = {
        "user_type": "patient",
        "email": "paciente_permisos@example.com",
        "password": "password123",
        "name": "Juan Permisos"
    }
    
    response = requests.post(
        f"{BASE_URL}/users/register/",
        headers={'Content-Type': 'application/json'},
        data=json.dumps(patient_data)
    )
    
    if response.status_code == 201:
        users['patient'] = response.json()['user']
        print(f"✓ Paciente creado: {users['patient']['name']}")
    
    # Crear doctor
    doctor_data = {
        "user_type": "doctor",
        "email": "doctor_permisos@example.com", 
        "password": "password123",
        "name": "Dr. Permisos"
    }
    
    response = requests.post(
        f"{BASE_URL}/users/register/",
        headers={'Content-Type': 'application/json'},
        data=json.dumps(doctor_data)
    )
    
    if response.status_code == 201:
        users['doctor'] = response.json()['user']
        print(f"✓ Doctor creado: {users['doctor']['name']}")
    
    # Crear familiar
    family_data = {
        "user_type": "family",
        "email": "familiar_permisos@example.com",
        "password": "password123",
        "name": "Ana Permisos"
    }
    
    response = requests.post(
        f"{BASE_URL}/users/register/",
        headers={'Content-Type': 'application/json'},
        data=json.dumps(family_data)
    )
    
    if response.status_code == 201:
        users['family'] = response.json()['user']
        print(f"✓ Familiar creado: {users['family']['name']}")
    
    if len(users) < 3:
        print("✗ No se pudieron crear todos los usuarios necesarios")
        return
    
    # Establecer relación doctor-paciente
    assign_doctor_data = {
        "caregiver_type": "doctor",
        "caregiver_id": users['doctor']['id'],
        "patient_id": users['patient']['id'],
        "specialty": "Medicina General"
    }
    
    response = requests.post(
        f"{BASE_URL}/assign-caregiver/",
        headers={
            'Content-Type': 'application/json',
            'User-ID': users['doctor']['id']
        },
        data=json.dumps(assign_doctor_data)
    )
    
    print(f"Asignación doctor-paciente: {response.status_code}")
    
    # Escenario 1: Familiar intenta remover doctor (debería fallar)
    print(f"\n1. Familiar intenta remover doctor (debería fallar)...")
    
    remove_data = {
        "caregiver_type": "doctor",
        "caregiver_id": users['doctor']['id'],
        "patient_id": users['patient']['id']
    }
    
    response = requests.delete(
        f"{BASE_URL}/remove-caregiver/",
        headers={
            'Content-Type': 'application/json',
            'User-ID': users['family']['id']  # Usando ID del familiar
        },
        data=json.dumps(remove_data)
    )
    
    if response.status_code == 403:
        print(f"✓ Error esperado: {response.json()['error']}")
    else:
        print(f"✗ Se esperaba error 403, pero se obtuvo: {response.status_code}")
    
    # Escenario 2: Paciente intenta ver relaciones de otro paciente (debería fallar)
    print(f"\n2. Paciente intenta ver relaciones de otro paciente...")
    
    response = requests.get(
        f"{BASE_URL}/patient/{users['patient']['id']}/relations/",
        headers={'User-ID': users['family']['id']}  # Familiar sin relación
    )
    
    if response.status_code == 403:
        print(f"✓ Error esperado: {response.json()['error']}")
    else:
        print(f"✗ Se esperaba error 403, pero se obtuvo: {response.status_code}")


if __name__ == "__main__":
    print("EJEMPLOS DE API - GESTIÓN DE CUIDADORES")
    print("=" * 50)
    
    try:
        example_api_calls()
        example_permission_scenarios()
        
    except requests.exceptions.ConnectionError:
        print("✗ Error: No se pudo conectar al servidor.")
        print("Asegúrate de que el servidor Django esté ejecutándose en http://localhost:8000")
    except Exception as e:
        print(f"✗ Error inesperado: {e}")
    
    print("\n" + "=" * 50)
    print("Ejemplos completados.")
