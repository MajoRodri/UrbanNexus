from db.models import Zona, Medicion, ETLLog

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

    ##CREATE##
    
    #Método que nos permite crear zonas en la base de datos
    def create_zone(self, municipio, cod_ine, id_estacion, estacion_referencia):
        zona = Zona(municipio=municipio, cod_ine=cod_ine, id_estacion=id_estacion, estacion_referencia=estacion_referencia)
        return self._save(zona)
    
    #Método que nos permite crear mediciones en la base de datos
    def create_measurement(self, id_zona, fecha, temperatura, humedad, viento, lluvia):
        medicion = Medicion(id_zona=id_zona, fecha=fecha, temperatura=temperatura, humedad=humedad, viento=viento, lluvia=lluvia)
        return self._save(medicion)
    
    #Método que nos permite crear logs del ETL en la base de datos
    def create_log_ETL(self, fecha_ejecucion, origen, filas_leidas, filas_insertadas, filas_modificadas, filas_descartadas, duplicados_eliminados, estado, mensaje):
        log = ETLLog(fecha_ejecucion=fecha_ejecucion, origen=origen, filas_leidas=filas_leidas, filas_insertadas=filas_insertadas, filas_modificadas=filas_modificadas, filas_descartadas=filas_descartadas, duplicados_eliminados=duplicados_eliminados, estado=estado, mensaje=mensaje)
        return self._save(log)
    
    ##READ##
    
    #Método que nos permite obtener todas las zonas por id
    def get_zone_by_id(self, id_zona):
        return self._fetch(Zona, id_zona)
    
    #Método que nos permite obtener todas las mediciones por id
    def get_measurement_by_id(self, id_measurement):
        return self._fetch(Medicion, id_measurement)
    
    #Método que nos permite obtener todas las zonas por municipio
    def get_zone_by_municipality(self, municipio):
        return self.db.query(Zona).filter(Zona.municipio == municipio).first()
    
    #Método que nos permite obtener todas las zonas por cod_ine
    def get_zone_by_cod_ine(self, cod_ine):
        return self.db.query(Zona).filter(Zona.cod_ine == cod_ine).first()

    #Método que nos permite obtener todas las mediciones por zona y fecha
    #Sirve para evitar duplicados en el ETL al identificar registros ya existentes
    def get_measurement_by_zone_date(self, id_zona, fecha):
        return self.db.query(Medicion).filter(Medicion.id_zona == id_zona, Medicion.fecha == fecha).first()

    def list_all_zones(self, skip=0, limit=100):
        return self.db.query(Zona).offset(skip).limit(limit).all()
    
    def list_all_measurements(self, skip=0, limit=100):
        return self.db.query(Medicion).offset(skip).limit(limit).all()
    
    def get_all_measurements_ordered(self):
    return (
        self.db.query(Medicion)
        .order_by(Medicion.fecha.asc())
        .all()
    )
    
    
    def list_all_logs_ETL(self):
        return self.db.query(ETLLog).all()
    
    ##UPDATE##
    
    #Método que nos permite actualizar zonas en la base de datos
    def update_zone(self, id_zona, municipio, cod_ine, id_estacion, estacion_referencia):
        zona = self.get_zone_by_id(id_zona)
        zona.municipio = municipio
        zona.cod_ine = cod_ine
        zona.id_estacion = id_estacion
        zona.estacion_referencia = estacion_referencia
        return self._save(zona)
    
    #Método que nos permite actualizar mediciones en la base de datos
    def update_measurement(self, id_measurement, id_zona, fecha, temperatura, humedad, viento, lluvia):
        medicion = self.get_measurement_by_id(id_measurement)
        medicion.id_zona = id_zona
        medicion.fecha = fecha
        medicion.temperatura = temperatura
        medicion.humedad = humedad
        medicion.viento = viento
        medicion.lluvia = lluvia
        return self._save(medicion)

    ##UPSERT (UPDATE + INSERT)
    
    #Método que nos permite insertar o actualizar mediciones en la base de datos
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
    
    #Método que nos permite eliminar zonas en la base de datos
    def delete_zone(self, id_zona):
        zona = self.get_zone_by_id(id_zona)
        self._delete(zona)
        return zona
    
    #Método que nos permite eliminar mediciones en la base de datos
    def delete_measurement(self, id_measurement):
        medicion = self.get_measurement_by_id(id_measurement)
        self._delete(medicion)
        return medicion