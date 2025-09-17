from rest_framework import serializers
from api.models import User, Schedule, Medication
from django.utils import timezone


class ScheduleAdminSerializer(serializers.ModelSerializer):
    """Serializer para schedules en vista administrativa"""
    medication_name = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()
    
    class Meta:
        model = Schedule
        fields = [
            'id', 'dose_amount', 'start_date', 'end_date', 
            'pattern', 'created_at', 'medication', 'medication_name', 'is_active'
        ]
    
    def get_medication_name(self, obj):
        return obj.medication.name if obj.medication else None
    
    def get_is_active(self, obj):
        if obj.end_date:
            return obj.end_date >= timezone.now().date()
        return True


class UserAdminSerializer(serializers.ModelSerializer):
    """Serializer para usuarios en vista administrativa"""
    schedules = serializers.SerializerMethodField()
    total_schedules = serializers.SerializerMethodField()
    active_schedules = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'name', 'user_type', 'created_at', 
            'is_active', 'auth0_id', 'schedules', 'total_schedules', 'active_schedules'
        ]
    
    def get_schedules(self, obj):
        schedules = obj.schedule_set.all().order_by('-created_at')
        return ScheduleAdminSerializer(schedules, many=True).data
    
    def get_total_schedules(self, obj):
        return obj.schedule_set.count()
    
    def get_active_schedules(self, obj):
        active_count = 0
        for schedule in obj.schedule_set.all():
            if not schedule.end_date or schedule.end_date >= timezone.now().date():
                active_count += 1
        return active_count
