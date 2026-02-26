#!/usr/bin/env python3
"""
Script para ejecutar la aplicación con configuración optimizada.

Ejecutar con: python run.py
"""

import uvicorn
import multiprocessing
import sys

if __name__ == "__main__":
    # Detectar número de CPUs disponibles
    workers = multiprocessing.cpu_count()
    
    # Mostrar información de ejecución
    print(f"🚀 Iniciando Reloj Interactivo - Valeria")
    print(f"📊 Workers: {workers}")
    print(f"🌐 URL: http://127.0.0.1:8000")
    print(f"📚 Docs: http://127.0.0.1:8000/docs")
    
    # Ejecutar con uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=False,  # Cambiar a True en desarrollo
        workers=workers,
        loop="uvloop",  # Usar uvloop para mejor rendimiento
        access_log=True,
        log_level="info"
    )
