"""Clase base para scrapers de supermercados."""

from abc import ABC, abstractmethod
from typing import Any
from dataclasses import dataclass, field


@dataclass
class OfertaScrap:
    """Estructura de datos de un producto/oferta extraído por el scraper."""

    supermercado: str
    nombre_producto: str
    categoria: str
    precio: float
    precio_normal: float | None = None
    descuento: int = 0
    es_oferta: bool = False
    imagen_url: str = ""
    url_producto: str = ""
    unidad: str = "ud"
    cantidad: float | None = None
    precio_anterior: float | None = None
    categoria_principal: str = ""
    producto_id: str = ""
    precio_referencia: float | None = None
    formato_referencia: str = ""
    iva: int = 0


class ScraperBase(ABC):
    """Clase abstracta base para todos los scrapers de supermercados."""

    def __init__(self, nombre: str, url_base: str = ""):
        self.nombre = nombre
        self.url_base = url_base

    @abstractmethod
    async def fetch_all(self) -> list[OfertaScrap]:
        """
        Obtiene todos los productos del supermercado.
        Returns:
            Lista de productos encontrados.
        """
        ...

    async def fetch_ofertas(self) -> list[OfertaScrap]:
        """Obtiene solo los productos en oferta."""
        todos = await self.fetch_all()
        return [p for p in todos if p.es_oferta]

    def __repr__(self) -> str:
        return f"<ScraperBase {self.nombre}>"
