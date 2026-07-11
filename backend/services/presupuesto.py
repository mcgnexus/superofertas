"""Servicio de filtrado y optimización de ofertas por presupuesto."""

from typing import Any


class PresupuestoService:
    """Filtra ofertas dentro de un presupuesto y optimiza la selección."""

    def __init__(self, db_session=None):
        self.db = db_session

    def filtrar_por_precio(self, ofertas: list[Any], precio_max: float) -> list[Any]:
        """Filtra ofertas cuyo precio sea menor o igual al precio máximo."""
        return [
            o for o in ofertas
            if self._obtener_precio(o) <= precio_max
        ]

    def filtrar_por_categoria(self, ofertas: list[Any], categoria: str) -> list[Any]:
        """Filtra ofertas por categoría de producto."""
        return [o for o in ofertas if categoria.lower() in self._obtener_categoria(o).lower()]

    def ordenar_por_relacion_calidad_precio(self, ofertas: list[Any]) -> list[Any]:
        """Ordena ofertas de mejor a peor relación calidad-precio."""
        return sorted(ofertas, key=lambda o: self._obtener_precio(o))

    def optimizar_seleccion(
        self, ofertas: list[Any], presupuesto: float, num_personas: int
    ) -> list[Any]:
        """
        Selecciona las mejores ofertas dentro del presupuesto.
        
        Estrategia: priorizar categorías básicas (proteínas, verduras,
        cereales, lácteos) y repartir el presupuesto equilibradamente.
        """
        if not ofertas:
            return []

        # Categorías prioritarias para una dieta equilibrada
        prioridades = {
            "frescos": 1, "fruta": 1, "verdura": 1, "verduras": 1,
            "carne": 2, "pescado": 2, "lácteos": 2, "lacteos": 2,
            "pan": 3, "cereales": 3, "arroz": 3, "pasta": 3,
            "bebidas": 4, "snacks": 5,
        }

        # Ordenar por prioridad de categoría y luego por precio
        def prioridad(oferta):
            cat = self._obtener_categoria(oferta).lower()
            return prioridades.get(cat, 9)

        ofertas_ordenadas = sorted(ofertas, key=lambda o: (prioridad(o), self._obtener_precio(o)))

        # Seleccionar dentro del presupuesto
        presupuesto_por_persona = presupuesto / max(num_personas, 1)
        seleccionadas = []
        gastado = 0.0

        for oferta in ofertas_ordenadas:
            precio = self._obtener_precio(oferta)
            if gastado + precio <= presupuesto:
                seleccionadas.append(oferta)
                gastado += precio

        return seleccionadas

    def _obtener_precio(self, oferta: Any) -> float:
        """Obtiene el precio de una oferta (dict u objeto ORM)."""
        if isinstance(oferta, dict):
            return oferta.get("precio_oferta") or oferta.get("precio", 0.0)
        return getattr(oferta, "precio_oferta", None) or getattr(oferta, "precio", 0.0)

    def _obtener_categoria(self, oferta: Any) -> str:
        """Obtiene la categoría de una oferta (dict u objeto ORM)."""
        if isinstance(oferta, dict):
            return oferta.get("categoria", "")
        return getattr(oferta, "categoria", "")
