import uuid
import json
import logging
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.core.cache import cache
from transbank.webpay.webpay_plus.transaction import Transaction, WebpayOptions
from transbank.common.integration_type import IntegrationType
from gt_store.models import Product
from .models import ProductoPedido
from .forms import PedidoForm
from usuarios.models import PerfilUsuario

logger = logging.getLogger(__name__)

# Clase para manejar la lógica del carrito de compras en sesión
class Carrito:
    def __init__(self, request):
        self.session = request.session
        carrito = self.session.get('carrito', {})
        if not carrito:
            carrito = self.session['carrito'] = {}
        self.carrito = carrito

    def agregar(self, producto):
        codigo = producto['codigo']
        if codigo not in self.carrito:
            self.carrito[codigo] = {
                'producto_id': codigo,
                'codigo': codigo,
                'nombre': producto['nombre'],
                'precio': float(producto['precio']),
                'cantidad': 1,
                'imagen': producto.get('imagen', ''),
                'stock': producto.get('stock', 10)
            }
        else:
            self.carrito[codigo]['cantidad'] += 1
        self.guardar()

    def guardar(self):
        self.session['carrito'] = self.carrito
        self.session.modified = True

    def eliminar(self, codigo):
        if codigo in self.carrito:
            del self.carrito[codigo]
            self.guardar()

    def restar(self, codigo):
        if codigo in self.carrito:
            self.carrito[codigo]['cantidad'] -= 1
            if self.carrito[codigo]['cantidad'] <= 0:
                self.eliminar(codigo)
            self.guardar()

    def limpiar(self):
        self.session['carrito'] = {}
        self.session.modified = True

# Vista que carga los productos en la tienda

def tienda(request):
    productos = Product.objects.all()
    return render(request, "GatoTech/index.html", {'productos': productos})

# Agrega un producto al carrito desde una API externa

def agregar_producto(request, codigo):
    carrito = Carrito(request)
    api_url = f"http://localhost:5000/api/productos?codigo={codigo}"
    headers = {"Authorization": "0db5b48e-0027-4ace-9ed8-6a04cd3cd292"}
    
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        productos = response.json()

        if not productos:
            messages.error(request, "Producto no encontrado")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

        producto_api = productos[0]
        producto = {
            'codigo': producto_api['codigo'],
            'nombre': producto_api['nombre'],
            'precio': float(producto_api['precio']),
            'imagen': producto_api.get('imagen', ''),
            'stock': producto_api.get('stock', 1)
        }

        carrito.agregar(producto)
        messages.success(request, f"{producto['nombre']} agregado al carrito")

    except requests.exceptions.RequestException:
        messages.error(request, "Error al conectar con el servidor de productos")
    except Exception as e:
        messages.error(request, f"Error inesperado: {str(e)}")

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

# Elimina un producto del carrito

def eliminar_producto(request, id_producto):
    carrito = Carrito(request)
    producto = get_object_or_404(Product, id_producto=id_producto)
    carrito.eliminar(producto)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

# Resta una unidad de un producto en el carrito

def restar_producto(request, codigo):
    carrito = Carrito(request)
    carrito.restar(codigo)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

# Limpia completamente el carrito

def limpiar_carrito(request):
    carrito = Carrito(request)
    carrito.limpiar()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

# Muestra el contenido actual del carrito con total

def carrito(request):
    carrito = request.session.get('carrito', {})
    total = sum(float(item['precio']) * item['cantidad'] for item in carrito.values())
    context = {
        'carrito': carrito,
        'total_carrito': total
    }
    return render(request, 'carrito/carrito.html', context)

# Captura los datos del usuario antes de iniciar el pago, con conversión de moneda

def datos_usuario_compra(request):
    carrito = request.session.get('carrito', {})
    if not carrito:
        messages.error(request, "No hay productos en el carrito")
        return redirect('carrito')

    try:
        total_carrito = sum(float(item['precio']) * item['cantidad'] for item in carrito.values())
        valor_dolar = obtener_tipo_cambio('USD')
        valor_euro = obtener_tipo_cambio('EUR')

        total_usd = round(total_carrito / valor_dolar, 2) if valor_dolar else None
        total_eur = round(total_carrito / valor_euro, 2) if valor_euro else None

        if request.method == 'POST':
            form = PedidoForm(request.POST)
            if form.is_valid():
                request.session['datos_compra'] = {
                    'form_data': form.cleaned_data,
                    'total_carrito': total_carrito
                }
                return redirect('iniciar_pago_webpay')
            else:
                messages.error(request, "Por favor corrige los errores en el formulario")
        else:
            initial_data = {}
            if request.user.is_authenticated:
                perfil_usuario = PerfilUsuario.objects.filter(email=request.user.email).first()
                if perfil_usuario:
                    initial_data = {
                        'nombre_usuario': perfil_usuario.nombre,
                        'apellido_usuario': perfil_usuario.apellido,
                        'telefono_usuario': perfil_usuario.telefono,
                        'email_usuario': perfil_usuario.email,
                        'rut_usuario': perfil_usuario.rut,
                    }
            form = PedidoForm(initial=initial_data)

        return render(request, 'carrito/continuacion_compra.html', {
            'form': form,
            'carrito': carrito,
            'total_carrito': total_carrito,
            'valor_dolar': valor_dolar,
            'valor_euro': valor_euro,
            'total_usd': total_usd,
            'total_eur': total_eur
        })

    except Exception as e:
        logger.error(f"Error en datos_usuario_compra: {str(e)}", exc_info=True)
        messages.error(request, "Ocurrió un error al procesar tu solicitud")
        return redirect('tienda')

