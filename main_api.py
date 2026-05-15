from dotenv import load_dotenv
load_dotenv(override=True)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse # <-- Añadido FileResponse
from api.routes.zones_routes import router as zones_router
from api.routes.records_routes import router as records_router
from api.routes.users_routes import router as users_router
from controllers.auth_fast_controller import router as auth_router
from controllers.invitation_fast_controller import router as invitation_router
from db.database import create_tables
from services.startup_service import create_default_superadmin
import subprocess
import os
import sys
import time

# Inicializar tablas de la base de datos
create_tables()
create_default_superadmin()

app = FastAPI(title="UrbanNexus_Launcher")

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir archivos estáticos (CSS, JS, Imágenes)
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- SOLUCIÓN FAVICON 404 ---
@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    """Sirve el logo como favicon para limpiar la consola de errores"""
    favicon_path = os.path.join("static", "img", "Logo.png")
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path)
    return None

@app.get("/", response_class=HTMLResponse)
def serve_showcase():
    """Sirve la web de presentación (Showcase)"""
    file_path = os.path.join("templates", "showcase.html")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h3>Error: showcase.html no encontrado en /templates</h3>"

# --- RUTAS DE NAVEGACIÓN Y LEGALES ---

@app.get("/", response_class=HTMLResponse)
async def serve_showcase():
    file_path = os.path.join("templates", "showcase.html")
    return FileResponse(file_path) if os.path.exists(file_path) else HTMLResponse("Error 404", 404)

@app.get("/login", include_in_schema=False)
async def login_bridge():
    # Esto asegura que si alguien entra por el puerto 8000/login, no de 404
    return RedirectResponse(url="http://127.0.0.1:5000/login")

@app.get("/privacy-policy", response_class=HTMLResponse)
async def privacy_policy():
    return """
    <html>
    <head><title>UrbanNexus // Privacy</title></head>
    <body style="background:#030712;color:#94a3b8;font-family:monospace;padding:80px;line-height:1.6;">
        <h1 style="color:#10b981;border-bottom:1px solid #1e293b;padding-bottom:10px;">PRIVACY_POLICY // SECURED_LAYER</h1>
        <p>UrbanNexus processes climate telemetry under asymmetric encryption and ACID persistence protocols.</p>
        <p style="font-size:12px;opacity:0.5;margin-top:40px;">STATUS: SECURE_STREAMS_ACTIVE // 2026</p>
    </body>
    </html>
    """

@app.get("/terms-of-service", response_class=HTMLResponse)
async def terms_of_service():
    return """
    <html>
    <head><title>UrbanNexus // Terms</title></head>
    <body style="background:#030712;color:#94a3b8;font-family:sans-serif;padding:80px;line-height:1.6;">
        <h1 style="color:#10b981;font-family:monospace;letter-spacing:-1px;">TERMS_OF_SERVICE // DISTRIBUTED_PROTOCOLS</h1>
        <p>El acceso al núcleo de UrbanNexus implica la aceptación de los protocolos de auditoría de infraestructura distribuida.</p>
        <hr style="border:1px solid #1e293b;margin:40px 0;">
        <p style="font-size:12px;opacity:0.5;font-family:monospace;">FIRMWARE: v4.5_STABLE // KERNEL_INIT</p>
    </body>
    </html>
    """

@app.post("/launch")
def launch():
    """Gatillo que ejecuta SOLO la app de Flask (app.py) heredando el entorno"""
    try:
        # Detectamos el intérprete de Python del entorno virtual activo
        python_actual = sys.executable
        
        # Heredamos las variables de entorno para que encuentre Flask
        env = os.environ.copy()
        env["PYTHONPATH"] = os.getcwd()

        # Lanzamos app.py directamente para evitar bucles
        subprocess.Popen([python_actual, "app.py"], env=env)
        
        # 🚨 RETARDO CRÍTICO: Forzamos a la API a esperar 3 segundos. 🚨
        print(">>> [KERNEL] Esperando 3 segundos a que el servidor Flask en el puerto 5000 se estabilice...")
        time.sleep(3)
        
        print(">>> [KERNEL] App Principal (Flask) lanzada desde Showcase.")
        return {"status": "success", "message": "Kernel Online"}
    except Exception as e:
        print(f">>> [KERNEL] Error al lanzar app.py: {str(e)}")
        return {"status": "error", "message": str(e)}

@app.get("/api/v1/root_status")
def root():
    """Mensaje de bienvenida de la API"""
    return {"message": "UrbanNexus API funcionando"}

# Inclusión de todas las rutas
app.include_router(invitation_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1/users", tags=["Users"])
app.include_router(zones_router, prefix="/api/v1/zones", tags=["Zones"])
app.include_router(records_router, prefix="/api/v1/records", tags=["Records"])
app.include_router(auth_router, prefix="/api/v1")