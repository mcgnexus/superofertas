"""App principal FastAPI."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from routers.ofertas import router as ofertas_router
from routers.menu import router as menu_router
from database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Crea las tablas de la BD al arrancar."""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="OfertasSuper + MenuSemanal IA",
    description="API para buscar ofertas de supermercados y generar menús semanales con IA",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS - permitir frontend PWA
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: restringir en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(ofertas_router)
app.include_router(menu_router)


@app.get("/")
async def root():
    return {
        "mensaje": "Bienvenido a OfertasSuper + MenuSemanal IA API",
        "docs": "/docs",
        "version": "0.1.0",
    }


@app.get("/health")
async def health_check():
    return {"estado": "ok"}
