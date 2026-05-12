from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from datetime import datetime
from controllers.compare_controller import compare_latest_records
from db.database import SessionLocal
from db.models import Medicion, Zona


view_bp = Blueprint("view", __name__, template_folder="../templates")


def _medicion_to_dict(medicion, zona):
    return {
        "id": medicion.id,
        "municipio": zona.municipio if zona else "Desconocido",
        "estacion_id": zona.id_estacion if zona else "N/A",
        "estacion_referencia": zona.estacion_referencia if zona else "N/A",
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

        return [
            _medicion_to_dict(medicion, zona)
            for medicion, zona in resultados
        ]

    finally:
        db.close()


@view_bp.route("/")
def index():
    return render_template("index.html")


@view_bp.route("/registro")
def registro():
    return render_template("registro.html")


@view_bp.route("/registro_usuario")
def registro_usuario():
    return render_template("registro_usuario.html")


@view_bp.route("/login")
def login():
    return render_template("login.html")


@view_bp.route("/admin/invitaciones")
def admin_invitaciones():
    if not session.get("id_empleado"):
        flash("Debes iniciar sesión para acceder.", "error")
        return redirect(url_for("view.login"))

    if session.get("rol") != "admin":
        flash("No tienes permisos para acceder a esta sección.", "error")
        return redirect(url_for("view.index"))

    return render_template("admin_invitaciones.html")


@view_bp.route("/api")
def api_view():
    return render_template("index.html")


@view_bp.route("/consulta", methods=["GET", "POST"])
def consulta():
    """
    Muestra el histórico de mediciones desde SQLite.
    """

    municipio = None
    fecha_raw = None

    if request.method == "POST":
        municipio = request.form.get("municipio", "").strip() or None
        fecha_raw = request.form.get("fecha", "").strip() or None

    registros = _buscar_registros_bd(
        municipio=municipio,
        fecha_raw=fecha_raw
    )

    return render_template(
        "consulta.html",
        registros=registros
    )


@view_bp.route("/comparar", methods=["GET", "POST"])
def comparar():
    """
    Realiza la comparativa entre BD/API.
    Temporalmente mantiene compare_latest_records si todavía existe.
    """

    if request.method == "GET":
        return render_template("comparar.html", resultado=None)

    municipio = request.form.get("municipio", "").strip()
    fecha_html = request.form.get("fecha", "").strip()

    if not municipio:
        return render_template(
            "comparar.html",
            resultado={
                "success": False,
                "message": "Debes introducir un municipio para comparar."
            }
        )

    resultado = compare_latest_records(municipio, fecha_html)

    return render_template("comparar.html", resultado=resultado)