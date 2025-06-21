from django.urls import path
from . import views
import requests

urlpatterns = [
        path('inicio/', views.index, name='inicio'),
        path('productos/<str:codigo>/', views.detalle_producto, name='detalle_producto'),
        path('herramientas-manuales/', views.herramientas_manuales, name='herramientas_manuales'),
        path('materiales-basicos/', views.materiales_basicos, name='materiales_basicos'),
        path('equipos-seguridad/', views.equipos_seguridad, name='equipos_seguridad'),
]
        

