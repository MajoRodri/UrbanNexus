import subprocess
import sys

# sys.executable apunta al intérprete de Python del entorno virtual activo,
# así no hay que escribir la ruta completa a mano.

# Levanta la app Flask (app.py) — interfaz web principal
flask = subprocess.Popen([sys.executable, "app.py"])

# Levanta la API FastAPI (main_api.py) con uvicorn en el puerto 8000.
# --reload hace que se reinicie automáticamente al detectar cambios en el código.
api = subprocess.Popen([
    sys.executable, "-m", "uvicorn",
    "main_api:app",
    "--reload",
    "--port", "8000"
])

print("Servidores iniciados. Presiona Ctrl+C para detener ambos.")

try:
    # Espera a que ambos procesos terminen (corren indefinidamente hasta que se interrumpan con Ctrl + C)
    flask.wait()
    api.wait()
except KeyboardInterrupt:
    # Ctrl+C llega aquí: termina ambos procesos de forma ordenada
    print("\nDeteniendo servidores...")
    flask.terminate()
    api.terminate()
