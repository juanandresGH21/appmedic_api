# Implementación del Patrón Factory Method con Permisos Diferenciados

## Resumen

Esta implementación utiliza el patrón Factory Method para crear diferentes tipos de usuarios (paciente, familiar, médico) con métodos y permisos específicos según su rol.

## Arquitectura

### 1. Factory Method Pattern

```python
# Factory abstracta
class UserFactory(ABC):
    @abstractmethod
    def create_user(self, email, password, name, **kwargs):
        pass

# Factories concretas
class PatientFactory(UserFactory)
class FamilyMemberFactory(UserFactory)
class DoctorFactory(UserFactory)

# Factory Context
class UserCreationService
```

### 2. Modelos Principales

#### User (BaseModel)
- Modelo principal de usuario con métodos específicos por tipo
- Campos: email, password_hash, name, user_type, timezone, created_at
- Métodos específicos:
  - `get_my_caregivers()` - Solo pacientes
  - `get_my_schedules()` - Solo pacientes
  - `get_my_patients()` - Solo doctores y familiares
  - `can_view_patient_data()` - Control de permisos
  - `can_manage_schedules()` - Control de permisos

#### DoctorPatientRelation
- Relaciona doctores con pacientes
- Campos: doctor, patient, specialty, notes, is_active

#### FamilyPatientRelation
- Relaciona familiares con pacientes
- Campos: family_member, patient, relationship_type, can_manage_medications, can_view_medical_data, emergency_contact

## Permisos por Tipo de Usuario

### Paciente
- ✅ Ver sus propios cuidadores (familiares y doctores)
- ✅ Ver sus propias programaciones de medicamentos
- ✅ Ver sus propios datos médicos
- ❌ Ver otros pacientes
- ❌ Gestionar medicamentos de otros

### Doctor
- ✅ Ver lista de sus pacientes asignados
- ✅ Ver y gestionar programaciones de sus pacientes
- ✅ Ver datos médicos de sus pacientes
- ❌ Ver pacientes no asignados
- ❌ Acceder a métodos de paciente

### Familiar
- ✅ Ver lista de pacientes bajo su cuidado
- ✅ Ver programaciones de sus pacientes (si tiene permisos)
- ✅ Gestionar medicamentos (si `can_manage_medications=True`)
- ❌ Ver pacientes no relacionados
- ❌ Acceder a métodos de paciente

## API Endpoints

### Autenticación y Registro
```
POST /api/users/register/
GET  /api/users/permissions/
```

### Endpoints para Pacientes
```
GET /api/patient/caregivers/      # Ver mis cuidadores
GET /api/patient/schedules/       # Ver mis programaciones
```

### Endpoints para Cuidadores
```
GET /api/caregiver/patients/                           # Ver mis pacientes
GET /api/caregiver/patient/{patient_id}/schedules/     # Ver programaciones de un paciente
```

### Gestión
```
POST /api/assign-caregiver/       # Asignar cuidador a paciente
DELETE /api/remove-caregiver/     # Remover cuidador de paciente
GET /api/patient/{patient_id}/relations/  # Listar todas las relaciones de un paciente
POST /api/demo/create-sample-users/  # Crear datos de ejemplo
```

## Ejemplos de Uso

### 1. Crear Usuarios con Factory Method

```python
# Crear paciente
patient = UserCreationService.create_user(
    user_type='patient',
    email='paciente@example.com',
    password='password123',
    name='Juan Pérez'
)

# Crear doctor
doctor = UserCreationService.create_user(
    user_type='doctor',
    email='doctor@example.com',
    password='password123',
    name='Dr. María García'
)

# Crear familiar
family = UserCreationService.create_user(
    user_type='family',
    email='familiar@example.com',
    password='password123',
    name='Ana Pérez'
)
```

### 2. Establecer Relaciones

```python
# Asignar doctor a paciente
doctor_relation = UserCreationService.assign_doctor_to_patient(
    doctor_user_id=doctor.id,
    patient_user_id=patient.id,
    specialty="Medicina General",
    notes="Paciente nuevo"
)

# Asignar familiar a paciente
family_relation = UserCreationService.assign_family_to_patient(
    family_user_id=family.id,
    patient_user_id=patient.id,
    relationship_type="spouse",
    can_manage_medications=True,
    emergency_contact=True
)
```

### 3. Usar Métodos Específicos

```python
# Paciente ve sus cuidadores
caregivers = patient.get_my_caregivers()
print(f"Familiares: {caregivers['family_members']}")
print(f"Doctores: {caregivers['doctors']}")

# Doctor ve sus pacientes
patients = doctor.get_my_patients()
for p in patients:
    schedules = doctor.get_patient_schedules(p.id)
    print(f"Paciente: {p.name}, Programaciones: {schedules.count()}")

# Familiar ve sus pacientes
patients = family.get_my_patients()
for p in patients:
    can_manage = family.can_manage_schedules(p.id)
    print(f"Paciente: {p.name}, Puede gestionar: {can_manage}")
```

### 4. API Requests

