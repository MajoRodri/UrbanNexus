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

    function validarIdEmpleado(id) {
        return /^[A-Za-z0-9]{3,}$/.test(id);
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

            const idEmpleado = document.getElementById("id_empleado").value.trim();
            const password = document.getElementById("password").value.trim();

            clearErrors("idEmpleadoError", "passwordError");

            if (!validarIdEmpleado(idEmpleado)) {
                showError("idEmpleadoError", "Introduce un ID de empleado válido (Ej: E4821T).");
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

            const nombres = document.getElementById("nombres").value.trim();
            const apellidos = document.getElementById("apellidos").value.trim();
            const password = document.getElementById("password").value.trim();
            const confirmPassword = document.getElementById("confirm_password").value.trim();

            clearErrors("nombresError", "apellidosError", "passwordError", "confirmPasswordError");

            if (nombres.length === 0) {
                showError("nombresError", "El nombre es obligatorio.");
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
