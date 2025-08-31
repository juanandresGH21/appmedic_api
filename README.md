# API de Gestión Médica con Factory Method Pattern

## Descripción

Esta API REST implementa un sistema de gestión médica utilizando el patrón Factory Method para la creación de usuarios con diferentes roles y permisos. El sistema permite gestionar pacientes, doctores, familiares, medicamentos y schedules de medicación.

## Arquitectura

### Factory Method Pattern

La aplicación implementa el patrón Factory Method para la creación de usuarios:

```
UserFactory (Abstract)
├── PatientFactory
├── DoctorFactory
└── FamilyMemberFactory
```

Cada factory crea usuarios con métodos y permisos específicos según su tipo.

### Modelos Principales

- **User**: Modelo base con diferentes tipos (patient, doctor, family)
- **DoctorPatientRelation**: Relación entre doctores y pacientes
- **FamilyPatientRelation**: Relación entre familiares y pacientes
- **Medication**: Medicamentos del sistema
- **Schedule**: Programación de medicamentos
- **Intake**: Registro de tomas de medicamentos

## Endpoints de la API

### 1. Gestión de Usuarios

#### POST /api/register/
Registra un nuevo usuario en el sistema.

**Body:**
```json
{
  "user_type": "patient|doctor|family",
  "email": "usuario@example.com",
  "password": "password123",
  "name": "Nombre Completo"
}
```

**Respuesta exitosa (201):**
```json
{
  "success": true,
  "message": "Usuario registrado exitosamente",
  "user": {
    "id": 1,
    "email": "usuario@example.com",
    "name": "Nombre Completo",
    "user_type": "patient",
    "created_at": "2024-01-01T10:00:00Z"
  }
}
```

### 2. Gestión de Cuidadores

#### POST /api/assign-doctor/
Asigna un doctor a un paciente.

**Body:**
```json
{
  "doctor_user_id": 2,
  "patient_user_id": 1,
  "specialty": "Medicina General"
}
```

#### POST /api/assign-family/
Asigna un familiar a un paciente.

**Body:**
```json
{
  "family_user_id": 3,
  "patient_user_id": 1,
  "relationship_type": "spouse|parent|child|sibling|other",
  "can_manage_medications": true,
  "emergency_contact": true
}
```

#### DELETE /api/remove-caregiver/
Remueve la asignación de un cuidador.

**Body:**
```json
{
  "doctor_user_id": 2,
  "patient_user_id": 1
}
```
O para familiares:
```json
{
  "family_user_id": 3,
  "patient_user_id": 1
}
```

### 3. Gestión de Medicamentos

#### GET /api/medications/
Lista todos los medicamentos.

#### POST /api/medications/
Crea un nuevo medicamento.

**Body:**
```json
{
  "name": "Aspirina",
  "form": "tablet|capsule|liquid|injection|drops|cream",
  "created_by": 2
}
```

#### PUT /api/medications/{id}/
Actualiza un medicamento existente.

#### DELETE /api/medications/{id}/
Elimina un medicamento.

### 4. Gestión de Schedules

#### GET /api/schedules/
Lista schedules. Filtrable por paciente.

**Query Parameters:**
- `patient_id`: ID del paciente para filtrar

#### POST /api/schedules/
Crea un nuevo schedule de medicación.

**Body:**
```json
{
  "user_id": 1,
  "medication_id": 1,
  "start_date": "2024-01-01",
  "end_date": "2024-01-31",
  "pattern": "daily_8am|daily_12pm|daily_8pm|twice_daily|three_times_daily|weekly|as_needed",
  "dose_amount": "100mg",
  "created_by_user_id": 2
}
```

#### GET /api/schedules/{id}/
Obtiene detalles de un schedule específico.

#### PUT /api/schedules/{id}/
Actualiza un schedule existente.

**Body:**
```json
{
  "dose_amount": "150mg",
  "pattern": "daily_12pm",
  "end_date": "2024-02-28",
  "user_id": 2
}
```

#### DELETE /api/schedules/{id}/
Elimina un schedule.

**Body:**
```json
{
  "user_id": 2
}
```

## Sistema de Permisos

### Permisos por Tipo de Usuario

#### Paciente
- `can_view_patient_data(patient_id)`: Solo sus propios datos
- `can_manage_schedules(patient_id)`: Solo sus propios schedules
- `get_my_schedules()`: Ver sus schedules
- `get_my_medications()`: Ver sus medicamentos

#### Doctor
- `can_view_patient_data(patient_id)`: Pacientes asignados
- `can_manage_schedules(patient_id)`: Pacientes asignados
- `get_assigned_patients()`: Lista de pacientes asignados
- `get_patient_schedules(patient_id)`: Schedules de pacientes asignados

#### Familiar
- `can_view_patient_data(patient_id)`: Pacientes relacionados
- `can_manage_schedules(patient_id)`: Solo si `can_manage_medications=True`
- `get_related_patients()`: Lista de pacientes relacionados
- `get_patient_schedules(patient_id)`: Schedules de pacientes relacionados

### Validaciones de Permisos

1. **Creación de Schedules**: Solo doctores asignados o familiares con permisos
2. **Actualización de Schedules**: Solo quien tiene permisos sobre el paciente
3. **Eliminación de Schedules**: Solo quien tiene permisos sobre el paciente
4. **Visualización de Datos**: Solo usuarios autorizados

