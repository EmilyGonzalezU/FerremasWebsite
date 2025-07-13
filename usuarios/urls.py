from django.urls import path
from . import views


urlpatterns = [
    path('registro/', views.registro_usuario, name='registro'),
    path('inicio sesion/', views.login_view, name='inicio_sesion'),
    path('cerrar_sesion/', views.cerrar_sesion, name='cerrar_sesion'),
    path('', views.inicio_sesion, name='redireccion'),
    path('tipo_usuario/', views.tipo_usuario, name='tipo_usuario'),


] 

