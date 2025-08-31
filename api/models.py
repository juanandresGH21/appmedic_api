import uuid
from abc import ABC, abstractmethod
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db import models
from config import settings as setting


class BaseModel(models.Model):
    created_by = models.IntegerField(null=True, blank=True)
    updated_by = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        abstract = True

# Abstract Factory para crear usuarios
class UserFactory(ABC):
    @abstractmethod
    def create_user(self, email, password, name, **kwargs):
        pass


# Concrete Factories para cada tipo de usuario
class PatientFactory(UserFactory):
    def create_user(self, email, password, name, **kwargs):
        user = User.objects.create_user(
            email=email,
            password=password,
            name=name,
            user_type='patient',
            # tz=kwargs.get('timezone', 'America/Bogota'),
            **kwargs
        )
        
        # Configuración específica para pacientes
        self._setup_patient_permissions(user, **kwargs)
        return user
    
    def _setup_patient_permissions(self, user, **kwargs):
        """Configuración específica para pacientes"""
        # Aquí se pueden agregar configuraciones adicionales para pacientes
        # Por ejemplo, crear recordatorios por defecto, configuraciones iniciales, etc.
        pass


class FamilyMemberFactory(UserFactory):
    def create_user(self, email, password, name, **kwargs):
        user = User.objects.create_user(
            email=email,
            password=password,
            name=name,
            user_type='family',
            # tz=kwargs.get('timezone', 'America/Bogota'),
            **kwargs
        )
        
        # Configuración específica para familiares
        self._setup_family_permissions(user, **kwargs)
        return user
    
    def _setup_family_permissions(self, user, **kwargs):
        """Configuración específica para familiares"""
        # Aquí se pueden agregar configuraciones adicionales para familiares
        # Por ejemplo, permisos por defecto, notificaciones, etc.
        pass
    
    def assign_to_patient(self, family_user, patient_user, relationship_type, 
                         can_manage_medications=False, emergency_contact=False):
        """Asignar familiar a un paciente con permisos específicos"""
        if family_user.user_type != 'family':
            raise ValueError("El usuario debe ser de tipo 'family'")
        if patient_user.user_type != 'patient':
            raise ValueError("El paciente debe ser de tipo 'patient'")
        
        relation, created = FamilyPatientRelation.objects.get_or_create(
            family_member=family_user,
            patient=patient_user,
            defaults={
                'relationship_type': relationship_type,
                'can_manage_medications': can_manage_medications,
                'emergency_contact': emergency_contact,
            }
        )
        return relation


class DoctorFactory(UserFactory):
    def create_user(self, email, password, name, **kwargs):
        user = User.objects.create_user(
            email=email,
            password=password,
            name=name,
            user_type='doctor',
            # tz=kwargs.get('timezone', 'America/Bogota'),
            **kwargs
        )
        
        # Configuración específica para doctores
        self._setup_doctor_permissions(user, **kwargs)
        return user
    
    def _setup_doctor_permissions(self, user, **kwargs):
        """Configuración específica para doctores"""
        # Aquí se pueden agregar configuraciones adicionales para doctores
        # Por ejemplo, especialidades, permisos avanzados, etc.
        pass
    
    def assign_to_patient(self, doctor_user, patient_user, specialty="", notes=""):
        """Asignar doctor a un paciente"""
        if doctor_user.user_type != 'doctor':
            raise ValueError("El usuario debe ser de tipo 'doctor'")
        if patient_user.user_type != 'patient':
            raise ValueError("El paciente debe ser de tipo 'patient'")
        
        relation, created = DoctorPatientRelation.objects.get_or_create(
            doctor=doctor_user,
            patient=patient_user,
            defaults={
                'specialty': specialty,
                'notes': notes,
            }
        )
        return relation


