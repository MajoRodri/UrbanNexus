from flask import Blueprint, render_template
from services.graph_service import GraphService

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
def dashboard():
    grafica_temp     = GraphService.generar_grafica_temperatura()
    grafica_humidity = GraphService.generar_grafica_humedad()
    grafica_wind     = GraphService.generar_grafica_viento()

    return render_template(
        "dashboard.html",
        temp_img=grafica_temp,
        humidity_img=grafica_humidity,
        wind_img=grafica_wind,
        empty=not any([grafica_temp, grafica_humidity, grafica_wind]),
    )