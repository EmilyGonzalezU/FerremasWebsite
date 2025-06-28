from django.test import TestCase

# Create your tests here.
from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch

class CarritoApiExternasTests(TestCase):
    def setUp(self):
        self.client = Client()
    
    @patch('requests.get')  # Aquí se parchea 'requests.get' usado en tu vista
    def test_agregar_producto_api_externa(self, mock_get):
        # Configuramos la respuesta simulada de la API externa
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [
            {
                'codigo': 'P123',
                'nombre': 'Producto de prueba',
                'precio': 100.0,
                'imagen': 'img.jpg',
                'stock': 5
            }
        ]

        url = reverse('Add', args=['P123'])  # Ruta para agregar producto
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)  # Esperamos redirección
        carrito = self.client.session.get('carrito')
        self.assertIsNotNone(carrito)
        self.assertIn('P123', carrito)
        self.assertEqual(carrito['P123']['nombre'], 'Producto de prueba')
