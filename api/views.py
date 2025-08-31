import traceback
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
import json
from .models import (
    UserCreationService, User, Medication, Schedule, Intake,
    DoctorPatientRelation, FamilyPatientRelation
)

from utils.format import Format


class PermissionMixin:
    """Mixin para validar permisos de usuario"""
    
    def get_user_from_request(self, request):
        """Obtener usuario autenticado (simulado por ahora)"""
        # En una implementación real, esto vendría de la autenticación
        user_id = request.headers.get('User-ID')
        if not user_id:
            raise ValueError("User-ID header requerido")
        
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ValueError("Usuario no encontrado")
    
    def check_permission(self, user, action, target_user_id=None):
        """Verificar si el usuario tiene permisos para una acción"""
        if action == 'view_patient_data' and target_user_id:
            return user.can_view_patient_data(target_user_id)
        elif action == 'manage_schedules' and target_user_id:
            return user.can_manage_schedules(target_user_id)
        return False


@method_decorator(csrf_exempt, name='dispatch')
class UserRegistrationView(View, PermissionMixin):
    """Vista para registro de usuarios usando el Factory Method"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            # Validar datos requeridos
            required_fields = ['user_type', 'email', 'password', 'name']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({
                        'error': f'Campo {field} es requerido'
                    }, status=400)

            user = User.objects.filter(email=data['email']).first()
            if user:
                return JsonResponse({
                    'error': 'El correo electrónico ya está en uso'
                }, status=400)

            # Crear usuario usando el Factory Method
            user = UserCreationService.create_user(
                user_type=data['user_type'],
                email=data['email'],
                password=data['password'],
                name=data['name'],
                tz=data.get('timezone', 'America/Bogota')
            )
            
            return JsonResponse({
                'success': True,
                'user': {
                    'id': str(user.id),
                    'email': user.email,
                    'name': user.name,
                    'user_type': user.user_type,
                    'timezone': user.tz,
                    'created_at': user.created_at.isoformat()
                }
            }, status=201)
            
        except ValueError as e:
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=400)
        except json.JSONDecodeError:
            traceback.print_exc()
            return JsonResponse({'error': 'JSON inválido'}, status=400)
        except Exception as e:
            traceback.print_exc()
            return JsonResponse({'error': 'Error interno del servidor'}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class UserPermissionsView(View, PermissionMixin):
    """Vista para obtener permisos del usuario actual"""
    
    def get(self, request):
        try:
            user = self.get_user_from_request(request)
            permissions = UserCreationService.get_user_permissions(user.id)
            
            return JsonResponse({
                'success': True,
                'permissions': permissions
            })
            
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': 'Error interno del servidor'}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class PatientCaregiversView(View, PermissionMixin):
    """Vista para que los pacientes vean sus cuidadores"""
    
    def get(self, request):
        try:
            user = self.get_user_from_request(request)
            
            if user.user_type != 'patient':
                return JsonResponse({
                    'error': 'Solo los pacientes pueden ver sus cuidadores'
                }, status=403)
            
            caregivers = user.get_my_caregivers()
            
            response_data = {
                'family_members': [
                    {
                        'id': str(fm.id),
                        'name': fm.name,
                        'email': fm.email,
                        'relationship': FamilyPatientRelation.objects.get(
                            family_member=fm, patient=user
                        ).relationship_type,
                        'can_manage_medications': FamilyPatientRelation.objects.get(
                            family_member=fm, patient=user
                        ).can_manage_medications,
                        'emergency_contact': FamilyPatientRelation.objects.get(
                            family_member=fm, patient=user
                        ).emergency_contact
                    }
                    for fm in caregivers['family_members']
                ],
                'doctors': [
                    {
                        'id': str(d.id),
                        'name': d.name,
                        'email': d.email,
                        'specialty': DoctorPatientRelation.objects.get(
                            doctor=d, patient=user
                        ).specialty
                    }
                    for d in caregivers['doctors']
                ]
            }
            
            return JsonResponse({
                'success': True,
                'caregivers': response_data
            })
            
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': 'Error interno del servidor'}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class PatientSchedulesView(View, PermissionMixin):
    """Vista para que los pacientes vean sus programaciones"""
    
    def get(self, request):
        try:
            user = self.get_user_from_request(request)
            
            if user.user_type != 'patient':
                return JsonResponse({
                    'error': 'Solo los pacientes pueden ver sus programaciones'
                }, status=403)
            
            schedules = user.get_my_schedules()
            
            schedules_data = []
            for schedule in schedules:
                schedules_data.append({
                    'id': str(schedule.id),
                    'medication': {
                        'id': str(schedule.medication.id),
                        'name': schedule.medication.name,
                        'form': schedule.medication.form
                    },
                    'start_date': Format.safe_isoformat(schedule.start_date),
                    'end_date': Format.safe_isoformat(schedule.end_date) if schedule.end_date else None,
                    'pattern': schedule.pattern,
                    'dose_amount': schedule.dose_amount
                })
            
            return JsonResponse({
                'success': True,
                'schedules': schedules_data
            })
            
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': 'Error interno del servidor'}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class CaregiverPatientsView(View, PermissionMixin):
    """Vista para que doctores y familiares vean sus pacientes"""
    
    def get(self, request):
        try:
            user = self.get_user_from_request(request)
            
            if user.user_type not in ['doctor', 'family']:
                return JsonResponse({
                    'error': 'Solo doctores y familiares pueden ver pacientes'
                }, status=403)
            
            patients = user.get_my_patients()
            
            patients_data = []
            for patient in patients:
                patient_data = {
                    'id': str(patient.id),
                    'name': patient.name,
                    'email': patient.email,
                    'timezone': patient.tz,
                    'created_at': patient.created_at.isoformat()
                }
                
                # Agregar información específica de la relación
                if user.user_type == 'doctor':
                    relation = DoctorPatientRelation.objects.get(
                        doctor=user, patient=patient
                    )
                    patient_data['specialty'] = relation.specialty
                    patient_data['notes'] = relation.notes
                elif user.user_type == 'family':
                    relation = FamilyPatientRelation.objects.get(
                        family_member=user, patient=patient
                    )
                    patient_data['relationship_type'] = relation.relationship_type
                    patient_data['can_manage_medications'] = relation.can_manage_medications
                    patient_data['emergency_contact'] = relation.emergency_contact
                
                patients_data.append(patient_data)
            
            return JsonResponse({
                'success': True,
                'patients': patients_data
            })
            
        except ValueError as e:
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            traceback.print_exc()
            return JsonResponse({'error': 'Error interno del servidor'}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class PatientSchedulesByCaregiverView(View, PermissionMixin):
    """Vista para que cuidadores vean las programaciones de sus pacientes"""
    
    def get(self, request, patient_id):
        try:
            user = self.get_user_from_request(request)
            
            # Verificar permisos
            if not user.can_view_patient_data(patient_id):
                return JsonResponse({
                    'error': 'No tienes permisos para ver este paciente'
                }, status=403)
            
            schedules = user.get_patient_schedules(patient_id)
            
            schedules_data = []
            for schedule in schedules:
                schedules_data.append({
                    'id': str(schedule.id),
                    'medication': {
                        'id': str(schedule.medication.id),
                        'name': schedule.medication.name,
                        'form': schedule.medication.form
                    },
                    'start_date': Format.safe_isoformat(schedule.start_date),
                    'end_date': Format.safe_isoformat(schedule.end_date) if schedule.end_date else None,
                    'pattern': schedule.pattern,
                    'dose_amount': schedule.dose_amount
                })
            
            return JsonResponse({
                'success': True,
                'schedules': schedules_data,
                'can_manage': user.can_manage_schedules(patient_id)
            })
            
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': 'Error interno del servidor'}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class AssignCaregiverView(View, PermissionMixin):
    """Vista para asignar cuidadores a pacientes"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            user = self.get_user_from_request(request)
            
            # Solo los doctores pueden asignar cuidadores por ahora
            if user.user_type != 'doctor':
                return JsonResponse({
                    'error': 'Solo los doctores pueden asignar cuidadores'
                }, status=403)
            
            caregiver_type = data.get('caregiver_type')
            
            if caregiver_type == 'family':
                relation = UserCreationService.assign_family_to_patient(
                    family_user_id=data['caregiver_id'],
                    patient_user_id=data['patient_id'],
                    relationship_type=data['relationship_type'],
                    can_manage_medications=data.get('can_manage_medications', False),
                    emergency_contact=data.get('emergency_contact', False)
                )
            elif caregiver_type == 'doctor':
                relation = UserCreationService.assign_doctor_to_patient(
                    doctor_user_id=data['caregiver_id'],
                    patient_user_id=data['patient_id'],
                    specialty=data.get('specialty', ''),
                    notes=data.get('notes', '')
                )
            else:
                return JsonResponse({
                    'error': 'Tipo de cuidador no válido'
                }, status=400)
            
            return JsonResponse({
                'success': True,
                'relation_id': str(relation.id),
                'message': 'Cuidador asignado exitosamente'
            })
            
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)
        except Exception as e:
            return JsonResponse({'error': 'Error interno del servidor'}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class RemoveCaregiverView(View, PermissionMixin):
    """Vista para remover asignaciones de cuidadores a pacientes"""
    
    def delete(self, request):
        try:
            data = json.loads(request.body)
            user = self.get_user_from_request(request)
            
            # Solo los doctores pueden remover cuidadores por ahora
            if user.user_type != 'doctor':
                return JsonResponse({
                    'error': 'Solo los doctores pueden remover cuidadores'
                }, status=403)
            
            caregiver_type = data.get('caregiver_type')
            caregiver_id = data.get('caregiver_id')
            patient_id = data.get('patient_id')
            
            # Validar campos requeridos
            if not all([caregiver_type, caregiver_id, patient_id]):
                return JsonResponse({
                    'error': 'Los campos caregiver_type, caregiver_id y patient_id son requeridos'
                }, status=400)
            
            # Verificar que el doctor tenga permisos sobre el paciente
            if not user.can_view_patient_data(patient_id):
                return JsonResponse({
                    'error': 'No tienes permisos para gestionar este paciente'
                }, status=403)
            
            deleted_count = 0
            relation_info = {}
            
            if caregiver_type == 'family':
                # Buscar y eliminar relación familiar
                try:
                    relation = FamilyPatientRelation.objects.get(
                        family_member_id=caregiver_id,
                        patient_id=patient_id
                    )
                    relation_info = {
                        'caregiver_name': relation.family_member.name,
                        'patient_name': relation.patient.name,
                        'relationship_type': relation.relationship_type,
                        'was_emergency_contact': relation.emergency_contact
                    }
                    relation.delete()
                    deleted_count = 1
                    
                except FamilyPatientRelation.DoesNotExist:
                    return JsonResponse({
                        'error': 'No se encontró la relación familiar especificada'
                    }, status=404)
                    
            elif caregiver_type == 'doctor':
                # Verificar que no se esté auto-eliminando sin tener otro doctor asignado
                if str(user.id) == str(caregiver_id):
                    other_doctors = DoctorPatientRelation.objects.filter(
                        patient_id=patient_id
                    ).exclude(doctor_id=caregiver_id).count()
                    
                    if other_doctors == 0:
                        return JsonResponse({
                            'error': 'No puedes removerte como doctor si eres el único asignado al paciente'
                        }, status=400)
                
                # Buscar y eliminar relación doctor-paciente
                try:
                    relation = DoctorPatientRelation.objects.get(
                        doctor_id=caregiver_id,
                        patient_id=patient_id
                    )
                    relation_info = {
                        'caregiver_name': relation.doctor.name,
                        'patient_name': relation.patient.name,
                        'specialty': relation.specialty
                    }
                    relation.delete()
                    deleted_count = 1
                    
                except DoctorPatientRelation.DoesNotExist:
                    return JsonResponse({
                        'error': 'No se encontró la relación doctor-paciente especificada'
                    }, status=404)
                    
            else:
                return JsonResponse({
                    'error': 'Tipo de cuidador no válido. Debe ser "family" o "doctor"'
                }, status=400)
            
            return JsonResponse({
                'success': True,
                'message': f'Relación {caregiver_type} eliminada exitosamente',
                'deleted_count': deleted_count,
                'relation_info': relation_info
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            traceback.print_exc()
            return JsonResponse({'error': 'Error interno del servidor'}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class ListCaregiverRelationsView(View, PermissionMixin):
    """Vista para listar todas las relaciones de un paciente"""
    
    def get(self, request, patient_id):
        try:
            user = self.get_user_from_request(request)
            
            # Verificar permisos
            if not user.can_view_patient_data(patient_id):
                return JsonResponse({
                    'error': 'No tienes permisos para ver este paciente'
                }, status=403)
            
            # Obtener paciente
            try:
                patient = User.objects.get(id=patient_id, user_type='patient')
            except User.DoesNotExist:
                return JsonResponse({
                    'error': 'Paciente no encontrado'
                }, status=404)
            
            # Obtener relaciones familiares
            family_relations = FamilyPatientRelation.objects.filter(patient_id=patient_id)
            family_data = []
            for relation in family_relations:
                family_data.append({
                    'id': str(relation.id),
                    'caregiver': {
                        'id': str(relation.family_member.id),
                        'name': relation.family_member.name,
                        'email': relation.family_member.email
                    },
                    'relationship_type': relation.relationship_type,
                    'can_manage_medications': relation.can_manage_medications,
                    'can_view_medical_data': relation.can_view_medical_data,
                    'emergency_contact': relation.emergency_contact,
                    'is_active': relation.is_active,
                    'created_at': relation.created_at.isoformat() if relation.created_at else None
                })
            
            # Obtener relaciones médicas
            doctor_relations = DoctorPatientRelation.objects.filter(patient_id=patient_id)
            doctor_data = []
            for relation in doctor_relations:
                doctor_data.append({
                    'id': str(relation.id),
                    'caregiver': {
                        'id': str(relation.doctor.id),
                        'name': relation.doctor.name,
                        'email': relation.doctor.email
                    },
                    'specialty': relation.specialty,
                    'notes': relation.notes,
                    'is_active': relation.is_active,
                    'created_at': relation.created_at.isoformat() if relation.created_at else None
                })
            
            return JsonResponse({
                'success': True,
                'patient': {
                    'id': str(patient.id),
                    'name': patient.name,
                    'email': patient.email
                },
                'relations': {
                    'family_members': family_data,
                    'doctors': doctor_data
                },
                'can_manage_relations': user.user_type == 'doctor'
            })
            
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            traceback.print_exc()
            return JsonResponse({'error': 'Error interno del servidor'}, status=500)


# Funciones de utilidad
@csrf_exempt
@require_http_methods(["POST"])
def create_sample_users_with_relations(request):
    """Crear usuarios de ejemplo con relaciones"""
    try:
        # Crear paciente
        patient = UserCreationService.create_user(
            user_type='patient',
            email='paciente_demo@example.com',
            password='password123',
            name='Juan Demo'
        )
        
        # Crear doctor
        doctor = UserCreationService.create_user(
            user_type='doctor',
            email='doctor_demo@example.com',
            password='password123',
            name='Dr. María Demo'
        )
        
        # Crear familiar
        family = UserCreationService.create_user(
            user_type='family',
            email='familiar_demo@example.com',
            password='password123',
            name='Ana Demo'
        )
        
        # Establecer relaciones
        doctor_relation = UserCreationService.assign_doctor_to_patient(
            doctor_user_id=doctor.id,
            patient_user_id=patient.id,
            specialty="Medicina General"
        )
        
        family_relation = UserCreationService.assign_family_to_patient(
            family_user_id=family.id,
            patient_user_id=patient.id,
            relationship_type="spouse",
            can_manage_medications=True,
            emergency_contact=True
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Usuarios de demostración creados',
            'users': {
                'patient': {
                    'id': str(patient.id),
                    'name': patient.name,
                    'email': patient.email
                },
                'doctor': {
                    'id': str(doctor.id),
                    'name': doctor.name,
                    'email': doctor.email
                },
                'family': {
                    'id': str(family.id),
                    'name': family.name,
                    'email': family.email
                }
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class ScheduleManagementView(View, PermissionMixin):
    """Vista para gestionar schedules (crear, actualizar, eliminar)"""
    
    def post(self, request):
        """Crear un nuevo schedule"""
        try:
            data = json.loads(request.body)
            user = self.get_user_from_request(request)
            
            # Validar campos requeridos
            required_fields = ['patient_id', 'medication_id', 'start_date', 'pattern', 'dose_amount']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({
                        'error': f'Campo {field} es requerido'
                    }, status=400)
            
            # Verificar permisos
            if not user.can_manage_schedules(data['patient_id']):
                return JsonResponse({
                    'error': 'No tienes permisos para crear schedules para este paciente'
                }, status=403)
            
            # Crear schedule
            schedule = UserCreationService.create_schedule(
                user_id=data['patient_id'],
                medication_id=data['medication_id'],
                start_date=data['start_date'],
                end_date=data.get('end_date'),
                pattern=data['pattern'],
                dose_amount=data['dose_amount'],
                created_by_user_id=user.id
            )
            
            return JsonResponse({
                'success': True,
                'schedule': {
                    'id': str(schedule.id),
                    'patient': {
                        'id': str(schedule.user.id),
                        'name': schedule.user.name
                    },
                    'medication': {
                        'id': str(schedule.medication.id),
                        'name': schedule.medication.name,
                        'form': schedule.medication.form
                    },
                    'start_date': Format.safe_isoformat(schedule.start_date),
                    'end_date': Format.safe_isoformat(schedule.end_date) if schedule.end_date else None,
                    'pattern': schedule.pattern,
                    'dose_amount': schedule.dose_amount,
                    'created_at': schedule.created_at.isoformat() if schedule.created_at else None
                }
            }, status=201)
            
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)
        except Exception as e:
            traceback.print_exc()
            return JsonResponse({'error': 'Error interno del servidor'}, status=500)
    
    def put(self, request, schedule_id):
        """Actualizar un schedule existente"""
        try:
            data = json.loads(request.body)
            user = self.get_user_from_request(request)
            
            # Actualizar schedule
            schedule = UserCreationService.update_schedule(
                schedule_id=schedule_id,
                user_id=user.id,
                **data
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Schedule actualizado exitosamente',
                'schedule': {
                    'id': str(schedule.id),
                    'patient': {
                        'id': str(schedule.user.id),
                        'name': schedule.user.name
                    },
                    'medication': {
                        'id': str(schedule.medication.id),
                        'name': schedule.medication.name,
                        'form': schedule.medication.form
                    },
                    'start_date': Format.safe_isoformat(schedule.start_date),
                    'end_date': Format.safe_isoformat(schedule.end_date) if schedule.end_date else None,
                    'pattern': schedule.pattern,
                    'dose_amount': schedule.dose_amount,
                    'updated_at': schedule.updated_at.isoformat() if schedule.updated_at else None
                }
            })
            
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)
        except Exception as e:
            traceback.print_exc()
            return JsonResponse({'error': 'Error interno del servidor'}, status=500)
    
    def delete(self, request, schedule_id):
        """Eliminar un schedule"""
        try:
            user = self.get_user_from_request(request)
            
            schedule_info = UserCreationService.delete_schedule(
                schedule_id=schedule_id,
                user_id=user.id
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Schedule eliminado exitosamente',
                'deleted_schedule': schedule_info
            })
            
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            traceback.print_exc()
            return JsonResponse({'error': 'Error interno del servidor'}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class ScheduleDetailView(View, PermissionMixin):
    """Vista para obtener detalles de un schedule específico"""
    
    def get(self, request, schedule_id):
        try:
            user = self.get_user_from_request(request)
            
            result = UserCreationService.get_schedule_details(
                schedule_id=schedule_id,
                user_id=user.id
            )
            
            schedule: Schedule = result['schedule']
            
            return JsonResponse({
                'success': True,
                'schedule': {
                    'id': str(schedule.id),
                    'patient': {
                        'id': str(schedule.user.id),
                        'name': schedule.user.name,
                        'email': schedule.user.email
                    },
                    'medication': {
                        'id': str(schedule.medication.id),
                        'name': schedule.medication.name,
                        'form': schedule.medication.form
                    },
                    'start_date': Format.safe_isoformat(schedule.start_date),
                    'end_date': Format.safe_isoformat(schedule.end_date) if schedule.end_date else None,
                    'pattern': schedule.pattern,
                    'dose_amount': schedule.dose_amount,
                    'created_at': schedule.created_at.isoformat() if schedule.created_at else None,
                    'updated_at': schedule.updated_at.isoformat() if schedule.updated_at else None
                },
                'can_modify': result['can_modify']
            })
            
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            traceback.print_exc()
            return JsonResponse({'error': 'Error interno del servidor'}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class MedicationManagementView(View, PermissionMixin):
    """Vista para gestionar medicamentos"""
    
    def get(self, request):
        """Listar todos los medicamentos"""
        try:
            medications = Medication.objects.all()
            
            medications_data = []
            for med in medications:
                medications_data.append({
                    'id': str(med.id),
                    'name': med.name,
                    'form': med.form,
                    'created_at': med.created_at.isoformat() if med.created_at else None
                })
            
            return JsonResponse({
                'success': True,
                'medications': medications_data,
                'total': len(medications_data)
            })
            
        except Exception as e:
            traceback.print_exc()
            return JsonResponse({'error': 'Error interno del servidor'}, status=500)
    
    def post(self, request):
        """Crear un nuevo medicamento"""
        try:
            data = json.loads(request.body)
            user = self.get_user_from_request(request)
            
            # Solo doctores pueden crear medicamentos
            if user.user_type != 'doctor':
                return JsonResponse({
                    'error': 'Solo los doctores pueden crear medicamentos'
                }, status=403)
            
            # Validar campos requeridos
            if 'name' not in data:
                return JsonResponse({
                    'error': 'El campo name es requerido'
                }, status=400)
            
            # Verificar si ya existe
            existing = Medication.objects.filter(name=data['name']).first()
            if existing:
                return JsonResponse({
                    'error': 'Ya existe un medicamento con ese nombre'
                }, status=400)
            
            medication = Medication.objects.create(
                name=data['name'],
                form=data.get('form', 'tablet'),
                created_by=user.id
            )
            
            return JsonResponse({
                'success': True,
                'medication': {
                    'id': str(medication.id),
                    'name': medication.name,
                    'form': medication.form,
                    'created_at': medication.created_at.isoformat() if medication.created_at else None
                }
            }, status=201)
            
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)
        except Exception as e:
            traceback.print_exc()
            return JsonResponse({'error': 'Error interno del servidor'}, status=500)
