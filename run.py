import subprocess
import sys
import os

# Sincronización de Entorno para que los subprocesos vean las librerías instaladas
env_actual = os.environ.copy()
env_actual["PYTHONPATH"] = os.getcwd()

print(">>> [SISTEMA] Iniciando Orquestador UrbanNexus...")

flask_app = subprocess.Popen([
    sys.executable, "app.py"
], env=env_actual)

api = subprocess.Popen([
    sys.executable, "-m", "uvicorn",
    "main_api:app",
    "--host", "0.0.0.0",
    "--port", "8000"
], env=env_actual)

print(">>> [SISTEMA] Flask activo en http://127.0.0.1:5000")
print(">>> [SISTEMA] FastAPI activo en http://127.0.0.1:8000")
print(">>> [SISTEMA] Presiona Ctrl+C para detener ambos servicios.")

try:
    api.wait()
except KeyboardInterrupt:
    print("\n[!] Deteniendo servidores por interrupción de usuario...")
    flask_app.terminate()
    api.terminate()
    sys.exit(0)