from fastapi import FastAPI

from app.routers import documents, health, query

app = FastAPI(
    title="Mi Asesor Legal API",
    description="Servicio RAG para consultar expedientes judiciales peruanos.",
    version="1.0.0",
)

app.include_router(health.router)
app.include_router(query.router)
app.include_router(documents.router)
