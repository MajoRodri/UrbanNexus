import requests

from flask import Blueprint, request, redirect, url_for, session, flash, render_template


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

    try:
        detalle = respuesta.json().get(
            "detail",
            "Error al registrar usuario."
        )
    except Exception:
        detalle = respuesta.text or "Error interno de la API."

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

        session.clear()
        session.permanent = False
        session["access_token"] = datos["access_token"]
        session["id_empleado"] = datos["id_empleado"]
        session["rol"] = datos["rol"]

        flash("Bienvenido.", "success")
        return redirect(url_for("view.index"))

    try:
        detalle = respuesta.json().get("detail", "Credenciales incorrectas.")
    except Exception:
        detalle = respuesta.text or "Credenciales incorrectas."
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
            headers={
                "Authorization": f"Bearer {session.get('access_token')}"
            },
            timeout=8
        )

    except requests.exceptions.RequestException:
        flash("No se pudo conectar con la API. Revisa que FastAPI esté arrancado.", "error")
        return redirect(url_for("view.admin_invitaciones"))

    if respuesta.status_code == 200:
        flash("Invitación enviada correctamente.", "success")
        return redirect(url_for("view.admin_invitaciones"))

    try:
        detalle = respuesta.json().get("detail", "Error al crear la invitación.")
    except Exception:
        detalle = respuesta.text or "Error al crear la invitación."
    flash(detalle, "error")
    return redirect(url_for("view.admin_invitaciones"))

@auth_bp.route("/admin/usuarios")
def admin_usuarios():
    if session.get("rol") != "admin":
        flash("No tienes permisos para gestionar usuarios.", "error")
        return redirect(url_for("view.index"))

    try:
        respuesta = requests.get(
            f"{FASTAPI_BASE_URL}/users",
            headers={
                "Authorization": f"Bearer {session.get('access_token')}"
            },
            timeout=8
        )

        if respuesta.status_code != 200:
            flash("No se pudieron cargar los usuarios.", "error")
            return redirect(url_for("view.index"))

        return render_template(
            "admin_usuarios.html",
            usuarios=respuesta.json()
        )

    except requests.exceptions.RequestException:
        flash("No se pudo conectar con la API.", "error")
        return redirect(url_for("view.index"))


@auth_bp.route("/admin/usuarios/<id_empleado>/rol", methods=["POST"])
def cambiar_rol_usuario(id_empleado):
    if session.get("rol") != "admin":
        flash("No tienes permisos para cambiar roles.", "error")
        return redirect(url_for("view.index"))

    nuevo_rol = request.form.get("rol")

    try:
        respuesta = requests.put(
            f"{FASTAPI_BASE_URL}/users/{id_empleado}/role",
            params={"rol": nuevo_rol},
            headers={
                "Authorization": f"Bearer {session.get('access_token')}"
            },
            timeout=8
        )

        if respuesta.status_code == 200:
            flash("Rol actualizado correctamente.", "success")
        else:
            flash("No se pudo actualizar el rol.", "error")

    except requests.exceptions.RequestException:
        flash("No se pudo conectar con la API.", "error")

    return redirect(url_for("auth.admin_usuarios"))


@auth_bp.route("/admin/usuarios/<id_empleado>/estado", methods=["POST"])
def cambiar_estado_usuario(id_empleado):
    if session.get("rol") != "admin":
        flash("No tienes permisos para cambiar estados.", "error")
        return redirect(url_for("view.index"))

    activo = request.form.get("activo") == "true"

    try:
        respuesta = requests.put(
            f"{FASTAPI_BASE_URL}/users/{id_empleado}/state",
            params={"activo": activo},
            headers={
                "Authorization": f"Bearer {session.get('access_token')}"
            },
            timeout=8
        )

        if respuesta.status_code == 200:
            flash("Estado actualizado correctamente.", "success")
        else:
            flash("No se pudo actualizar el estado.", "error")

    except requests.exceptions.RequestException:
        flash("No se pudo conectar con la API.", "error")

    return redirect(url_for("auth.admin_usuarios"))


@auth_bp.route("/admin/usuarios/<id_empleado>/delete", methods=["POST"])
def eliminar_usuario(id_empleado):
    if session.get("rol") != "admin":
        flash("No tienes permisos para eliminar usuarios.", "error")
        return redirect(url_for("view.index"))

    try:
        respuesta = requests.delete(
            f"{FASTAPI_BASE_URL}/users/{id_empleado}",
            headers={
                "Authorization": f"Bearer {session.get('access_token')}"
            },
            timeout=8
        )

        if respuesta.status_code == 200:
            flash("Usuario eliminado correctamente.", "success")
        else:
            flash("No se pudo eliminar el usuario.", "error")

    except requests.exceptions.RequestException:
        flash("No se pudo conectar con la API.", "error")

    return redirect(url_for("auth.admin_usuarios"))

@auth_bp.route("/cambiar_password", methods=["POST"])
def cambiar_password():
    if not session.get("id_empleado"):
        flash("Debes iniciar sesion para acceder.", "error")
        return redirect(url_for("view.login"))

    password_actual = request.form.get("password_actual", "").strip()
    password_nueva = request.form.get("password_nueva", "").strip()
    password_confirmar = request.form.get("password_confirmar", "").strip()

    if not password_actual or not password_nueva or not password_confirmar:
        flash("Todos los campos son obligatorios.", "error")
        return redirect(url_for("view.perfil"))

    if password_nueva != password_confirmar:
        flash("La nueva contrasena y su confirmacion no coinciden.", "error")
        return redirect(url_for("view.perfil"))

    if len(password_nueva) < 6:
        flash("La nueva contrasena debe tener al menos 6 caracteres.", "error")
        return redirect(url_for("view.perfil"))

    try:
        respuesta = requests.put(
            f"{FASTAPI_BASE_URL}/auth/change-password",
            json={
                "id_empleado": session.get("id_empleado"),
                "password_actual": password_actual,
                "password_nueva": password_nueva
            },
            timeout=8
        )
    except requests.exceptions.RequestException:
        flash("No se pudo conectar con la API.", "error")
        return redirect(url_for("view.perfil"))

    if respuesta.status_code == 200:
        flash("Contrasena actualizada correctamente.", "success")
        return redirect(url_for("view.perfil"))

    try:
        detalle = respuesta.json().get("detail", "Error al cambiar la contrasena.")
    except Exception:
        detalle = "Error al cambiar la contrasena."
    flash(detalle, "error")
    return redirect(url_for("view.perfil"))


@auth_bp.route("/logout")
def logout():
    session.clear()

    flash("Sesión cerrada correctamente.", "success")
    return redirect(url_for("view.login"))