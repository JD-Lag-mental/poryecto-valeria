#!/usr/bin/env python3
"""
🔄 Keep Alive Script - Mantiene la aplicación activa en Render
Previene que la instancia gratuita se duerma por inactividad
"""

import asyncio
import os
import sys
from datetime import datetime
import httpx

# Obtener URL del ambiente
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL", "http://localhost:8000")
HEALTH_ENDPOINT = f"{RENDER_EXTERNAL_URL}/health"

# Intervalo en segundos (840 = 14 minutos)
PING_INTERVAL = 840

# Número máximo de reintentos
MAX_RETRIES = 3
RETRY_DELAY = 5  # segundos


async def keep_alive():
    """Hace ping periódicamente al endpoint /health"""
    print(f"""
    ╔════════════════════════════════════════════════════════════╗
    ║           🔄 KEEP ALIVE INICIADO                          ║
    ║                                                            ║
    ║  URL: {HEALTH_ENDPOINT:<40}  ║
    ║  Intervalo: {PING_INTERVAL}s ({PING_INTERVAL // 60} minutos)               ║
    ║                                                            ║
    ║  Este script mantiene tu app activa evitando sleep        ║
    ╚════════════════════════════════════════════════════════════╝
    """)

    attempt = 0

    while True:
        try:
            await asyncio.sleep(PING_INTERVAL)

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(HEALTH_ENDPOINT)
                status = "✅" if response.status_code == 200 else "⚠️"

                print(f"{status} [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] PING -> {response.status_code}")

                if response.status_code == 200:
                    attempt = 0  # Reiniciar contador de reintentos
                else:
                    print(f"   ⚠️  Respuesta inesperada: {response.text[:100]}")

        except Exception as e:
            attempt += 1
            print(f"❌ [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error: {str(e)}")

            if attempt < MAX_RETRIES:
                print(f"   🔄 Reintentando en {RETRY_DELAY}s... ({attempt}/{MAX_RETRIES})")
                await asyncio.sleep(RETRY_DELAY)
            else:
                print(f"   ⚠️  Alcanzado máximo de reintentos. Continuando...")
                attempt = 0
                await asyncio.sleep(PING_INTERVAL)


if __name__ == "__main__":
    print("📡 Iniciando Keep Alive Service...")
    try:
        asyncio.run(keep_alive())
    except KeyboardInterrupt:
        print("\n\n❌ Keep Alive detenido")
        sys.exit(0)
