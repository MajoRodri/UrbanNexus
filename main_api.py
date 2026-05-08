from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes.zones_router import router as zones_router
from api.routes.records_router import router as records_router

app = FastAPI(
    title="UrbanNexus",
    description="API de zonas y registros climáticos",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(zones_router, prefix="/api/v1/zones", tags=["Zones"])
app.include_router(records_router, prefix="/api/v1/records", tags=["Records"])

@app.get("/")
def root():
    return {"message": "UrbanNexus API funcionando"}