```bash
# Registrar usuario
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_type": "patient",
    "email": "nuevo@example.com",
    "password": "password123",
    "name": "Nuevo Usuario"
  }'

# Ver mis cuidadores (como paciente)
curl -X GET http://localhost:8000/api/patient/caregivers/ \
  -H "User-ID: {patient_id}"

# Ver mis pacientes (como doctor)
curl -X GET http://localhost:8000/api/caregiver/patients/ \
  -H "User-ID: {doctor_id}"

# Asignar familiar a paciente
curl -X POST http://localhost:8000/api/assign-caregiver/ \
  -H "Content-Type: application/json" \
  -H "User-ID: {doctor_id}" \
  -d '{
    "caregiver_type": "family",
    "caregiver_id": "{family_id}",
    "patient_id": "{patient_id}",
    "relationship_type": "parent",
    "can_manage_medications": true,
    "emergency_contact": true
  }'

# Remover cuidador de paciente
curl -X DELETE http://localhost:8000/api/remove-caregiver/ \
  -H "Content-Type: application/json" \
  -H "User-ID: {doctor_id}" \
  -d '{
    "caregiver_type": "family",
    "caregiver_id": "{family_id}",
    "patient_id": "{patient_id}"
  }'

# Listar todas las relaciones de un paciente
curl -X GET http://localhost:8000/api/patient/{patient_id}/relations/ \
  -H "User-ID: {doctor_id}"
```

## Nuevas Funcionalidades Agregadas

### Gestión de Asignaciones de Cuidadores

#### 1. Remover Cuidadores
- **Endpoint**: `DELETE /api/remove-caregiver/`
- **Permisos**: Solo doctores pueden remover cuidadores
- **Validaciones**:
  - No se puede remover al único doctor de un paciente
  - Verificación de permisos sobre el paciente
  - Validación de existencia de la relación

#### 2. Listar Relaciones de Pacientes
- **Endpoint**: `GET /api/patient/{patient_id}/relations/`
- **Permisos**: Solo usuarios con acceso al paciente
- **Información devuelta**:
  - Lista completa de familiares con permisos
  - Lista completa de doctores con especialidades
  - Metadatos de cada relación

#### 3. Métodos en UserCreationService
- `remove_family_from_patient()`: Remover familiar de paciente
- `remove_doctor_from_patient()`: Remover doctor de paciente (con validaciones)
- `get_patient_relations()`: Obtener todas las relaciones de un paciente

### Ejemplos de Uso

#### Remover Familiar
```python
# Usando el servicio
result = UserCreationService.remove_family_from_patient(
    family_user_id=family_id,
    patient_user_id=patient_id
)

# Via API
DELETE /api/remove-caregiver/
{
    "caregiver_type": "family",
    "caregiver_id": "family_uuid",
    "patient_id": "patient_uuid"
}
```

#### Remover Doctor (con validaciones)
```python
# Usando el servicio
try:
    result = UserCreationService.remove_doctor_from_patient(
        doctor_user_id=doctor_id,
        patient_user_id=patient_id
    )
except ValueError as e:
    print(f"Error: {e}")  # "No se puede remover al único doctor"

# Via API
DELETE /api/remove-caregiver/
{
    "caregiver_type": "doctor",
    "caregiver_id": "doctor_uuid", 
    "patient_id": "patient_uuid"
}
```

#### Listar Relaciones
```python
# Usando el servicio
relations = UserCreationService.get_patient_relations(patient_id)
print(f"Total cuidadores: {relations['total_caregivers']}")

# Via API
GET /api/patient/{patient_id}/relations/
# Respuesta:
{
    "success": true,
    "patient": {...},
    "relations": {
        "family_members": [...],
        "doctors": [...]
    },
    "can_manage_relations": true
}
```

### Validaciones de Seguridad

1. **Protección del último doctor**: No se puede eliminar al único doctor de un paciente
2. **Verificación de permisos**: Solo usuarios autorizados pueden gestionar relaciones
3. **Validación de existencia**: Se verifica que la relación exista antes de eliminar
4. **Logs de auditoría**: Se registra información de la relación eliminada

## Ventajas de esta Implementación

1. **Desacoplamiento**: El Factory Method permite crear usuarios sin acoplar el código a clases concretas
2. **Extensibilidad**: Fácil agregar nuevos tipos de usuario registrando nuevas factories
3. **Seguridad**: Sistema de permisos robusto que previene acceso no autorizado
4. **Mantenibilidad**: Lógica de permisos centralizada en el modelo User
5. **Escalabilidad**: Fácil agregar nuevas relaciones y permisos

## Configuración y Uso

### 1. Configurar Django
```bash
# Crear migraciones
python manage.py makemigrations api

# Aplicar migraciones
python manage.py migrate

# Crear superusuario (opcional)
python manage.py createsuperuser
```

### 2. Configurar URLs
En `config/urls.py`:
```python
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls_permissions')),
]
```

### 3. Probar la API
```bash
# Ejecutar servidor
python manage.py runserver

# Crear usuarios de ejemplo
curl -X POST http://localhost:8000/api/demo/create-sample-users/
```

## Extensiones Futuras

1. **Autenticación JWT**: Implementar autenticación real en lugar del header User-ID
2. **Roles adicionales**: Agregar enfermeros, administradores, etc.
3. **Permisos granulares**: Sistema de permisos más detallado
4. **Notificaciones**: Sistema de notificaciones según el tipo de usuario
5. **Auditoría**: Log de acciones según permisos
