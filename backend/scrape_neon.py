#!/usr/bin/env python3
"""Scraping rapido a Neon con urllib e inserts por lotes."""

import os
import sys
import json
import time
import urllib.request

# Configurar BD
os.environ["DATABASE_URL"] = "postgresql://neondb_owner:npg_0GYbju2XcZVn@ep-wispy-leaf-aliinft3-pooler.c-3.eu-central-1.aws.neon.tech/neondb?sslmode=require"

backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

from database import SessionLocal, Oferta, Producto, Supermercado, Base, engine
from sqlalchemy import text

print("Creando tablas...")
Base.metadata.create_all(bind=engine)

# Scrapear usando urllib (mas fiable que httpx aqui)
API_BASE = "https://tienda.mercadona.es/api"
print("Obteniendo categorias...")

resp = urllib.request.urlopen(f"{API_BASE}/categories/", timeout=30)
data = json.loads(resp.read())
categorias = data.get("results", [])
print(f"  {len(categorias)} categorias principales")

productos = []
visitadas = set()

def scrape_cat(subcats, ruta):
    """Procesa subcategorias recursivamente."""
    for sub in subcats:
        sub_id = sub.get("id")
        sub_nombre = sub.get("name", "")
        if sub_id is None or sub_id in visitadas:
            continue
        visitadas.add(sub_id)

        prods = sub.get("products", [])
        if prods:
            cat_princ = ruta[0] if ruta else ""
            for p in prods:
                pi = p.get("price_instructions", {})
                precio = pi.get("bulk_price")
                if precio is None:
                    continue
                productos.append({
                    "nombre": p.get("display_name", ""),
                    "categoria": sub_nombre,
                    "seccion": cat_princ,
                    "precio": precio,
                    "imagen": p.get("thumbnail", ""),
                    "url": p.get("share_url", ""),
                    "unidad": pi.get("unit_name", "ud"),
                    "producto_id": str(p["id"]),
                    "precio_unit": pi.get("unit_price"),
                    "precio_ant": pi.get("previous_unit_price"),
                    "reducido": pi.get("price_decreased", False),
                })
        else:
            try:
                r = urllib.request.urlopen(f"{API_BASE}/categories/{sub_id}/", timeout=15)
                d = json.loads(r.read())
                scrape_cat(d.get("categories", []), ruta + [sub_nombre])
            except Exception:
                pass

t0 = time.time()
for cat in categorias:
    try:
        r = urllib.request.urlopen(f"{API_BASE}/categories/{cat['id']}/", timeout=15)
        d = json.loads(r.read())
    except Exception:
        continue
    subcats = d.get("categories", [])
    scrape_cat(subcats, [cat["name"]])

t1 = time.time()
print(f"Scrapeado: {len(productos)} productos en {t1-t0:.0f}s")

# Insertar en Neon (bulk)
print("Conectando a Neon...")
db = SessionLocal()

# Upsert supermercado
sup = db.query(Supermercado).filter(Supermercado.nombre == "Mercadona").first()
if not sup:
    sup = Supermercado(nombre="Mercadona", ubicacion="Nacional")
    db.add(sup)
    db.flush()

# Limpiar datos viejos
db.query(Oferta).filter(Oferta.supermercado_id == sup.id).delete()
db.query(Producto).filter(Producto.supermercado_id == sup.id).delete()

# Insertar en batches
batch_size = 100
ofertas_count = 0
for i in range(0, len(productos), batch_size):
    batch = productos[i:i+batch_size]
    for p in batch:
        prod = Producto(
            nombre=p["nombre"],
            categoria=p["categoria"],
            precio_unitario=p["precio"],
            supermercado_id=sup.id,
            imagen_url=p["imagen"],
            url_producto=p["url"],
            unidad=p["unidad"],
        )
        db.add(prod)
        db.flush()
        
        # Detectar oferta
        es_oferta = p["reducido"] or (
            p["precio_ant"] is not None 
            and p["precio_unit"] is not None
            and float(p["precio_ant"]) > float(p["precio_unit"])
        )
        desc = 0
        if es_oferta and p["precio_ant"] and p["precio_unit"]:
            desc = round((float(p["precio_ant"]) - float(p["precio_unit"])) / float(p["precio_ant"]) * 100)
        
        db.add(Oferta(
            producto_id=prod.id,
            supermercado_id=sup.id,
            precio_oferta=p["precio"],
            precio_normal=p["precio"],
            descuento=desc,
        ))
        if es_oferta:
            ofertas_count += 1
    
    db.commit()
    print(f"  Insertados {min(i+batch_size, len(productos))}/{len(productos)}")

t2 = time.time()
print(f"\nTotal: {len(productos)} productos, {ofertas_count} ofertas")
print(f"Tiempo: scrape={t1-t0:.0f}s, insert={t2-t1:.0f}s")

# Verificar
print(f"\nVerificando Neon...")
db2 = SessionLocal()
print(f"  Supermercados: {db2.query(Supermercado).count()}")
print(f"  Productos: {db2.query(Producto).count()}")
print(f"  Ofertas: {db2.query(Oferta).count()}")
db2.close()
db.close()
