from pyexpat.errors import messages
from venv import logger
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from . import models
from itertools import chain
import random
import requests
from django.shortcuts import render
from .models import Pc, Notebook, Procesador, Placa_madre, Tarjeta_video, almacenamiento, Fuente_poder, Ram, Gabinete
from .filters import ProcesadorFilter, PlacaMadreFilter, TarjetaVideoFilter, AlmacenamientoFilter, FuentePoderFilter, RamFilter, GabineteFilter

# Create your views here.
def index(request):
    api_url = "http://localhost:5000/api/productos"
    headers = {"Authorization": "0db5b48e-0027-4ace-9ed8-6a04cd3cd292"}
    
    productos_por_categoria = {
        'herramientas_manuales': [],
        'materiales_basicos': [],
        'equipos_de_seguridad': []
    }
    
    try:
        params = {'categoria': 'herramientas manuales'}
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status()
        productos_por_categoria['herramientas_manuales'] = response.json()
        
        params = {'categoria': 'materiales basicos'}
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status()
        productos_por_categoria['materiales_basicos'] = response.json()
        
        params = {'categoria': 'equipos de seguridad'}
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status()
        productos_por_categoria['equipos_de_seguridad'] = response.json()
        
        
    except requests.exceptions.RequestException as e:
        print(f"Error en la conexión: {str(e)}")
    
    return render(request, 'gt_store/index.html', {
        'herramientas_manuales': productos_por_categoria['herramientas_manuales'],
        'materiales_basicos': productos_por_categoria['materiales_basicos'],
        'equipos_de_seguridad': productos_por_categoria['equipos_de_seguridad'], 
        'sucursal': 'Viña del Mar'
    })

def general_pc(request):
    productos = models.Pc.objects.all()

    context = {"productos": productos}
                
    return render(request, 'gt_store/general_pc.html', context)

#Computation
def general_notebooks(request):
    notebooks = models.Notebook.objects.all()
    context = {"productos": notebooks}
    return render(request, 'gt_store/general_notebook.html', context)

def general_note_gamer(request):
    note_gamer = models.Notebook.objects.filter(tipo_notebook__iexact='notebook_gamer')
    context = {"productos":note_gamer}
    return render(request, 'gt_store/general_notebook.html', context)

def general_note_escritorio(request):
    note_escritorio = models.Notebook.objects.filter(tipo_notebook__iexact='notebook_oficina')
    context = {"productos":note_escritorio}
    return render(request, 'gt_store/general_notebook.html', context)

def general_pc_gamer(request):
    pc_gamer = models.Pc.objects.filter(tipo_pc__iexact='pc_gamer')
    context = {"productos":pc_gamer}
    return render(request, 'gt_store/general_pc.html', context)

def general_pc_escritorio(request):
    pc_escritorio = models.Pc.objects.filter(tipo_pc__iexact='pc_escritorio')
    context = {"productos": pc_escritorio}
    return render(request, 'gt_store/general_pc.html', context)


#Perifericos
def general_keyboard(request):
    productos = models.Teclado.objects.all()
    context = {"productos": productos}
    return render(request, 'gt_store/general_teclado.html', context)

def general_mecanico(request):
    productos = models.Teclado.objects.filter(teclado_tipo__iexact='mecanico')
    context = {"productos": productos}
    return render(request, 'gt_store/general_teclado.html', context)

def general_membrana(request):
    productos = models.Teclado.objects.filter(teclado_tipo__iexact='membrana')
    context = {"productos": productos}
    return render(request, 'gt_store/general_teclado.html', context)


def general_mouse(request):
    productos = models.Mouse.objects.all()
    context = {"productos": productos}
    return render(request, 'gt_store/general_mouse.html', context)

def general_mouse_optico(request):
    productos = models.Mouse.objects.filter(mouse_sensor__iexact='Optico')
    context = {"productos": productos}
    return render(request, 'gt_store/general_mouse.html', context)

def general_mouse_laser(request):
    productos = models.Mouse.objects.filter(mouse_sensor__iexact='Laser')
    context = {"productos": productos}
    return render(request, 'gt_store/general_mouse.html', context)

def general_headset(request):
    productos = models.Audifono.objects.all()
    context = {"productos": productos}
    return render(request, 'gt_store/general_audifono.html', context)

def general_headset_headset(request):
    productos = models.Audifono.objects.filter(audifono_tipo_auricular__iexact='HEADSET')
    context = {"productos": productos}
    return render(request, 'gt_store/general_audifono.html', context)

def general_monitor(request):
    productos = models.Monitor.objects.all()
    context = {"productos": productos}
    return render(request, 'gt_store/general_monitor.html', context)
