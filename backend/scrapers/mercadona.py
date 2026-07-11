"""Scraper real de Mercadona usando API pública."""

from typing import Any
import httpx

from .base import ScraperBase, OfertaScrap


class MercadonaScraper(ScraperBase):
    """Scraper de Mercadona via su API pública de tienda online."""

    def __init__(self):
        super().__init__(nombre="Mercadona", url_base="https://tienda.mercadona.es/api")

    async def fetch_all(self) -> list[OfertaScrap]:
        """
        Obtiene todos los productos de Mercadona recorriendo
        recursivamente el arbol de categorias.
        """
        resultados: list[OfertaScrap] = []
        visitadas: set[int] = set()

        async with httpx.AsyncClient(base_url=self.url_base, timeout=30) as client:

            async def procesar_subcategorias(
                lista_cats: list[dict], ruta: list[str]
            ) -> None:
                for sub in lista_cats:
                    sub_id = sub.get("id")
                    sub_nombre = sub.get("name", "")
                    if sub_id is None or sub_id in visitadas:
                        continue
                    visitadas.add(sub_id)

                    prods = sub.get("products", [])
                    if prods:
                        # Categoria hoja con productos
                        for p in prods:
                            pi = p.get("price_instructions", {})
                            precio_ant_raw = pi.get("previous_unit_price")
                            precio_unit = pi.get("unit_price")
                            precio = pi.get("bulk_price")
                            if precio is None:
                                continue

                            precio_ant: float | None = None
                            if precio_ant_raw is not None:
                                try:
                                    precio_ant = float(str(precio_ant_raw).strip())
                                except (ValueError, TypeError):
                                    pass

                            es_oferta = pi.get("price_decreased", False) or (
                                precio_ant is not None
                                and precio_unit is not None
                                and precio_ant > float(str(precio_unit).strip())
                            )
                            # precio_normal es el precio por unidad actual (unit_price)
                            precio_unit_val = float(str(precio_unit).strip()) if precio_unit else precio
                            descuento = 0
                            if (
                                es_oferta
                                and precio_ant is not None
                                and precio_ant > 0
                            ):
                                descuento = round(
                                    (precio_ant - precio_unit_val)
                                    / precio_ant
                                    * 100
                                )

                            resultados.append(
                                OfertaScrap(
                                    supermercado="Mercadona",
                                    nombre_producto=p.get("display_name", ""),
                                    categoria=sub_nombre,
                                    categoria_principal=ruta[0] if ruta else "",
                                    precio=precio,
                                    precio_normal=precio_unit_val,
                                    precio_anterior=precio_ant,
                                    descuento=descuento,
                                    es_oferta=es_oferta,
                                    imagen_url=p.get("thumbnail", ""),
                                    url_producto=p.get("share_url", ""),
                                    unidad=pi.get("unit_name", "ud"),
                                    cantidad=pi.get("unit_size"),
                                    producto_id=str(p["id"]),
                                    precio_referencia=pi.get("reference_price"),
                                    formato_referencia=pi.get("reference_format", ""),
                                    iva=pi.get("iva", 0),
                                )
                            )
                    else:
                        # Bajamos un nivel mas
                        resp = await client.get(f"/categories/{sub_id}/")
                        if resp.status_code != 200:
                            continue
                        data = resp.json()
                        sub_subcats = data.get("categories", [])
                        if sub_subcats:
                            await procesar_subcategorias(
                                sub_subcats, ruta + [sub_nombre]
                            )

            # Obtener las 26 categorias principales
            resp = await client.get("/categories/")
            if resp.status_code != 200:
                return resultados
            data = resp.json()

            for cat_princ in data.get("results", []):
                subcats = cat_princ.get("categories", [])
                await procesar_subcategorias(subcats, [cat_princ["name"]])

        return resultados

    async def scrape(self, codigo_postal: str | None = None) -> list[OfertaScrap]:
        return await self.fetch_all()
