# Django REST Framework - Endpoints API v2

## Endpoints Implementados

### 1. Registro de Usuarios
**Endpoint:** `POST /api/v2/register/`
**Descripción:** Registra un nuevo usuario usando el Factory Method pattern
**Permisos:** Público (sin autenticación)

#### Request Body:
```json
{
    "user_type": "patient",  // "patient", "doctor", "family"
    "email": "usuario@example.com",
    "password": "password123",
    "name": "Juan Pérez",
    "timezone": "America/Bogota"  // Opcional, por defecto: "America/Bogota"
}
```

#### Response Success (201):
```json
{
    "success": true,
    "user": {
        "id": "1",
        "email": "usuario@example.com",
        "name": "Juan Pérez",
        "user_type": "patient",
        "timezone": "America/Bogota",
        "created_at": "2025-09-08T10:30:00Z"
    },
    "message": "Usuario registrado exitosamente"
}
```

#### Response Error (400):
```json
{
    "success": false,
    "errors": {
        "email": ["El correo electrónico ya está en uso"],
        "password": ["Este campo es obligatorio"]
    }
}
```

### 2. Listar Pacientes por Cuidador
**Endpoint:** `GET /api/v2/caregivers/patients/`
**Descripción:** Lista los pacientes asignados a un doctor o familiar
**Permisos:** Requiere User-ID header

#### Headers:
```
User-ID: 2  // ID del doctor o familiar
```

#### Response Success (200):
```json
{
    "success": true,
    "patients": [
        {
            "id": "1",
            "name": "Juan Pérez",
            "email": "juan@example.com",
            "timezone": "America/Bogota",
            "created_at": "2025-09-08T10:30:00Z",
            "doctors": [
                {
                    "id": "2",
                    "name": "Dr. María García",
                    "email": "maria@example.com",
                    "specialty": "Medicina General"
                }
            ],
            "family_members": [
                {
                    "id": "3",
                    "name": "Ana Pérez",
                    "email": "ana@example.com",
                    "relationship": "spouse",
                    "can_manage_medications": true,
                    "emergency_contact": true
                }
            ],
            "total_schedules": 5
        }
    ],
    "total_patients": 1,
    "caregiver_type": "doctor",
    "caregiver_name": "Dr. María García"
}
```

#### Response Error (403):
```json
{
    "success": false,
    "error": "Solo doctores y familiares pueden acceder a esta información"
}
```

## Ventajas del DRF vs Django Views Normales

### ✅ **Con DRF (Nuevos Endpoints):**

1. **Validación Automática:**
   - Validación de tipos de datos
   - Validación de campos requeridos
   - Validaciones personalizadas en serializers

2. **Serialización Consistente:**
   - Conversión automática modelo → JSON
   - Campos calculados (SerializerMethodField)
   - Relaciones anidadas automáticas

3. **Código Más Limpio:**
   - Menos líneas de código
   - Separación clara: View lógica / Serializer datos
   - Reutilización de serializers

4. **Testing Mejorado:**
   - APITestCase con utilidades específicas
   - Cliente de testing integrado

5. **Documentación Automática:**
   - Browsable API en desarrollo
   - Integración con Swagger/OpenAPI

6. **Manejo de Errores Estandarizado:**
   - Respuestas de error consistentes
   - Status codes HTTP apropiados

### ❌ **Django Views Normales (Endpoints Actuales):**

1. **Código Repetitivo:**
   - Parsing manual de JSON
   - Validación manual de campos
   - Serialización manual de respuestas

2. **Inconsistencias:**
   - Diferentes formatos de respuesta
   - Manejo de errores variable

3. **Mantenimiento:**
   - Más difícil agregar nuevos campos
   - Validaciones dispersas en el código

## Migración Recomendada

### Paso 1: Comparar Endpoints (Actual vs DRF)

**Registro - Vista Actual (`/api/register/`):**
- 50+ líneas de código
- Validación manual
- Manejo de errores manual
- Serialización manual

**Registro - Vista DRF (`/api/v2/register/`):**
- 20 líneas de código en view
- Validación en serializer (reutilizable)
- Manejo de errores automático
- Serialización automática

### Paso 2: Testing

Puedes probar ambos endpoints lado a lado:

```bash
# Endpoint actual (Django views)
POST http://localhost:8000/api/register/

# Endpoint nuevo (DRF)
POST http://localhost:8000/api/v2/register/
```

### Paso 3: Migración Gradual

1. Mantén ambas versiones funcionando
2. Migra frontend gradualmente a `/api/v2/`
3. Una vez migrado, elimina endpoints antiguos

## Próximos Pasos Sugeridos

1. **Agregar Autenticación JWT:**
   ```python
   # settings.py
   REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] = [
       'rest_framework_simplejwt.authentication.JWTAuthentication',
   ]
   ```

2. **Serializers Adicionales:**
   - MedicationSerializer
   - ScheduleSerializer
   - IntakeSerializer

3. **ViewSets para CRUD Completo:**
   ```python
   from rest_framework.viewsets import ModelViewSet
   
   class PatientViewSet(ModelViewSet):
       queryset = User.objects.filter(user_type='patient')
       serializer_class = PatientSerializer
   ```

4. **Filtros y Búsqueda:**
   ```python
   from django_filters.rest_framework import DjangoFilterBackend
   
   class PatientViewSet(ModelViewSet):
       filter_backends = [DjangoFilterBackend]
       filterset_fields = ['user_type', 'created_at']
   ```

¿Quieres que implemente alguno de estos próximos pasos o tienes preguntas sobre los endpoints actuales?
