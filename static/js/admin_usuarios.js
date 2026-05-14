document.addEventListener("DOMContentLoaded", () => {
    const deleteForms = document.querySelectorAll(".delete-user-form");

    deleteForms.forEach((form) => {
        form.addEventListener("submit", (event) => {
            const confirmar = confirm("¿Seguro que quieres eliminar este usuario? Esta acción no se puede deshacer.");

            if (!confirmar) {
                event.preventDefault();
            }
        });
    });
});