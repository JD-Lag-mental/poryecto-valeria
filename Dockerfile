FROM python:3.12-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements primero para mejor caché en Docker
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY main.py .

# Exponer puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Comando para ejecutar la aplicación con múltiples workers
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
