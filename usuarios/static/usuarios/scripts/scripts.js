document.addEventListener('DOMContentLoaded', function() {
    // Configuración de validación
    const config = {
        id_nombre: {
            regex: /^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/,
            errorEmpty: "Por favor ingrese su nombre",
            errorInvalid: "Solo se permiten letras y espacios"
        },
        id_apellido: {
            regex: /^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/,
            errorEmpty: "Por favor ingrese su apellido",
            errorInvalid: "Solo se permiten letras y espacios"
        },
        id_email: {
            regex: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
            errorEmpty: "Por favor ingrese su email",
            errorInvalid: "Ingrese un email válido"
        },
        id_telefono: {
            regex: /^\d{8,12}$/,
            errorEmpty: "Por favor ingrese su teléfono",
            errorInvalid: "Debe tener entre 8 y 12 dígitos"
        },
        id_rut: {
            validator: Fn.validaRut,
            errorEmpty: "Por favor ingrese su RUT",
            errorInvalid: "Ingrese un RUT válido (ej: 12345678-9)"
        },
        id_pass: {
            minLength: 8,
            errorEmpty: "Por favor ingrese una contraseña",
            errorInvalid: "La contraseña debe tener al menos 8 caracteres"
        }
    };

    // Función para validar RUT
    const Fn = {
        validaRut: function(rutCompleto) {
            if (!rutCompleto) return false;
            rutCompleto = rutCompleto.replace("‐", "-").replace(/\./g, "");
            if (!/^[0-9]+[-|‐]{1}[0-9kK]{1}$/.test(rutCompleto))
                return false;
            var tmp = rutCompleto.split('-');
            var digv = tmp[1];
            var rut = tmp[0];
            if (digv == 'K') digv = 'k';
            return (this.dv(rut) == digv);
        },
        dv: function(T) {
            var M = 0, S = 1;
            for (; T; T = Math.floor(T / 10))
                S = (S + T % 10 * (9 - M++ % 6)) % 11;
            return S ? S - 1 : 'k';
        }
    };

    // Función de validación genérica
    function validarCampo(campo, config) {
        const value = campo.value.trim();
        const errorElement = campo.closest('.has-validation').querySelector('.invalid-feedback');
        
        // Limpiar errores anteriores
        campo.classList.remove('is-invalid');
        
        if (!value) {
            campo.classList.add('is-invalid');
            errorElement.textContent = config.errorEmpty;
            return false;
        }
        
        if (config.validator) {
            if (!config.validator(value)) {
                campo.classList.add('is-invalid');
                errorElement.textContent = config.errorInvalid;
                return false;
            }
        } else if (config.regex && !config.regex.test(value)) {
            campo.classList.add('is-invalid');
            errorElement.textContent = config.errorInvalid;
            return false;
        } else if (config.minLength && value.length < config.minLength) {
            campo.classList.add('is-invalid');
            errorElement.textContent = config.errorInvalid;
            return false;
        }
        
        return true;
    }

    // Añadir event listeners
    const form = document.querySelector('form');
    
    // Validación en tiempo real
    Object.keys(config).forEach(fieldId => {
        const campo = document.getElementById(fieldId);
        if (campo) {
            campo.addEventListener('blur', () => validarCampo(campo, config[fieldId]));
            campo.addEventListener('input', () => {
                if (campo.classList.contains('is-invalid')) {
                    validarCampo(campo, config[fieldId]);
                }
            });
        }
    });

    // Validar al enviar el formulario
    form.addEventListener('submit', function(event) {
        let esValido = true;
        form.classList.add('was-validated');
        
        Object.keys(config).forEach(fieldId => {
            const campo = document.getElementById(fieldId);
            if (campo && !validarCampo(campo, config[fieldId])) {
                esValido = false;
            }
        });
        
        if (!esValido) {
            event.preventDefault();
            event.stopPropagation();
            
            const primerError = form.querySelector('.is-invalid');
            if (primerError) {
                primerError.focus();
            }
        }
    }, false);
});