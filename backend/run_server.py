#!/usr/bin/env python3
"""Script para levantar el servidor backend con variables del .env."""

import os
import sys
from dotenv import load_dotenv

# Cargar .env si existe
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)

# Asegurar path del backend
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

# Validar variables criticas
db_url = os.getenv("DATABASE_URL", "")
if not db_url:
    print("ERROR: DATABASE_URL no configurada. Revisa .env")
    sys.exit(1)

if __name__ == "__main__":
    import uvicorn
    print(f"Conectando a BD: {db_url[:40]}...{db_url[-10:]}")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info",
    )
