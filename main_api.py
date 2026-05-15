from dotenv import load_dotenv
load_dotenv(override=True)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
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

# Inicializar tablas y superadmin
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

# Servir estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    favicon_path = os.path.join("static", "img", "Logo.png")
    return FileResponse(favicon_path) if os.path.exists(favicon_path) else None

# --- ENDPOINT RAÍZ CORREGIDO PARA TESTS ---
@app.get("/")
def serve_root():
    """
    Devuelve un mensaje JSON para que los tests no fallen con JSONDecodeError.
    Para ver la web, se puede usar el endpoint /showcase o FileResponse aquí.
    """
    return {"message": "UrbanNexus API funcionando correctamente"}

@app.get("/showcase", response_class=HTMLResponse)
async def serve_showcase():
    """Endpoint específico para servir la web de presentación"""
    file_path = os.path.join("templates", "showcase.html")
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return HTMLResponse("Error: showcase.html no encontrado", status_code=404)

@app.get("/login", include_in_schema=False)
async def login_bridge():
    return RedirectResponse(url="http://127.0.0.1:5000/login")

@app.get("/privacy-policy", response_class=HTMLResponse)
async def privacy_policy():
    return """
    <html><body style="background:#030712;color:#94a3b8;font-family:monospace;padding:80px;">
    <h1 style="color:#10b981;">PRIVACY_POLICY</h1><p>Secured under ACID protocols.</p>
    </body></html>
    """

@app.get("/terms-of-service", response_class=HTMLResponse)
async def terms_of_service():
    return """
    <html><body style="background:#030712;color:#94a3b8;font-family:sans-serif;padding:80px;">
    <h1 style="color:#10b981;">TERMS_OF_SERVICE</h1><p>Audit infrastructure accepted.</p>
    </body></html>
    """

@app.post("/launch")
def launch():
    try:
        python_actual = sys.executable
        env = os.environ.copy()
        env["PYTHONPATH"] = os.getcwd()
        subprocess.Popen([python_actual, "app.py"], env=env)
        time.sleep(3)
        return {"status": "success", "message": "Kernel Online"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/v1/root_status")
def root_status():
    return {"message": "UrbanNexus API funcionando"}

# Rutas de la API
app.include_router(invitation_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1/users", tags=["Users"])
app.include_router(zones_router, prefix="/api/v1/zones", tags=["Zones"])
app.include_router(records_router, prefix="/api/v1/records", tags=["Records"])
app.include_router(auth_router, prefix="/api/v1")