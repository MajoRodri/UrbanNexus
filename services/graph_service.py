import os
import pandas as pd
import matplotlib.pyplot as plt

from db.database import SessionLocal
from repositories.sqlite_repository import SQLiteRepository


class GraphService:

    @staticmethod
    def generar_grafica_temperatura():

        db = SessionLocal()
        repo = SQLiteRepository(db)

        try:
            mediciones = repo.get_all_measurements_ordered()

            if not mediciones:
                return None

            datos = []

            for m in mediciones:
                datos.append({
                    "fecha": m.fecha,
                    "temperatura": m.temperatura
                })

            df = pd.DataFrame(datos)

            plt.figure(figsize=(10, 5))

            plt.plot(
                df["fecha"],
                df["temperatura"],
                marker="o"
            )

            plt.title("Temperatura")
            plt.xlabel("Fecha")
            plt.ylabel("°C")

            plt.xticks(rotation=45)

            os.makedirs("static/img", exist_ok=True)

            ruta = "static/img/temperatura.png"

            plt.tight_layout()

            plt.savefig(ruta)

            plt.close()

            return ruta

        finally:
            db.close()