# Muestra el checkout con precios convertidos a USD y EUR

def checkout_con_conversion(request):
    carrito = request.session.get('carrito', {})
    total_clp = sum(float(item['precio']) * item['cantidad'] for item in carrito.values())
    valor_dolar = obtener_tipo_cambio('USD')
    valor_euro = obtener_tipo_cambio('EUR')
    total_usd = round(total_clp / valor_dolar, 2) if valor_dolar else None
    total_eur = round(total_clp / valor_euro, 2) if valor_euro else None
    return render(request, 'checkout.html', {
        'total_clp': total_clp,
        'valor_dolar': valor_dolar,
        'valor_euro': valor_euro,
        'total_usd': total_usd,
        'total_eur': total_eur
    })

# Inicia la transacción de pago con WebPay

def iniciar_pago_webpay(request):
    carrito = request.session.get('carrito', {})
    if not carrito:
        messages.error(request, "No hay productos en el carrito")
        return redirect('carrito')

    total = int(sum(float(item['precio']) * item['cantidad'] for item in carrito.values()))

    tx = Transaction(WebpayOptions(
        commerce_code=settings.TRANSBANK["commerce_code"],
        api_key=settings.TRANSBANK["api_key"],
        integration_type=IntegrationType.TEST
    ))

    buy_order = str(int(datetime.now().timestamp()))[:26]
    session_id = request.session.session_key or "sess_" + str(uuid.uuid4())[:8]
    return_url = request.build_absolute_uri('/webpay/respuesta/')

    try:
        response = tx.create(buy_order=buy_order, session_id=session_id, amount=total, return_url=return_url)
        token = getattr(response, 'token', response.get('token'))
        url = getattr(response, 'url', response.get('url'))

        if not token or not url:
            raise ValueError("Respuesta de WebPay incompleta")

        request.session['webpay_data'] = {
            'token': token,
            'buy_order': buy_order,
            'amount': total,
            'session_id': session_id
        }
        return redirect(f"{url}?token_ws={token}")

    except Exception as e:
        logger.error(f"Error al iniciar pago WebPay: {str(e)}", exc_info=True)
        messages.error(request, f"Error al iniciar el pago: {str(e)}")
        return redirect('datos_usuario_compra')

# Procesa la respuesta de WebPay después del pago

def webpay_respuesta(request):
    token = request.GET.get("token_ws")
    if not token:
        return render(request, "gt_store/pago_error.html", {"error": "Token no proporcionado"})

    webpay_data = request.session.get('webpay_data', {})
    datos_compra = request.session.get('datos_compra', {})

    tx = Transaction(WebpayOptions(
        commerce_code=settings.TRANSBANK["commerce_code"],
        api_key=settings.TRANSBANK["api_key"],
        integration_type=IntegrationType.TEST
    ))

    try:
        commit_response = tx.commit(token)
        if commit_response.response_code == 0:
            request.session.pop('carrito', None)
            request.session.pop('datos_compra', None)
            request.session.pop('webpay_data', None)
            return redirect('pago_exitoso')
        else:
            error_msg = f"Código de error: {commit_response.response_code}"
            logger.error(f"Error en WebPay: {error_msg}")
            return render(request, "gt_store/pago_error.html", {"error": error_msg})

    except Exception as e:
        logger.error(f"Error en webpay_respuesta: {str(e)}")
        return render(request, "gt_store/pago_error.html", {"error": "Error al procesar el pago"})

# Obtiene el tipo de cambio desde mindicador.cl como respaldo

def obtener_tipo_cambio(moneda='USD'):
    try:
        response = requests.get('https://mindicador.cl/api')
        data = response.json()
        if moneda.upper() == 'USD':
            return float(data['dolar']['valor'])
        elif moneda.upper() == 'EUR':
            return float(data['euro']['valor'])
        else:
            raise ValueError("Moneda no soportada")
    except Exception as e:
        logger.error(f"Error al obtener tipo de cambio: {str(e)}", exc_info=True)
        return None