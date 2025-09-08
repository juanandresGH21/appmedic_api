from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # Registro y autenticación
    path('users/register/', views.UserRegistrationView.as_view(), name='user_register'),
    path('users/permissions/', views.UserPermissionsView.as_view(), name='user_permissions'),
    
    # Endpoints para pacientes
    path('patient/caregivers/', views.PatientCaregiversView.as_view(), name='patient_caregivers'),
    path('patient/schedules/', views.PatientSchedulesView.as_view(), name='patient_schedules'),
    
    # Endpoints para cuidadores (doctores y familiares)
    path('caregiver/patients/', views.CaregiverPatientsView.as_view(), name='caregiver_patients'),
    path('caregiver/patient/<str:patient_id>/schedules/', 
         views.PatientSchedulesByCaregiverView.as_view(), 
         name='patient_schedules_by_caregiver'),
    
    # Asignación de cuidadores
    path('assign-caregiver/', views.AssignCaregiverView.as_view(), name='assign_caregiver'),
    path('remove-caregiver/', views.RemoveCaregiverView.as_view(), name='remove_caregiver'),
    path('patient/<str:patient_id>/relations/', views.ListCaregiverRelationsView.as_view(), name='list_caregiver_relations'),
    
    # Gestión de schedules
    path('schedules/', views.ScheduleManagementView.as_view(), name='schedule_management'),
    path('schedules/<str:schedule_id>/', views.ScheduleManagementView.as_view(), name='schedule_update_delete'),
    path('schedule/<str:schedule_id>/detail/', views.ScheduleDetailView.as_view(), name='schedule_detail'),
    
    # Gestión de medicamentos
    path('medications/', views.MedicationManagementView.as_view(), name='medication_management'),
    
    # Utilidades
    path('demo/create-sample-users/', views.create_sample_users_with_relations, name='create_sample_users'),

    path('auth/login/', views.LoginView.as_view(), name='login'),

]
