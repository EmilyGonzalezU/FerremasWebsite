document.addEventListener('DOMContentLoaded', function() {
    // Configuración de validación
    const config = {
        nombre: {
            regex: /^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/,
            errorEmpty: "Ingrese su nombre",
            errorInvalid: "Solo se permiten letras y espacios"
        },
        apellido: {
            regex: /^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/,
            errorEmpty: "Ingrese su apellido",
            errorInvalid: "Solo se permiten letras y espacios"
        },
        email: {
            regex: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
            errorEmpty: "Ingrese su e-mail",
            errorInvalid: "Ingrese un e-mail válido"
        },
        telefono: {
            regex: /^\d{8,12}$/,
            errorEmpty: "Ingrese su teléfono",
            errorInvalid: "Debe tener 8-12 dígitos"
        },
        rut: {
            validator: Fn.validaRut,
            errorEmpty: "Ingrese su RUT",
            errorInvalid: "Ingrese un RUT válido (ej: 12345678-9)"
        },
        pass: {
            minLength: 8,
            errorEmpty: "Ingrese su contraseña",
            errorInvalid: "Mínimo 8 caracteres"
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
        const errorElement = document.getElementById(`msgError${campo.id.charAt(0).toUpperCase() + campo.id.slice(1)}`);
        
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
        
        campo.classList.remove('is-invalid');
        errorElement.textContent = "";
        return true;
    }

    // Añadir event listeners
    const form = document.querySelector('form');
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
        
        Object.keys(config).forEach(fieldId => {
            const campo = document.getElementById(fieldId);
            if (campo && !validarCampo(campo, config[fieldId])) {
                esValido = false;
            }
        });
        
        if (!esValido) {
            event.preventDefault();
            // Enfocar el primer campo con error
            const primerError = form.querySelector('.is-invalid');
            if (primerError) {
                primerError.focus();
            }
        }
    });
});