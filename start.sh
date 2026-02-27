#!/usr/bin/env bash
# Start script para Render
# Este script se ejecuta cuando Render inicia la aplicación

pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port $PORT
