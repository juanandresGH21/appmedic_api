"""
Vistas DRF que utilizan la nueva Factory
"""
import traceback
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction
from django.core.exceptions import PermissionDenied
from django.utils import timezone

from .factories import UserServiceFactory
from .serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    CaregiverAssignmentSerializer,
    CaregiverRemovalSerializer,
    UserPermissionsSerializer,
    PatientScheduleRequestSerializer,
    UserServiceMethodSerializer,
    UserAdminSerializer,
)


class PermissionMixin:
    """Mixin para validar permisos de usuario"""
    
    def get_user_from_request(self, request):
        """Obtener usuario autenticado desde header"""
        if request.user and request.user.is_authenticated:
            return request.user
        user_id = request.META.get('HTTP_USER_ID')
        if not user_id:
            raise ValueError("User-ID header requerido")
        
        try:
            from api.models import User
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ValueError("Usuario no encontrado")


class UserRegistrationViewV2(APIView):
    """Vista para registro usando la nueva factory"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Registrar usuario con la nueva factory"""
        serializer = UserRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    # Usar la nueva factory
                    user = UserServiceFactory.create_user_with_service(
                        user_type=serializer.validated_data['user_type'],
                        email=serializer.validated_data['email'],
                        password=serializer.validated_data['password'],
                        name=serializer.validated_data['name'],
                        tz=serializer.validated_data.get('timezone', 'America/Bogota'),
                        auth0_id=serializer.validated_data['auth0_id']
                    )
                    
                    # Obtener permisos usando el servicio específico
                    service = UserServiceFactory.get_service(user.user_type)
                    permissions = service.get_user_permissions(user.id)
                    
                    user_data = UserSerializer(user).data
                    
                    return Response({
                        'success': True,
                        'user': user_data,
                        'permissions': permissions,
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


class UserPermissionsViewV2(APIView, PermissionMixin):
    """Vista para obtener permisos usando servicios específicos"""
    
    def get(self, request):
        """Obtener permisos detallados del usuario"""
        try:
            user = self.get_user_from_request(request)
            
            # Usar el servicio específico del usuario
            service = UserServiceFactory.get_service(user.user_type)
            permissions = service.get_user_permissions(user.id)
            
            serializer = UserPermissionsSerializer(permissions)
            
            return Response({
                'success': True,
                'permissions': serializer.data
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


class CaregiverManagementViewV2(APIView, PermissionMixin):
    """Vista para gestionar cuidadores usando servicios específicos"""
    
    def post(self, request):
        """Asignar un cuidador usando el servicio específico"""
        try:
            user = self.get_user_from_request(request)
            serializer = CaregiverAssignmentSerializer(data=request.data)
            
            if serializer.is_valid():
                # Usar el servicio específico del usuario
                service = UserServiceFactory.get_service(user.user_type)
                
                result = service.assign_caregiver(
                    user_id=user.id,
                    caregiver_id=serializer.validated_data['caregiver_id'],
                    caregiver_type=serializer.validated_data['caregiver_type'],
                    **{k: v for k, v in serializer.validated_data.items() 
                       if k not in ['caregiver_id', 'caregiver_type']}
                )
                
                return Response({
                    'success': True,
                    'result': result
                }, status=status.HTTP_201_CREATED)
            
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except PermissionDenied as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_403_FORBIDDEN)
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
    
    def delete(self, request):
        """Remover un cuidador usando el servicio específico"""
        try:
            user = self.get_user_from_request(request)
            serializer = CaregiverRemovalSerializer(data=request.data)
            
            if serializer.is_valid():
                # Usar el servicio específico del usuario
                service = UserServiceFactory.get_service(user.user_type)
                
                result = service.remove_caregiver(
                    user_id=user.id,
                    patient_id=serializer.validated_data['patient_id'],
                    caregiver_id=serializer.validated_data['caregiver_id']
                )
                
                return Response({
                    'success': True,
                    'result': result
                }, status=status.HTTP_200_OK)
            
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except PermissionDenied as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_403_FORBIDDEN)
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


class PatientSchedulesViewV2(APIView, PermissionMixin):
    """Vista para obtener schedules usando servicios específicos"""
    
    def post(self, request):
        """Obtener schedules de un paciente"""
        try:
            user = self.get_user_from_request(request)
            serializer = PatientScheduleRequestSerializer(data=request.data)
            
            if serializer.is_valid():
                patient_id = serializer.validated_data['patient_id']
                
                # Usar el servicio específico del usuario
                service = UserServiceFactory.get_service(user.user_type)
                
                schedules = service.get_patient_schedules(user.id, patient_id)
                
                # Serializar los schedules (necesitarías crear un ScheduleSerializer)
                schedules_data = [
                    {
                        'id': str(schedule.id),
                        'medication_name': schedule.medication.name,
                        'dose_amount': schedule.dose_amount,
                        'start_date': schedule.start_date,
                        'end_date': schedule.end_date,
                        'pattern': schedule.pattern,
                        'created_at': schedule.created_at
                    }
                    for schedule in schedules
                ]
                
                return Response({
                    'success': True,
                    'schedules': schedules_data,
                    'patient_id': patient_id,
                    'total_schedules': len(schedules),
                    'can_manage': service.can_manage_schedules(user.id, patient_id)
                }, status=status.HTTP_200_OK)
            
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except PermissionDenied as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_403_FORBIDDEN)
        except NotImplementedError as e:
            return Response({
                'success': False,
                'error': f'Funcionalidad no disponible para {user.user_type}: {str(e)}'
            }, status=status.HTTP_403_FORBIDDEN)
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


class UserServiceMethodViewV2(APIView, PermissionMixin):
    """Vista genérica para ejecutar métodos del servicio de usuario"""
    
    def post(self, request):
        """Ejecutar un método específico del servicio de usuario"""
        try:
            user = self.get_user_from_request(request)
            serializer = UserServiceMethodSerializer(data=request.data)
            
            if serializer.is_valid():
                method_name = serializer.validated_data['method_name']
                args = serializer.validated_data.get('args', [])
                kwargs = serializer.validated_data.get('kwargs', {})
                
                # Ejecutar el método usando la factory
                result = UserServiceFactory.execute_user_method(
                    user_id=user.id,
                    method_name=method_name,
                    *args,
                    **kwargs
                )
                
                return Response({
                    'success': True,
                    'method': method_name,
                    'result': result
                }, status=status.HTTP_200_OK)
            
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except AttributeError as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_403_FORBIDDEN)
        except NotImplementedError as e:
            return Response({
                'success': False,
                'error': f'Método no disponible para {user.user_type}: {str(e)}'
            }, status=status.HTTP_403_FORBIDDEN)
        except PermissionDenied as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_403_FORBIDDEN)
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


