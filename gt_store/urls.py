from django.urls import path
from . import views
import requests

urlpatterns = [
        path('inicio/', views.index, name='inicio'),
        path('productos/<str:codigo>/', views.detalle_producto, name='detalle_producto'),
]
        

