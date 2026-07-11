"""Scraper de Carrefour usando API cloud.

Requiere cookie de sesion de Carrefour (obtenida del navegador).
La cookie se puede pasar via variable de entorno COOKIE_CARREFOUR
o en el constructor.
"""

from typing import Any
import httpx
import os

from .base import ScraperBase, OfertaScrap

CATEGORY_API = "https://www.carrefour.es/cloud-api/categories-api/v1/categories/menu/"
PRODUCT_API = "https://www.carrefour.es/cloud-api/plp-food-papi/v1"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "es-ES,es;q=0.9",
    "Referer": "https://www.carrefour.es/supermercado",
}


class CarrefourScraper(ScraperBase):
    """Scraper de Carrefour via su API cloud (requiere cookie de sesion)."""

    def __init__(self, cookie: str | None = None):
        super().__init__(nombre="Carrefour", url_base="https://www.carrefour.es")
        self.cookie = cookie or os.getenv("COOKIE_CARREFOUR", "")

    async def fetch_all(self) -> list[OfertaScrap]:
        if not self.cookie:
            print("[Carrefour] No hay cookie. Usa COOKIE_CARREFOUR o pasala al constructor.")
            return []

        headers = {**HEADERS, "Cookie": self.cookie}
        resultados: list[OfertaScrap] = []

        async with httpx.AsyncClient(headers=headers, timeout=30) as client:
            # Obtener categorias
            resp = await client.get(CATEGORY_API)
            if resp.status_code == 403:
                print("[Carrefour] Cookie expirada. Renueva desde tu navegador.")
                return []
            if resp.status_code != 200:
                return []

            data = resp.json()
            rutas_categoria = self._extraer_rutas(data)

            for ruta in rutas_categoria[:50]:  # Limitar a 50 categorias
                try:
                    resp = await client.get(f"{PRODUCT_API}{ruta}?offset=0")
                    if resp.status_code != 200:
                        continue
                    prods = resp.json()
                    items = prods.get("results", [])
                    for item in items:
                        for p in item.get("items", []):
                            resultados.append(
                                OfertaScrap(
                                    supermercado="Carrefour",
                                    nombre_producto=p.get("name", ""),
                                    categoria=item.get("name", ""),
                                    precio=float(p.get("price", 0)),
                                    imagen_url=p.get("images", {}).get("desktop", ""),
                                    url_producto=f"https://www.carrefour.es{p.get('url', '')}",
                                    unidad=p.get("measure_unit", "ud"),
                                    producto_id=str(p.get("product_id", "")),
                                )
                            )
                except Exception:
                    continue

        return resultados

    def _extraer_rutas(self, data: dict) -> list[str]:
        """Extrae las rutas de categorias de la respuesta de la API."""
        rutas = []
        menu = data.get("menu", [])
        for item in menu:
            childs = item.get("childs", [])
            for child in childs:
                url = child.get("url_rel", "")
                if url.startswith("/supermercado") and "ofertas" not in url:
                    rutas.append(url)
                    # Subcategorias
                    sub_childs = child.get("childs", [])
                    for sub in sub_childs:
                        sub_url = sub.get("url_rel", "")
                        if sub_url:
                            rutas.append(sub_url)
        return rutas

    async def scrape(self, codigo_postal: str | None = None) -> list[OfertaScrap]:
        return await self.fetch_all()
