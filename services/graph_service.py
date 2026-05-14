import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from db.database import SessionLocal
from repositories.sqlite_repository import SQLiteRepository

# Paleta de colores para los distritos (sobre fondo oscuro)
_COLORES = ["#4ABFCC", "#f59e0b", "#ef4444", "#a78bfa", "#34d399", "#fb923c", "#60a5fa", "#f472b6"]

_BG       = "#071C20"
_CARD_BG  = "#0C2830"
_TEXT     = "#E8F5F2"
_MUTED    = "#7EC8C0"
_GRID     = "#1C3D45"


class GraphService:

    @staticmethod
    def _cargar_datos(campo):
        db = SessionLocal()
        repo = SQLiteRepository(db)
        try:
            mediciones = repo.list_all_measurements_with_zones()
            if not mediciones:
                return None

            datos = [
                {
                    "fecha": m.fecha,
                    "distrito": m.zona.municipio if m.zona else f"Zona {m.id_zona}",
                    "valor": getattr(m, campo)
                }
                for m in mediciones
            ]
            df = pd.DataFrame(datos)
            df["fecha"] = pd.to_datetime(df["fecha"])
            return df
        finally:
            db.close()

    @staticmethod
    def _generar_grafica(campo, titulo, unidad, ruta):
        df = GraphService._cargar_datos(campo)
        if df is None:
            return "/static/img/empty.png"

        # Media por fecha y distrito (por si hay varios registros el mismo día)
        df_pivot = (
            df.groupby(["fecha", "distrito"])["valor"]
            .mean()
            .unstack()
        )

        fig, ax = plt.subplots(figsize=(13, 6), facecolor=_BG)
        ax.set_facecolor(_CARD_BG)

        for i, distrito in enumerate(df_pivot.columns):
            color = _COLORES[i % len(_COLORES)]
            ax.plot(df_pivot.index, df_pivot[distrito], marker="o", linewidth=1.5,
                    markersize=4, color=color, label=distrito)

        # Línea de media general
        media = df_pivot.mean(axis=1)
        ax.plot(media.index, media.values, color=_TEXT, linewidth=2.5,
                linestyle="--", label="Media general", zorder=5)

        ax.set_title(titulo, fontsize=13, color=_TEXT, pad=12)
        ax.set_xlabel("Fecha", color=_MUTED, fontsize=9)
        ax.set_ylabel(unidad, color=_MUTED, fontsize=9)
        ax.tick_params(axis="x", rotation=45, colors=_MUTED, labelsize=8)
        ax.tick_params(axis="y", colors=_MUTED, labelsize=8)
        ax.grid(axis="y", color=_GRID, linestyle="--", linewidth=0.6)
        ax.grid(axis="x", color=_GRID, linestyle=":", linewidth=0.4)
        for spine in ax.spines.values():
            spine.set_edgecolor(_GRID)

        legend = ax.legend(loc="upper left", fontsize=8, framealpha=0.3,
                           facecolor=_CARD_BG, edgecolor=_GRID, labelcolor=_TEXT)

        os.makedirs("static/img", exist_ok=True)
        plt.tight_layout()
        plt.savefig(ruta, dpi=120, facecolor=_BG)
        plt.close()

        return "/" + ruta

    @staticmethod
    def generar_grafica_temperatura():
        return GraphService._generar_grafica(
            "temperatura", "Temperatura por Distrito", "°C", "static/img/temperatura.png"
        )

    @staticmethod
    def generar_grafica_humedad():
        return GraphService._generar_grafica(
            "humedad", "Humedad por Distrito", "%", "static/img/humedad.png"
        )

    @staticmethod
    def generar_grafica_viento():
        return GraphService._generar_grafica(
            "viento", "Viento por Distrito", "km/h", "static/img/viento.png"
        )
