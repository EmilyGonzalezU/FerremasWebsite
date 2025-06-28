#Test
from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import PerfilUsuario
from django.contrib.auth.hashers import make_password

class UsuarioTests(TestCase):

    def setUp(self):
        self.user_password = 'password123'
        self.usuario = PerfilUsuario.objects.create(
            nombre='Emily',
            apellido='Gonzalez',
            email='emily@ferremas.com',
            contrasena=make_password(self.user_password),
            telefono='123456789',
            rut='12345678-9'
        )
        self.client = Client()

    def test_registro_usuario_get(self):
        response = self.client.get(reverse('registro'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'usuarios/registro.html')

    def test_registro_usuario_post_valido(self):
        data = {
            'nombre': 'Osvaldo',
            'apellido': 'Reyes',
            'email': 'osr@ferremas.com',
            'contrasena': 'pass123456',
            'telefono': '987654321',
            'rut': '98765432-1',
        }
        response = self.client.post(reverse('registro'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(PerfilUsuario.objects.filter(email='osr@ferremas.com').exists())

    def test_login_usuario_correcto(self):
        data = {
            'email': self.usuario.email,
            'password': self.user_password,
        }
        response = self.client.post(reverse('inicio_sesion'), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session['user_email'], self.usuario.email)

    def test_login_usuario_incorrecto(self):
        data = {
            'email': self.usuario.email,
            'password': 'password1234',
        }
        response = self.client.post(reverse('inicio_sesion'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Contraseña incorrecta.")
