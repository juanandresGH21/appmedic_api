"""
Ejemplos de uso del patrón Factory Method con permisos y métodos específicos por tipo de usuario
"""

from api.models import UserCreationService, User, DoctorPatientRelation, FamilyPatientRelation


def example_create_users_with_relations():
    """
    Ejemplo completo de creación de usuarios y establecimiento de relaciones
    """
    print("=== Creando usuarios con el Factory Method ===")
    
    # Crear un paciente
    patient = UserCreationService.create_user(
        user_type='patient',
        email='paciente@example.com',
        password='password123',
        name='Juan Pérez'
    )
    print(f"Paciente creado: {patient}")
    
    # Crear un doctor
    doctor = UserCreationService.create_user(
        user_type='doctor',
        email='doctor@example.com',
        password='password123',
        name='Dr. María García'
    )
    print(f"Doctor creado: {doctor}")
    
    # Crear un familiar
    family_member = UserCreationService.create_user(
        user_type='family',
        email='familiar@example.com',
        password='password123',
        name='Ana Pérez'
    )
    print(f"Familiar creado: {family_member}")
    
    # Establecer relaciones
    print("\n=== Estableciendo relaciones ===")
    
    # Asignar doctor al paciente
    doctor_relation = UserCreationService.assign_doctor_to_patient(
        doctor_user_id=doctor.id,
        patient_user_id=patient.id,
        specialty="Medicina General",
        notes="Paciente nuevo, primera consulta"
    )
    print(f"Relación doctor-paciente creada: {doctor_relation}")
    
    # Asignar familiar al paciente
    family_relation = UserCreationService.assign_family_to_patient(
        family_user_id=family_member.id,
        patient_user_id=patient.id,
        relationship_type="spouse",
        can_manage_medications=True,
        emergency_contact=True
    )
    print(f"Relación familiar-paciente creada: {family_relation}")
    
    return patient, doctor, family_member


def example_patient_methods(patient):
    """
    Demostrar métodos específicos del paciente
    """
    print(f"\n=== Métodos del paciente: {patient.name} ===")
    
    # Ver cuidadores
    try:
        caregivers = patient.get_my_caregivers()
        print("Mis cuidadores:")
        print(f"  Familiares: {[f.name for f in caregivers['family_members']]}")
        print(f"  Doctores: {[d.name for d in caregivers['doctors']]}")
    except Exception as e:
        print(f"Error obteniendo cuidadores: {e}")
    
    # Ver programaciones
    try:
        schedules = patient.get_my_schedules()
        print(f"Mis programaciones: {schedules.count()} encontradas")
        for schedule in schedules:
            print(f"  - {schedule}")
    except Exception as e:
        print(f"Error obteniendo programaciones: {e}")


def example_doctor_methods(doctor):
    """
    Demostrar métodos específicos del doctor
    """
    print(f"\n=== Métodos del doctor: {doctor.name} ===")
    
    # Ver pacientes
    try:
        patients = doctor.get_my_patients()
        print("Mis pacientes:")
        for patient in patients:
            print(f"  - {patient.name} ({patient.email})")
            
            # Ver programaciones de cada paciente
            schedules = doctor.get_patient_schedules(patient.id)
            print(f"    Programaciones: {schedules.count()}")
    except Exception as e:
        print(f"Error obteniendo pacientes: {e}")


def example_family_methods(family_member):
    """
    Demostrar métodos específicos del familiar
    """
    print(f"\n=== Métodos del familiar: {family_member.name} ===")
    
    # Ver pacientes bajo su cuidado
    try:
        patients = family_member.get_my_patients()
        print("Pacientes bajo mi cuidado:")
        for patient in patients:
            print(f"  - {patient.name} ({patient.email})")
            
            # Verificar permisos
            can_manage = family_member.can_manage_schedules(patient.id)
            print(f"    Puede gestionar medicamentos: {can_manage}")
            
            if can_manage:
                schedules = family_member.get_patient_schedules(patient.id)
                print(f"    Programaciones: {schedules.count()}")
    except Exception as e:
        print(f"Error obteniendo pacientes: {e}")


def example_permissions_system():
    """
    Demostrar el sistema de permisos
    """
    print("\n=== Sistema de permisos ===")
    
    # Crear usuarios de ejemplo
    patient, doctor, family_member = example_create_users_with_relations()
    
    # Probar permisos
    users = [patient, doctor, family_member]
    
    for user in users:
        print(f"\nPermisos para {user.name} ({user.user_type}):")
        
        # Ver si puede ver datos del paciente
        can_view = user.can_view_patient_data(patient.id)
        print(f"  Puede ver datos del paciente: {can_view}")
        
        # Ver si puede gestionar programaciones del paciente
        can_manage = user.can_manage_schedules(patient.id)
        print(f"  Puede gestionar programaciones: {can_manage}")
        
        # Obtener permisos completos
        try:
            permissions = UserCreationService.get_user_permissions(user.id)
            print(f"  Permisos completos: {permissions}")
        except Exception as e:
            print(f"  Error obteniendo permisos: {e}")


def example_permission_errors():
    """
    Demostrar errores de permisos cuando se intenta acceder a métodos incorrectos
    """
    print("\n=== Errores de permisos ===")
    
    # Crear usuarios
    patient = UserCreationService.create_user(
        user_type='patient',
        email='test_patient@example.com',
        password='password123',
        name='Test Patient'
    )
    
    doctor = UserCreationService.create_user(
        user_type='doctor',
        email='test_doctor@example.com',
        password='password123',
        name='Test Doctor'
    )
    
    # Intentar que el doctor use métodos de paciente
    try:
        caregivers = doctor.get_my_caregivers()
        print(f"Error: El doctor pudo ver cuidadores: {caregivers}")
    except PermissionError as e:
        print(f"✓ Error esperado: {e}")
    
    try:
        schedules = doctor.get_my_schedules()
        print(f"Error: El doctor pudo ver sus programaciones: {schedules}")
    except PermissionError as e:
        print(f"✓ Error esperado: {e}")
    
    # Intentar que el paciente use métodos de doctor
    try:
        patients = patient.get_my_patients()
        print(f"Error: El paciente pudo ver pacientes: {patients}")
    except PermissionError as e:
        print(f"✓ Error esperado: {e}")


def main():
    """
    Función principal para ejecutar todos los ejemplos
    """
    print("EJEMPLOS DEL PATRÓN FACTORY METHOD CON PERMISOS")
    print("=" * 50)
    
    try:
        # Crear usuarios y relaciones
        patient, doctor, family_member = example_create_users_with_relations()
        
        # Demostrar métodos específicos de cada tipo
        example_patient_methods(patient)
        example_doctor_methods(doctor)
        example_family_methods(family_member)
        
        # Demostrar sistema de permisos
        example_permissions_system()
        
        # Demostrar errores de permisos
        example_permission_errors()
        
    except Exception as e:
        print(f"Error ejecutando ejemplos: {e}")


if __name__ == "__main__":
    # Para ejecutar estos ejemplos, usar:
    # python manage.py shell
    # exec(open('user_permissions_example.py').read())
    
    print("Para ejecutar estos ejemplos, ejecuta:")
    print("python manage.py shell")
    print("exec(open('user_permissions_example.py').read())")
