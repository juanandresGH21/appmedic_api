# Integración Auth0 con Modelo User Local

## Descripción General

Este sistema integra Auth0 con tu modelo User personalizado, permitiendo:
- Login automático con tokens de Auth0
- Sincronización entre Auth0 y base de datos local
- Mantenimiento del Factory Method pattern
- Gestión de permisos por tipo de usuario

## Endpoints Disponibles

### 1. Login con Auth0
**Endpoint:** `POST /auth/login/`  
**Autenticación:** Token Auth0 en header Authorization

```bash
# Ejemplo de uso
curl -X POST http://localhost:8000/auth/login/ \
  -H "Authorization: Bearer YOUR_AUTH0_TOKEN" \
  -H "Content-Type: application/json"
```

**Respuesta exitosa:**
```json
{
  "success": true,
  "message": "Login successful",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "Juan Pérez",
    "user_type": "patient",
    "permissions": ["view_own_data", "manage_own_schedules"],
    "created_at": "2024-01-01T10:00:00Z",
    "auth0_id": "auth0|123456789"
  },
  "token_valid": true
}
```

### 2. Obtener Perfil
**Endpoint:** `GET /auth/profile/`  
**Autenticación:** Token Auth0 en header Authorization

```bash
curl -X GET http://localhost:8000/auth/profile/ \
  -H "Authorization: Bearer YOUR_AUTH0_TOKEN"
```

### 3. Actualizar Perfil
**Endpoint:** `PUT /auth/profile/update/`  
**Autenticación:** Token Auth0 en header Authorization

```bash
curl -X PUT http://localhost:8000/auth/profile/update/ \
  -H "Authorization: Bearer YOUR_AUTH0_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Juan Carlos Pérez",
    "user_type": "doctor",
    "tz": "America/Mexico_City"
  }'
```

### 4. Logout
**Endpoint:** `POST /auth/logout/`  
**Autenticación:** Token Auth0 en header Authorization

```bash
curl -X POST http://localhost:8000/auth/logout/ \
  -H "Authorization: Bearer YOUR_AUTH0_TOKEN"
```

## Flujo de Autenticación

### 1. Primer Login (Usuario Nuevo)
1. Usuario se autentica en Auth0 (frontend)
2. Frontend obtiene el token JWT
3. Frontend envía token a `/auth/login/`
4. Sistema:
   - Decodifica el token
   - Extrae `sub` (Auth0 ID) y `email`
   - Crea nuevo usuario con `user_type='patient'` por defecto
   - Retorna información del usuario

### 2. Login Existente (Usuario con Auth0 ID)
1. Sistema busca usuario por `auth0_id`
2. Actualiza email/nombre si han cambiado
3. Retorna información actualizada

### 3. Login Existente (Usuario sin Auth0 ID)
1. Sistema busca usuario por `email`
2. Vincula cuenta con `auth0_id`
3. Retorna información del usuario

## Configuración Requerida

### 1. Variables de Entorno (.env)
```env
# Auth0 Configuration
AUTH0_DOMAIN=your-auth0-domain.auth0.com
AUTH0_API_IDENTIFIER=your-api-identifier
AUTH0_ISSUER=https://your-auth0-domain.auth0.com/
```

### 2. Settings.py
```python
# Auth0 Settings
AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
AUTH0_API_IDENTIFIER = os.getenv('AUTH0_API_IDENTIFIER')
AUTH0_ISSUER = os.getenv('AUTH0_ISSUER')

# Custom User Model
AUTH_USER_MODEL = 'api.User'
```

## Gestión de Permisos

El sistema mantiene el Factory Method pattern original:

```python
# Los permisos se asignan según el user_type
permissions = UserCreationService.get_user_permissions(user.id)

# Cambiar tipo de usuario (solo por API o admin)
user.user_type = 'doctor'
user.save()
```

## Manejo de Errores

### Errores Comunes
1. **Token Inválido (401)**
   - Token expirado
   - Token malformado
   - Sin header Authorization

2. **Usuario No Encontrado (404)**
   - Auth0 ID no existe en base local
   - Email no registrado

3. **Datos Incompletos (400)**
   - Token sin `sub` o `email`
   - JSON inválido en actualizaciones

## Ejemplo de Uso Frontend (JavaScript)

```javascript
// Después del login en Auth0
const loginWithAuth0 = async (auth0Token) => {
  try {
    const response = await fetch('/auth/login/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${auth0Token}`,
        'Content-Type': 'application/json'
      }
    });
    
    const data = await response.json();
    
    if (data.success) {
      // Guardar información del usuario
      localStorage.setItem('user', JSON.stringify(data.user));
      localStorage.setItem('auth0_token', auth0Token);
      
      // Redireccionar según tipo de usuario
      switch(data.user.user_type) {
        case 'patient':
          window.location.href = '/dashboard/patient';
          break;
        case 'doctor':
          window.location.href = '/dashboard/doctor';
          break;
        case 'family':
          window.location.href = '/dashboard/family';
          break;
      }
    }
  } catch (error) {
    console.error('Login error:', error);
  }
};

// Obtener perfil del usuario
const getUserProfile = async () => {
  const token = localStorage.getItem('auth0_token');
  
  const response = await fetch('/auth/profile/', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return await response.json();
};
```

## Testing

### Test Manual con cURL

1. **Obtener token de Auth0** (usar Auth0 Dashboard o frontend)

2. **Probar login:**
```bash
curl -X POST http://localhost:8000/auth/login/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGci..." \
  -H "Content-Type: application/json"
```

3. **Verificar usuario creado:**
```bash
curl -X GET http://localhost:8000/auth/profile/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGci..."
```

### Test con Python
```python
import requests
import json

# Configuración
BASE_URL = 'http://localhost:8000'
AUTH0_TOKEN = 'your_auth0_token_here'

headers = {
    'Authorization': f'Bearer {AUTH0_TOKEN}',
    'Content-Type': 'application/json'
}

# Test login
response = requests.post(f'{BASE_URL}/auth/login/', headers=headers)
print("Login Response:", response.json())

# Test profile
response = requests.get(f'{BASE_URL}/auth/profile/', headers=headers)
print("Profile Response:", response.json())
```

## Notas Importantes

1. **Seguridad:** En producción, configurar verificación de firma JWT
2. **Factory Pattern:** Se mantiene completamente funcional
3. **Migraciones:** Usuario existentes pueden vincularse por email
4. **Tipos de Usuario:** Por defecto se crean como 'patient'
5. **Auth0 Logout:** Se maneja principalmente en el frontend

## Próximos Pasos

1. Configurar verificación de firma JWT para producción
2. Implementar refresh tokens si es necesario  
3. Agregar middleware para autenticación automática
4. Configurar roles y permisos avanzados en Auth0
5. Implementar audit log para login/logout
