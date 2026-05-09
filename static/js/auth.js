document.addEventListener("DOMContentLoaded", function () {

    const loginForm = document.getElementById("loginForm");
    const registroForm = document.getElementById("registroForm");

    function showError(elementId, message) {
        const el = document.getElementById(elementId);
        if (el) {
            el.textContent = message;
            el.style.color = "#f87171";
            el.style.fontSize = "0.78rem";
        }
    }

    function clearErrors(...ids) {
        ids.forEach(id => showError(id, ""));
    }

    function validarNumEmpleado(num) {
        return /^\d{6}$/.test(num);
    }

    function validarPassword(password) {
        if (password.length < 8) return "La contraseña debe tener al menos 8 caracteres.";
        if (!/[A-Z]/.test(password)) return "Debe contener al menos una letra mayúscula.";
        if (!/\d/.test(password)) return "Debe contener al menos un número.";
        return "";
    }

    if (loginForm) {
        loginForm.addEventListener("submit", function (e) {
            let valid = true;

            const numEmpleado = document.getElementById("num_empleado").value.trim();
            const password = document.getElementById("password").value.trim();

            clearErrors("numEmpleadoError", "passwordError");

            if (!validarNumEmpleado(numEmpleado)) {
                showError("numEmpleadoError", "Introduce un número de empleado válido (6 dígitos).");
                valid = false;
            }

            if (password.length === 0) {
                showError("passwordError", "La contraseña es obligatoria.");
                valid = false;
            }

            if (!valid) e.preventDefault();
        });
    }

    if (registroForm) {
        registroForm.addEventListener("submit", function (e) {
            let valid = true;

            const numEmpleado = document.getElementById("num_empleado").value.trim();
            const nombre = document.getElementById("nombre").value.trim();
            const apellidos = document.getElementById("apellidos").value.trim();
            const password = document.getElementById("password").value.trim();
            const confirmPassword = document.getElementById("confirm_password").value.trim();

            clearErrors("numEmpleadoError", "nombreError", "apellidosError", "passwordError", "confirmPasswordError");

            if (!validarNumEmpleado(numEmpleado)) {
                showError("numEmpleadoError", "El número de empleado debe tener 6 dígitos.");
                valid = false;
            }

            if (nombre.length === 0) {
                showError("nombreError", "El nombre es obligatorio.");
                valid = false;
            }

            if (apellidos.length === 0) {
                showError("apellidosError", "Los apellidos son obligatorios.");
                valid = false;
            }

            const errorPassword = validarPassword(password);
            if (errorPassword) {
                showError("passwordError", errorPassword);
                valid = false;
            }

            if (password !== confirmPassword) {
                showError("confirmPasswordError", "Las contraseñas no coinciden.");
                valid = false;
            }

            if (!valid) e.preventDefault();
        });
    }

});
