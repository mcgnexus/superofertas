"""Script de scraping automatico para usar desde cron o terminal."""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scrapers.mercadona import MercadonaScraper
from database import SessionLocal, Oferta, Producto, Supermercado, Base, engine


async def scrape_mercadona(db) -> dict:
    """Scrapea Mercadona y guarda en BD. Retorna resumen."""
    scraper = MercadonaScraper()
    productos = await scraper.fetch_all()

    if not productos:
        return {"error": "No se encontraron productos"}

    sup = db.query(Supermercado).filter(Supermercado.nombre == "Mercadona").first()
    if not sup:
        sup = Supermercado(nombre="Mercadona", ubicacion="Nacional")
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
            descuento=p.descuento,
        ))
        insertados += 1

    db.commit()
    ofertas_count = len([p for p in productos if p.es_oferta])
    return {
        "supermercado": "Mercadona",
        "productos": insertados,
        "ofertas_detectadas": ofertas_count,
        "categorias": len(set(p.categoria for p in productos)),
    }


async def main():
    """Ejecuta todos los scrapers disponibles y guarda en BD."""
    import time
    t0 = time.time()

    # Asegurar tablas
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    resultados = []

    print("=== Scraping automatico de supermercados ===")
    print()

    # Mercadona (siempre disponible)
    print("[Mercadona] Scrapeando...")
    try:
        r = await scrape_mercadona(db)
        resultados.append(r)
        print(f"  OK: {r['productos']} productos, {r['ofertas_detectadas']} ofertas, {r['categorias']} categorias")
    except Exception as e:
        print(f"  ERROR: {e}")

    elapsed = time.time() - t0
    print(f"\nTiempo total: {elapsed:.0f}s")
    print("\nResumen:")
    for r in resultados:
        if "error" in r:
            print(f"  {r.get('supermercado','?')}: ERROR - {r['error']}")
        else:
            print(f"  {r['supermercado']}: {r['productos']} productos, {r['ofertas_detectadas']} ofertas")

    db.close()
    return resultados


if __name__ == "__main__":
    asyncio.run(main())
