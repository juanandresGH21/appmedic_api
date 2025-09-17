from django.urls import path, include
from .views import (
    UserRegistrationView,
    CaregiverPatientsView,
    user_registration_function_view
)
from .advanced_views import (
    UserRegistrationViewV2,
    UserPermissionsViewV2,
    CaregiverManagementViewV2,
    PatientSchedulesViewV2,
    UserServiceMethodViewV2,
    AdminAllUsersSchedulesView

)

app_name = 'apirest'

urlpatterns = [
    # Endpoints principales con la nueva factory
    path('users/register/', UserRegistrationViewV2.as_view(), name='user-registration'),
    path('users/permissions/', UserPermissionsViewV2.as_view(), name='user-permissions'),
    path('caregivers/manage/', CaregiverManagementViewV2.as_view(), name='caregiver-management'),
    path('patient/schedules/', PatientSchedulesViewV2.as_view(), name='patient-schedules'),
    path('users/execute-method/', UserServiceMethodViewV2.as_view(), name='user-method'),
    path('admin/patients/', AdminAllUsersSchedulesView.as_view(), name='admin-method'),
    
    # Endpoints de compatibilidad (versión básica)
    path('caregiver/patients/', CaregiverPatientsView.as_view(), name='caregiver-patients'),
    path('register-alt/', user_registration_function_view, name='user-registration-alt'),
]
