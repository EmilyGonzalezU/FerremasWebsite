document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('login-form');
    const emailInput = document.getElementById('id_email');
    const passwordInput = document.getElementById('id_password');
    
    // Función para validar email
    const validarEmail = () => {
        const email = emailInput.value.trim();
        const errorElement = emailInput.closest('.has-validation').querySelector('.invalid-feedback');
        
        if (!email) {
            emailInput.classList.add('is-invalid');
            errorElement.textContent = "Por favor ingrese su correo electrónico";
            return false;
        }
        
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
            emailInput.classList.add('is-invalid');
            errorElement.textContent = "Por favor ingrese un correo electrónico válido";
            return false;
        }
        
        emailInput.classList.remove('is-invalid');
        errorElement.textContent = "";
        return true;
    };

    // Función para validar contraseña
    const validarPassword = () => {
        const password = passwordInput.value;
        const errorElement = passwordInput.closest('.has-validation').querySelector('.invalid-feedback');
        
        if (!password) {
            passwordInput.classList.add('is-invalid');
            errorElement.textContent = "Por favor ingrese su contraseña";
            return false;
        }
        
        if (password.length < 8) {
            passwordInput.classList.add('is-invalid');
            errorElement.textContent = "La contraseña debe tener al menos 8 caracteres";
            return false;
        }
        
        passwordInput.classList.remove('is-invalid');
        errorElement.textContent = "";
        return true;
    };

    // Validación en tiempo real
    emailInput.addEventListener('input', function() {
        if (emailInput.classList.contains('is-invalid')) {
            validarEmail();
        }
    });

    passwordInput.addEventListener('input', function() {
        if (passwordInput.classList.contains('is-invalid')) {
            validarPassword();
        }
    });

    // Validación al perder foco
    emailInput.addEventListener('blur', validarEmail);
    passwordInput.addEventListener('blur', validarPassword);

    // Validar al enviar el formulario
    form.addEventListener('submit', function(e) {
        form.classList.add('was-validated');
        
        const emailValido = validarEmail();
        const passwordValido = validarPassword();
        
        if (!emailValido || !passwordValido) {
            e.preventDefault();
            
            // Enfocar el primer campo con error
            if (!emailValido) {
                emailInput.focus();
            } else if (!passwordValido) {
                passwordInput.focus();
            }
        }
    });
});