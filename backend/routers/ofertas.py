"""Router de ofertas - API pública y scraping."""

import os
from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal, Oferta, Producto, Supermercado

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _guardar_en_bd(db: Session, productos: list, nombre_sup: str) -> int:
    """Guarda productos de un supermercado en BD. Retorna cantidad."""
    sup = db.query(Supermercado).filter(Supermercado.nombre == nombre_sup).first()
    if not sup:
        sup = Supermercado(nombre=nombre_sup, ubicacion="Nacional")
        db.add(sup)
        db.flush()

    db.query(Oferta).filter(Oferta.supermercado_id == sup.id).delete()
    db.query(Producto).filter(Producto.supermercado_id == sup.id).delete()

    insertados = 0
    for p in productos[:500]:
        prod = Producto(
            nombre=p.nombre_producto,
            categoria=p.categoria,
            precio_unitario=p.precio,
            supermercado_id=sup.id,
            imagen_url=p.imagen_url,
            url_producto=p.url_producto,
            unidad=p.unidad,
        )
        db.add(prod)
        db.flush()
        db.add(Oferta(
            producto_id=prod.id, supermercado_id=sup.id,
            precio_oferta=p.precio, precio_normal=p.precio,
        ))
        insertados += 1

    db.commit()
    return insertados


@router.get("/api/ofertas")
async def get_ofertas(
    db: Session = Depends(get_db),
    supermercado: Optional[str] = Query(None),
    categoria: Optional[str] = Query(None),
    precio_max: Optional[float] = Query(None),
    limit: Optional[int] = Query(50),
):
    """Obtiene productos con sus precios de la base de datos."""
    query = db.query(Oferta).join(Producto).join(Supermercado)

    if supermercado:
        query = query.filter(Supermercado.nombre.ilike(f"%{supermercado}%"))
    if categoria:
        query = query.filter(Producto.categoria.ilike(f"%{categoria}%"))
    if precio_max:
        query = query.filter(Oferta.precio_oferta <= precio_max)

    ofertas = query.limit(limit).all()

    return [
        {
            "id": o.id,
            "producto": o.producto.nombre if o.producto else "",
            "categoria": o.producto.categoria if o.producto else "",
            "supermercado": o.supermercado.nombre if o.supermercado else "",
            "precio": o.precio_oferta,
            "imagen": o.producto.imagen_url if o.producto else "",
            "url": o.producto.url_producto if o.producto else "",
            "unidad": o.producto.unidad if o.producto else "",
        }
        for o in ofertas
    ]


@router.post("/api/scrape/mercadona")
async def scrape_mercadona(db: Session = Depends(get_db)):
    """Scrapea Mercadona (API publica, sin cookie)."""
    try:
        from scrapers.mercadona import MercadonaScraper
        prods = await MercadonaScraper().fetch_all()
        if prods:
            n = _guardar_en_bd(db, prods, "Mercadona")
            return {"scrapeado": n, "mensaje": f"Mercadona: {n} productos"}
        return {"scrapeado": 0, "mensaje": "No se encontraron productos"}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.post("/api/scrape/carrefour")
async def scrape_carrefour(db: Session = Depends(get_db)):
    """Scrapea Carrefour (requiere COOKIE_CARREFOUR en .env)."""
    cookie = os.getenv("COOKIE_CARREFOUR", "")
    if not cookie:
        return {"scrapeado": 0, "mensaje": "Sin cookie. Configura COOKIE_CARREFOUR en .env"}
    try:
        from scrapers.carrefour import CarrefourScraper
        prods = await CarrefourScraper(cookie=cookie).fetch_all()
        if prods:
            n = _guardar_en_bd(db, prods, "Carrefour")
            return {"scrapeado": n, "mensaje": f"Carrefour: {n} productos"}
        return {"scrapeado": 0, "mensaje": "Cookie expirada o sin productos"}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.post("/api/scrape/dia")
async def scrape_dia(db: Session = Depends(get_db)):
    """Scrapea Dia (requiere COOKIE_DIA en .env)."""
    cookie = os.getenv("COOKIE_DIA", "")
    if not cookie:
        return {"scrapeado": 0, "mensaje": "Sin cookie. Configura COOKIE_DIA en .env"}
    try:
        from scrapers.dia import DiaScraper
        prods = await DiaScraper(cookie=cookie).fetch_all()
        if prods:
            n = _guardar_en_bd(db, prods, "Dia")
            return {"scrapeado": n, "mensaje": f"Dia: {n} productos"}
        return {"scrapeado": 0, "mensaje": "Cookie expirada o sin productos"}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.post("/api/scrape/all")
async def scrape_all(db: Session = Depends(get_db)):
    """Ejecuta todos los scrapers disponibles."""
    resultados = {}

    # Mercadona
    try:
        from scrapers.mercadona import MercadonaScraper
        prods = await MercadonaScraper().fetch_all()
        if prods:
            n = _guardar_en_bd(db, prods, "Mercadona")
            resultados["Mercadona"] = f"{n} productos"
    except Exception as e:
        resultados["Mercadona"] = f"ERROR: {e}"

    # Carrefour
    cookie_c = os.getenv("COOKIE_CARREFOUR", "")
    if cookie_c:
        try:
            from scrapers.carrefour import CarrefourScraper
            prods = await CarrefourScraper(cookie=cookie_c).fetch_all()
            if prods:
                n = _guardar_en_bd(db, prods, "Carrefour")
                resultados["Carrefour"] = f"{n} productos"
        except Exception as e:
            resultados["Carrefour"] = f"ERROR: {e}"
    else:
        resultados["Carrefour"] = "sin cookie"

    # Dia
    cookie_d = os.getenv("COOKIE_DIA", "")
    if cookie_d:
        try:
            from scrapers.dia import DiaScraper
            prods = await DiaScraper(cookie=cookie_d).fetch_all()
            if prods:
                n = _guardar_en_bd(db, prods, "Dia")
                resultados["Dia"] = f"{n} productos"
        except Exception as e:
            resultados["Dia"] = f"ERROR: {e}"
    else:
        resultados["Dia"] = "sin cookie"

    return resultados


@router.get("/api/scrape/mercadona/productos")
async def get_scraped_products(
    ofertas_only: Optional[bool] = Query(False),
    limit: Optional[int] = Query(50),
    categoria: Optional[str] = Query(None),
):
    """Obtiene productos directamente del scraper de Mercadona (sin DB)."""
    try:
        from scrapers.mercadona import MercadonaScraper
        productos = await MercadonaScraper().fetch_all()
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    if ofertas_only:
        productos = [p for p in productos if p.es_oferta]
    if categoria:
        productos = [
            p for p in productos
            if categoria.lower() in p.categoria.lower()
            or categoria.lower() in p.categoria_principal.lower()
        ]

    productos = sorted(productos, key=lambda x: x.descuento, reverse=True)[:limit]

    return [
        {
            "producto": p.nombre_producto,
            "precio": p.precio,
            "precio_referencia": p.precio_normal,
            "precio_anterior": p.precio_anterior,
            "descuento": p.descuento,
            "es_oferta": p.es_oferta,
            "categoria": p.categoria,
            "seccion": p.categoria_principal,
            "imagen": p.imagen_url,
            "url": p.url_producto,
            "unidad": p.unidad,
            "formato_referencia": p.formato_referencia,
        }
        for p in productos
    ]
