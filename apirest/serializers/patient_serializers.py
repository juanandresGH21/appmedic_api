from rest_framework import serializers
from api.models import User, DoctorPatientRelation, FamilyPatientRelation
from .user_serializers import UserBasicInfoSerializer


class DoctorRelationSerializer(serializers.ModelSerializer):
    """Serializer para relaciones doctor-paciente"""
    doctor = UserBasicInfoSerializer(read_only=True)
    
    class Meta:
        model = DoctorPatientRelation
        fields = ['id', 'doctor', 'specialty', 'notes', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class FamilyRelationSerializer(serializers.ModelSerializer):
    """Serializer para relaciones familia-paciente"""
    family_member = UserBasicInfoSerializer(read_only=True)
    relationship_display = serializers.CharField(source='get_relationship_type_display', read_only=True)
    
    class Meta:
        model = FamilyPatientRelation
        fields = [
            'id', 'family_member', 'relationship_type', 'relationship_display',
            'can_manage_medications', 'can_view_medical_data', 'emergency_contact',
            'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class PatientListSerializer(serializers.ModelSerializer):
    """Serializer para listar pacientes con información de relaciones"""
    doctors = serializers.SerializerMethodField()
    family_members = serializers.SerializerMethodField()
    total_schedules = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'name', 'email', 'tz', 'created_at',
            'doctors', 'family_members', 'total_schedules'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_doctors(self, obj):
        """Obtener doctores asignados al paciente"""
        doctor_relations = DoctorPatientRelation.objects.filter(
            patient=obj, 
            is_active=True
        ).select_related('doctor')
        
        return [
            {
                'id': str(relation.doctor.id),
                'name': relation.doctor.name,
                'email': relation.doctor.email,
                'specialty': relation.specialty
            }
            for relation in doctor_relations
        ]
    
    def get_family_members(self, obj):
        """Obtener familiares asignados al paciente"""
        family_relations = FamilyPatientRelation.objects.filter(
            patient=obj,
            is_active=True
        ).select_related('family_member')
        
        return [
            {
                'id': str(relation.family_member.id),
                'name': relation.family_member.name,
                'email': relation.family_member.email,
                'relationship': relation.relationship_type,
                'can_manage_medications': relation.can_manage_medications,
                'emergency_contact': relation.emergency_contact
            }
            for relation in family_relations
        ]
    
    def get_total_schedules(self, obj):
        """Obtener total de schedules activos del paciente"""
        from api.models import Schedule
        return Schedule.objects.filter(user=obj).count()
    
    def to_representation(self, instance):
        """Personalizar la representación"""
        data = super().to_representation(instance)
        # Cambiar 'tz' por 'timezone'
        data['timezone'] = data.pop('tz')
        return data


class PatientDetailSerializer(PatientListSerializer):
    """Serializer detallado para un paciente específico"""
    recent_schedules = serializers.SerializerMethodField()
    
    class Meta(PatientListSerializer.Meta):
        fields = PatientListSerializer.Meta.fields + ['recent_schedules']
    
    def get_recent_schedules(self, obj):
        """Obtener los últimos 5 schedules del paciente"""
        from api.models import Schedule
        schedules = Schedule.objects.filter(user=obj).order_by('-created_at')[:5]
        
        return [
            {
                'id': str(schedule.id),
                'medication_name': schedule.medication.name,
                'dose_amount': schedule.dose_amount,
                'start_date': schedule.start_date,
                'end_date': schedule.end_date,
                'pattern': schedule.pattern
            }
            for schedule in schedules
        ]
