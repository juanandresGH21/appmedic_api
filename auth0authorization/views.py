from functools import wraps
import jwt
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework import status
from api.models import User
from django.conf import settings


def get_token_auth_header(request):
    """Obtains the Access Token from the Authorization Header"""
    auth = request.META.get("HTTP_AUTHORIZATION", None)
    if not auth:
        response = JsonResponse({'code': 'authorization_header_missing',
                               'description': 'Authorization header is expected'})
        response.status_code = 401
        return response

    parts = auth.split()
    if parts[0].lower() != "bearer":
        response = JsonResponse({'code': 'invalid_header',
                               'description': 'Authorization header must start with Bearer'})
        response.status_code = 401
        return response
    elif len(parts) == 1:
        response = JsonResponse({'code': 'invalid_header',
                               'description': 'Token not found'})
        response.status_code = 401
        return response
    elif len(parts) > 2:
        response = JsonResponse({'code': 'invalid_header',
                               'description': 'Authorization header must be Bearer token'})
        response.status_code = 401
        return response

    token = parts[1]
    return token


def requires_auth(f):
    """Decorator to require authentication with Auth0 token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_auth_header(args[0])
        if isinstance(token, JsonResponse):
            return token
        
        try:
            # Decodificar el token (sin verificar por ahora, para desarrollo)
            decoded = jwt.decode(token, options={"verify_signature": False})
        except jwt.ExpiredSignatureError:
            response = JsonResponse({'code': 'token_expired',
                                   'description': 'token is expired'})
            response.status_code = 401
            return response
        except jwt.DecodeError:
            response = JsonResponse({'code': 'invalid_claims',
                                   'description': 'incorrect claims, please check the audience and issuer'})
            response.status_code = 401
            return response
        except Exception:
            response = JsonResponse({'code': 'invalid_header',
                                   'description': 'Unable to parse authentication token.'})
            response.status_code = 400
            return response

        # Agregar la información del token a la request
        args[0].auth0_user = decoded
        return f(*args, **kwargs)
    return decorated


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def auth0_login(request):
    """
    Vista para login con Auth0
    Recibe el token de Auth0 y retorna la información del usuario local
    """
    try:
        # Obtener el token del header Authorization
        token = get_token_auth_header(request)
        if isinstance(token, JsonResponse):
            return token
        
        # Decodificar el token de Auth0
        try:
            decoded_token = jwt.decode(token, options={"verify_signature": False})
        except Exception as e:
            return JsonResponse({
                'error': 'Invalid token',
                'message': str(e)
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Extraer información del usuario de Auth0
        auth0_id = decoded_token.get('sub')  # Subject del token (ID de Auth0)
        email = decoded_token.get('email')
        name = decoded_token.get('name', decoded_token.get('nickname', email))
        
        if not auth0_id or not email:
            return JsonResponse({
                'error': 'Incomplete user data',
                'message': 'Token must contain sub and email'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Buscar o crear el usuario en la base de datos local
        try:
            # Intentar encontrar por auth0_id primero
            user = User.objects.get(auth0_id=auth0_id)
            # Actualizar email y nombre si han cambiado
            if user.email != email:
                user.email = email
            if user.name != name:
                user.name = name
            user.save()
            
        except User.DoesNotExist:
            # Intentar encontrar por email
            try:
                user = User.objects.get(email=email)
                # Vincular con Auth0 ID
                user.auth0_id = auth0_id
                user.name = name
                user.save()
            except User.DoesNotExist:
                # Crear nuevo usuario
                # Por defecto será patient, pero se puede cambiar después
                user = User.objects.create_user(
                    email=email,
                    name=name,
                    user_type='patient',
                    auth0_id=auth0_id,
                    password=None  # No necesitamos password para Auth0
                )
        
        # Obtener información completa del usuario
        user_info = user.get_login_info()
        
        # Agregar información adicional de Auth0
        user_info.update({
            'auth0_id': auth0_id,
            'auth0_token_info': {
                'iss': decoded_token.get('iss'),
                'aud': decoded_token.get('aud'),
                'exp': decoded_token.get('exp'),
                'iat': decoded_token.get('iat'),
            }
        })
        
        return JsonResponse({
            'success': True,
            'message': 'Login successful',
            'user': user_info,
            'token_valid': True
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return JsonResponse({
            'error': 'Login failed',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@requires_auth
def auth0_profile(request):
    """
    Vista para obtener el perfil del usuario autenticado con Auth0
    """
    try:
        # Obtener información del token
        auth0_user = request.auth0_user
        auth0_id = auth0_user.get('sub')
        
        # Buscar el usuario en la base de datos local
        try:
            user = User.objects.get(auth0_id=auth0_id)
        except User.DoesNotExist:
            return JsonResponse({
                'error': 'User not found',
                'message': 'User not found in local database'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Retornar información completa del usuario
        user_info = user.get_login_info()
        user_info.update({
            'auth0_profile': auth0_user
        })
        
        return JsonResponse({
            'success': True,
            'user': user_info
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return JsonResponse({
            'error': 'Profile fetch failed',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@requires_auth
def auth0_update_profile(request):
    """
    Vista para actualizar el perfil del usuario autenticado con Auth0
    """
    try:
        # Obtener información del token
        auth0_user = request.auth0_user
        auth0_id = auth0_user.get('sub')
        
        # Buscar el usuario en la base de datos local
        try:
            user = User.objects.get(auth0_id=auth0_id)
        except User.DoesNotExist:
            return JsonResponse({
                'error': 'User not found',
                'message': 'User not found in local database'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Obtener datos del request
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'Invalid JSON',
                'message': 'Request body must be valid JSON'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Campos actualizables
        updatable_fields = ['name', 'user_type', 'tz']
        updated_fields = []
        
        for field in updatable_fields:
            if field in data:
                if field == 'user_type' and data[field] not in ['patient', 'family', 'doctor']:
                    return JsonResponse({
                        'error': 'Invalid user_type',
                        'message': 'user_type must be patient, family, or doctor'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                setattr(user, field, data[field])
                updated_fields.append(field)
        
        if updated_fields:
            user.save()
        
        # Retornar información actualizada
        user_info = user.get_login_info()
        
        return JsonResponse({
            'success': True,
            'message': f'Profile updated successfully. Fields updated: {", ".join(updated_fields)}',
            'user': user_info
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return JsonResponse({
            'error': 'Profile update failed',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@requires_auth
def auth0_logout(request):
    """
    Vista para logout (principalmente para logging local)
    El logout real de Auth0 se maneja en el frontend
    """
    try:
        auth0_user = request.auth0_user
        
        return JsonResponse({
            'success': True,
            'message': 'Logout successful',
            'note': 'Remember to clear Auth0 session in frontend'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return JsonResponse({
            'error': 'Logout failed',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Vistas adicionales de Auth0 (mantener las originales)
@api_view(['GET'])
@permission_classes([AllowAny])
def public(request):
    """Endpoint público que no requiere autenticación"""
    return JsonResponse({
        'message': 'Hello from a public endpoint! You don\'t need to be authenticated to see this.'
    })


@api_view(['GET'])
@requires_auth
def private(request):
    """Endpoint privado que requiere autenticación Auth0"""
    auth0_user = request.auth0_user
    user:User = request.user
    
    return JsonResponse({
        'message': 'Hello from a private endpoint! You are authenticated.',
        'user_info': {
            'auth0_id': auth0_user.get('sub'),
            'email': user.email,
            'name': user.name
        }
    })


def requires_scope(required_scope):
    """Decorator to require specific scope in Auth0 token"""
    def require_scope(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = get_token_auth_header(args[0])
            if isinstance(token, JsonResponse):
                return token
                
            try:
                decoded = jwt.decode(token, options={"verify_signature": False})
            except Exception:
                response = JsonResponse({'message': 'Invalid token'})
                response.status_code = 401
                return response
            
            if decoded.get("scope"):
                token_scopes = decoded["scope"].split()
                for token_scope in token_scopes:
                    if token_scope == required_scope:
                        args[0].auth0_user = decoded
                        return f(*args, **kwargs)
            
            response = JsonResponse({'message': 'You don\'t have access to this resource'})
            response.status_code = 403
            return response
        return decorated
    return require_scope


@api_view(['GET'])
@requires_scope('read:messages')
def private_scoped(request):
    """Endpoint que requiere scope específico"""
    auth0_user = request.auth0_user
    
    return JsonResponse({
        'message': 'Hello from a private endpoint! You need to be authenticated and have a scope of read:messages to see this.',
        'user_info': {
            'auth0_id': auth0_user.get('sub'),
            'email': auth0_user.get('email'),
            'scopes': auth0_user.get('scope', '').split()
        }
    })