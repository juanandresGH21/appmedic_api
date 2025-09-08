# Advanced Factory Pattern - Django REST Framework v2

## Arquitectura de la Nueva Factory

### 🏗️ **Estructura del Patrón**

```
UserServiceInterface (ABC)
├── PatientService
├── DoctorService
└── FamilyService

UserServiceFactory (Factory Principal)
```

### 🎯 **Principales Mejoras**

1. **Servicios Específicos por Usuario**: Cada tipo tiene su propio servicio con métodos personalizados
2. **Manejo de Permisos**: Validación automática según el tipo de usuario
3. **Métodos Contextuales**: Funcionalidades que solo están disponibles para ciertos tipos
4. **Integración DRF**: Diseñado específicamente para Django REST Framework

---

## 📋 **Métodos por Tipo de Usuario**

### 👤 **PatientService**
| Método | Disponible | Descripción |
|--------|------------|-------------|
| `create_user` | ✅ | Crear paciente |
| `get_my_caregivers` | ✅ | Ver sus cuidadores |
| `get_patient_schedules` | ✅ | Ver sus propios schedules |
| `can_view_patient_data` | ✅ | Solo sus propios datos |
| `can_manage_schedules` | ✅ | Solo sus propios schedules |
| `remove_caregiver` | ❌ | `PermissionDenied` |
| `assign_caregiver` | ❌ | `PermissionDenied` |
| `get_my_patients` | ❌ | `NotImplementedError` |

### 👨‍⚕️ **DoctorService**
| Método | Disponible | Descripción |
|--------|------------|-------------|
| `create_user` | ✅ | Crear doctor |
| `get_my_patients` | ✅ | Ver sus pacientes asignados |
| `get_patient_schedules` | ✅ | Ver schedules de pacientes |
| `assign_caregiver` | ✅ | Asignar doctores/familiares |
| `remove_caregiver` | ✅ | Remover cuidadores |
| `can_view_patient_data` | ✅ | Pacientes asignados |
| `can_manage_schedules` | ✅ | Pacientes asignados |
| `get_my_caregivers` | ❌ | `NotImplementedError` |

### 👨‍👩‍👧‍👦 **FamilyService**
| Método | Disponible | Descripción |
|--------|------------|-------------|
| `create_user` | ✅ | Crear familiar |
| `get_my_patients` | ✅ | Ver pacientes asignados |
| `get_patient_schedules` | ✅ | Ver schedules según permisos |
| `can_view_patient_data` | ✅ | Según relación |
| `can_manage_schedules` | ✅ | Según `can_manage_medications` |
| `remove_caregiver` | ❌ | `PermissionDenied` |
| `assign_caregiver` | ❌ | `PermissionDenied` |
| `get_my_caregivers` | ❌ | `NotImplementedError` |

---

## 🔗 **Nuevos Endpoints**

### 1. Registro Avanzado con Permisos
**POST** `/api/v2/advanced/users/register/`

```json
{
    "user_type": "doctor",
    "email": "doctor@example.com",
    "password": "password123",
    "name": "Dr. Juan Pérez"
}
```

**Response:**
```json
{
    "success": true,
    "user": {
        "id": "1",
        "email": "doctor@example.com",
        "name": "Dr. Juan Pérez",
        "user_type": "doctor",
        "timezone": "America/Bogota"
    },
    "permissions": {
        "user_type": "doctor",
        "can_assign_caregivers": true,
        "can_manage_patient_schedules": true,
        "patients": [],
        "total_patients": 0
    }
}
```

### 2. Gestión Avanzada de Cuidadores
**POST** `/api/v2/advanced/caregivers/manage/`

**Headers:** `User-ID: 2` (Doctor)

```json
{
    "caregiver_id": 3,
    "patient_id": 1,
    "caregiver_type": "family",
    "relationship_type": "spouse",
    "can_manage_medications": true,
    "emergency_contact": true
}
```

### 3. Permisos Detallados por Usuario
**GET** `/api/v2/advanced/users/permissions/`

**Headers:** `User-ID: 1`

**Response para Familiar:**
```json
{
    "success": true,
    "permissions": {
        "user_type": "family",
        "can_view_patients": true,
        "can_assign_caregivers": false,
        "patients": [
            {
                "id": "1",
                "name": "María García",
                "permissions": {
                    "can_manage_medications": true,
                    "emergency_contact": true,
                    "relationship_type": "spouse"
                }
            }
        ],
        "permissions_by_patient": {
            "1": {
                "can_manage_medications": true,
                "can_view_medical_data": true,
                "emergency_contact": true,
                "relationship_type": "spouse"
            }
        }
    }
}
```

