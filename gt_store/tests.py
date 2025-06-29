from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch

class ApiIntegracionTests(TestCase):
    def setUp(self):
        self.client = Client()

    @patch('requests.get')
    def test_index_api_categorias(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [{
            "codigo_producto": 1,
            "categoria": "herramientas manuales",
            "marca": "Truper",
            "codigo": "H123",
            "nombre": "Martillo",
            "precio": 8990,
            "dscto": 10,
            "stock": 5,
            "precio_anterior": 9990,
            "imagen": "martillo.jpg",
            "descripcion": "Martillo de carpintero",
            "sucursal_id": 1
        }]

        response = self.client.get(reverse('inicio'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('herramientas_manuales', response.context)
        self.assertTrue(len(response.context['herramientas_manuales']) > 0)

    @patch('requests.get')
    def test_detalle_producto_api(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [{
            "codigo_producto": 2,
            "categoria": "herramientas manuales",
            "marca": "Stanley",
            "codigo": "H124",
            "nombre": "Destornillador",
            "precio": 4990,
            "dscto": 5,
            "stock": 10,
            "precio_anterior": 5990,
            "imagen": "destornillador.jpg",
            "descripcion": "Destornillador multipropósito",
            "sucursal_id": 1
        }]

        response = self.client.get(reverse('detalle_producto', args=['H124']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Destornillador')

    @patch('requests.get')
    def test_herramientas_manuales_api(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [{
            "codigo_producto": 3,
            "categoria": "herramientas manuales",
            "marca": "Bosch",
            "codigo": "H125",
            "nombre": "Sierra Manual",
            "precio": 12990,
            "dscto": 15,
            "stock": 7,
            "precio_anterior": 14990,
            "imagen": "sierra.jpg",
            "descripcion": "Sierra manual para madera",
            "sucursal_id": 1
        }]

        response = self.client.get(reverse('herramientas_manuales'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sierra Manual')

    @patch('requests.get')
    def test_materiales_basicos_api(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [{
            "codigo_producto": 4,
            "categoria": "materiales basicos",
            "marca": "Cementos Melón",
            "codigo": "M200",
            "nombre": "Cemento Gris",
            "precio": 5990,
            "dscto": 0,
            "stock": 50,
            "precio_anterior": None,
            "imagen": "cemento.jpg",
            "descripcion": "Saco de cemento 25 kg",
            "sucursal_id": 1
        }]

        response = self.client.get(reverse('materiales_basicos'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cemento Gris')

    @patch('requests.get')
    def test_equipos_seguridad_api(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [{
            "codigo_producto": 5,
            "categoria": "equipos de seguridad",
            "marca": "3M",
            "codigo": "E300",
            "nombre": "Casco de Seguridad",
            "precio": 7990,
            "dscto": 0,
            "stock": 20,
            "precio_anterior": None,
            "imagen": "casco.jpg",
            "descripcion": "Casco para obra",
            "sucursal_id": 1
        }]

        response = self.client.get(reverse('equipos_seguridad'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Casco de Seguridad')
