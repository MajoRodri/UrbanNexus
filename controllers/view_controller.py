from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
from datetime import datetime
from db.database import SessionLocal
from db.models import Medicion, Zona
from controllers.scheduler_controller import toggle_ingesta, update_times, get_status


view_bp = Blueprint("view", __name__, template_folder="../templates")

# --- Helpers de rol ---

def _rol():
    return session.get("rol")

def _logueado():
    return bool(session.get("id_empleado"))

def _es_operador():
    """admin y tecnico pueden operar (registrar, ingesta, API)."""
    return _rol() in ("admin", "tecnico")

def _es_admin():
    return _rol() == "admin"


# --- Helpers de query ---

def _medicion_to_dict(medicion, zona):
    return {
        "id": medicion.id,
        "municipio": zona.municipio if zona else "Desconocido",
        "fecha": medicion.fecha.strftime("%d/%m/%Y %H:%M") if hasattr(medicion.fecha, "strftime") else medicion.fecha,
        "temperatura": medicion.temperatura,
        "humedad": medicion.humedad,
        "viento": medicion.viento,
        "lluvia": medicion.lluvia,
    }


def _buscar_registros_bd(municipio=None, fecha_raw=None):
    db = SessionLocal()
    try:
        query = (
            db.query(Medicion, Zona)
            .join(Zona, Medicion.id_zona == Zona.id)
            .order_by(Medicion.fecha.desc())
        )
        if municipio:
            query = query.filter(Zona.municipio.ilike(f"%{municipio}%"))
        if fecha_raw:
            try:
                fecha_obj = datetime.strptime(fecha_raw, "%Y-%m-%d").date()
                query = query.filter(Medicion.fecha >= datetime.combine(fecha_obj, datetime.min.time()))
                query = query.filter(Medicion.fecha <= datetime.combine(fecha_obj, datetime.max.time()))
            except ValueError:
                pass
        resultados = query.limit(200).all()
        return [_medicion_to_dict(m, z) for m, z in resultados]
    finally:
        db.close()


# --- Rutas públicas ---

@view_bp.route("/")
def index():
    return render_template("index.html")

@view_bp.route("/registro_usuario")
def registro_usuario():
    return render_template("registro_usuario.html")

@view_bp.route("/login")
def login():
    return render_template("login.html")


# --- Rutas para cualquier usuario logueado ---

@view_bp.route("/consulta", methods=["GET", "POST"])
def consulta():
    if not _logueado():
        flash("Debes iniciar sesión para acceder.", "error")
        return redirect(url_for("view.login"))

    municipio = None
    fecha_raw = None
    if request.method == "POST":
        municipio = request.form.get("municipio", "").strip() or None
        fecha_raw = request.form.get("fecha", "").strip() or None

    registros = _buscar_registros_bd(municipio=municipio, fecha_raw=fecha_raw)
    return render_template("consulta.html", registros=registros)


# --- Rutas para admin y tecnico ---

@view_bp.route("/registro")
def registro():
    if not _logueado():
        flash("Debes iniciar sesión para acceder.", "error")
        return redirect(url_for("view.login"))
    if not _es_operador():
        flash("No tienes permisos para acceder a esta sección.", "error")
        return redirect(url_for("view.index"))
    return render_template("registro.html")


@view_bp.route("/admin/scheduler")
def admin_scheduler():
    if not _logueado():
        flash("Debes iniciar sesión para acceder.", "error")
        return redirect(url_for("view.login"))
    if not _es_operador():
        flash("No tienes permisos para acceder a esta sección.", "error")
        return redirect(url_for("view.index"))
    return render_template("admin_scheduler.html", status=get_status())


@view_bp.route("/admin/scheduler/toggle", methods=["POST"])
def scheduler_toggle():
    if not _es_operador():
        return jsonify({"error": "Sin permisos"}), 403
    config = toggle_ingesta()
    return jsonify(config)


@view_bp.route("/admin/scheduler/config", methods=["POST"])
def scheduler_config():
    if not _es_operador():
        return jsonify({"error": "Sin permisos"}), 403
    data = request.get_json(silent=True) or {}
    times = data.get("times", [])
    if not isinstance(times, list) or not times:
        return jsonify({"error": "Lista de horarios inválida"}), 400
    config = update_times(times)
    return jsonify(config)


@view_bp.route("/admin/scheduler/status")
def scheduler_status():
    if not _es_operador():
        return jsonify({"error": "Sin permisos"}), 403
    return jsonify(get_status())


# --- Perfil de usuario ---

@view_bp.route("/perfil")
def perfil():
    if not _logueado():
        flash("Debes iniciar sesion para acceder.", "error")
        return redirect(url_for("view.login"))
    return render_template("perfil.html")


# --- Rutas solo admin ---

@view_bp.route("/admin/invitaciones")
def admin_invitaciones():
    if not _logueado():
        flash("Debes iniciar sesión para acceder.", "error")
        return redirect(url_for("view.login"))
    if not _es_admin():
        flash("No tienes permisos para acceder a esta sección.", "error")
        return redirect(url_for("view.index"))
    return render_template("admin_invitaciones.html")
