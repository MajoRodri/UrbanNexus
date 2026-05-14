import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from db.database import SessionLocal
from repositories.sqlite_repository import SQLiteRepository


class GraphService:

    @staticmethod
    def generar_grafica_temperatura():

        db = SessionLocal()
        repo = SQLiteRepository(db)

        try:
            mediciones = repo.list_all_measurements()

            if not mediciones:
                return "/static/img/empty.png"

            datos = [
                {"fecha": m.fecha, "temperatura": m.temperatura}
                for m in mediciones
            ]

            df = pd.DataFrame(datos)
            df["fecha"] = pd.to_datetime(df["fecha"])
            df = df.sort_values("fecha")

            plt.figure(figsize=(10, 5))
            plt.plot(df["fecha"], df["temperatura"], marker="o")

            plt.title("Temperatura")
            plt.xlabel("Fecha")
            plt.ylabel("°C")
            plt.xticks(rotation=45)

            os.makedirs("static/img", exist_ok=True)

            ruta = "static/img/temperatura.png"

            plt.tight_layout()
            plt.savefig(ruta)
            plt.close()

            return "/" + ruta

        finally:
            db.close()

    # 🌡️ HUMEDAD
    @staticmethod
    def generar_grafica_humedad():

        db = SessionLocal()
        repo = SQLiteRepository(db)

        try:
            mediciones = repo.list_all_measurements()

            if not mediciones:
                return "/static/img/empty.png"

            datos = [
                {"fecha": m.fecha, "humedad": m.humedad}
                for m in mediciones
            ]

            df = pd.DataFrame(datos)
            df["fecha"] = pd.to_datetime(df["fecha"])
            df = df.sort_values("fecha")

            plt.figure(figsize=(10, 5))
            plt.plot(df["fecha"], df["humedad"], marker="o")

            plt.title("Humedad")
            plt.xlabel("Fecha")
            plt.ylabel("%")
            plt.xticks(rotation=45)

            os.makedirs("static/img", exist_ok=True)

            ruta = "static/img/humedad.png"

            plt.tight_layout()
            plt.savefig(ruta)
            plt.close()

            return "/" + ruta

        finally:
            db.close()

    # 🌬️ VIENTO
    @staticmethod
    def generar_grafica_viento():

        db = SessionLocal()
        repo = SQLiteRepository(db)

        try:
            mediciones = repo.list_all_measurements()

            if not mediciones:
                return "/static/img/empty.png"

            datos = [
                {"fecha": m.fecha, "viento": m.viento}
                for m in mediciones
            ]

            df = pd.DataFrame(datos)
            df["fecha"] = pd.to_datetime(df["fecha"])
            df = df.sort_values("fecha")

            plt.figure(figsize=(10, 5))
            plt.plot(df["fecha"], df["viento"], marker="o")

            plt.title("Viento")
            plt.xlabel("Fecha")
            plt.ylabel("km/h")
            plt.xticks(rotation=45)

            os.makedirs("static/img", exist_ok=True)

            ruta = "static/img/viento.png"

            plt.tight_layout()
            plt.savefig(ruta)
            plt.close()

            return "/" + ruta

        finally:
            db.close()