### 4. Schedules por Servicio Específico
**POST** `/api/v2/advanced/patients/schedules/`

**Headers:** `User-ID: 2` (Doctor o Familiar)

```json
{
    "patient_id": 1
}
```

### 5. Ejecución Genérica de Métodos
**POST** `/api/v2/advanced/users/execute-method/`

```json
{
    "method_name": "get_my_patients",
    "args": [],
    "kwargs": {}
}
```

---

## 🔄 **Comparación: Factory Original vs Avanzada**

### **Factory Original (UserCreationService)**
```python
# Método genérico para todos
UserCreationService.get_user_permissions(user_id)

# Sin validación específica por tipo
UserCreationService.assign_family_to_patient(...)
```

### **Factory Avanzada (UserServiceFactory)**
```python
# Servicio específico por tipo
service = UserServiceFactory.get_service('doctor')
permissions = service.get_user_permissions(user_id)

# Validación automática por tipo de usuario
service.assign_caregiver(doctor_id, family_id, 'family', ...)
# ☝️ Solo funciona si el usuario es doctor
```

---

## 🛡️ **Manejo de Errores Mejorado**

### **Errores Específicos por Contexto**

```python
# Paciente intenta asignar cuidador
{
    "success": false,
    "error": "Los pacientes no pueden asignar cuidadores por sí mismos"
}

# Familiar intenta ver schedules sin permisos
{
    "success": false,
    "error": "No tienes permisos para ver este paciente"
}

# Método no disponible
{
    "success": false,
    "error": "Método no disponible para family: Los familiares no tienen cuidadores asignados"
}
```

---

## 🧪 **Ejemplos de Uso**

### **Caso 1: Doctor asigna Familiar a Paciente**
```bash
# 1. Doctor se autentica
curl -X POST http://localhost:8000/api/v2/advanced/caregivers/manage/ \
  -H "User-ID: 2" \
  -H "Content-Type: application/json" \
  -d '{
    "caregiver_id": 3,
    "patient_id": 1,
    "caregiver_type": "family",
    "relationship_type": "child",
    "can_manage_medications": false,
    "emergency_contact": true
  }'
```

### **Caso 2: Familiar ve sus pacientes**
```bash
curl -X POST http://localhost:8000/api/v2/advanced/users/execute-method/ \
  -H "User-ID: 3" \
  -H "Content-Type: application/json" \
  -d '{
    "method_name": "get_my_patients"
  }'
```

### **Caso 3: Paciente intenta asignar cuidador (Error esperado)**
```bash
curl -X POST http://localhost:8000/api/v2/advanced/caregivers/manage/ \
  -H "User-ID: 1" \
  -H "Content-Type: application/json" \
  -d '{
    "caregiver_id": 2,
    "patient_id": 1,
    "caregiver_type": "doctor"
  }'

# Response: 403 Forbidden
# "Los pacientes no pueden asignar cuidadores por sí mismos"
```

---

## 🚀 **Ventajas de la Factory Avanzada**

1. **Seguridad por Diseño**: Cada tipo de usuario solo puede hacer lo que le corresponde
2. **Código Más Limpio**: Lógica específica en servicios específicos
3. **Extensibilidad**: Fácil agregar nuevos tipos de usuario o métodos
4. **Testing**: Cada servicio se puede probar independientemente
5. **Documentación**: Métodos claramente definidos por tipo
6. **DRF Nativo**: Diseñado desde cero para REST Framework

---

## 🔧 **Próximas Implementaciones Sugeridas**

1. **Autenticación JWT**:
   ```python
   class JWTPermissionMixin:
       def get_user_from_jwt(self, request):
           # Implementar JWT auth
   ```

2. **Servicios Adicionales**:
   ```python
   class AdminService(UserServiceInterface):
       # Permisos de super usuario
   
   class NurseService(UserServiceInterface):
       # Permisos de enfermera
   ```

3. **Logging Avanzado**:
   ```python
   def assign_caregiver(self, user_id, caregiver_id, caregiver_type, **kwargs):
       logger.info(f"Doctor {user_id} asignando {caregiver_type} {caregiver_id}")
       # ... lógica
   ```

4. **Caché de Permisos**:
   ```python
   @cached_property
   def get_user_permissions(self, user_id):
       # Cache para permisos frecuentemente consultados
   ```

¿Te gustaría que implemente alguna de estas funcionalidades adicionales o tienes preguntas sobre la factory avanzada?
