from rest_framework import serializers
from api.models import User


class UserRegistrationSerializer(serializers.Serializer):
    """Serializer para el registro de usuarios"""
    user_type = serializers.ChoiceField(
        choices=['patient', 'doctor', 'family'],
        help_text="Tipo de usuario"
    )
    email = serializers.EmailField(
        help_text="Correo electrónico único"
    )
    password = serializers.CharField(
        min_length=8,
        write_only=True,
        help_text="Contraseña (mínimo 8 caracteres)"
    )
    name = serializers.CharField(
        max_length=100,
        help_text="Nombre completo del usuario"
    )
    timezone = serializers.CharField(
        max_length=50,
        default='America/Bogota',
        required=False,
        help_text="Zona horaria del usuario"
    )
    auth0_id = serializers.CharField(
        max_length=100,
        help_text="ID de Auth0 del usuario"
    )
    
    def validate_email(self, value):
        """Validar que el email no esté en uso"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("El correo electrónico ya está en uso")
        return value
    
    def validate_user_type(self, value):
        """Validar tipo de usuario"""
        valid_types = ['patient', 'doctor', 'family']
        if value not in valid_types:
            raise serializers.ValidationError(f"Tipo de usuario debe ser uno de: {', '.join(valid_types)}")
        return value


class UserSerializer(serializers.ModelSerializer):
    """Serializer para mostrar información de usuario"""
    
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'user_type', 'tz', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def to_representation(self, instance):
        """Personalizar la representación de salida"""
        data = super().to_representation(instance)
        # Cambiar 'tz' por 'timezone' para consistencia con el frontend
        data['timezone'] = data.pop('tz')
        return data


class UserBasicInfoSerializer(serializers.ModelSerializer):
    """Serializer básico para información de usuario (sin datos sensibles)"""
    
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'user_type']
        read_only_fields = ['id', 'name', 'email', 'user_type']
