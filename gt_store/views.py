from pyexpat.errors import messages
from venv import logger
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404

from gato_tech import settings
from . import models
from itertools import chain
import random
import requests
from django.shortcuts import render
from .models import Pc, Notebook, Procesador, Placa_madre, Tarjeta_video, almacenamiento, Fuente_poder, Ram, Gabinete
from .filters import ProcesadorFilter, PlacaMadreFilter, TarjetaVideoFilter, AlmacenamientoFilter, FuentePoderFilter, RamFilter, GabineteFilter
import logging
import requests

logger = logging.getLogger(__name__)


def index(request):
    api_url = f"https://ferremasapi.onrender.com/api/productos"
    headers = {"Authorization": "b0e01ad6-5479-41b5-97a1-1bfd7cddc3d8"}
    
    #categorias faltan 2
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

def detalle_producto(request, codigo):
    api_url = f"https://ferremasapi.onrender.com/api/productos?codigo={codigo}"
    headers = {"Authorization": "b0e01ad6-5479-41b5-97a1-1bfd7cddc3d8"}
    
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
        

def registro (request):
    return render(request, 'usuarios/registro.html')

def herramientas_manuales(request):
    api_url = f"https://ferremasapi.onrender.com/api/productos"
    headers = {"Authorization": "b0e01ad6-5479-41b5-97a1-1bfd7cddc3d8"}
    
    try:
        params = {'categoria': 'herramientas manuales'}
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status()
        productos = response.json()
        
        return render(request, 'gt_store/general_almacenamiento.html', {
            'productos': productos,
            'categoria': 'Herramientas Manuales',
            'sucursal': 'Viña del Mar'
        })
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error en la conexión: {str(e)}")
        return render(request, 'gt_store/error.html', {
            'mensaje': 'Error al cargar herramientas manuales'
        })

def materiales_basicos(request):
    api_url = f"https://ferremasapi.onrender.com/api/productos"
    headers = {"Authorization": "b0e01ad6-5479-41b5-97a1-1bfd7cddc3d8"}
    
    try:
        params = {'categoria': 'materiales basicos'}
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status()
        productos = response.json()
        
        return render(request, 'gt_store/general_audifono.html', {
            'productos': productos,
            'categoria': 'Materiales Básicos',
            'sucursal': 'Viña del Mar'
        })
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error en la conexión: {str(e)}")
        return render(request, 'gt_store/error.html', {
            'mensaje': 'Error al cargar materiales básicos'
        })

def equipos_seguridad(request):
    api_url = f"https://ferremasapi.onrender.com/api/productos"
    headers = {"Authorization": "b0e01ad6-5479-41b5-97a1-1bfd7cddc3d8"}
    
    try:
        params = {'categoria': 'equipos de seguridad'}
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status()
        productos = response.json()
        
        return render(request, 'gt_store/general_fuente_poder.html', {
            'productos': productos,
            'categoria': 'Equipos de Seguridad',
            'sucursal': 'Viña del Mar'
        })
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error en la conexión: {str(e)}")
        return render(request, 'gt_store/error.html', {
            'mensaje': 'Error al cargar equipos de seguridad'
        })
