from typing import Self
import uuid
import json
import logging
from django.urls import reverse
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
                'acumulado': float(producto['precio']),
                'imagen': producto.get('imagen', ''),
                'stock': producto.get('stock', 10)
            }
        else:
            self.carrito[codigo]['cantidad'] += 1
            self.carrito[codigo]['acumulado'] = self.carrito[codigo]['precio'] * self.carrito[codigo]['cantidad'] 
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
            self.carrito[codigo]['acumulado'] = self.carrito[codigo]['precio'] * self.carrito[codigo]['cantidad']  # Actualiza acumulado
            if self.carrito[codigo]['cantidad'] <= 0:
                self.eliminar(codigo)
            self.guardar()

    def limpiar(self):
        self.session['carrito'] = {}
        self.session.modified = True


def tienda(request):
    productos = Product.objects.all()
    return render(request, "GatoTech/index.html", {'productos': productos})


def agregar_producto(request, codigo):
    carrito = Carrito(request)
    
    api_url = f"https://ferremasapi.onrender.com/api/productos?codigo={codigo}"
    headers = {"Authorization": "b0e01ad6-5479-41b5-97a1-1bfd7cddc3d8"}
    
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


def eliminar_producto(request, id_producto):
    carrito = Carrito(request)
    producto = get_object_or_404(Product, id_producto=id_producto)
    carrito.eliminar(producto)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def restar_producto(request, codigo):
    carrito = Carrito(request)
    carrito.restar(codigo)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def limpiar_carrito(request):
    carrito = Carrito(request)
    carrito.limpiar()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def carrito(request):
    carrito = request.session.get('carrito', {})
    total = sum(float(item['precio']) * item['cantidad'] for item in carrito.values())
    context = {
        'carrito': carrito,
        'total_carrito': total
    }
    return render(request, 'carrito/carrito.html', context)


def datos_usuario_compra(request):
    carrito = request.session.get('carrito', {})
    if not carrito:
        messages.error(request, "No hay productos en el carrito")
        return redirect('carrito')

    try:
        total_carrito = sum(float(item['precio']) * item['cantidad'] for item in carrito.values())

        if request.method == 'POST':
            form = PedidoForm(request.POST)
            if form.is_valid():
                request.session['datos_compra'] = {
                    'form_data': form.cleaned_data,
                    'total_carrito': total_carrito
                }
                request.session['carrito_para_pago'] = carrito.copy()

                return redirect('iniciar_pago_webpay')
            else:
                messages.error(request, "Por favor corrige los errores en el formulario")
        else:
            initial_data = {}
            
            user_email = request.session.get('user_email')
            if user_email:
                perfil_usuario = PerfilUsuario.objects.filter(email=user_email).first()
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
            'is_logged_in': request.user.is_authenticated or 'user_email' in request.session  # Para saber si mostrar campos como readonly
        })

    except Exception as e:
        logger.error(f"Error en datos_usuario_compra: {str(e)}", exc_info=True)
        messages.error(request, "Ocurrió un error al procesar tu solicitud")
        return redirect('inicio')
    


def iniciar_pago_webpay(request):
    carrito = request.session.get('carrito', {})
    if not carrito:
        messages.error(request, "No hay productos en el carrito")
        return redirect('carrito')

    total = sum(float(item['precio']) * item['cantidad'] for item in carrito.values())
    total = int(round(total))

    if total <= 0:
        messages.error(request, "El monto total debe ser mayor a cero")
        return redirect('datos_usuario_compra')

    tx = Transaction(WebpayOptions(
        commerce_code=settings.TRANSBANK["commerce_code"],
        api_key=settings.TRANSBANK["api_key"],
        integration_type=IntegrationType.TEST
    ))

    buy_order = str(int(datetime.now().timestamp()))[:26]
    session_id = request.session.session_key or "sess_" + str(uuid.uuid4())[:8]
    return_url = request.build_absolute_uri('/carrito/webpay/respuesta/')

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

        request.session['carrito_para_pago'] = carrito

        return redirect(f"{url}?token_ws={token}")

    except Exception as e:
        logger.error(f"Error al iniciar pago WebPay: {str(e)}", exc_info=True)
        messages.error(request, f"Error al iniciar el pago: {str(e)}")
        return redirect('datos_usuario_compra')
    
