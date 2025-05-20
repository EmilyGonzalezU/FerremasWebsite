from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect
from gt_store.models import Product
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import  ProductoPedido
from .forms import PedidoForm
from usuarios.models import  PerfilUsuario
import requests
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

class Carrito:
    def __init__(self, request):
        self.request = request
        self.session = request.session
        carrito = self.session.get("carrito")
        if not carrito:
            self.session["carrito"] = {}
            self.carrito = self.session["carrito"]
        else:
            self.carrito = carrito

    def agregar(self, producto):
        id = str(producto.codigo)
        if id not in self.carrito.keys():
            self.carrito[id] = {
                "producto_id": producto.codigo,
                "imagen": producto.imagen,
                "nombre": producto.nombre,
                "stock": producto.stock,
                "acumulado_transferencia": producto.precio,
                "cantidad": 1,
            }
        else:
            self.carrito[id]["cantidad"] += 1
            self.carrito[id]["acumulado_transferencia"] += producto.precio

        self.guardar_carrito()

    def guardar_carrito(self):
        self.session["carrito"] = self.carrito
        self.session.modified = True

    def eliminar(self, producto):
        id = str(producto.id_producto)
        if id in self.carrito:
            del self.carrito[id]
            self.guardar_carrito()

    def restar(self, producto):
        id = str(producto.id_producto)
        if id in self.carrito.keys():
            self.carrito[id]["cantidad"] -= 1
            self.carrito[id]["acumulado_transferencia"] -= producto.precio_transferencia
            self.carrito[id]["acumulado_normal"] -= producto.precio_normal
            if self.carrito[id]["cantidad"] <= 0:
                self.eliminar(producto)
            self.guardar_carrito()

    def limpiar(self):
        self.session["carrito"] = {}
        self.session.modified = True

def tienda(request):
    productos = Product.objects.all()
    return render(request, "GatoTech/index.html", {'productos': productos})

def agregar_producto(request, codigo):
    carrito = Carrito(request)
    producto = get_object_or_404(Product, codigo=codigo)  # ✅ Use `codigo` instead of `id_producto`
    carrito.agregar(producto)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def eliminar_producto(request, id_producto):
    carrito = Carrito(request)
    producto = get_object_or_404(Product, id_producto=id_producto)
    carrito.eliminar(producto)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def restar_producto(request, id_producto):
    carrito = Carrito(request)
    producto = get_object_or_404(Product, id_producto=id_producto)
    carrito.restar(producto)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def limpiar_carrito(request):
    carrito = Carrito(request)
    carrito.limpiar()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def carrito(request):
    return render(request, 'carrito/carrito.html')

#Compra

def datos_usuario_compra(request):
    carrito = request.session.get('carrito', {})
    total_transferencia = sum(item['acumulado_transferencia'] for item in carrito.values())
    total_normal = sum(item['acumulado_normal'] for item in carrito.values())

    if request.method == 'POST':
        form = PedidoForm(request.POST)
        if form.is_valid():
            pedido = form.save(commit=False)
            
            if request.user.is_authenticated:
                pedido.usuario = request.user
                # Opcionalmente, puedes rellenar los campos del usuario con la información del perfil
                perfil_usuario = PerfilUsuario.objects.filter(email=request.user.email).first()
                if perfil_usuario:
                    pedido.nombre_usuario = perfil_usuario.nombre
                    pedido.apellido_usuario = perfil_usuario.apellido
                    pedido.telefono_usuario = perfil_usuario.telefono
                    pedido.email_usuario = perfil_usuario.email
                    pedido.rut_usuario = perfil_usuario.rut
            pedido.total_transferencia = total_transferencia
            pedido.total_normal = total_normal
            pedido.save()

            for item in carrito.values():
                try:
                    producto = Product.objects.get(id_producto=item['producto_id'])
                    ProductoPedido.objects.create(
                        pedido=pedido,
                        producto=producto,
                        cantidad=item['cantidad'],
                        precio=item['acumulado_normal']
                    )
                except Product.DoesNotExist:
                    messages.error(request, f"Producto con id {item['producto_id']} no encontrado.")
                    return redirect('carrito_datos')  

            for item in carrito.values():
                try:
                    producto = Product.objects.get(id_producto=item['producto_id'])
                    producto.stock -= item['cantidad']
                    producto.save()
                except Product.DoesNotExist:
                    messages.error(request, f"Producto con id {item['producto_id']} no encontrado al actualizar stock.")
                    return redirect('carrito_datos')  

            request.session.pop('carrito', None)

            messages.success(request, "Compra realizada con éxito.")
            return redirect('realizado')
    else:
        form = PedidoForm()

    context = {
        'form': form,
        'carrito': carrito,
    }

    return render(request, 'carrito/continuacion_compra.html', context)

#Pedido realizado
def pago_exitoso (request):
    return render(request, 'carrito/resultado.html')