from datetime import datetime
from flask import Blueprint, request, jsonify, session
from models.registro_climatico import RegistroClimatico
from repositories.sqlite_repository import SQLiteRepository
from db.database import SessionLocal
from services.alert_service import AlertService

manual_bp = Blueprint('manual', __name__)
alert_service = AlertService()


def _parsear_fecha(fecha_str):
    ahora = datetime.now().replace(microsecond=0)
    for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            fecha_date = datetime.strptime(fecha_str, fmt).date()
            return datetime.combine(fecha_date, ahora.time())
        except (ValueError, TypeError):
            continue
    try:
        return datetime.strptime(fecha_str, "%Y-%m-%dT%H:%M:%S")
    except (ValueError, TypeError):
        pass
    return ahora


@manual_bp.route('/api/registrar', methods=['POST'])
def registrar_datos_manuales():
    if session.get("rol") not in ("admin", "tecnico"):
        return jsonify({"status": "error", "message": "Sin permisos"}), 403

    datos = request.get_json()
    if not datos:
        return jsonify({"status": "error", "message": "No se recibieron datos"}), 400

    try:
        nuevo_registro = RegistroClimatico(
            datos.get("estacion_id"),
            datos.get("fecha"),
            float(datos.get("temperatura", 0)),
            float(datos.get("humedad", 0)),
            float(datos.get("viento", 0)),
            float(datos.get("lluvia", 0))
        )

        registro_dict = nuevo_registro.to_dict()
        registro_dict["municipio"] = datos.get("municipio", "Desconocido")
        registro_dict["fuente"] = datos.get("fuente", "manual")

        lista_alertas = alert_service.evaluar_alertas(registro_dict)

        db = SessionLocal()
        try:
            repo = SQLiteRepository(db)

            zona = repo.get_zone_by_municipality(registro_dict["municipio"])

            if not zona:
                zona = repo.create_zone(
                    municipio=registro_dict["municipio"],
                    cod_ine=f"MANUAL-{registro_dict['municipio']}-{registro_dict['estacion_id']}",
                    id_estacion=registro_dict["estacion_id"],
                    estacion_referencia=registro_dict["municipio"]
                )

            medicion = repo.create_measurement(
                id_zona=zona.id,
                fecha=_parsear_fecha(registro_dict["fecha"]),
                temperatura=registro_dict["temperatura"],
                humedad=registro_dict["humedad"],
                viento=registro_dict["viento"],
                lluvia=registro_dict["lluvia"]
            )
        finally:
            db.close()

        return jsonify({
            "status": "success",
            "message": "Registro guardado con éxito en la base de datos",
            "alertas": lista_alertas,
            "municipio": registro_dict["municipio"],
            "id_medicion": medicion.id
        }), 201

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error interno: {str(e)}"
        }), 500
