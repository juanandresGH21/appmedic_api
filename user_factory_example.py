"""
Ejemplo de uso del patrón Factory Method para la creación de usuarios
"""

from api.models import UserCreationService, PatientFactory, DoctorFactory, FamilyMemberFactory


def example_usage():
    """
    Ejemplo de cómo usar el Factory Method para crear diferentes tipos de usuarios
    """
    
    # Método 1: Usar el servicio de creación de usuarios (Recomendado)
    print("=== Usando UserCreationService ===")
    
    # Crear un paciente
    patient = UserCreationService.create_user(
        user_type='patient',
        email='paciente@example.com',
        password='password123',
        name='Juan Pérez',
        timezone='America/Bogota'
    )
    print(f"Paciente creado: {patient}")
    
    # Crear un médico
    doctor = UserCreationService.create_user(
        user_type='doctor',
        email='doctor@example.com',
        password='password123',
        name='Dr. María García',
        timezone='America/Bogota'
    )
    print(f"Médico creado: {doctor}")
    
    # Crear un familiar
    family_member = UserCreationService.create_user(
        user_type='family',
        email='familiar@example.com',
        password='password123',
        name='Ana Pérez',
        timezone='America/Bogota'
    )
    print(f"Familiar creado: {family_member}")
    
    
    # Método 2: Usar las factories directamente
    print("\n=== Usando Factories directamente ===")
    
    patient_factory = PatientFactory()
    patient2 = patient_factory.create_user(
        email='paciente2@example.com',
        password='password123',
        name='Carlos López'
    )
    print(f"Paciente creado con factory: {patient2}")
    
    doctor_factory = DoctorFactory()
    doctor2 = doctor_factory.create_user(
        email='doctor2@example.com',
        password='password123',
        name='Dra. Sofía Martínez'
    )
    print(f"Médico creado con factory: {doctor2}")


def example_extending_factory():
    """
    Ejemplo de cómo extender el sistema con nuevos tipos de usuario
    """
    
    # Crear una nueva factory para administradores
    class AdminFactory:
        def create_user(self, email, password, name, **kwargs):
            from api.models import User
            return User.objects.create_user(
                email=email,
                password=password,
                name=name,
                user_type='admin',
                timezone=kwargs.get('timezone', 'America/Bogota'),
                **kwargs
            )
    
    # Registrar la nueva factory
    UserCreationService.register_factory('admin', AdminFactory())
    
    # Ahora se puede usar para crear administradores
    admin = UserCreationService.create_user(
        user_type='admin',
        email='admin@example.com',
        password='password123',
        name='Administrador Sistema'
    )
    print(f"Administrador creado: {admin}")


def example_with_error_handling():
    """
    Ejemplo con manejo de errores
    """
    
    try:
        # Intentar crear un tipo de usuario no soportado
        invalid_user = UserCreationService.create_user(
            user_type='invalid_type',
            email='test@example.com',
            password='password123',
            name='Test User'
        )
    except ValueError as e:
        print(f"Error esperado: {e}")
    
    try:
        # Intentar crear usuario sin email
        no_email_user = UserCreationService.create_user(
            user_type='patient',
            email='',
            password='password123',
            name='Test User'
        )
    except ValueError as e:
        print(f"Error esperado: {e}")


if __name__ == "__main__":
    # Estos ejemplos requieren que Django esté configurado
    # Para ejecutarlos, usar: python manage.py shell < user_factory_example.py
    
    print("Para ejecutar estos ejemplos, ejecuta:")
    print("python manage.py shell")
    print("Luego importa y ejecuta las funciones de este archivo")
