"""
Advanced Factory Pattern for Django REST Framework
Versión mejorada con métodos específicos por tipo de usuario
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from django.db import transaction
from django.core.exceptions import PermissionDenied

from api.models import (
    User, UserCreationService, Medication, Schedule, Intake,
    DoctorPatientRelation, FamilyPatientRelation
)


class UserServiceInterface(ABC):
    """Interfaz base para servicios de usuario con métodos específicos"""
    
    @abstractmethod
    def create_user(self, email: str, password: str, name: str, **kwargs) -> User:
        """Crear un nuevo usuario"""
        pass
    
    @abstractmethod
    def remove_caregiver(self, user_id: int, patient_id: int, caregiver_id: int) -> Dict[str, Any]:
        """Remover un cuidador (implementación específica por tipo)"""
        pass
    
    @abstractmethod
    def assign_caregiver(self, user_id: int, caregiver_id: int, caregiver_type: str, **kwargs) -> Dict[str, Any]:
        """Asignar un cuidador (implementación específica por tipo)"""
        pass
    
    @abstractmethod
    def can_view_patient_data(self, user_id: int, patient_id: int) -> bool:
        """Verificar si puede ver datos del paciente"""
        pass
    
    @abstractmethod
    def can_manage_schedules(self, user_id: int, patient_id: int) -> bool:
        """Verificar si puede gestionar schedules"""
        pass
    
    @abstractmethod
    def get_user_permissions(self, user_id: int) -> Dict[str, Any]:
        """Obtener permisos y capacidades específicas del usuario"""
        pass
    
    # Métodos opcionales que pueden ser implementados según el tipo de usuario
    def get_my_caregivers(self, user_id: int) -> Dict[str, List]:
        """Obtener cuidadores (solo para pacientes)"""
        raise NotImplementedError("Este método no está disponible para este tipo de usuario")
    
    def get_my_patients(self, user_id: int) -> List[User]:
        """Obtener pacientes (solo para doctores y familiares)"""
        raise NotImplementedError("Este método no está disponible para este tipo de usuario")
    
    def get_patient_schedules(self, user_id: int, patient_id: int) -> List[Schedule]:
        """Obtener schedules de un paciente (para cuidadores)"""
        raise NotImplementedError("Este método no está disponible para este tipo de usuario")


class PatientService(UserServiceInterface):
    """Servicio específico para pacientes"""
    
    def create_user(self, email: str, password: str, name: str, **kwargs) -> User:
        """Crear un paciente usando la factory original"""
        return UserCreationService.create_user(
            user_type='patient',
            email=email,
            password=password,
            name=name,
            **kwargs
        )
    
    def remove_caregiver(self, user_id: int, patient_id: int, caregiver_id: int) -> Dict[str, Any]:
        """Los pacientes no pueden remover cuidadores directamente"""
        raise PermissionDenied("Los pacientes no pueden remover cuidadores por sí mismos")
    
    def assign_caregiver(self, user_id: int, caregiver_id: int, caregiver_type: str, **kwargs) -> Dict[str, Any]:
        """Los pacientes no pueden asignar cuidadores directamente"""
        raise PermissionDenied("Los pacientes no pueden asignar cuidadores por sí mismos")
    
    def can_view_patient_data(self, user_id: int, patient_id: int) -> bool:
        """Los pacientes solo pueden ver sus propios datos"""
        return str(user_id) == str(patient_id)
    
    def can_manage_schedules(self, user_id: int, patient_id: int) -> bool:
        """Los pacientes pueden gestionar sus propios schedules"""
        return str(user_id) == str(patient_id)
    
    def get_my_caregivers(self, user_id: int) -> Dict[str, List]:
        """Obtener todos los cuidadores del paciente"""
        try:
            user = User.objects.get(id=user_id, user_type='patient')
            return user.get_my_caregivers()
        except User.DoesNotExist:
            raise ValueError("Paciente no encontrado")
    
    def get_my_patients(self, user_id: int) -> List[User]:
        """Los pacientes no tienen pacientes asignados"""
        raise NotImplementedError("Los pacientes no pueden ver otros pacientes")
    
    def get_patient_schedules(self, user_id: int, patient_id: int) -> List[Schedule]:
        """Los pacientes pueden ver solo sus propios schedules"""
        if not self.can_view_patient_data(user_id, patient_id):
            raise PermissionDenied("No tienes permisos para ver estos schedules")
        
        try:
            user = User.objects.get(id=user_id, user_type='patient')
            return user.get_my_schedules()
        except User.DoesNotExist:
            raise ValueError("Paciente no encontrado")
    
    def get_user_permissions(self, user_id: int) -> Dict[str, Any]:
        """Obtener permisos específicos del paciente"""
        try:
            user = User.objects.get(id=user_id, user_type='patient')
            caregivers = user.get_my_caregivers()
            
            return {
                'user_type': 'patient',
                'can_view_own_data': True,
                'can_manage_own_schedules': True,
                'can_view_caregivers': True,
                'can_remove_caregivers': False,
                'can_assign_caregivers': False,
                'patients': [],
                'caregivers': caregivers,
                'total_doctors': len(caregivers['doctors']),
                'total_family': len(caregivers['family_members']),
            }
        except User.DoesNotExist:
            raise ValueError("Usuario no encontrado")


class DoctorService(UserServiceInterface):
    """Servicio específico para doctores"""
    
    def create_user(self, email: str, password: str, name: str, **kwargs) -> User:
        """Crear un doctor usando la factory original"""
        return UserCreationService.create_user(
            user_type='doctor',
            email=email,
            password=password,
            name=name,
            **kwargs
        )
    
    def remove_caregiver(self, user_id: int, patient_id: int, caregiver_id: int) -> Dict[str, Any]:
        """Doctores pueden remover otros cuidadores"""
        try:
            doctor = User.objects.get(id=user_id, user_type='doctor')
            caregiver = User.objects.get(id=caregiver_id)
            
            # Verificar que el doctor tenga permisos sobre el paciente
            if not doctor.can_view_patient_data(patient_id):
                raise PermissionDenied("No tienes permisos sobre este paciente")
            
            # Determinar el tipo de cuidador automáticamente
            if caregiver.user_type == 'family':
                # Remover familiar
                relation_info = UserCreationService.remove_family_from_patient(
                    family_user_id=caregiver_id,
                    patient_user_id=patient_id
                )
                return {
                    'caregiver_type': 'family',
                    'message': 'Familiar removido exitosamente',
                    'relation_info': relation_info
                }
            elif caregiver.user_type == 'doctor':
                # Remover doctor
                relation_info = UserCreationService.remove_doctor_from_patient(
                    doctor_user_id=caregiver_id,
                    patient_user_id=patient_id
                )
                return {
                    'caregiver_type': 'doctor',
                    'message': 'Doctor removido exitosamente',
                    'relation_info': relation_info
                }
            else:
                raise ValueError(f"El usuario {caregiver_id} no es un tipo de cuidador válido")
                
        except User.DoesNotExist:
            raise ValueError("Usuario no encontrado")
    
    def assign_caregiver(self, user_id: int, caregiver_id: int, caregiver_type: str, **kwargs) -> Dict[str, Any]:
        """Doctores pueden asignar otros cuidadores"""
        doctor = User.objects.get(id=user_id, user_type='doctor')
        patient_id = kwargs.get('patient_id')
        
        if not patient_id:
            raise ValueError("patient_id es requerido para asignar cuidadores")
        
        # Verificar permisos sobre el paciente
        if not doctor.can_view_patient_data(patient_id):
            raise PermissionDenied("No tienes permisos sobre este paciente")
        
        if caregiver_type == 'family':
            relation = UserCreationService.assign_family_to_patient(
                family_user_id=caregiver_id,
                patient_user_id=patient_id,
                relationship_type=kwargs.get('relationship_type', 'other'),
                can_manage_medications=kwargs.get('can_manage_medications', False),
                emergency_contact=kwargs.get('emergency_contact', False)
            )
            return {
                'relation_type': 'family',
                'relation_id': str(relation.id),
                'message': 'Familiar asignado exitosamente'
            }
        elif caregiver_type == 'doctor':
            relation = UserCreationService.assign_doctor_to_patient(
                doctor_user_id=caregiver_id,
                patient_user_id=patient_id,
                specialty=kwargs.get('specialty', ''),
                notes=kwargs.get('notes', '')
            )
            return {
                'relation_type': 'doctor',
                'relation_id': str(relation.id),
                'message': 'Doctor asignado exitosamente'
            }
        else:
            raise ValueError(f"Tipo de cuidador '{caregiver_type}' no válido")
    
    def can_view_patient_data(self, user_id: int, patient_id: int) -> bool:
        """Verificar si el doctor puede ver datos del paciente"""
        try:
            doctor = User.objects.get(id=user_id, user_type='doctor')
            return doctor.can_view_patient_data(patient_id)
        except User.DoesNotExist:
            return False
    
    def can_manage_schedules(self, user_id: int, patient_id: int) -> bool:
        """Los doctores pueden gestionar schedules de sus pacientes"""
        return self.can_view_patient_data(user_id, patient_id)
    
    def get_my_caregivers(self, user_id: int) -> Dict[str, List]:
        """Los doctores no tienen cuidadores"""
        raise NotImplementedError("Los doctores no tienen cuidadores asignados")
    
    def get_my_patients(self, user_id: int) -> List[User]:
        """Obtener todos los pacientes del doctor"""
        try:
            doctor = User.objects.get(id=user_id, user_type='doctor')
            return doctor.get_my_patients()
        except User.DoesNotExist:
            raise ValueError("Doctor no encontrado")
    
    def get_patient_schedules(self, user_id: int, patient_id: int) -> List[Schedule]:
        """Obtener schedules de un paciente específico"""
        if not self.can_view_patient_data(user_id, patient_id):
            raise PermissionDenied("No tienes permisos para ver este paciente")
        
        try:
            doctor = User.objects.get(id=user_id, user_type='doctor')
            return doctor.get_patient_schedules(patient_id)
        except User.DoesNotExist:
            raise ValueError("Doctor no encontrado")
    
    def get_user_permissions(self, user_id: int) -> Dict[str, Any]:
        """Obtener permisos específicos del doctor"""
        try:
            doctor = User.objects.get(id=user_id, user_type='doctor')
            patients = doctor.get_my_patients()
            
            return {
                'user_type': 'doctor',
                'can_view_own_data': True,
                'can_manage_own_schedules': False,
                'can_view_patients': True,
                'can_manage_patient_schedules': True,
                'can_assign_caregivers': True,
                'can_remove_caregivers': True,
                'patients': [
                    {
                        'id': str(p.id),
                        'name': p.name,
                        'email': p.email,
                        'created_at': p.created_at
                    } for p in patients
                ],
                'caregivers': [],
                'total_patients': len(patients),
            }
        except User.DoesNotExist:
            raise ValueError("Usuario no encontrado")


class FamilyService(UserServiceInterface):
    """Servicio específico para familiares"""
    
    def create_user(self, email: str, password: str, name: str, **kwargs) -> User:
        """Crear un familiar usando la factory original"""
        return UserCreationService.create_user(
            user_type='family',
            email=email,
            password=password,
            name=name,
            **kwargs
        )
    
    def remove_caregiver(self, user_id: int, patient_id: int, caregiver_id: int) -> Dict[str, Any]:
        """Los familiares tienen permisos limitados para remover cuidadores"""
        raise PermissionDenied("Los familiares no pueden remover cuidadores")
    
    def assign_caregiver(self, user_id: int, caregiver_id: int, caregiver_type: str, **kwargs) -> Dict[str, Any]:
        """Los familiares no pueden asignar cuidadores"""
        raise PermissionDenied("Los familiares no pueden asignar cuidadores")
    
    def can_view_patient_data(self, user_id: int, patient_id: int) -> bool:
        """Verificar si el familiar puede ver datos del paciente"""
        try:
            family = User.objects.get(id=user_id, user_type='family')
            return family.can_view_patient_data(patient_id)
        except User.DoesNotExist:
            return False
    
    def can_manage_schedules(self, user_id: int, patient_id: int) -> bool:
        """Los familiares pueden gestionar schedules según su relación"""
        try:
            family = User.objects.get(id=user_id, user_type='family')
            return family.can_manage_schedules(patient_id)
        except User.DoesNotExist:
            return False
    
    def get_my_caregivers(self, user_id: int) -> Dict[str, List]:
        """Los familiares no tienen cuidadores"""
        raise NotImplementedError("Los familiares no tienen cuidadores asignados")
    
    def get_my_patients(self, user_id: int) -> List[User]:
        """Obtener todos los pacientes del familiar"""
        try:
            family = User.objects.get(id=user_id, user_type='family')
            return family.get_my_patients()
        except User.DoesNotExist:
            raise ValueError("Familiar no encontrado")
    
    def get_patient_schedules(self, user_id: int, patient_id: int) -> List[Schedule]:
        """Obtener schedules de un paciente específico"""
        if not self.can_view_patient_data(user_id, patient_id):
            raise PermissionDenied("No tienes permisos para ver este paciente")
        
        try:
            family = User.objects.get(id=user_id, user_type='family')
            return family.get_patient_schedules(patient_id)
        except User.DoesNotExist:
            raise ValueError("Familiar no encontrado")
    
    def get_user_permissions(self, user_id: int) -> Dict[str, Any]:
        """Obtener permisos específicos del familiar"""
        try:
            family = User.objects.get(id=user_id, user_type='family')
            patients = family.get_my_patients()
            
            # Obtener relaciones específicas para saber permisos detallados
            family_relations = FamilyPatientRelation.objects.filter(family_member=family)
            
            permissions_by_patient = {}
            for relation in family_relations:
                permissions_by_patient[str(relation.patient.id)] = {
                    'can_manage_medications': relation.can_manage_medications,
                    'can_view_medical_data': relation.can_view_medical_data,
                    'emergency_contact': relation.emergency_contact,
                    'relationship_type': relation.relationship_type,
                }
            
            return {
                'user_type': 'family',
                'can_view_own_data': True,
                'can_manage_own_schedules': False,
                'can_view_patients': True,
                'can_manage_patient_schedules': False,  # Depende de cada relación
                'can_assign_caregivers': False,
                'can_remove_caregivers': False,
                'patients': [
                    {
                        'id': str(p.id),
                        'name': p.name,
                        'email': p.email,
                        'permissions': permissions_by_patient.get(str(p.id), {}),
                        'created_at': p.created_at
                    } for p in patients
                ],
                'caregivers': [],
                'total_patients': len(patients),
                'permissions_by_patient': permissions_by_patient,
            }
        except User.DoesNotExist:
            raise ValueError("Usuario no encontrado")


class UserServiceFactory:
    """Factory principal que retorna el servicio específico según el tipo de usuario"""
    
    _services = {
        'patient': PatientService(),
        'doctor': DoctorService(),
        'family': FamilyService(),
    }
    
    @classmethod
    def get_service(cls, user_type: str) -> UserServiceInterface:
        """Obtener el servicio específico para el tipo de usuario"""
        service = cls._services.get(user_type)
        if not service:
            raise ValueError(f"Tipo de usuario '{user_type}' no soportado")
        return service
    
    @classmethod
    def get_service_by_user_id(cls, user_id: int) -> UserServiceInterface:
        """Obtener el servicio basado en el ID del usuario"""
        try:
            user = User.objects.get(id=user_id)
            return cls.get_service(user.user_type)
        except User.DoesNotExist:
            raise ValueError("Usuario no encontrado")
    
    @classmethod
    def register_service(cls, user_type: str, service: UserServiceInterface):
        """Registrar un nuevo servicio dinámicamente"""
        cls._services[user_type] = service
    
    @classmethod
    def create_user_with_service(cls, user_type: str, email: str, password: str, name: str, **kwargs) -> User:
        """Crear usuario usando el servicio específico"""
        service = cls.get_service(user_type)
        return service.create_user(email, password, name, **kwargs)
    
    @classmethod
    def execute_user_method(cls, user_id: int, method_name: str, *args, **kwargs):
        """Ejecutar un método específico del servicio de usuario"""
        service = cls.get_service_by_user_id(user_id)
        method = getattr(service, method_name, None)
        
        if not method:
            raise AttributeError(f"El método '{method_name}' no está disponible para este tipo de usuario")
        
        return method(user_id, *args, **kwargs)
