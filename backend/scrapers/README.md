"""Ayuda para obtener cookies de supermercados con Cloudflare (Carrefour, Dia).

Como obtener la cookie:
1. Abre Chrome/Edge/Firefox en tu ordenador
2. Navega a https://www.carrefour.es/supermercado
3. Abre DevTools (F12) > Application > Cookies > carrefour.es
4. Copia TODO el contenido de la columna "Value" de todas las cookies
5. Pegalo en el archivo .env como:
   COOKIE_CARREFOUR="cookie1=valor1; cookie2=valor2; ..."

O usa una extension como "Cookie-Editor" para exportar en formato string.

Para verificar que la cookie funciona:
   python3 -c "from scrapers.carrefour import CarrefourScraper; import asyncio; r=asyncio.run(CarrefourScraper('COOKIE_AQUI').fetch_all()); print(f'{len(r)} productos')"
"""
