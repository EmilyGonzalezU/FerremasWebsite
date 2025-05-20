from django.urls import path
from . import views
import requests

urlpatterns = [
        path('inicio/', views.index, name='home'),
        path('Herramientas?Manuales/', views.general_pc, name='general_pc'),
        path('martillos/', views.general_pc_gamer, name="pc_gamer"),
        path('destornilladores/', views.general_pc_escritorio, name="pc_escritorio"),
        path('llaves/', views.general_processors, name='general_processors'),
        path('herramientas?electricas/', views.general_proce_amd, name='general_proce_amd'),
        path('taladros/', views.general_proce_intel, name='general_proce_intel'),        
        path('sierras/', views.general_placa, name='general_placa'),
        path('lijadoras/', views.general_placa_amd, name='general_placa_amd'),
        path('materiales?de?construccion/', views.general_placa_intel, name='general_placa_intel'),
        path('materiales?de?construccion/', views.general_ram, name='general_ram'),
        path('materiales?basicos/', views.general_almacenamiento, name='general_almacenamiento'),
        path('cemento/', views.general_hdd, name='general_hdd'),
        path('arena/', views.general_ssd, name='general_ssd'),
        path('ladrillos/', views.general_nvme, name='general_nvme'),
        path('acabados/', views.general_fP, name='general_fP'),
        path('pinturas/', views.general_gpu, name='general_gpu'),
        path('barnices/', views.general_gpu_amd, name='general_gpu_amd'),
        path('ceramicas/', views.general_gpu_intel, name='general_gpu_intel'),
        path('equipos?de?seguridad/', views.general_gpu_nvidia, name='general_gpu_nvidia'),
        path('cascos/', views.general_gabinete, name='general_gabinete'), 
        path('guantes/', views.general_notebooks, name='general_notebooks'),
        path('lentes?de?seguridad/', views.general_note_gamer, name='general_note_gamer'),
        path('accesorios?varios/', views.general_note_escritorio, name='general_note_escritorio'),
        path('tornillos?y?anclajes/', views.general_mouse, name='general_mouse'),
        path('fijaciones?y?adhesivos/', views.general_mouse_optico, name='general_mouse_optico'),
        path('equipos?de?medicion/', views.general_mouse_laser, name='general_mouse_laser'),
        path('productos/<str:codigo>/', views.detalle_producto, name='detalle_producto'),
        path('suge/', views.products, name='products')
]
        

