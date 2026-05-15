import pandas as pd
from flask_apscheduler import APScheduler
from services.weather_api_service import WeatherAPIService
from services.normalizer_service import normalizar_datos_clima
from etl.transform import transform
from etl.extract import extract_station_reference
from etl.load import sync_zones, load_measurements, log_execution
from db.database import SessionLocal
from datetime import datetime
import logging
import json
import os

scheduler = APScheduler()

CONFIG_PATH = 'data/scheduler_config.json'
_CATALOG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config', 'municipios.json')

DEFAULT_CONFIG = {
    "enabled": False,
    "times": ["07:00", "15:00", "20:00"]
}


def _load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, encoding='utf-8') as f:
            return json.load(f)
    return DEFAULT_CONFIG.copy()


def _save_config(config):
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def _cargar_catalogo():
    try:
        with open(_CATALOG_PATH, encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error al cargar catálogo de distritos: {e}")
        return {}


def _tarea_ingesta(slot=""):
    catalogo = _cargar_catalogo()
    if not catalogo:
        logging.error(f"Ingesta ({slot}): catálogo vacío, abortando.")
        return

    try:
        weather = WeatherAPIService()
    except ValueError as e:
        logging.error(f"Ingesta ({slot}): {e}")
        return

    # EXTRACT: obtener datos crudos de WeatherAPI para cada distrito
    fecha_str = datetime.now().replace(second=0, microsecond=0).strftime("%Y-%m-%dT%H:%M")
    registros_crudos = []

    for nombre, coords in catalogo.items():
        try:
            lat, lon = [x.strip() for x in coords.split(',')]
        except ValueError:
            logging.error(f"Ingesta ({slot}): coordenadas inválidas para '{nombre}': {coords}")
            continue

        raw_data = weather.obtener_clima_por_coordenadas(float(lat), float(lon))
        if raw_data is None:
            logging.warning(f"Ingesta ({slot}): sin datos de WeatherAPI para '{nombre}'")
            continue

        data = normalizar_datos_clima(raw_data)
        registros_crudos.append({
            "estacion_id": nombre,
            "fecha": fecha_str,
            "temperatura": data.get("temperatura"),
            "humedad": data.get("humedad"),
            "viento": data.get("viento"),
            "lluvia": data.get("lluvia"),
        })

    if not registros_crudos:
        logging.error(f"Ingesta ({slot}): no se obtuvieron datos de ningún distrito.")
        return

    # TRANSFORM: limpieza y validación con Pandas
    df_raw = pd.DataFrame(registros_crudos)
    referencia = extract_station_reference()
    df_limpio, stats = transform(df_raw, referencia)

    # LOAD: persistir en SQLite + log de trazabilidad
    db = SessionLocal()
    try:
        mapa_zonas = sync_zones(db, referencia)
        insertadas, omitidas = load_measurements(db, df_limpio, mapa_zonas)

        total_duplicados = stats["duplicados_eliminados"] + omitidas
        total_descartados = stats["descartados_nulos"] + stats["descartados_sin_zona"]

        log_execution(db, f"scheduler/{slot}", {
            "filas_leidas": stats["filas_leidas"],
            "filas_insertadas": insertadas,
            "filas_modificadas": 0,
            "filas_descartadas": total_descartados,
            "duplicados_eliminados": total_duplicados,
        })

        logging.info(
            f"Ingesta ({slot}): leídas={stats['filas_leidas']}, "
            f"insertadas={insertadas}, descartadas={total_descartados}, "
            f"duplicadas={omitidas}"
        )
    except Exception as e:
        logging.error(f"Error en carga ETL ({slot}): {e}")
    finally:
        db.close()


def _apply_jobs(config):
    for job in scheduler.get_jobs():
        job.remove()

    if not config.get("enabled"):
        return

    for i, time_str in enumerate(config.get("times", [])):
        try:
            hour, minute = time_str.split(":")
            scheduler.add_job(
                id=f'ingesta_{i}',
                func=_tarea_ingesta,
                kwargs={"slot": time_str},
                trigger='cron',
                hour=int(hour),
                minute=int(minute)
            )
        except (ValueError, Exception) as e:
            logging.error(f"Error al programar slot {time_str}: {e}")


def toggle_ingesta():
    config = _load_config()
    config["enabled"] = not config["enabled"]
    _save_config(config)
    _apply_jobs(config)
    return config


def update_times(times):
    config = _load_config()
    config["times"] = times
    _save_config(config)
    _apply_jobs(config)
    return config


def get_status():
    config = _load_config()
    jobs = scheduler.get_jobs()
    next_runs = [
        {"time": j.kwargs.get("slot"), "next": str(j.next_run_time)[:16] if j.next_run_time else "—"}
        for j in jobs
    ]
    return {**config, "next_runs": next_runs}


def init_scheduler(app):
    app.config['SCHEDULER_API_ENABLED'] = False
    scheduler.init_app(app)
    scheduler.start()
    config = _load_config()
    _apply_jobs(config)
