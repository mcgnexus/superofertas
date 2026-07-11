"""Scraper de Dia usando curl_cffi (bypassea Cloudflare)."""

import json
import os
from typing import Any

from .base import ScraperBase, OfertaScrap


class DiaScraper(ScraperBase):
    """Scraper de Dia via API interna con bypass de Cloudflare."""

    def __init__(self, cookie: str | None = None):
        super().__init__(nombre="Dia", url_base="https://www.dia.es")
        self.cookie = cookie or os.getenv("COOKIE_DIA", "")

    async def fetch_all(self, max_paginas: int = 5) -> list[OfertaScrap]:
        """Scrapea productos de Dia (sincrono via curl_cffi en thread)."""
        if not self.cookie:
            print("[Dia] No hay cookie. Usa COOKIE_DIA o pasala al constructor.")
            return []

        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        def _scrape() -> list[OfertaScrap]:
            from curl_cffi import requests as curl

            s = curl.Session(impersonate="chrome120")
            for par in self.cookie.split(";"):
                par = par.strip()
                if "=" in par:
                    k, v = par.split("=", 1)
                    s.cookies.set(k, v)

            s.get("https://www.dia.es/")
            s.get("https://www.dia.es/compra-online/")

            headers = {
                "Accept": "application/json, text/plain, */*",
                "Referer": "https://www.dia.es/compra-online/",
            }

            resultados: list[OfertaScrap] = []
            ids_vistos: set[str] = set()
            max_total = max_paginas * 20

            for pagina in range(1, max_paginas + 1):
                try:
                    url = f"https://www.dia.es/api/v1/plp-back/reduced?navigation=/c/L00000&page={pagina}&pageSize=20"
                    r = s.get(url, headers=headers, timeout=15)
                    if r.status_code not in (200, 404):
                        break

                    data = r.json()
                    items = data.get("plp_items", [])
                    if not items:
                        break

                    for item in items:
                        pid = str(item.get("object_id", ""))
                        if pid in ids_vistos:
                            continue
                        ids_vistos.add(pid)

                        prices = item.get("prices", {})
                        precio = prices.get("price")
                        if precio is None:
                            continue

                        resultados.append(
                            OfertaScrap(
                                supermercado="Dia",
                                nombre_producto=item.get("display_name", ""),
                                categoria=item.get("category_name", item.get("department", "")),
                                precio=float(precio),
                                imagen_url=f"https://www.dia.es{item.get('image', '')}" if item.get("image") else "",
                                url_producto=f"https://www.dia.es{item.get('url', '')}" if item.get("url") else "",
                                unidad=prices.get("measure_unit", "ud"),
                                producto_id=pid,
                            )
                        )

                        if len(resultados) >= max_total:
                            break

                    if len(resultados) >= max_total:
                        break

                except Exception:
                    break

            return resultados

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _scrape)

    async def scrape(self, codigo_postal: str | None = None) -> list[OfertaScrap]:
        return await self.fetch_all()
