from django import forms
from .models import PerfilUsuario
from django.contrib.auth.hashers import make_password
from django.core.validators import RegexValidator

class RegistroUsuarioForm(forms.ModelForm):
    contrasena = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control py-2',
            'id': 'pass',
            'required': 'required',
            'placeholder': 'Ingresa tu contraseña'
        }),
        min_length=8,
        error_messages={
            'required': 'La contraseña es obligatoria',
            'min_length': 'La contraseña debe tener al menos 8 caracteres'
        }
    )

    class Meta:
        model = PerfilUsuario
        fields = ['nombre', 'apellido', 'email', 'telefono', 'rut', 'contrasena']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control py-2',
                'id': 'nombre',
                'required': 'required',
                'placeholder': 'Ingresa tu nombre'
            }),
            'apellido': forms.TextInput(attrs={
                'class': 'form-control py-2',
                'id': 'apellido',
                'required': 'required',
                'placeholder': 'Ingresa tu apellido'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control py-2',
                'id': 'email',
                'required': 'required',
                'placeholder': 'tucorreo@ejemplo.com'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control py-2',
                'id': 'telefono',
                'required': 'required',
                'placeholder': 'Ingresa tu teléfono'
            }),
            'rut': forms.TextInput(attrs={
                'class': 'form-control py-2',
                'id': 'rut',
                'required': 'required',
                'placeholder': 'Ingresa tu RUT (sin puntos con guión)'
            }),
        }
        error_messages = {
            'nombre': {
                'required': 'El nombre es obligatorio'
            },
            'apellido': {
                'required': 'El apellido es obligatorio'
            },
            'email': {
                'required': 'El email es obligatorio',
                'invalid': 'Ingresa un email válido'
            },
            'telefono': {
                'required': 'El teléfono es obligatorio'
            },
            'rut': {
                'required': 'El RUT es obligatorio'
            }
        }

    def clean_telefono(self):
        telefono = self.cleaned_data['telefono']
        if not telefono.isdigit() or len(telefono) < 8:
            raise forms.ValidationError("El teléfono debe tener al menos 8 dígitos")
        return telefono

    def clean_rut(self):
        rut = self.cleaned_data['rut']
        # Aquí puedes añadir tu validación personalizada de RUT
        return rut

    def save(self, commit=True):
        user = super().save(commit=False)
        user.contrasena = make_password(self.cleaned_data['contrasena'])
        if commit:
            user.save()
        return user