def total_carrito(request):
    carrito = request.session.get('carrito', {})
    total = sum(
        float(item['precio']) * item['cantidad']
        for item in carrito.values()
    )
    return {'total_carrito': total}