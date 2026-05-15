import subprocess
import sys
import os

# Sincronización de Entorno para que los subprocesos vean las librerías instaladas
env_actual = os.environ.copy()
env_actual["PYTHONPATH"] = os.getcwd()

print(">>> [SISTEMA] Iniciando Orquestador UrbanNexus...")

# Lanzamos ÚNICAMENTE la Showcase (FastAPI) en el puerto 8000
# El archivo app.py se lanzará cuando presiones el botón en la web
api = subprocess.Popen([
    sys.executable, "-m", "uvicorn",
    "main_api:app",
    "--port", "8000"
], env=env_actual)

print(">>> [SISTEMA] Showcase activa en http://127.0.0.1:8000")
print(">>> [SISTEMA] Presiona Ctrl+C para detener el servicio.")

try:
    # Mantenemos el proceso vivo
    api.wait()
except KeyboardInterrupt:
    print("\n[!] Deteniendo servidores por interrupción de usuario...")
    api.terminate()
    sys.exit(0)