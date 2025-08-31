"""
Ejemplos de gestión de cuidadores usando Django shell
Ejecutar con: python manage.py shell < caregiver_management_django_examples.py
"""

from api.models import UserCreationService, User, DoctorPatientRelation, FamilyPatientRelation

def create_test_users():
    """Crear usuarios de prueba"""
    print("=== Creando usuarios de prueba ===")
    
    # Crear paciente
    patient = UserCreationService.create_user(
        user_type='patient',
        email='paciente_test@example.com',
        password='password123',
        name='Juan Test'
    )
    print(f"✓ Paciente creado: {patient.name} (ID: {patient.id})")
    
    # Crear doctor principal
    doctor1 = UserCreationService.create_user(
        user_type='doctor',
        email='doctor1_test@example.com',
        password='password123',
        name='Dr. María Test'
    )
    print(f"✓ Doctor 1 creado: {doctor1.name} (ID: {doctor1.id})")
    
    # Crear doctor secundario
    doctor2 = UserCreationService.create_user(
        user_type='doctor',
        email='doctor2_test@example.com',
        password='password123',
        name='Dr. Carlos Test'
    )
    print(f"✓ Doctor 2 creado: {doctor2.name} (ID: {doctor2.id})")
    
    # Crear familiares
    family1 = UserCreationService.create_user(
        user_type='family',
        email='esposa_test@example.com',
        password='password123',
        name='Ana Test (Esposa)'
    )
    print(f"✓ Familiar 1 creado: {family1.name} (ID: {family1.id})")
    
    family2 = UserCreationService.create_user(
        user_type='family',
        email='hijo_test@example.com',
        password='password123',
        name='Pedro Test (Hijo)'
    )
    print(f"✓ Familiar 2 creado: {family2.name} (ID: {family2.id})")
    
    return patient, doctor1, doctor2, family1, family2


def setup_initial_relations(patient, doctor1, doctor2, family1, family2):
    """Establecer relaciones iniciales"""
    print(f"\n=== Estableciendo relaciones iniciales ===")
    
    # Asignar doctores al paciente
    doctor1_relation = UserCreationService.assign_doctor_to_patient(
        doctor_user_id=doctor1.id,
        patient_user_id=patient.id,
        specialty="Medicina General",
        notes="Doctor principal"
    )
    print(f"✓ Doctor 1 asignado: {doctor1_relation}")
    
    doctor2_relation = UserCreationService.assign_doctor_to_patient(
        doctor_user_id=doctor2.id,
        patient_user_id=patient.id,
        specialty="Cardiología",
        notes="Especialista en corazón"
    )
    print(f"✓ Doctor 2 asignado: {doctor2_relation}")
    
    # Asignar familiares al paciente
    family1_relation = UserCreationService.assign_family_to_patient(
        family_user_id=family1.id,
        patient_user_id=patient.id,
        relationship_type="spouse",
        can_manage_medications=True,
        emergency_contact=True
    )
    print(f"✓ Familiar 1 asignado: {family1_relation}")
    
    family2_relation = UserCreationService.assign_family_to_patient(
        family_user_id=family2.id,
        patient_user_id=patient.id,
        relationship_type="child",
        can_manage_medications=False,
        emergency_contact=False
    )
    print(f"✓ Familiar 2 asignado: {family2_relation}")
    
    return doctor1_relation, doctor2_relation, family1_relation, family2_relation


def demonstrate_patient_methods(patient):
    """Demostrar métodos específicos del paciente"""
    print(f"\n=== Métodos del paciente: {patient.name} ===")
    
    # Ver cuidadores
    try:
        caregivers = patient.get_my_caregivers()
        print(f"Cuidadores del paciente:")
        print(f"  - Familiares: {len(caregivers['family_members'])}")
        for fm in caregivers['family_members']:
            relation = FamilyPatientRelation.objects.get(family_member=fm, patient=patient)
            print(f"    * {fm.name} ({relation.relationship_type}) - Puede gestionar medicamentos: {relation.can_manage_medications}")
        
        print(f"  - Doctores: {len(caregivers['doctors'])}")
        for doc in caregivers['doctors']:
            relation = DoctorPatientRelation.objects.get(doctor=doc, patient=patient)
            print(f"    * {doc.name} ({relation.specialty})")
    
    except Exception as e:
        print(f"Error: {e}")


