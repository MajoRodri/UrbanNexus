import base64
from io import BytesIO
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

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
            df["fecha"] = pd.to_datetime(df["fecha"]).dt.normalize()  # agrupa por día
            return df
        finally:
            db.close()

    @staticmethod
    def _generar_grafica(campo, titulo, unidad, ruta=None):
        df = GraphService._cargar_datos(campo)
        if df is None:
            return None

        # Media por fecha y distrito (por si hay varios registros el mismo día)
        df_pivot = (
            df.groupby(["fecha", "distrito"])["valor"]
            .mean()
            .unstack()
        )

        # Figura más alta para dejar espacio a la leyenda debajo
        fig, ax = plt.subplots(figsize=(13, 7), facecolor=_BG)
        ax.set_facecolor(_CARD_BG)

        for i, distrito in enumerate(df_pivot.columns):
            color = _COLORES[i % len(_COLORES)]
            ax.plot(df_pivot.index, df_pivot[distrito], linewidth=1.8,
                    color=color, label=distrito)
            ax.fill_between(df_pivot.index, df_pivot[distrito],
                            alpha=0.12, color=color)

        # Línea de media general
        media = df_pivot.mean(axis=1)
        ax.plot(media.index, media.values, color=_TEXT, linewidth=2.5,
                linestyle="--", label="Media general", zorder=5)
        ax.fill_between(media.index, media.values, alpha=0.08, color=_TEXT)

        # Escalar el eje Y al rango real de los datos (no desde 0)
        todos_valores = df_pivot.values
        vmin = pd.DataFrame(todos_valores).min().min()
        vmax = pd.DataFrame(todos_valores).max().max()
        margen = (vmax - vmin) * 0.15 or 1
        ax.set_ylim(vmin - margen, vmax + margen)

        media_global = float(df_pivot.values.mean())
        ax.text(
            0.99, 0.97,
            f"Media general: {media_global:.1f} {unidad}",
            transform=ax.transAxes,
            ha="right", va="top",
            fontsize=9, color=_TEXT,
            bbox=dict(boxstyle="round,pad=0.4", facecolor=_CARD_BG, edgecolor=_GRID, alpha=0.8),
        )

        ax.set_title(titulo, fontsize=13, color=_TEXT, pad=12)
        ax.set_xlabel("Fecha", color=_MUTED, fontsize=9)
        ax.set_ylabel(unidad, color=_MUTED, fontsize=9)
        rango_dias = (df_pivot.index.max() - df_pivot.index.min()).days
        if rango_dias <= 3:
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
        elif rango_dias <= 14:
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
        else:
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b '%y"))
            ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))

        ax.tick_params(axis="x", rotation=45, colors=_MUTED, labelsize=8)
        ax.tick_params(axis="y", colors=_MUTED, labelsize=8)
        ax.grid(axis="y", color=_GRID, linestyle="--", linewidth=0.6)
        ax.grid(axis="x", color=_GRID, linestyle=":", linewidth=0.4)
        for spine in ax.spines.values():
            spine.set_edgecolor(_GRID)

        # Leyenda horizontal debajo del gráfico, fuera del área de datos
        ax.legend(
            loc="upper center",
            bbox_to_anchor=(0.5, -0.18),
            ncol=6,
            fontsize=7.5,
            framealpha=0.2,
            facecolor=_CARD_BG,
            edgecolor=_GRID,
            labelcolor=_TEXT,
        )

        fig.subplots_adjust(bottom=0.22)
        buf = BytesIO()
        plt.savefig(buf, format="png", dpi=120, facecolor=_BG, bbox_inches="tight")
        plt.close()
        buf.seek(0)
        data = base64.b64encode(buf.read()).decode("utf-8")
        return f"data:image/png;base64,{data}"

    @staticmethod
    def generar_grafica_temperatura():
        return GraphService._generar_grafica("temperatura", "Temperatura por Distrito", "°C")

    @staticmethod
    def generar_grafica_humedad():
        return GraphService._generar_grafica("humedad", "Humedad por Distrito", "%")

    @staticmethod
    def generar_grafica_viento():
        return GraphService._generar_grafica("viento", "Viento por Distrito", "km/h")
