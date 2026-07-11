"""Router para generación de menús semanales con IA."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from database import SessionLocal, Oferta, Producto, Supermercado, Menu
from services.menu_ia import MenuIAService
from services.presupuesto import PresupuestoService
from datetime import datetime
from typing import Optional

router = APIRouter()


class MenuRequest(BaseModel):
    """Modelo de petición para generar un menú semanal."""
    presupuesto: float = Field(..., gt=0, description="Presupuesto total en euros")
    num_personas: int = Field(default=4, ge=1, le=20)
    supermercados: list[str] = Field(default=["Mercadona"])
    restricciones: list[str] | None = None  # ej: ["celíaco", "vegano", "sin lactosa"]


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/api/menu/generar")
async def generar_menu(request: MenuRequest, db: Session = Depends(get_db)):
    """
    Genera un menú semanal con recetas usando las ofertas disponibles
    y un presupuesto determinado, mediante IA.
    """
    presupuesto = request.presupuesto
    num_personas = request.num_personas
    restricciones = request.restricciones or []

    # 1. Obtener ofertas de los supermercados seleccionados
    query = db.query(Oferta).join(Producto).join(Supermercado)
    query = query.filter(Supermercado.nombre.in_(request.supermercados))
    ofertas_db = query.all()

    if not ofertas_db:
        raise HTTPException(
            status_code=404,
            detail="No hay ofertas disponibles para los supermercados seleccionados"
        )

    # 2. Filtrar y optimizar por presupuesto
    svc_presupuesto = PresupuestoService(db)
    ofertas_optimizadas = svc_presupuesto.optimizar_seleccion(
        ofertas_db, presupuesto, num_personas
    )

    if not ofertas_optimizadas:
        raise HTTPException(
            status_code=404,
            detail="No hay ofertas dentro del presupuesto indicado"
        )

    # 3. Preparar datos de productos para la IA
    productos_ia = [
        {
            "nombre": o.producto.nombre,
            "categoria": o.producto.categoria,
            "precio": o.precio_oferta,
        }
        for o in ofertas_optimizadas
    ]

    # 4. Generar menú con IA
    svc_ia = MenuIAService()
    try:
        menu_generado = await svc_ia.generar_menu_semanal(
            productos=productos_ia,
            presupuesto=presupuesto,
            num_personas=num_personas,
            restricciones=restricciones,
        )
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Error al generar menú con IA: {str(e)}"
        )

    # 5. Guardar en base de datos
    menu_db = Menu(
        presupuesto=presupuesto,
        num_personas=num_personas,
        fecha_creacion=datetime.now(),
    )
    db.add(menu_db)
    db.commit()
    db.refresh(menu_db)

    return {
        "menu_id": menu_db.id,
        "presupuesto": presupuesto,
        "num_personas": num_personas,
        "supermercados": request.supermercados,
        "restricciones": restricciones,
        "productos_utilizados": len(ofertas_optimizadas),
        "menu": menu_generado,
    }


@router.get("/api/menu/{menu_id}")
async def obtener_menu(menu_id: int, db: Session = Depends(get_db)):
    """Obtiene un menú guardado por su ID."""
    menu = db.query(Menu).filter(Menu.id == menu_id).first()
    if not menu:
        raise HTTPException(status_code=404, detail="Menú no encontrado")
    return {
        "id": menu.id,
        "presupuesto": menu.presupuesto,
        "num_personas": menu.num_personas,
        "fecha_creacion": menu.fecha_creacion,
    }
