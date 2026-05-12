import requests

from flask import Blueprint, request, redirect, url_for, session, flash


auth_bp = Blueprint("auth", __name__)

FASTAPI_BASE_URL = "http://127.0.0.1:8000/api/v1"


@auth_bp.route("/registro_usuario", methods=["POST"])
def registrar_usuario():
    nombres = request.form.get("nombres", "").strip()
    apellidos = request.form.get("apellidos", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "").strip()
    confirm_password = request.form.get("confirm_password", "").strip()
    codigo_invitacion = request.form.get("codigo_invitacion", "").strip()

    if not nombres or not apellidos or not email or not password or not confirm_password or not codigo_invitacion:
        flash("Todos los campos son obligatorios.", "error")
        return redirect(url_for("view.registro_usuario"))

    if password != confirm_password:
        flash("Las contraseñas no coinciden.", "error")
        return redirect(url_for("view.registro_usuario"))

    try:
        respuesta = requests.post(
            f"{FASTAPI_BASE_URL}/auth/register",
            json={
                "nombres": nombres,
                "apellidos": apellidos,
                "email": email,
                "password": password,
                "codigo_invitacion": codigo_invitacion
            },
            timeout=5
        )

    except requests.exceptions.RequestException:
        flash("No se pudo conectar con la API. Revisa que FastAPI esté arrancado.", "error")
        return redirect(url_for("view.registro_usuario"))

    if respuesta.status_code == 200:
        flash("Registro completado correctamente. Ya puedes iniciar sesión.", "success")
        return redirect(url_for("view.login"))

    detalle = respuesta.json().get("detail", "Error al registrar usuario.")
    flash(detalle, "error")
    return redirect(url_for("view.registro_usuario"))


@auth_bp.route("/login", methods=["POST"])
def login():
    id_empleado = request.form.get("id_empleado", "").strip()
    password = request.form.get("password", "").strip()

    if not id_empleado or not password:
        flash("Introduce tu ID de empleado y contraseña.", "error")
        return redirect(url_for("view.login"))

    try:
        respuesta = requests.post(
            f"{FASTAPI_BASE_URL}/auth/login",
            json={
                "id_empleado": id_empleado,
                "password": password
            },
            timeout=5
        )

    except requests.exceptions.RequestException:
        flash("No se pudo conectar con la API. Revisa que FastAPI esté arrancado.", "error")
        return redirect(url_for("view.login"))

    if respuesta.status_code == 200:
        datos = respuesta.json()

        session["access_token"] = datos["access_token"]
        session["id_empleado"] = datos["id_empleado"]
        session["rol"] = datos["rol"]

        flash("Bienvenido.", "success")
        return redirect(url_for("view.index"))

    detalle = respuesta.json().get("detail", "Credenciales incorrectas.")
    flash(detalle, "error")
    return redirect(url_for("view.login"))

@auth_bp.route("/crear_invitacion", methods=["POST"])
def crear_invitacion():
    if not session.get("id_empleado"):
        flash("Debes iniciar sesión para crear invitaciones.", "error")
        return redirect(url_for("view.login"))

    if session.get("rol") != "admin":
        flash("No tienes permisos para crear invitaciones.", "error")
        return redirect(url_for("view.index"))

    nombres = request.form.get("nombres", "").strip()
    apellidos = request.form.get("apellidos", "").strip()
    email = request.form.get("email", "").strip()
    rol = request.form.get("rol", "").strip()

    if not nombres or not apellidos or not email or not rol:
        flash("Todos los campos son obligatorios.", "error")
        return redirect(url_for("view.admin_invitaciones"))

    try:
        respuesta = requests.post(
            f"{FASTAPI_BASE_URL}/invitations/create",
            json={
                "nombres": nombres,
                "apellidos": apellidos,
                "email": email,
                "rol": rol
            },
            timeout=8
        )

    except requests.exceptions.RequestException:
        flash("No se pudo conectar con la API. Revisa que FastAPI esté arrancado.", "error")
        return redirect(url_for("view.admin_invitaciones"))

    if respuesta.status_code == 200:
        flash("Invitación enviada correctamente.", "success")
        return redirect(url_for("view.admin_invitaciones"))

    detalle = respuesta.json().get("detail", "Error al crear la invitación.")
    flash(detalle, "error")
    return redirect(url_for("view.admin_invitaciones"))


@auth_bp.route("/logout")
def logout():
    session.pop("access_token", None)
    session.pop("id_empleado", None)
    session.pop("rol", None)
    session.pop("email", None)

    flash("Sesión cerrada correctamente.", "success")
    return redirect(url_for("view.index"))