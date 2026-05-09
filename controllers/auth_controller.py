import json
import os
import re

from flask import Blueprint, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash  # nueva librería: genera y verifica contraseñas con hash seguro (reemplaza hashlib)
from models.usuario import Usuario


auth_bp = Blueprint("auth", __name__)

MAX_INTENTOS_LOGIN = 3  # constante nueva: número máximo de intentos de login permitidos antes de bloquear


class AuthController:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_dir = os.path.join(self.base_dir, "data")
        self.usuarios_path = os.path.join(self.data_dir, "usuarios.json")
        self.empleados_path = os.path.join(self.data_dir, "empleados.json")  # nueva ruta: apunta al archivo de empleados autorizados

        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def cargar_usuarios(self):
        if not os.path.exists(self.usuarios_path):
            return []
        try:
            with open(self.usuarios_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def guardar_usuarios(self, usuarios):
        with open(self.usuarios_path, "w", encoding="utf-8") as f:
            json.dump(usuarios, f, indent=4, ensure_ascii=False)

    # método nuevo: lee la lista de empleados autorizados desde empleados.json
    def cargar_empleados(self):
        try:
            with open(self.empleados_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    # método nuevo: valida que el número de empleado tenga exactamente 6 dígitos
    def validar_num_empleado(self, num_empleado):
        if not re.fullmatch(r"\d{6}", num_empleado):  # \d{6} = exactamente 6 dígitos numéricos
            return False, "El número de empleado debe tener exactamente 6 dígitos."
        return True, ""

    # método nuevo: valida que nombre o apellidos solo contengan letras (incluyendo tildes y ñ)
    def validar_nombre(self, valor, campo):
        if not re.fullmatch(r"[A-Za-záéíóúÁÉÍÓÚüÜñÑ\s]+", valor):  # no permite números ni símbolos
            return False, f"El campo '{campo}' solo puede contener letras."
        return True, ""

    # método nuevo: valida reglas de seguridad para la contraseña
    def validar_password(self, password):
        if len(password) < 8:  # mínimo 8 caracteres (antes eran 6)
            return False, "La contraseña debe tener al menos 8 caracteres."
        if not re.search(r"[A-Z]", password):  # regla nueva: debe tener al menos una mayúscula
            return False, "La contraseña debe contener al menos una letra mayúscula."
        if not re.search(r"\d", password):  # regla nueva: debe tener al menos un número
            return False, "La contraseña debe contener al menos un número."
        return True, ""

    # método modificado: ahora recibe num_empleado, nombre y apellidos en vez de email
    def registrar_usuario(self, num_empleado, nombre, apellidos, password):
        valido, mensaje = self.validar_num_empleado(num_empleado)
        if not valido:
            return False, mensaje

        # validación nueva: recorre nombre y apellidos con el mismo validador
        for campo, valor in [("nombre", nombre), ("apellidos", apellidos)]:
            valido, mensaje = self.validar_nombre(valor, campo)
            if not valido:
                return False, mensaje

        valido, mensaje = self.validar_password(password)
        if not valido:
            return False, mensaje

        empleados = self.cargar_empleados()  # carga la lista de empleados autorizados
        if num_empleado not in empleados:  # verificación nueva: solo empleados de la lista pueden registrarse
            return False, "El número de empleado no está autorizado."

        usuarios = self.cargar_usuarios()
        for usuario in usuarios:
            if usuario.get("num_empleado") == num_empleado:  # .get() evita error si la clave no existe
                return False, "Este número de empleado ya tiene una cuenta registrada."

        password_hash = generate_password_hash(password)  # nuevo: genera hash seguro con werkzeug (antes era sha256 plano)
        nuevo_usuario = Usuario(num_empleado, nombre.strip(), apellidos.strip(), password_hash)  # nuevo: incluye nombre y apellidos
        usuarios.append(nuevo_usuario.to_dict())
        self.guardar_usuarios(usuarios)

        return True, "Registro completado con éxito."

    # método modificado: ahora busca por num_empleado y usa check_password_hash para comparar
    def iniciar_sesion(self, num_empleado, password):
        usuarios = self.cargar_usuarios()
        for usuario in usuarios:
            if usuario.get("num_empleado") == num_empleado:
                if check_password_hash(usuario["password_hash"], password):  # nuevo: compara el hash guardado con la contraseña ingresada
                    return True, "Login correcto."
                return False, "Contraseña incorrecta."  # nuevo: diferencia entre usuario no encontrado y contraseña mal
        return False, "Número de empleado no registrado."


auth_controller = AuthController()


@auth_bp.route("/registro_usuario", methods=["POST"])
def registrar_usuario():
    num_empleado = request.form.get("num_empleado", "").strip()  # nuevo campo del formulario
    nombre = request.form.get("nombre", "").strip()              # nuevo campo del formulario
    apellidos = request.form.get("apellidos", "").strip()        # nuevo campo del formulario
    password = request.form.get("password", "").strip()
    confirm_password = request.form.get("confirm_password", "").strip()

    # validación nueva: verifica que ningún campo esté vacío antes de continuar
    if not num_empleado or not nombre or not apellidos or not password:
        flash("Todos los campos son obligatorios.", "error")
        return redirect(url_for("view.registro_usuario"))

    if password != confirm_password:
        flash("Las contraseñas no coinciden.", "error")
        return redirect(url_for("view.registro_usuario"))

    exito, mensaje = auth_controller.registrar_usuario(num_empleado, nombre, apellidos, password)

    if exito:
        flash(mensaje, "success")
        return redirect(url_for("view.login"))

    flash(mensaje, "error")
    return redirect(url_for("view.registro_usuario"))


@auth_bp.route("/login", methods=["POST"])
def login():
    intentos = session.get("login_intentos", 0)  # nuevo: lee cuántos intentos fallidos lleva el usuario en esta sesión

    # nuevo: si ya alcanzó el límite, bloquea el acceso sin siquiera intentar el login
    if intentos >= MAX_INTENTOS_LOGIN:
        flash("Has superado los 3 intentos permitidos. Contacta con el administrador.", "error")
        return redirect(url_for("view.login"))

    num_empleado = request.form.get("num_empleado", "").strip()  # nuevo: usa num_empleado en vez de email
    password = request.form.get("password", "").strip()

    # validación nueva: revisa que los campos no lleguen vacíos
    if not num_empleado or not password:
        flash("Introduce tu número de empleado y contraseña.", "error")
        return redirect(url_for("view.login"))

    exito, mensaje = auth_controller.iniciar_sesion(num_empleado, password)

    if exito:
        session.pop("login_intentos", None)  # nuevo: limpia el contador de intentos al entrar correctamente
        session["usuario"] = num_empleado    # guarda el num_empleado en sesión (antes guardaba el email)
        flash("Bienvenido.", "success")
        return redirect(url_for("view.index"))

    intentos += 1                           # nuevo: incrementa el contador de intentos fallidos
    session["login_intentos"] = intentos    # nuevo: guarda el contador actualizado en la sesión
    restantes = MAX_INTENTOS_LOGIN - intentos  # nuevo: calcula cuántos intentos le quedan

    # nuevo: muestra mensajes diferentes según si aún tiene intentos o los agotó
    if restantes > 0:
        flash(f"{mensaje} Te quedan {restantes} intento(s).", "error")
    else:
        flash("Has agotado los 3 intentos. Contacta con el administrador.", "error")

    return redirect(url_for("view.login"))


@auth_bp.route("/logout")
def logout():
    session.pop("usuario", None)
    session.pop("login_intentos", None)  # nuevo: también limpia el contador de intentos al cerrar sesión
    flash("Sesión cerrada correctamente.", "success")
    return redirect(url_for("view.index"))
