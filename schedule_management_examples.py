"""
Ejemplos de uso de las APIs para gestionar schedules y medicamentos
Ejecutar con: python manage.py shell < schedule_management_examples.py
"""

from api.models import UserCreationService, User, Medication, Schedule
from datetime import date, timedelta

def create_test_data():
    """Crear datos de prueba para los ejemplos"""
    print("=== Creando datos de prueba ===")
    
    # Crear usuarios
    patient = UserCreationService.create_user(
        user_type='patient',
        email='paciente_schedules@example.com',
        password='password123',
        name='Juan Schedules'
    )
    print(f"✓ Paciente creado: {patient.name} (ID: {patient.id})")
    
    doctor = UserCreationService.create_user(
        user_type='doctor',
        email='doctor_schedules@example.com',
        password='password123',
        name='Dr. Ana Schedules'
    )
    print(f"✓ Doctor creado: {doctor.name} (ID: {doctor.id})")
    
    family = UserCreationService.create_user(
        user_type='family',
        email='family_schedules@example.com',
        password='password123',
        name='María Schedules (Esposa)'
    )
    print(f"✓ Familiar creado: {family.name} (ID: {family.id})")
    
    # Establecer relaciones
    UserCreationService.assign_doctor_to_patient(
        doctor_user_id=doctor.id,
        patient_user_id=patient.id,
        specialty="Medicina General"
    )
    print(f"✓ Doctor asignado al paciente")
    
    UserCreationService.assign_family_to_patient(
        family_user_id=family.id,
        patient_user_id=patient.id,
        relationship_type="spouse",
        can_manage_medications=True,
        emergency_contact=True
    )
    print(f"✓ Familiar asignado al paciente con permisos de gestión")
    
    # Crear medicamentos
    med1 = Medication.objects.create(
        name="Aspirina",
        form="tablet",
        created_by=doctor.id
    )
    print(f"✓ Medicamento creado: {med1.name}")
    
    med2 = Medication.objects.create(
        name="Ibuprofeno",
        form="capsule",
        created_by=doctor.id
    )
    print(f"✓ Medicamento creado: {med2.name}")
    
    med3 = Medication.objects.create(
        name="Vitamina D",
        form="drops",
        created_by=doctor.id
    )
    print(f"✓ Medicamento creado: {med3.name}")
    
    return patient, doctor, family, [med1, med2, med3]


