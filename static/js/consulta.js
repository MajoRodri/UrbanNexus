document.addEventListener("DOMContentLoaded", () => {
    const editButtons = document.querySelectorAll(".js-edit");
    const cancelButtons = document.querySelectorAll(".js-cancel");
    const deleteButtons = document.querySelectorAll(".js-delete");

    editButtons.forEach((button) => {
        button.addEventListener("click", () => {
            const row = button.closest("tr");

            row.querySelectorAll(".view-mode").forEach((element) => {
                element.hidden = true;
            });

            row.querySelectorAll(".edit-mode").forEach((element) => {
                if (element.dataset.originalValue !== undefined) {
                    element.value = element.dataset.originalValue;
                }
                element.hidden = false;
            });
        });
    });

    cancelButtons.forEach((button) => {
        button.addEventListener("click", () => {
            const row = button.closest("tr");

            row.querySelectorAll(".edit-mode").forEach((element) => {
                element.hidden = true;
            });

            row.querySelectorAll(".view-mode").forEach((element) => {
                element.hidden = false;
            });
        });
    });

    deleteButtons.forEach((button) => {
        button.addEventListener("click", () => {
            const confirmed = confirm(
                "¿Seguro que quieres eliminar este registro?"
            );

            if (!confirmed) {
                return;
            }

            const form = document.createElement("form");

            form.method = "POST";

            form.action = button.dataset.deleteUrl;

            document.body.appendChild(form);

            form.submit();

        });

    });
});