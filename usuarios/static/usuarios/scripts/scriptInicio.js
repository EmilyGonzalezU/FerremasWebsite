document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('sing-up-form');
    
    const validarEmail = () => {
        const email = document.getElementById('email').value.trim();
        const errorElement = document.getElementById('msgErrorMailInicio');
        
        if (email === "") {
            errorElement.textContent = "Ingrese su e-mail.";
            return false;
        } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
            errorElement.textContent = "Ingrese un e-mail válido.";
            return false;
        } else {
            errorElement.textContent = "";
            return true;
        }
    };

    const validarPassword = () => {
        const pass = document.getElementById('password').value;
        const errorElement = document.getElementById('msgErrorPassInicio');
        
        if (pass === "" || pass.length < 8) {
            errorElement.textContent = "Ingrese su contraseña (mínimo 8 caracteres).";
            return false;
        } else {
            errorElement.textContent = "";
            return true;
        }
    };

    form.addEventListener('submit', function(e) {
        if (!validarEmail() || !validarPassword()) {
            e.preventDefault();
        }
    });

    // Validación en tiempo real
    document.getElementById('email').addEventListener('input', validarEmail);
    document.getElementById('password').addEventListener('input', validarPassword);
});