def webpay_respuesta(request):
    token = request.GET.get("token_ws")
    if not token:
        return redirect('pago_rechazado')

    try:
        tx = Transaction(WebpayOptions(
            commerce_code=settings.TRANSBANK["commerce_code"],
            api_key=settings.TRANSBANK["api_key"],
            integration_type=IntegrationType.TEST
        ))
        
        commit_response = tx.commit(token)

        response_code = getattr(commit_response, 'response_code', None)
        if response_code is None and isinstance(commit_response, dict):
            response_code = commit_response.get('response_code')

        if response_code == 0:
            webpay_data = request.session.get('webpay_data', {})
            carrito = request.session.get('carrito_para_pago', {})
            datos_compra = request.session.get('datos_compra', {}).get('form_data', {})

            request.session['transaccion_exitosa'] = {
                'buy_order': webpay_data.get('buy_order'),
                'amount': webpay_data.get('amount'),
                'authorization_code': getattr(commit_response, 'authorization_code', ''),
                'transaction_date': getattr(commit_response, 'transaction_date', '') or datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'card_number': getattr(getattr(commit_response, 'card_detail', None), 'card_number', '')[-4:],
                'payment_type': getattr(commit_response, 'payment_type_code', ''),
                'nombre_cliente': datos_compra.get('nombre_usuario'),
                'email_cliente': datos_compra.get('email_usuario'),
                'rut_cliente': datos_compra.get('rut_usuario'),
                'productos': [
                    {
                        'nombre': item['nombre'],
                        'precio': item['precio'],
                        'cantidad': item['cantidad'],
                        'subtotal': item['precio'] * item['cantidad']
                    } for item in carrito.values()
                ],
                'total': webpay_data.get('amount')
            }

            for key in ['carrito', 'carrito_para_pago', 'datos_compra', 'webpay_data']:
                request.session.pop(key, None)

            return redirect('pago_exitoso')
        else:
            webpay_data = request.session.get('webpay_data', {})
            carrito = request.session.get('carrito_para_pago', {})
            datos_compra = request.session.get('datos_compra', {}).get('form_data', {})

            request.session['error_pago'] = {
                'codigo': response_code,
                'mensaje': f"Transbank rechazó el pago. Código: {response_code}",
                'buy_order': webpay_data.get('buy_order'),
                'card_number': getattr(getattr(commit_response, 'card_detail', None), 'card_number', '')[-4:],
                'payment_type': getattr(commit_response, 'payment_type_code', ''),
                'nombre_cliente': datos_compra.get('nombre_usuario'),
                'email_cliente': datos_compra.get('email_usuario'),
                'rut_cliente': datos_compra.get('rut_usuario'),
                'productos': [
                    {
                        'nombre': item['nombre'],
                        'precio': item['precio'],
                        'cantidad': item['cantidad'],
                        'subtotal': item['precio'] * item['cantidad']
                    } for item in carrito.values()
                ],
                'total': sum(item['precio'] * item['cantidad'] for item in carrito.values())
            }
            
            return redirect('pago_rechazado')

    except Exception as e:
        logger.error(f"Error en webpay_respuesta: {str(e)}", exc_info=True)
        request.session['error_pago'] = {
            'codigo': 'ERROR',
            'mensaje': f"Error al procesar el pago: {str(e)}",
            'productos': [
                {
                    'nombre': item['nombre'],
                    'precio': item['precio'],
                    'cantidad': item['cantidad'],
                    'subtotal': item['precio'] * item['cantidad']
                } for item in request.session.get('carrito_para_pago', {}).values()
            ]
        }
        return redirect('pago_rechazado')

    
def pago_exitoso(request):
    transaccion_data = request.session.get('transaccion_exitosa', {})
    if not transaccion_data:
        return redirect('inicio')

    context = {
        'nombre_cliente': transaccion_data.get('nombre_cliente', 'Cliente'),
        'email_cliente': transaccion_data.get('email_cliente', '---'),
        'rut_cliente': transaccion_data.get('rut_cliente', '---'),
        'numero_orden': transaccion_data.get('buy_order', '---'),
        'fecha': transaccion_data.get('transaction_date', '---'),
        'estado': 'Aprobado',
        'tipo_pago': transaccion_data.get('payment_type', '---'),
        'tarjeta': f"**** **** **** {transaccion_data.get('card_number', '')}",
        'autorizacion': transaccion_data.get('authorization_code', '---'),
        'productos': transaccion_data.get('productos', []),
        'total': transaccion_data.get('total', 0)
    }

    request.session.pop('transaccion_exitosa', None)

    return render(request, 'carrito/pago_exito.html', context)

def pago_rechazado(request):
    error_data = request.session.get('error_pago', {})
    carrito = request.session.get('carrito_para_pago', {})
    datos_compra = request.session.get('datos_compra', {}).get('form_data', {})

    context = {
        'numero_orden': error_data.get('buy_order', '---'),
        'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'estado': 'Rechazado',
        'tipo_pago': error_data.get('payment_type', '---'),
        'tarjeta': f"**** **** **** {error_data.get('card_number', '')}",
        'codigo_error': error_data.get('codigo', 'No disponible'),
        'mensaje_error': error_data.get('mensaje', 'El pago fue rechazado o cancelado.'),
        'nombre_cliente': error_data.get('nombre_cliente', datos_compra.get('nombre_usuario', 'Cliente')),
        'email_cliente': error_data.get('email_cliente', datos_compra.get('email_usuario', '---')),
        'rut_cliente': error_data.get('rut_cliente', datos_compra.get('rut_usuario', '---')),
        'productos': error_data.get('productos', [
            {
                'nombre': item['nombre'],
                'precio': item['precio'],
                'cantidad': item['cantidad'],
                'subtotal': item['precio'] * item['cantidad']
            } for item in carrito.values()
        ]),
        'total': error_data.get('total', sum(item['precio'] * item['cantidad'] for item in carrito.values()))
    }

    return render(request, "carrito/pago_rechazado.html", context)