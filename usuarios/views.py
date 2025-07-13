from django.shortcuts import render, redirect
from .forms import RegistroUsuarioForm  
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from .models import PerfilUsuario
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout

def registro_usuario(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('inicio')
    else:
        form = RegistroUsuarioForm()
    
    return render(request, 'tu_template.html', {
        'form': form,
        'form_class': 'was-validated' if request.method == 'POST' else ''
    })
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import LoginForm  # Asegúrate de tener este formulario

def inicio_sesion(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                login(request, user)
                return redirect('pagina_principal')  # Redirige a tu página principal
            else:
                messages.error(request, "Correo electrónico o contraseña incorrectos")
        # Si el formulario no es válido, se mostrarán los errores automáticamente
    else:
        form = LoginForm()
    
    return render(request, 'tu_template_login.html', {'form': form})

@csrf_exempt
def login_view(request):
    context = {}
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        nombre = request.POST.get('nombre')
        form_source = request.POST.get('form_source')

        if not email:
            context['email_error'] = "Ingrese su e-mail."
        elif not ("@" in email and "." in email):
            context['email_error'] = "Ingrese un e-mail válido."
        else:
            try:
                user = PerfilUsuario.objects.get(email=email)
                if check_password(password, user.contrasena):
                    request.session['user_id'] = user.id
                    request.session['user_nombre'] = user.nombre
                    request.session['user_apellido'] = user.apellido
                    request.session['user_telefono'] = user.telefono
                    request.session['user_email'] = user.email
                    request.session['user_rut'] = user.rut
                    return redirect('inicio')
                else:
                    context['password_error'] = "Contraseña incorrecta."
            except PerfilUsuario.DoesNotExist:
                context['email_error'] = "El email no existe."

        if not password or len(password) < 8:
            context['password_error'] = "Ingrese su contraseña (mínimo 8 caracteres)."

        if form_source == 'modal':
            context['modal_errors'] = True

    return render(request, 'usuarios/inicioSesion.html', context)


def login_usuario (request):
    return render(request, 'usuarios/usuario.html')



def cerrar_sesion(request):
    logout(request)
    return redirect('inicio') 
#Tipo usuario
def tipo_usuario(request):
    return render(request, 'usuarios/tipo_usuario.html')