class AdminAllUsersSchedulesView(APIView, PermissionMixin):
    """Vista administrativa para obtener todos los usuarios y sus schedules - Solo para doctores"""
    
    def get(self, request):
        """Obtener todos los usuarios y sus schedules - Solo doctores"""
        try:
            user = self.get_user_from_request(request)
            
            # Verificar que sea doctor
            if user.user_type != 'doctor':
                return Response({
                    'success': False,
                    'error': 'Solo los doctores pueden acceder a esta información'
                }, status=status.HTTP_403_FORBIDDEN)
            
            from api.models import User
            
            # Obtener todos los usuarios con optimización de consultas
            all_users = User.objects.all().prefetch_related(
                'schedule_set__medication'
            ).order_by('created_at')
            
            # Serializar usuarios (el serializer maneja toda la lógica)
            users_serializer = UserAdminSerializer(all_users, many=True)
            users_data = users_serializer.data
            
            # Calcular estadísticas simples
            total_users = len(users_data)
            total_schedules = sum(user['total_schedules'] for user in users_data)
            
            # Contar usuarios por tipo
            users_by_type = {}
            for user_data in users_data:
                user_type = user_data['user_type']
                users_by_type[user_type] = users_by_type.get(user_type, 0) + 1
            
            # Crear datos de estadísticas
            statistics_data = {
                'total_users': total_users,
                'total_schedules': total_schedules,
                'users_by_type': users_by_type,
                'requested_by_doctor_id': user.id,
                'requested_by_doctor_name': user.name,
                'requested_by_doctor_email': user.email
            }
            
            # Datos de respuesta final
            response_data = {
                'success': True,
                'users': users_data,
                'statistics': statistics_data,
                'message': f'Se encontraron {total_users} usuarios con {total_schedules} schedules en total'
            }
            
            # Serializar respuesta completa
            # response_serializer = AdminAllUsersSchedulesResponseSerializer(data=response_data)
            # response_serializer.is_valid(raise_exception=True)
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            traceback.print_exc()
            return Response({
                'success': False,
                'error': 'Error interno del servidor'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