def demonstrate_schedule_creation(patient, doctor, family, medications):
    """Demostrar creación de schedules"""
    print(f"\n=== Creación de Schedules ===")
    
    # 1. Doctor crea schedule para paciente
    print(f"1. Doctor crea schedule de Aspirina para el paciente")
    try:
        schedule1 = UserCreationService.create_schedule(
            user_id=patient.id,
            medication_id=medications[0].id,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            pattern="daily_8am",
            dose_amount="100mg",
            created_by_user_id=doctor.id
        )
        print(f"✓ Schedule creado: {schedule1.medication.name} - {schedule1.dose_amount}")
        print(f"  - ID: {schedule1.id}")
        print(f"  - Patrón: {schedule1.pattern}")
        print(f"  - Fecha inicio: {schedule1.start_date}")
        print(f"  - Fecha fin: {schedule1.end_date}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # 2. Familiar con permisos crea schedule
    print(f"\n2. Familiar con permisos crea schedule de Vitamina D")
    try:
        schedule2 = UserCreationService.create_schedule(
            user_id=patient.id,
            medication_id=medications[2].id,
            start_date=date.today(),
            pattern="daily_morning",
            dose_amount="1000 UI",
            created_by_user_id=family.id
        )
        print(f"✓ Schedule creado: {schedule2.medication.name} - {schedule2.dose_amount}")
        print(f"  - ID: {schedule2.id}")
        print(f"  - Creado por: {family.name}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # 3. Crear otro familiar sin permisos e intentar crear schedule
    print(f"\n3. Creando familiar sin permisos e intentando crear schedule")
    try:
        family_no_perms = UserCreationService.create_user(
            user_type='family',
            email='family_no_perms@example.com',
            password='password123',
            name='Pedro Sin Permisos'
        )
        
        UserCreationService.assign_family_to_patient(
            family_user_id=family_no_perms.id,
            patient_user_id=patient.id,
            relationship_type="sibling",
            can_manage_medications=False,  # Sin permisos
            emergency_contact=False
        )
        
        # Intentar crear schedule (debería fallar)
        schedule3 = UserCreationService.create_schedule(
            user_id=patient.id,
            medication_id=medications[1].id,
            start_date=date.today(),
            pattern="twice_daily",
            dose_amount="200mg",
            created_by_user_id=family_no_perms.id
        )
        print(f"✗ ERROR: El familiar sin permisos pudo crear un schedule")
    except Exception as e:
        print(f"✓ Error esperado: {e}")
    
    return [schedule1, schedule2] if 'schedule1' in locals() and 'schedule2' in locals() else []


def demonstrate_schedule_updates(schedules, doctor, family):
    """Demostrar actualización de schedules"""
    print(f"\n=== Actualización de Schedules ===")
    
    if not schedules:
        print("No hay schedules para actualizar")
        return
    
    schedule = schedules[0]
    
    # 1. Doctor actualiza dosificación
    print(f"1. Doctor actualiza dosificación del schedule")
    try:
        updated_schedule = UserCreationService.update_schedule(
            schedule_id=schedule.id,
            user_id=doctor.id,
            dose_amount="150mg",
            pattern="daily_12pm"
        )
        print(f"✓ Schedule actualizado:")
        print(f"  - Nueva dosificación: {updated_schedule.dose_amount}")
        print(f"  - Nuevo patrón: {updated_schedule.pattern}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # 2. Familiar con permisos actualiza fechas
    if len(schedules) > 1:
        schedule2 = schedules[1]
        print(f"\n2. Familiar actualiza fechas del schedule")
        try:
            updated_schedule2 = UserCreationService.update_schedule(
                schedule_id=schedule2.id,
                user_id=family.id,
                end_date=date.today() + timedelta(days=60)
            )
            print(f"✓ Schedule actualizado:")
            print(f"  - Nueva fecha fin: {updated_schedule2.end_date}")
        except Exception as e:
            print(f"✗ Error: {e}")


def demonstrate_schedule_deletion(schedules, doctor, patient):
    """Demostrar eliminación de schedules"""
    print(f"\n=== Eliminación de Schedules ===")
    
    if not schedules:
        print("No hay schedules para eliminar")
        return
    
    # Crear un schedule adicional para eliminar
    print(f"1. Creando schedule adicional para eliminar")
    try:
        med_temp = Medication.objects.create(
            name="Paracetamol Temporal",
            form="tablet",
            created_by=doctor.id
        )
        
        schedule_to_delete = UserCreationService.create_schedule(
            user_id=patient.id,
            medication_id=med_temp.id,
            start_date=date.today(),
            pattern="as_needed",
            dose_amount="500mg",
            created_by_user_id=doctor.id
        )
        print(f"✓ Schedule temporal creado: {schedule_to_delete.id}")
        
        # Eliminar el schedule
        print(f"\n2. Eliminando schedule temporal")
        deleted_info = UserCreationService.delete_schedule(
            schedule_id=schedule_to_delete.id,
            user_id=doctor.id
        )
        print(f"✓ Schedule eliminado:")
        print(f"  - Paciente: {deleted_info['patient_name']}")
        print(f"  - Medicamento: {deleted_info['medication_name']}")
        print(f"  - Dosificación: {deleted_info['dose_amount']}")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def demonstrate_schedule_viewing(patient, doctor, family):
    """Demostrar visualización de schedules"""
    print(f"\n=== Visualización de Schedules ===")
    
    # 1. Paciente ve sus schedules
    print(f"1. Paciente ve sus schedules")
    try:
        patient_schedules = patient.get_my_schedules()
        print(f"✓ Schedules del paciente: {patient_schedules.count()}")
        for schedule in patient_schedules:
            print(f"  - {schedule.medication.name}: {schedule.dose_amount} ({schedule.pattern})")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # 2. Doctor ve schedules del paciente
    print(f"\n2. Doctor ve schedules del paciente")
    try:
        doctor_view_schedules = doctor.get_patient_schedules(patient.id)
        print(f"✓ Schedules vistos por doctor: {doctor_view_schedules.count()}")
        for schedule in doctor_view_schedules:
            print(f"  - {schedule.medication.name}: {schedule.dose_amount}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # 3. Familiar ve schedules del paciente
    print(f"\n3. Familiar ve schedules del paciente")
    try:
        family_view_schedules = family.get_patient_schedules(patient.id)
        print(f"✓ Schedules vistos por familiar: {family_view_schedules.count()}")
        for schedule in family_view_schedules:
            print(f"  - {schedule.medication.name}: {schedule.dose_amount}")
    except Exception as e:
        print(f"✗ Error: {e}")


def demonstrate_permissions_validation(patient, doctor, family):
    """Demostrar validación de permisos"""
    print(f"\n=== Validación de Permisos ===")
    
    # Crear otro paciente sin relación
    other_patient = UserCreationService.create_user(
        user_type='patient',
        email='otro_paciente_schedules@example.com',
        password='password123',
        name='Otro Paciente'
    )
    print(f"✓ Otro paciente creado: {other_patient.name}")
    
    # 1. Doctor intenta ver schedules de paciente no asignado
    print(f"\n1. Doctor intenta ver schedules de paciente no asignado")
    try:
        unauthorized_schedules = doctor.get_patient_schedules(other_patient.id)
        print(f"✗ ERROR: Doctor pudo ver schedules no autorizados")
    except Exception as e:
        print(f"✓ Error esperado: {e}")
    
    # 2. Familiar intenta crear schedule para paciente no relacionado
    print(f"\n2. Familiar intenta crear schedule para paciente no relacionado")
    try:
        med = Medication.objects.first()
        unauthorized_schedule = UserCreationService.create_schedule(
            user_id=other_patient.id,
            medication_id=med.id,
            start_date=date.today(),
            pattern="daily",
            dose_amount="100mg",
            created_by_user_id=family.id
        )
        print(f"✗ ERROR: Familiar pudo crear schedule no autorizado")
    except Exception as e:
        print(f"✓ Error esperado: {e}")


def main():
    """Función principal para ejecutar todos los ejemplos"""
    print("EJEMPLOS DE GESTIÓN DE SCHEDULES")
    print("=" * 50)
    
    try:
        # 1. Crear datos de prueba
        patient, doctor, family, medications = create_test_data()
        
        # 2. Demostrar creación de schedules
        schedules = demonstrate_schedule_creation(patient, doctor, family, medications)
        
        # 3. Demostrar actualización de schedules
        demonstrate_schedule_updates(schedules, doctor, family)
        
        # 4. Demostrar visualización de schedules
        demonstrate_schedule_viewing(patient, doctor, family)
        
        # 5. Demostrar eliminación de schedules
        demonstrate_schedule_deletion(schedules, doctor, patient)
        
        # 6. Demostrar validación de permisos
        demonstrate_permissions_validation(patient, doctor, family)
        
        print(f"\n{'=' * 50}")
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
