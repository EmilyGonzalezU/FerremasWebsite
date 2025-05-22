
from django.urls import path
from . import views


urlpatterns = [
    path('agregar/<str:codigo>/', views.agregar_producto, name="Add"),
    path('eliminar/<str:codigo>/', views.eliminar_producto, name="Del"),
    path('restar/<str:codigo>/', views.restar_producto, name="Sub"),
    path('limpiar/', views.limpiar_carrito, name="CLS"),
    path('carrito/', views.carrito, name="carrito"),
     path('datos/', views.datos_usuario_compra, name="datos_usuario_compra"),
    path('checkout/', views.checkout_con_conversion, name='checkout_con_conversion'),
    path('webpay/iniciar/', views.iniciar_pago_webpay, name='iniciar_pago_webpay'),
    path('webpay/respuesta/', views.webpay_respuesta, name='webpay_respuesta'),
]