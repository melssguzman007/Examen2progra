from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
   
    path('registro/', views.registro_view, name='registro'),
    
    path('', views.dashboard_view, name='dashboard'),
    
    path('alumno/pdf/<int:alumno_id>/', views.generar_y_enviar_pdf, name='enviar_pdf'),
]