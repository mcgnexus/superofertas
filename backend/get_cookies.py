#!/usr/bin/env python3
"""Obtiene cookies de Carrefour usando Chromium headless + CDP."""

import json
import os
import subprocess
import time
import sys
from http.client import HTTPConnection


def get_carrefour_cookie() -> str:
    """Abre Carrefour en Chromium, supera Cloudflare y extrae cookies."""

    # 1. Lanzar Chromium headless con debug remoto
    port = 9222
    chrome_args = [
        "chromium-browser",
        "--headless=new",
        f"--remote-debugging-port={port}",
        "--remote-allow-origins=*",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "--window-size=1280,720",
        "--user-data-dir=/tmp/chrome-carrefour",
    ]
    proc = subprocess.Popen(
        chrome_args,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # 2. Esperar a que Chromium este listo
    for _ in range(30):
        try:
            conn = HTTPConnection("127.0.0.1", port, timeout=3)
            conn.request("GET", "/json/version")
            resp = conn.getresponse()
            if resp.status == 200:
                info = json.loads(resp.read())
                ws_url = info.get("webSocketDebuggerUrl", "")
                if ws_url:
                    break
            conn.close()
        except Exception:
            pass
        time.sleep(1)
    else:
        proc.kill()
        return ""

    # 3. Conectar via websocket CDP
    import websocket

    ws = websocket.create_connection(ws_url, timeout=30)

    def send_cmd(method: str, params: dict = None):
        msg = {"id": 1, "method": method, "params": params or {}}
        ws.send(json.dumps(msg))
        resp = ws.recv()
        return json.loads(resp)

    # 4. Navegar a Carrefour
    send_cmd("Page.enable")
    send_cmd("Page.navigate", {"url": "https://www.carrefour.es/supermercado"})
    
    # 5. Esperar a que cargue
    print("[Carrefour] Esperando a que Cloudflare nos deje pasar...")
    time.sleep(8)

    # 6. Obtener cookies
    result = send_cmd("Network.getAllCookies")
    cookies = result.get("result", {}).get("cookies", [])

    # 7. Cerrar
    ws.close()
    proc.terminate()
    proc.wait()

    # 8. Formatear cookies
    if not cookies:
        print("[Carrefour] No se obtuvieron cookies - Cloudflare nos bloqueo")
        return ""

    cookie_str = "; ".join([f'{c["name"]}={c["value"]}' for c in cookies])
    print(f"[Carrefour] {len(cookies)} cookies obtenidas ({len(cookie_str)} chars)")
    return cookie_str


def get_dia_cookie() -> str:
    """Obtiene cookies de Dia via Chromium."""
    port = 9223
    chrome_args = [
        "chromium-browser",
        "--headless=new",
        f"--remote-debugging-port={port}",
        "--remote-allow-origins=*",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--window-size=1280,720",
        "--user-data-dir=/tmp/chrome-dia",
    ]
    proc = subprocess.Popen(
        chrome_args,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    for _ in range(30):
        try:
            conn = HTTPConnection("127.0.0.1", port, timeout=3)
            conn.request("GET", "/json/version")
            resp = conn.getresponse()
            if resp.status == 200:
                info = json.loads(resp.read())
                ws_url = info.get("webSocketDebuggerUrl", "")
                if ws_url:
                    break
            conn.close()
        except Exception:
            pass
        time.sleep(1)
    else:
        proc.kill()
        return ""

    import websocket

    ws = websocket.create_connection(ws_url, timeout=30)

    def send_cmd(method: str, params: dict = None):
        msg = {"id": 1, "method": method, "params": params or {}}
        ws.send(json.dumps(msg))
        resp = ws.recv()
        return json.loads(resp)

    send_cmd("Page.enable")
    send_cmd("Page.navigate", {"url": "https://www.dia.es/"})
    print("[Dia] Esperando que cargue...")
    time.sleep(8)

    result = send_cmd("Network.getAllCookies")
    cookies = result.get("result", {}).get("cookies", [])

    ws.close()
    proc.terminate()
    proc.wait()

    if not cookies:
        print("[Dia] No se obtuvieron cookies")
        return ""

    cookie_str = "; ".join([f'{c["name"]}={c["value"]}' for c in cookies])
    print(f"[Dia] {len(cookies)} cookies obtenidas ({len(cookie_str)} chars)")
    return cookie_str


if __name__ == "__main__":
    print("=== Obteniendo cookies de supermercados ===\n")

    cf = get_carrefour_cookie()
    if cf:
        print(f"\nCOOKIE_CARREFOUR=\"{cf}\"")
    
    print()
    
    di = get_dia_cookie()
    if di:
        print(f"\nCOOKIE_DIA=\"{di}\"")
    
    print("\nCopialas a backend/.env")