#Components
def general_processors(request):
    productos = models.Procesador.objects.all()
    context = {"productos": productos}
    return render(request, 'gt_store/general_procesador.html', context)

def general_proce_amd(request):
    productos = models.Procesador.objects.filter(marca__iexact='AMD')
    context = {"productos": productos}
    return render(request, 'gt_store/general_procesador.html', context)

def general_proce_intel(request):
    productos = models.Procesador.objects.filter(marca__iexact='INTEL')
    context = {"productos": productos}
    return render(request, 'gt_store/general_procesador.html', context)

def general_placa(request):
    productos = models.Placa_madre.objects.all()
    context = {"productos": productos}
    return render(request, 'gt_store/general_placa.html', context)

def general_placa_amd(request):
    productos = models.Placa_madre.objects.filter(marca__iexact='AMD')
    context = {"productos": productos}
    return render(request, 'gt_store/general_placa.html', context)

def general_placa_intel(request):
    productos = models.Placa_madre.objects.filter(marca__iexact='INTEL')
    context = {"productos": productos}
    return render(request, 'gt_store/general_placa.html', context)

def general_almacenamiento(request):
    productos = models.almacenamiento.objects.all()
    context = {"productos": productos}
    return render(request, 'gt_store/general_almacenamiento.html', context)

def general_ssd(request):
    productos = models.almacenamiento.objects.filter(tipo_almacenamiento__iexact='SSD')
    context = {"productos": productos}
    return render(request, 'gt_store/general_almacenamiento.html', context)

def general_hdd(request):
    productos = models.almacenamiento.objects.filter(tipo_almacenamiento__iexact='HDD')
    context = {"productos": productos}
    return render(request, 'gt_store/general_almacenamiento.html', context)

def general_nvme(request):
    productos = models.almacenamiento.objects.filter(tipo_almacenamiento__iexact='NVME')
    context = {"productos": productos}
    return render(request, 'gt_store/general_almacenamiento.html', context)

def general_fP(request):
    productos = models.Fuente_poder.objects.all()
    context = {"productos": productos}
    return render(request, 'gt_store/general_fuente_poder.html', context)

def general_gpu(request):
    productos = models.Tarjeta_video.objects.all()
    context = {"productos": productos}
    return render(request, 'gt_store/general_gpu.html', context)

def general_gpu_amd(request):
    productos = models.Tarjeta_video.objects.filter(marca__iexact='AMD')
    context = {"productos": productos}
    return render(request, 'gt_store/general_gpu.html', context)

def general_gpu_intel(request):
    productos = models.Tarjeta_video.objects.filter(marca__iexact='INTEL')
    context = {"productos": productos}
    return render(request, 'gt_store/general_gpu.html', context)

def general_gpu_nvidia(request):
    productos = models.Tarjeta_video.objects.filter(marca__iexact='NVIDIA')
    context = {"productos": productos}
    return render(request, 'gt_store/general_gpu.html', context)


def general_gabinete(request):
    productos = models.Gabinete.objects.all()
    context = {"productos": productos}
    return render(request, 'gt_store/general_gabinete.html', context)

def general_ram(request):
    productos = models.Ram.objects.all()
    context = {"productos": productos}
    return render(request, 'gt_store/general_ram.html', context)


#test detalle producto

import logging
import requests

logger = logging.getLogger(__name__)

def detalle_producto(request, codigo):
    api_url = f"http://localhost:5000/api/productos?codigo={codigo}"
    headers = {"Authorization": "0db5b48e-0027-4ace-9ed8-6a04cd3cd292"}
    
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        
        productos = response.json()
        
        # Verifica si se encontró el producto
        if not productos or not isinstance(productos, list):
            logger.error(f"Producto no encontrado: {codigo}")
            return render(request, 'gt_store/error.html', {
                'mensaje': 'Producto no encontrado'
            })
            
        producto = productos[0]
        
        return render(request, 'gt_store/detalle_productos.html', {
            'producto': producto
        })
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error de conexión: {str(e)}")
        return render(request, 'gt_store/error.html', {
            'mensaje': 'Error al conectar con el servidor de productos'
        })
    except (ValueError, IndexError, KeyError) as e:
        logger.error(f"Error procesando datos: {str(e)}")
        return render(request, 'gt_store/error.html', {
            'mensaje': 'Error al procesar la información del producto'
        })
        
def products (request):
    producto = models.Product.objects.all()
    context = {"productos": producto}
    return render(request, 'gt_store/sugerencia.html', context)


def registro (request):
    return render(request, 'usuarios/registro.html')

#test filtro
