from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from django.db import transaction

from api.models import User, UserCreationService
from .serializers import (
    UserRegistrationSerializer, 
    UserSerializer, 
    PatientListSerializer
)


class PermissionMixin:
    """Mixin para validar permisos de usuario con DRF"""
    
    def get_user_from_request(self, request):
        """Obtener usuario autenticado desde header"""
        user_id = request.META.get('HTTP_USER_ID')
        if not user_id:
            raise ValueError("User-ID header requerido")
        
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ValueError("Usuario no encontrado")


class UserRegistrationView(APIView):
    """Vista DRF para registro de usuarios usando Factory Method"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Registrar un nuevo usuario"""
        serializer = UserRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    # Crear usuario usando el Factory Method
                    user = UserCreationService.create_user(
                        user_type=serializer.validated_data['user_type'],
                        email=serializer.validated_data['email'],
                        password=serializer.validated_data['password'],
                        name=serializer.validated_data['name'],
                        tz=serializer.validated_data.get('timezone', 'America/Bogota')
                    )
                    
                    # Serializar respuesta
                    user_serializer = UserSerializer(user)
                    
                    return Response({
                        'success': True,
                        'user': user_serializer.data,
                        'message': 'Usuario registrado exitosamente'
                    }, status=status.HTTP_201_CREATED)
                    
            except ValueError as e:
                return Response({
                    'success': False,
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({
                    'success': False,
                    'error': 'Error interno del servidor'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class CaregiverPatientsView(APIView, PermissionMixin):
    """Vista DRF para que doctores y familiares vean sus pacientes"""
    
    def get(self, request):
        """Listar pacientes del cuidador autenticado"""
        try:
            user = self.get_user_from_request(request)
            
            # Verificar que sea doctor o familiar
            if user.user_type not in ['doctor', 'family']:
                return Response({
                    'success': False,
                    'error': 'Solo doctores y familiares pueden acceder a esta información'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Obtener pacientes según el tipo de usuario
            patients = user.get_my_patients()
            
            # Serializar los datos
            serializer = PatientListSerializer(patients, many=True)
            
            return Response({
                'success': True,
                'patients': serializer.data,
                'total_patients': len(patients),
                'caregiver_type': user.user_type,
                'caregiver_name': user.name
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'success': False,
                'error': 'Error interno del servidor'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Vista funcional alternativa para registro (usando decoradores)
@api_view(['POST'])
@permission_classes([AllowAny])
def user_registration_function_view(request):
    """Vista funcional para registro de usuarios (alternativa)"""
    if request.method == 'POST':
        serializer = UserRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    user = UserCreationService.create_user(**serializer.validated_data)
                    user_data = UserSerializer(user).data
                    
                    return Response({
                        'success': True,
                        'user': user_data
                    }, status=status.HTTP_201_CREATED)
                    
            except Exception as e:
                return Response({
                    'success': False,
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
