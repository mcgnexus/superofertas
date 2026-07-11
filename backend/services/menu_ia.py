"""Servicio de generación de menús semanales con IA."""

import json
import urllib.request
import urllib.error
from typing import Any

import os

_IA_API_URL = os.getenv("IA_API_URL", "https://api.deepseek.com/v1/chat/completions")
_IA_API_KEY = os.getenv("IA_API_KEY", "")
_IA_MODEL = os.getenv("IA_MODEL", "deepseek-chat")


class MenuIAService:
    """Genera menús semanales con recetas usando una API de IA (formato OpenAI)."""

    def __init__(self, api_url: str | None = None, api_key: str | None = None, model: str | None = None):
        self.api_url = api_url or _IA_API_URL
        self.api_key = api_key or _IA_API_KEY
        self.model = model or _IA_MODEL

    async def generar_menu_semanal(
        self,
        productos: list[dict[str, Any]],
        presupuesto: float,
        num_personas: int,
        restricciones: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Genera un menú semanal (7 días, 5 comidas/día) con recetas
        usando solo los productos indicados dentro del presupuesto.
        """
        productos_str = "\n".join([
            f"- {p['nombre']} ({p.get('categoria', '')}): {p.get('precio', 0):.2f}€"
            for p in productos
        ])

        restricciones_str = ", ".join(restricciones) if restricciones else "ninguna"

        prompt = f"""Eres un nutricionista experto y chef. Genera un menú semanal de 7 días con 5 comidas por día (desayuno, media mañana, comida, merienda, cena) usando ÚNICAMENTE los productos disponibles en oferta.

RESTRICCIONES DIETÉTICAS: {restricciones_str}
PRESUPUESTO TOTAL: {presupuesto:.2f}€ para {num_personas} persona(s) para toda la semana.

PRODUCTOS DISPONIBLES EN OFERTA:
{productos_str}

Responde EXCLUSIVAMENTE con un JSON válido con esta estructura:
{{
  "titulo": "Menú semanal con ofertas",
  "presupuesto_estimado": 0.0,
  "ahorro_estimado": 0.0,
  "dias": [
    {{
      "dia": 1,
      "nombre": "Lunes",
      "comidas": [
        {{
          "tipo": "Desayuno",
          "nombre_plato": "...",
          "ingredientes": ["...", "..."],
          "instrucciones": "...",
          "tiempo_minutos": 15,
          "calorias_aprox": 400
        }}
      ]
    }}
  ]
}}

Distribuye los ingredientes de forma inteligente para no gastar más del presupuesto. Incluye todos los días de Lunes a Domingo."""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "Eres un asistente experto en nutrición y cocina española. Siempre respondes con JSON válido."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.7,
        }

        # Usar urllib en vez de httpx para evitar problemas de DNS en el event loop
        req_data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(self.api_url, data=req_data, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"Error API IA ({e.code}): {e.read().decode('utf-8', errors='replace')[:200]}")

        contenido = data.get("choices", [{}])[0].get("message", {}).get("content", "{}")

        # Intentar parsear el JSON de la respuesta
        try:
            return json.loads(contenido)
        except json.JSONDecodeError:
            inicio = contenido.find("{")
            fin = contenido.rfind("}") + 1
            if inicio >= 0 and fin > inicio:
                return json.loads(contenido[inicio:fin])
            return {"error": "No se pudo parsear la respuesta de la IA", "contenido": contenido}