def demonstrate_removal_operations(patient, doctor1, doctor2, family1, family2):
    """Demostrar operaciones de eliminación"""
    print(f"\n=== Operaciones de eliminación ===")
    
    # 1. Remover un familiar
    print(f"1. Removiendo familiar: {family2.name}")
    try:
        result = UserCreationService.remove_family_from_patient(
            family_user_id=family2.id,
            patient_user_id=patient.id
        )
        print(f"✓ Familiar removido exitosamente:")
        print(f"  - Nombre: {result['family_member_name']}")
        print(f"  - Relación: {result['relationship_type']}")
        print(f"  - Era contacto de emergencia: {result['was_emergency_contact']}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # 2. Intentar remover el único doctor (debería fallar si solo hay uno)
    # Primero removemos uno para que quede solo uno
    print(f"\n2. Removiendo doctor secundario: {doctor2.name}")
    try:
        result = UserCreationService.remove_doctor_from_patient(
            doctor_user_id=doctor2.id,
            patient_user_id=patient.id
        )
        print(f"✓ Doctor removido exitosamente:")
        print(f"  - Nombre: {result['doctor_name']}")
        print(f"  - Especialidad: {result['specialty']}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # 3. Intentar remover el último doctor (debería fallar)
    print(f"\n3. Intentando remover el último doctor: {doctor1.name}")
    try:
        result = UserCreationService.remove_doctor_from_patient(
            doctor_user_id=doctor1.id,
            patient_user_id=patient.id
        )
        print(f"✗ No debería haber llegado aquí: {result}")
    except Exception as e:
        print(f"✓ Error esperado: {e}")


def demonstrate_relation_listing(patient):
    """Demostrar listado de relaciones"""
    print(f"\n=== Listado de relaciones ===")
    
    try:
        relations = UserCreationService.get_patient_relations(patient.id)
        
        print(f"Relaciones del paciente {relations['patient'].name}:")
        print(f"  - Total de cuidadores: {relations['total_caregivers']}")
        print(f"  - Familiares: {relations['family_relations'].count()}")
        print(f"  - Doctores: {relations['doctor_relations'].count()}")
        
        print(f"\nDetalle de familiares:")
        for relation in relations['family_relations']:
            print(f"  - {relation.family_member.name} ({relation.relationship_type})")
            print(f"    * Puede gestionar medicamentos: {relation.can_manage_medications}")
            print(f"    * Contacto de emergencia: {relation.emergency_contact}")
        
        print(f"\nDetalle de doctores:")
        for relation in relations['doctor_relations']:
            print(f"  - {relation.doctor.name} ({relation.specialty})")
            print(f"    * Notas: {relation.notes}")
        
    except Exception as e:
        print(f"Error: {e}")


def demonstrate_permission_checks(patient, doctor1, family1):
    """Demostrar verificaciones de permisos"""
    print(f"\n=== Verificaciones de permisos ===")
    
    # Permisos del paciente
    print(f"1. Permisos del paciente {patient.name}:")
    print(f"  - Puede ver datos del paciente {patient.id}: {patient.can_view_patient_data(patient.id)}")
    print(f"  - Puede gestionar horarios del paciente {patient.id}: {patient.can_manage_schedules(patient.id)}")
    
    # Permisos del doctor
    print(f"\n2. Permisos del doctor {doctor1.name}:")
    print(f"  - Puede ver datos del paciente {patient.id}: {doctor1.can_view_patient_data(patient.id)}")
    print(f"  - Puede gestionar horarios del paciente {patient.id}: {doctor1.can_manage_schedules(patient.id)}")
    
    # Permisos del familiar
    print(f"\n3. Permisos del familiar {family1.name}:")
    print(f"  - Puede ver datos del paciente {patient.id}: {family1.can_view_patient_data(patient.id)}")
    print(f"  - Puede gestionar horarios del paciente {patient.id}: {family1.can_manage_schedules(patient.id)}")
    
    # Intentar usar métodos incorrectos
    print(f"\n4. Intentos de uso incorrecto:")
    
    # Doctor intenta usar métodos de paciente
    try:
        doctor1.get_my_caregivers()
        print(f"✗ El doctor pudo usar get_my_caregivers() - ERROR")
    except PermissionError as e:
        print(f"✓ Error esperado para doctor.get_my_caregivers(): {e}")
    
    # Familiar intenta ver pacientes sin relación
    try:
        # Crear otro paciente sin relación
        other_patient = UserCreationService.create_user(
            user_type='patient',
            email='otro_paciente@example.com',
            password='password123',
            name='Otro Paciente'
        )
        
        can_view = family1.can_view_patient_data(other_patient.id)
        print(f"✓ Familiar puede ver otro paciente sin relación: {can_view}")
        
    except Exception as e:
        print(f"Error: {e}")


def main():
    """Función principal para ejecutar todos los ejemplos"""
    print("EJEMPLOS DE GESTIÓN DE CUIDADORES - DJANGO SHELL")
    print("=" * 60)
    
    try:
        # 1. Crear usuarios de prueba
        patient, doctor1, doctor2, family1, family2 = create_test_users()
        
        # 2. Establecer relaciones iniciales
        setup_initial_relations(patient, doctor1, doctor2, family1, family2)
        
        # 3. Demostrar métodos del paciente
        demonstrate_patient_methods(patient)
        
        # 4. Demostrar operaciones de eliminación
        demonstrate_removal_operations(patient, doctor1, doctor2, family1, family2)
        
        # 5. Listar relaciones después de cambios
        demonstrate_relation_listing(patient)
        
        # 6. Verificar permisos
        demonstrate_permission_checks(patient, doctor1, family1)
        
        print(f"\n{'=' * 60}")
        print("Ejemplos completados exitosamente!")
        
    except Exception as e:
        print(f"Error ejecutando ejemplos: {e}")
        import traceback
        traceback.print_exc()


# Ejecutar ejemplos
if __name__ == "__main__":
    main()

# Si se ejecuta desde el shell, también ejecutar automáticamente
main()