# Manager personalizado para User
class UserManager(models.Manager):
    def create_user(self, email, password, name, user_type='patient', **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        
        user = self.model(
            email=email,
            name=name,
            user_type=user_type,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user


# Modelo User
class User(BaseModel):
    USER_TYPE_CHOICES = [
        ('patient', 'Paciente'),
        ('family', 'Familiar'),
        ('doctor', 'Médico'),
    ]
    
    email = models.EmailField(max_length=255, unique=True)
    password_hash = models.CharField(max_length=255)
    name = models.CharField(max_length=100)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='patient')
    tz = models.CharField(max_length=50, default='America/Bogota')
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']
    
    def set_password(self, raw_password):
        from django.contrib.auth.hashers import make_password
        self.password_hash = make_password(raw_password)
    
    def check_password(self, raw_password):
        from django.contrib.auth.hashers import check_password
        return check_password(raw_password, self.password_hash)
    
    # Métodos de permisos generales
    def can_view_patient_data(self, patient_id):
        """Determina si el usuario puede ver datos de un paciente específico"""
        if self.user_type == 'patient':
            return str(self.id) == str(patient_id)
        elif self.user_type == 'doctor':
            return DoctorPatientRelation.objects.filter(
                doctor=self, patient_id=patient_id
            ).exists()
        elif self.user_type == 'family':
            return FamilyPatientRelation.objects.filter(
                family_member=self, patient_id=patient_id
            ).exists()
        return False
    
    def can_manage_schedules(self, patient_id):
        """Determina si el usuario puede gestionar horarios de un paciente"""
        if self.user_type == 'doctor':
            return self.can_view_patient_data(patient_id)
        elif self.user_type == 'family':
            relation = FamilyPatientRelation.objects.filter(
                family_member=self, patient_id=patient_id
            ).first()
            return relation and relation.can_manage_medications
        return False
    
    # Métodos específicos según el tipo de usuario
    def get_my_caregivers(self):
        """Solo para pacientes: obtiene sus cuidadores"""
        if self.user_type != 'patient':
            raise PermissionError("Solo los pacientes pueden ver sus cuidadores")
        
        family_relations = FamilyPatientRelation.objects.filter(patient=self)
        doctor_relations = DoctorPatientRelation.objects.filter(patient=self)
        
        return {
            'family_members': [rel.family_member for rel in family_relations],
            'doctors': [rel.doctor for rel in doctor_relations]
        }
    
    def get_my_schedules(self):
        """Solo para pacientes: obtiene sus programaciones"""
        if self.user_type != 'patient':
            raise PermissionError("Solo los pacientes pueden ver sus programaciones")
        
        return Schedule.objects.filter(user=self)
    
    def get_my_patients(self):
        """Para doctores y familiares: obtiene su lista de pacientes"""
        if self.user_type == 'doctor':
            relations = DoctorPatientRelation.objects.filter(doctor=self)
            return [rel.patient for rel in relations]
        elif self.user_type == 'family':
            relations = FamilyPatientRelation.objects.filter(family_member=self)
            return [rel.patient for rel in relations]
        else:
            raise PermissionError("Solo doctores y familiares pueden ver pacientes")
    
    def get_patient_schedules(self, patient_id):
        """Para doctores y familiares: obtiene las programaciones de un paciente"""
        if not self.can_view_patient_data(patient_id):
            raise PermissionError("No tienes permisos para ver este paciente")
        
        return Schedule.objects.filter(user_id=patient_id)
    
    class Meta:
        db_table = 'Users'
    
    def __str__(self):
        return f"{self.name} ({self.email})"


# Factory Context - Clase que utiliza las factories
class UserCreationService:
    _factories = {
        'patient': PatientFactory(),
        'family': FamilyMemberFactory(),
        'doctor': DoctorFactory(),
    }
    
    @classmethod
    def create_user(cls, user_type, email, password, name, **kwargs) -> User:
        factory = cls._factories.get(user_type)
        if not factory:
            raise ValueError(f"Tipo de usuario '{user_type}' no soportado")
        
        return factory.create_user(email, password, name, **kwargs)
    
    @classmethod
    def register_factory(cls, user_type, factory):
        """Permite registrar nuevos tipos de factory dinámicamente"""
        cls._factories[user_type] = factory
    
    @classmethod
    def assign_family_to_patient(cls, family_user_id, patient_user_id, 
                                relationship_type, can_manage_medications=False, 
                                emergency_contact=False):
        """Asignar un familiar a un paciente"""
        try:
            family_user = User.objects.get(id=family_user_id, user_type='family')
            patient_user = User.objects.get(id=patient_user_id, user_type='patient')
            
            family_factory = cls._factories['family']
            return family_factory.assign_to_patient(
                family_user, patient_user, relationship_type,
                can_manage_medications, emergency_contact
            )
        except User.DoesNotExist as e:
            raise ValueError(f"Usuario no encontrado: {e}")
    
    @classmethod
    def assign_doctor_to_patient(cls, doctor_user_id, patient_user_id, 
                                specialty="", notes=""):
        """Asignar un doctor a un paciente"""
        try:
            doctor_user = User.objects.get(id=doctor_user_id, user_type='doctor')
            patient_user = User.objects.get(id=patient_user_id, user_type='patient')
            
            doctor_factory = cls._factories['doctor']
            return doctor_factory.assign_to_patient(
                doctor_user, patient_user, specialty, notes
            )
        except User.DoesNotExist as e:
            raise ValueError(f"Usuario no encontrado: {e}")
    
    @classmethod
    def get_user_permissions(cls, user_id):
        """Obtener los permisos y capacidades de un usuario"""
        try:
            user = User.objects.get(id=user_id)
            
            permissions = {
                'user_type': user.user_type,
                'can_view_own_data': True,
                'can_manage_own_schedules': user.user_type == 'patient',
            }
            
            if user.user_type == 'patient':
                permissions.update({
                    'can_view_caregivers': True,
                    'can_view_own_schedules': True,
                    'patients': [],
                    'caregivers': user.get_my_caregivers(),
                })
            elif user.user_type == 'doctor':
                patients = user.get_my_patients()
                permissions.update({
                    'can_view_patients': True,
                    'can_manage_patient_schedules': True,
                    'patients': [{'id': str(p.id), 'name': p.name, 'email': p.email} for p in patients],
                    'caregivers': [],
                })
            elif user.user_type == 'family':
                patients = user.get_my_patients()
                permissions.update({
                    'can_view_patients': True,
                    'can_manage_patient_schedules': False,  # Depende de la relación específica
                    'patients': [{'id': str(p.id), 'name': p.name, 'email': p.email} for p in patients],
                    'caregivers': [],
                })
            
            return permissions
            
        except User.DoesNotExist:
            raise ValueError("Usuario no encontrado")
    
    @classmethod
    def remove_family_from_patient(cls, family_user_id, patient_user_id):
        """Remover un familiar de un paciente"""
        try:
            relation = FamilyPatientRelation.objects.get(
                family_member_id=family_user_id,
                patient_id=patient_user_id
            )
            
            relation_info = {
                'family_member_name': relation.family_member.name,
                'patient_name': relation.patient.name,
                'relationship_type': relation.relationship_type,
                'was_emergency_contact': relation.emergency_contact
            }
            
            relation.delete()
            return relation_info
            
        except FamilyPatientRelation.DoesNotExist:
            raise ValueError("No se encontró la relación familiar especificada")
    
    @classmethod
    def remove_doctor_from_patient(cls, doctor_user_id, patient_user_id):
        """Remover un doctor de un paciente"""
        try:
            # Verificar que no sea el único doctor
            total_doctors = DoctorPatientRelation.objects.filter(
                patient_id=patient_user_id
            ).count()
            
            if total_doctors <= 1:
                raise ValueError("No se puede remover al único doctor asignado al paciente")
            
            relation = DoctorPatientRelation.objects.get(
                doctor_id=doctor_user_id,
                patient_id=patient_user_id
            )
            
            relation_info = {
                'doctor_name': relation.doctor.name,
                'patient_name': relation.patient.name,
                'specialty': relation.specialty
            }
            
            relation.delete()
            return relation_info
            
        except DoctorPatientRelation.DoesNotExist:
            raise ValueError("No se encontró la relación doctor-paciente especificada")
    
    @classmethod
    def get_patient_relations(cls, patient_id):
        """Obtener todas las relaciones de un paciente"""
        try:
            patient = User.objects.get(id=patient_id, user_type='patient')
            
            family_relations = FamilyPatientRelation.objects.filter(patient=patient)
            doctor_relations = DoctorPatientRelation.objects.filter(patient=patient)
            
            return {
                'patient': patient,
                'family_relations': family_relations,
                'doctor_relations': doctor_relations,
                'total_caregivers': family_relations.count() + doctor_relations.count()
            }
            
        except User.DoesNotExist:
            raise ValueError("Paciente no encontrado")
    
    @classmethod
    def create_schedule(cls, user_id, medication_id, start_date, pattern, dose_amount, 
                       end_date=None, created_by_user_id=None):
        """Crear un nuevo schedule para un paciente"""
        try:
            # Verificar que el usuario sea paciente
            patient = User.objects.get(id=user_id, user_type='patient')
            medication = Medication.objects.get(id=medication_id)
            
            # Verificar permisos del usuario que crea el schedule
            if created_by_user_id:
                creator = User.objects.get(id=created_by_user_id)
                if not creator.can_manage_schedules(user_id):
                    raise ValueError("No tienes permisos para crear schedules para este paciente")

            if Schedule.objects.filter(user=patient, medication=medication, start_date=start_date).exists():
                raise ValueError("Ya existe un schedule para este paciente y medicamento en la misma fecha")

            schedule = Schedule.objects.create(
                user=patient,
                medication=medication,
                start_date=start_date,
                end_date=end_date,
                pattern=pattern,
                dose_amount=dose_amount,
                created_by=created_by_user_id
            )
            
            return schedule
            
        except User.DoesNotExist:
            raise ValueError("Usuario no encontrado")
        except Medication.DoesNotExist:
            raise ValueError("Medicamento no encontrado")
    
    @classmethod
    def update_schedule(cls, schedule_id, user_id, **update_fields):
        """Actualizar un schedule existente"""
        try:
            schedule = Schedule.objects.get(id=schedule_id)
            user = User.objects.get(id=user_id)
            
            # Verificar permisos
            if not user.can_manage_schedules(schedule.user.id):
                raise ValueError("No tienes permisos para modificar este schedule")
            
            # Actualizar campos permitidos
            allowed_fields = ['start_date', 'end_date', 'pattern', 'dose_amount', 'medication_id']
            for field, value in update_fields.items():
                if field in allowed_fields:
                    if field == 'medication_id':
                        medication = Medication.objects.get(id=value)
                        schedule.medication = medication
                    else:
                        setattr(schedule, field, value)
            
            schedule.updated_by = user_id
            schedule.save()
            
            return schedule
            
        except Schedule.DoesNotExist:
            raise ValueError("Schedule no encontrado")
        except User.DoesNotExist:
            raise ValueError("Usuario no encontrado")
        except Medication.DoesNotExist:
            raise ValueError("Medicamento no encontrado")
    
    @classmethod
    def delete_schedule(cls, schedule_id, user_id):
        """Eliminar un schedule"""
        try:
            schedule = Schedule.objects.get(id=schedule_id)
            user = User.objects.get(id=user_id)
            
            # Verificar permisos
            if not user.can_manage_schedules(schedule.user.id):
                raise ValueError("No tienes permisos para eliminar este schedule")
            
            schedule_info = {
                'id': str(schedule.id),
                'patient_name': schedule.user.name,
                'medication_name': schedule.medication.name,
                'dose_amount': schedule.dose_amount,
                'pattern': schedule.pattern
            }
            
            schedule.delete()
            return schedule_info
            
        except Schedule.DoesNotExist:
            raise ValueError("Schedule no encontrado")
        except User.DoesNotExist:
            raise ValueError("Usuario no encontrado")
    
    @classmethod
    def get_schedule_details(cls, schedule_id, user_id):
        """Obtener detalles de un schedule específico"""
        try:
            schedule = Schedule.objects.get(id=schedule_id)
            user = User.objects.get(id=user_id)
            
            # Verificar permisos
            if not user.can_view_patient_data(schedule.user.id):
                raise ValueError("No tienes permisos para ver este schedule")
            
            return {
                'schedule': schedule,
                'can_modify': user.can_manage_schedules(schedule.user.id)
            }
            
        except Schedule.DoesNotExist:
            raise ValueError("Schedule no encontrado")
        except User.DoesNotExist:
            raise ValueError("Usuario no encontrado")


# Modelo Medication
class Medication(BaseModel):
    FORM_CHOICES = [
        ('tablet', 'Tableta'),
        ('capsule', 'Cápsula'),
        ('liquid', 'Líquido'),
        ('injection', 'Inyección'),
        ('cream', 'Crema'),
        ('drops', 'Gotas'),
    ]
    
    name = models.CharField(max_length=150)
    form = models.CharField(max_length=50, choices=FORM_CHOICES, default='tablet')
    
    class Meta:
        db_table = 'Medications'
    
    def __str__(self):
        return f"{self.name} ({self.form})"


# Modelo Schedule
class Schedule(BaseModel):
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    pattern = models.CharField(max_length=255)  # rrule/cron/simple
    dose_amount = models.CharField(max_length=50)  # ej: "10 mg"
    
    class Meta:
        db_table = 'Schedules'
    
    def __str__(self):
        return f"{self.medication.name} - {self.user.name}"


# Modelo Intake
class Intake(BaseModel):
    STATUS_CHOICES = [
        ('planned', 'Planificado'),
        ('taken', 'Tomado'),
        ('missed', 'Perdido'),
        ('skipped', 'Saltado'),
    ]
    
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    planned_at = models.DateTimeField()  # UTC
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    taken_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'Intakes'
    
    def __str__(self):
        return f"{self.schedule.medication.name} - {self.status}"


# Modelo para relaciones Doctor-Paciente
class DoctorPatientRelation(BaseModel):
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doctor_relations')
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient_doctor_relations')
    specialty = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'DoctorPatientRelations'
        unique_together = ('doctor', 'patient')
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.doctor.user_type != 'doctor':
            raise ValidationError('El usuario debe ser de tipo doctor')
        if self.patient.user_type != 'patient':
            raise ValidationError('El paciente debe ser de tipo patient')
    
    def __str__(self):
        return f"Dr. {self.doctor.name} -> {self.patient.name}"


# Modelo para relaciones Familiar-Paciente
class FamilyPatientRelation(BaseModel):
    RELATIONSHIP_CHOICES = [
        ('parent', 'Padre/Madre'),
        ('child', 'Hijo/Hija'),
        ('spouse', 'Cónyuge'),
        ('sibling', 'Hermano/Hermana'),
        ('grandparent', 'Abuelo/Abuela'),
        ('grandchild', 'Nieto/Nieta'),
        ('other', 'Otro'),
    ]
    
    family_member = models.ForeignKey(User, on_delete=models.CASCADE, related_name='family_relations')
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient_family_relations')
    relationship_type = models.CharField(max_length=20, choices=RELATIONSHIP_CHOICES)
    can_manage_medications = models.BooleanField(default=False)
    can_view_medical_data = models.BooleanField(default=True)
    emergency_contact = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'FamilyPatientRelations'
        unique_together = ('family_member', 'patient')
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.family_member.user_type != 'family':
            raise ValidationError('El usuario debe ser de tipo family')
        if self.patient.user_type != 'patient':
            raise ValidationError('El paciente debe ser de tipo patient')
    
    def __str__(self):
        return f"{self.family_member.name} ({self.relationship_type}) -> {self.patient.name}"
