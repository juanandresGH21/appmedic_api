from django.urls import path

from . import views

urlpatterns = [
    # Rutas originales de Auth0
    path('public/', views.public, name='auth0_public'),
    path('private/', views.private, name='auth0_private'),
    path('private-scoped/', views.private_scoped, name='auth0_private_scoped'),
    
    # Nuevas rutas para integración con modelo User
    path('login/', views.auth0_login, name='auth0_login'),
    path('profile/', views.auth0_profile, name='auth0_profile'),
    path('profile/update/', views.auth0_update_profile, name='auth0_update_profile'),
    path('logout/', views.auth0_logout, name='auth0_logout'),

    # path("login", views.LoginView.as_view()),
]