## Códigos de Estado HTTP

- **200**: Operación exitosa
- **201**: Recurso creado exitosamente
- **400**: Error en los datos enviados
- **403**: Sin permisos para realizar la operación
- **404**: Recurso no encontrado
- **500**: Error interno del servidor

## Respuestas de Error

Formato estándar de respuestas de error:

```json
{
  "success": false,
  "error": "Descripción del error",
  "details": "Detalles adicionales (opcional)"
}
```

## Ejemplos de Uso

### Flujo Básico

1. **Registrar usuarios**:
   ```bash
   # Registrar paciente
   curl -X POST http://localhost:8000/api/register/ \
     -H "Content-Type: application/json" \
     -d '{"user_type": "patient", "email": "paciente@example.com", "password": "123", "name": "Juan Pérez"}'
   
   # Registrar doctor
   curl -X POST http://localhost:8000/api/register/ \
     -H "Content-Type: application/json" \
     -d '{"user_type": "doctor", "email": "doctor@example.com", "password": "123", "name": "Dr. Ana López"}'
   ```

2. **Asignar doctor a paciente**:
   ```bash
   curl -X POST http://localhost:8000/api/assign-doctor/ \
     -H "Content-Type: application/json" \
     -d '{"doctor_user_id": 2, "patient_user_id": 1, "specialty": "Medicina General"}'
   ```

3. **Crear medicamento**:
   ```bash
   curl -X POST http://localhost:8000/api/medications/ \
     -H "Content-Type: application/json" \
     -d '{"name": "Aspirina", "form": "tablet", "created_by": 2}'
   ```

4. **Crear schedule**:
   ```bash
   curl -X POST http://localhost:8000/api/schedules/ \
     -H "Content-Type: application/json" \
     -d '{"user_id": 1, "medication_id": 1, "start_date": "2024-01-01", "pattern": "daily_8am", "dose_amount": "100mg", "created_by_user_id": 2}'
   ```

## Instalación y Configuración

### Requisitos
- Python 3.8+
- Django 4.0+
- Django REST Framework

### Instalación

1. **Clonar el repositorio**:
   ```bash
   git clone <repo-url>
   cd backend
   ```

2. **Crear entorno virtual**:
   ```bash
   python -m venv env
   # Windows
   env\Scripts\activate
   # Linux/Mac
   source env/bin/activate
   ```

3. **Instalar dependencias**:
   ```bash
   pip install django djangorestframework
   ```

4. **Ejecutar migraciones**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Ejecutar servidor**:
   ```bash
   python manage.py runserver
   ```

### Configuración de Base de Datos

El proyecto está configurado para usar SQLite por defecto. Para cambiar a PostgreSQL:

1. Instalar psycopg2: `pip install psycopg2`
2. Actualizar `settings.py`:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'medical_app',
           'USER': 'your_user',
           'PASSWORD': 'your_password',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```

## Pruebas

### Ejecutar Ejemplos

1. **Ejemplos del ORM**:
   ```bash
   python manage.py shell < schedule_management_examples.py
   ```

2. **Ejemplos de API REST**:
   ```bash
   # Asegúrate de que el servidor esté ejecutándose
   python api_rest_examples.py
   ```

### Estructura de Pruebas

```
backend/
├── schedule_management_examples.py  # Ejemplos de uso del ORM
├── api_rest_examples.py            # Ejemplos de APIs REST
└── api/
    ├── models.py                   # Modelos y Factory Pattern
    ├── views.py                    # Vistas de la API
    ├── urls.py                     # URLs de la API
    └── tests.py                    # Pruebas unitarias
```

## Patrones de Diseño Implementados

### Factory Method
- **UserFactory**: Factory abstracto para crear usuarios
- **Concrete Factories**: PatientFactory, DoctorFactory, FamilyMemberFactory
- **Product**: User con diferentes comportamientos según el tipo

### Service Layer
- **UserCreationService**: Servicio para gestionar operaciones complejas
- Encapsula lógica de negocio y validaciones
- Mantiene consistencia en las operaciones

### Repository Pattern
- Métodos específicos en cada tipo de usuario
- Abstracción de consultas a la base de datos
- Encapsulación de lógica de acceso a datos

## Próximos Pasos

1. **Autenticación**: Implementar JWT o Session-based authentication
2. **Paginación**: Agregar paginación a las listas de recursos
3. **Filtros**: Implementar filtros avanzados en las APIs
4. **Notificaciones**: Sistema de recordatorios para medicamentos
5. **Histórico**: Tracking de cambios en schedules
6. **Validaciones**: Validaciones más robustas en formularios
7. **Tests**: Pruebas unitarias y de integración completas
8. **Documentation**: Swagger/OpenAPI documentation
9. **Deployment**: Configuración para producción

## Contribución

Para contribuir al proyecto:

1. Fork del repositorio
2. Crear rama para la feature: `git checkout -b feature/nueva-funcionalidad`
3. Commit de cambios: `git commit -am 'Agregar nueva funcionalidad'`
4. Push a la rama: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

## Licencia

[Especificar licencia del proyecto]
