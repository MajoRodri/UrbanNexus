from flask import Blueprint, request, jsonify
from models.registro_climatico import RegistroClimatico
from repositories.sqlite_repository import SQLiteRepository
from db.database import SessionLocal
from services.alert_service import AlertService  # Importación desde tu carpeta 'service'

manual_bp = Blueprint('manual', __name__)

# Instancias globales
repo = SQLiteRepository(SessionLocal())
alert_service = AlertService()

@manual_bp.route('/api/registrar', methods=['POST'])
def registrar_datos_manuales():
    """
    Recibe datos JSON, los valida, los guarda y evalúa alertas climáticas.
    """
    try:
        datos = request.get_json()
        if not datos:
            return jsonify({"status": "error", "message": "No se recibieron datos"}), 400

        # 1. Crear el objeto de registro (Persona 2)
        nuevo_registro = RegistroClimatico(
            datos.get("estacion_id"),
            datos.get("fecha"),
            float(datos.get("temperatura", 0)),
            float(datos.get("humedad", 0)),
            float(datos.get("viento", 0)),
            float(datos.get("lluvia", 0))
        )

        # 2. Preparar el diccionario final
        registro_dict = nuevo_registro.to_dict()
        registro_dict["municipio"] = datos.get("municipio", "Desconocido")
        registro_dict["fuente"] = "manual"

        # 3. EVALUAR ALERTAS (Tu AlertService)
        # El controlador envía el registro al motor de alertas antes de confirmar
        lista_alertas = alert_service.evaluar_alertas(registro_dict)

        try:
            zona = repo.get_zone_by_municipality(
                registro_dict["municipio"]
            )

            if not zona:
                zona = repo.create_zone(
                    municipio=registro_dict["municipio"],
                    cod_ine=f"MANUAL-{registro_dict['municipio']}-{registro_dict['estacion_id']}",
                id_estacion=registro_dict["estacion_id"],
                estacion_referencia=registro_dict["municipio"]
            )

            medicion = repo.create_measurement(
                id_zona=zona.id,
                fecha=registro_dict["fecha"],
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