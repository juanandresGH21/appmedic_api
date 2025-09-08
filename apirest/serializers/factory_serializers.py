from rest_framework import serializers
from api.models import User, DoctorPatientRelation, FamilyPatientRelation


class CaregiverAssignmentSerializer(serializers.Serializer):
    """Serializer para asignar cuidadores"""
    caregiver_id = serializers.IntegerField(help_text="ID del cuidador a asignar")
    patient_id = serializers.IntegerField(help_text="ID del paciente")
    caregiver_type = serializers.ChoiceField(
        choices=['doctor', 'family'],
        help_text="Tipo de cuidador"
    )
    
    # Campos específicos para doctores
    specialty = serializers.CharField(
        max_length=100, 
        required=False, 
        allow_blank=True,
        help_text="Especialidad del doctor (solo para doctores)"
    )
    notes = serializers.CharField(
        required=False, 
        allow_blank=True,
        help_text="Notas adicionales (solo para doctores)"
    )
    
    # Campos específicos para familiares
    relationship_type = serializers.ChoiceField(
        choices=FamilyPatientRelation.RELATIONSHIP_CHOICES,
        required=False,
        help_text="Tipo de relación familiar (solo para familiares)"
    )
    can_manage_medications = serializers.BooleanField(
        default=False,
        help_text="Puede gestionar medicamentos (solo para familiares)"
    )
    emergency_contact = serializers.BooleanField(
        default=False,
        help_text="Es contacto de emergencia (solo para familiares)"
    )
    
    def validate(self, data):
        """Validación cruzada según el tipo de cuidador"""
        caregiver_type = data.get('caregiver_type')
        caregiver_id = data.get('caregiver_id')
        
        # Verificar que el cuidador existe y es del tipo correcto
        try:
            caregiver = User.objects.get(id=caregiver_id)
            if caregiver.user_type != caregiver_type:
                raise serializers.ValidationError(
                    f"El usuario {caregiver_id} no es de tipo {caregiver_type}"
                )
        except User.DoesNotExist:
            raise serializers.ValidationError("Cuidador no encontrado")
        
        # Verificar que el paciente existe
        try:
            patient = User.objects.get(id=data.get('patient_id'), user_type='patient')
        except User.DoesNotExist:
            raise serializers.ValidationError("Paciente no encontrado")
        
        # Validaciones específicas por tipo
        if caregiver_type == 'family' and not data.get('relationship_type'):
            raise serializers.ValidationError(
                "relationship_type es requerido para familiares"
            )
        
        return data


class CaregiverRemovalSerializer(serializers.Serializer):
    """Serializer para remover cuidadores"""
    caregiver_id = serializers.IntegerField(help_text="ID del cuidador a remover")
    patient_id = serializers.IntegerField(help_text="ID del paciente")
    
    def validate(self, data):
        """Validar que el cuidador y paciente existen, y que hay una relación"""
        caregiver_id = data.get('caregiver_id')
        patient_id = data.get('patient_id')
        
        # Verificar que el paciente existe
        try:
            patient = User.objects.get(id=patient_id, user_type='patient')
        except User.DoesNotExist:
            raise serializers.ValidationError("Paciente no encontrado")
        
        # Verificar que el cuidador existe
        try:
            caregiver = User.objects.get(id=caregiver_id)
        except User.DoesNotExist:
            raise serializers.ValidationError("Cuidador no encontrado")
        
        # Verificar que el cuidador es de un tipo válido (doctor o family)
        if caregiver.user_type not in ['doctor', 'family']:
            raise serializers.ValidationError("El usuario especificado no es un cuidador válido")
        
        # Verificar que existe una relación entre el cuidador y el paciente
        relation_exists = False
        if caregiver.user_type == 'doctor':
            relation_exists = DoctorPatientRelation.objects.filter(
                doctor_id=caregiver_id, 
                patient_id=patient_id
            ).exists()
        elif caregiver.user_type == 'family':
            relation_exists = FamilyPatientRelation.objects.filter(
                family_member_id=caregiver_id, 
                patient_id=patient_id
            ).exists()
        
        if not relation_exists:
            raise serializers.ValidationError("No existe relación entre el cuidador y el paciente")
        
        return data


class UserPermissionsSerializer(serializers.Serializer):
    """Serializer para mostrar permisos de usuario"""
    user_type = serializers.CharField(read_only=True)
    can_view_own_data = serializers.BooleanField(read_only=True)
    can_manage_own_schedules = serializers.BooleanField(read_only=True)
    can_view_patients = serializers.BooleanField(read_only=True, default=False)
    can_manage_patient_schedules = serializers.BooleanField(read_only=True, default=False)
    can_assign_caregivers = serializers.BooleanField(read_only=True, default=False)
    can_remove_caregivers = serializers.BooleanField(read_only=True, default=False)
    can_view_caregivers = serializers.BooleanField(read_only=True, default=False)
    
    patients = serializers.ListField(read_only=True, default=list)
    caregivers = serializers.DictField(read_only=True, default=dict)
    total_patients = serializers.IntegerField(read_only=True, default=0)
    total_doctors = serializers.IntegerField(read_only=True, default=0)
    total_family = serializers.IntegerField(read_only=True, default=0)
    
    # Campo adicional para familiares
    permissions_by_patient = serializers.DictField(read_only=True, required=False)


class PatientScheduleRequestSerializer(serializers.Serializer):
    """Serializer para solicitar schedules de un paciente"""
    patient_id = serializers.IntegerField(help_text="ID del paciente")
    
    def validate_patient_id(self, value):
        """Validar que el paciente existe"""
        try:
            User.objects.get(id=value, user_type='patient')
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("Paciente no encontrado")


class UserServiceMethodSerializer(serializers.Serializer):
    """Serializer genérico para ejecutar métodos del servicio de usuario"""
    method_name = serializers.CharField(help_text="Nombre del método a ejecutar")
    args = serializers.ListField(
        required=False, 
        default=list,
        help_text="Argumentos posicionales"
    )
    kwargs = serializers.DictField(
        required=False, 
        default=dict,
        help_text="Argumentos con nombre"
    )
    
    def validate_method_name(self, value):
        """Validar que el método es permitido"""
        allowed_methods = [
            'get_my_caregivers',
            'get_my_patients', 
            'get_patient_schedules',
            'can_view_patient_data',
            'can_manage_schedules',
            'get_user_permissions'
        ]
        
        if value not in allowed_methods:
            raise serializers.ValidationError(
                f"Método '{value}' no permitido. Métodos disponibles: {allowed_methods}"
            )
        
        return value
