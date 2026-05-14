from flask import Blueprint, render_template, url_for
from services.graph_service import GraphService

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
def dashboard():

    grafica_temp = GraphService.generar_grafica_temperatura()
    grafica_humidity = GraphService.generar_grafica_humedad()
    grafica_wind = GraphService.generar_grafica_viento()

    return render_template(
        "dashboard.html",

        # 🌡️ TEMPERATURA
        temp_img=grafica_temp or url_for('static', filename='img/empty.png'),

        # 💧 HUMEDAD
        humidity_img=grafica_humidity or url_for('static', filename='img/empty.png'),

        # 🌬️ VIENTO
        wind_img=grafica_wind or url_for('static', filename='img/empty.png'),

        # 🚨 CONTROL DE ESTADO
        empty=False if (grafica_temp or grafica_humidity or grafica_wind) else True
    )