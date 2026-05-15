from sqlalchemy.orm import joinedload
from db.models import Zona, Medicion, ETLLog, Usuario
from services.alert_service import AlertService
from utils.employee_id import generate_unique_id
from datetime import datetime

##Cuando no se encuentra registro##
class RecordNotFoundError(Exception):
    pass

class SQLiteRepository:
    def __init__(self, db):
        self.db = db

    ##Función auxiliar que nos permite persistir objetos nuevos o actualizados en la base de datos##
    def _save(self, obj):
        try:
            self.db.add(obj)
            self.db.commit()
            self.db.refresh(obj)
            return obj
        except Exception:
            self.db.rollback()
            raise
            
    ##Función auxiliar que nos permite eliminar objetos de la base de datos##
    def _delete(self, obj):
        try:
            self.db.delete(obj)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
    
    ##Investigando encontré una función que permite hacer la query del objeto, con ID incluido, y si no existe lanzar la excepción 
    def _fetch(self, model_class, id_record):
        obj = self.db.query(model_class).filter(model_class.id == id_record).first()
        if obj is None:
            raise RecordNotFoundError(f"Error: No se ha encontrado el registro con id {id_record} en {model_class.__name__}")
        return obj

    ##FUNCIÓN AUXILIAR PARA CALCULAR ALERTAS##
    def _calcular_alertas_medicion(self, temperatura, humedad, viento, lluvia):
        alert_service = AlertService()

        alertas = alert_service.evaluar_alertas({
            "fecha": datetime.now().isoformat(),
            "temperatura": temperatura,
            "humedad": humedad,
            "viento": viento,
            "lluvia": lluvia
        })

        resultado = {
            "alerta_calor": None,
            "alerta_helada": None,
            "alerta_viento": None,
            "alerta_lluvia": None,
            "alerta_humedad": None
        }

        for alerta in alertas:
            if "CALOR" in alerta:
                resultado["alerta_calor"] = alerta
            elif "FRIO" in alerta:
                resultado["alerta_helada"] = alerta
            elif "VIENTO" in alerta:
                resultado["alerta_viento"] = alerta
            elif "LLUVIA" in alerta:
                resultado["alerta_lluvia"] = alerta
            elif "HUMEDAD" in alerta:
                resultado["alerta_humedad"] = alerta

        return resultado

    ##CREATE##
    def create_zone(self, municipio, cod_ine, id_estacion, estacion_referencia):
        zona = Zona(municipio=municipio, cod_ine=cod_ine, id_estacion=id_estacion, estacion_referencia=estacion_referencia)
        return self._save(zona)
    
    def create_measurement(self, id_zona, fecha, temperatura, humedad, viento, lluvia):
        alertas = self._calcular_alertas_medicion(temperatura, humedad, viento, lluvia)
        medicion = Medicion(id_zona=id_zona, fecha=fecha, temperatura=temperatura, humedad=humedad, viento=viento, lluvia=lluvia, **alertas)
        return self._save(medicion)
    
    def create_log_ETL(self, fecha_ejecucion, origen, filas_leidas, filas_insertadas, filas_modificadas, filas_descartadas, duplicados_eliminados, estado, mensaje):
        log = ETLLog(fecha_ejecucion=fecha_ejecucion, origen=origen, filas_leidas=filas_leidas, filas_insertadas=filas_insertadas, filas_modificadas=filas_modificadas, filas_descartadas=filas_descartadas, duplicados_eliminados=duplicados_eliminados, estado=estado, mensaje=mensaje)
        return self._save(log)
    
    ##READ##
    def get_zone_by_id(self, id_zona):
        return self._fetch(Zona, id_zona)
    
    def get_measurement_by_id(self, id_measurement):
        return self._fetch(Medicion, id_measurement)
    
    def get_zone_by_municipality(self, municipio):
        return self.db.query(Zona).filter(Zona.municipio == municipio).first()
    
    def get_zone_by_cod_ine(self, cod_ine):
        return self.db.query(Zona).filter(Zona.cod_ine == cod_ine).first()

    def get_measurement_by_zone_date(self, id_zona, fecha):
        return self.db.query(Medicion).filter(Medicion.id_zona == id_zona, Medicion.fecha == fecha).first()

    def list_all_zones(self, skip=0, limit=100):
        return self.db.query(Zona).offset(skip).limit(limit).all()
    
    def list_all_measurements(self, skip=0, limit=100):
        return self.db.query(Medicion).offset(skip).limit(limit).all()
    
    def get_all_measurements_ordered(self):
        return self.db.query(Medicion).order_by(Medicion.fecha.asc()).all()

    def list_all_measurements_with_zones(self):
        return self.db.query(Medicion).options(joinedload(Medicion.zona)).order_by(Medicion.fecha.asc()).all()
    
    def list_all_logs_ETL(self):
        return self.db.query(ETLLog).all()
    
    ##UPDATE##
    def update_zone(self, id_zona, municipio, cod_ine, id_estacion, estacion_referencia):
        zona = self.get_zone_by_id(id_zona)
        zona.municipio = municipio
        zona.cod_ine = cod_ine
        zona.id_estacion = id_estacion
        zona.estacion_referencia = estacion_referencia
        return self._save(zona)
    
    def update_measurement(self, id_measurement, id_zona, fecha, temperatura, humedad, viento, lluvia):
        medicion = self.get_measurement_by_id(id_measurement)
        alertas = self._calcular_alertas_medicion(temperatura, humedad, viento, lluvia)

        medicion.id_zona = id_zona
        medicion.fecha = fecha
        medicion.temperatura = temperatura
        medicion.humedad = humedad
        medicion.viento = viento
        medicion.lluvia = lluvia

        medicion.alerta_calor = alertas["alerta_calor"]
        medicion.alerta_helada = alertas["alerta_helada"]
        medicion.alerta_viento = alertas["alerta_viento"]
        medicion.alerta_lluvia = alertas["alerta_lluvia"]
        medicion.alerta_humedad = alertas["alerta_humedad"]

        return self._save(medicion)

    ##UPSERT (UPDATE + INSERT)
    def upsert_measurement(self, id_zona, fecha, temperatura, humedad, viento, lluvia):
        medicion = self.get_measurement_by_zone_date(id_zona, fecha)
        if medicion:
            medicion.temperatura = temperatura
            medicion.humedad = humedad
            medicion.viento = viento
            medicion.lluvia = lluvia
            return self._save(medicion)
        return self.create_measurement(id_zona, fecha, temperatura, humedad, viento, lluvia)
    
    ##DELETE##
    def delete_zone(self, id_zona):
        zona = self.get_zone_by_id(id_zona)
        self._delete(zona)
        return zona
    
    def delete_measurement(self, id_measurement):
        medicion = self.get_measurement_by_id(id_measurement)
        self._delete(medicion)
        return medicion

    ###USERS###
    def get_user_by_employee_id(self, id_empleado):
        user = self.db.query(Usuario).filter(Usuario.id_empleado == id_empleado).first()
        if user is None:
            raise RecordNotFoundError(f"Usuario con id_empleado {id_empleado} no encontrado")
        return user

    def list_all_users(self):
        return self.db.query(Usuario).all()
    
    def update_user_role(self, id_empleado, rol):
        user = self.get_user_by_employee_id(id_empleado)
        if user.rol == rol:
            return user
        user.rol = rol
        return self._save(user)

    def update_user_state(self, id_empleado, activo):
        user = self.get_user_by_employee_id(id_empleado)
        user.activo = activo
        return self._save(user)
    
    def delete_user(self, id_empleado):
        user = self.get_user_by_employee_id(id_empleado)
        self._delete(user)
        return user 

    def update_zone_climate(self, zona_id, temperatura, humedad, viento, lluvia):
        """Actualiza los datos climáticos y evita valores nulos en la zona"""
        zona = self.get_zone_by_id(zona_id)
        zona.temperatura = temperatura
        zona.humedad = humedad
        zona.viento = viento
        zona.lluvia = lluvia
        return self._save(zona)