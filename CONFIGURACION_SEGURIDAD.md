# Configuración de Seguridad para Valeria

Este archivo contiene ejemplos de configuración para diferentes ambientes.

## 📋 Tabla de Cambios de Seguridad v3.0.0

| Componente | Cambio | Impacto |
|-----------|--------|---------|
| **Backend** | Rate Limiting por IP | 🟢 Alto |
| **CORS** | Restricción de orígenes | 🟢 Alto |
| **Headers** | CSP + X-Frame-Options | 🟢 Alto |
| **Frontend** | Sanitización XSS | 🟢 Alto |
| **Input** | Validación con Enum | 🟢 Alto |
| **Errores** | Sin información sensible | 🟡 Medio |
| **Logging** | Auditoría de acceso | 🟡 Medio |

---

## 🌐 DESARROLLO LOCAL

```python
# .env
ALLOWED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
LOG_LEVEL=DEBUG
```

```bash
# Ejecutar
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

---

## 🚀 PRODUCCIÓN

### Docker Seguro

```dockerfile
FROM python:3.12-slim

# Crear usuario no-root
RUN useradd -m appuser

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY cert.pem .
COPY key.pem .

# Cambiar permisos
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 443

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('https://localhost/health', context=__import__('ssl')._create_unverified_context())" || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "443", \
     "--ssl-keyfile=/app/key.pem", "--ssl-certfile=/app/cert.pem", \
     "--workers", "4"]
```

### Variable de Entorno

```bash
# .env.production
ALLOWED_ORIGINS=https://tudominio.com,https://www.tudominio.com
RATE_LIMIT_REQUESTS=1000
RATE_LIMIT_WINDOW=3600
LOG_LEVEL=INFO
ENVIRONMENT=production
```

### Docker Compose Seguro

```yaml
version: '3.8'

services:
  valeria-api:
    build: .
    ports:
      - "443:443"
    environment:
      - ALLOWED_ORIGINS=https://tudominio.com
      - LOG_LEVEL=INFO
    volumes:
      - /etc/letsencrypt/live/tudominio.com/fullchain.pem:/app/cert.pem:ro
      - /etc/letsencrypt/live/tudominio.com/privkey.pem:/app/key.pem:ro
    restart: unless-stopped
    networks:
      - secure-network
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp

networks:
  secure-network:
    driver: bridge
```

---

## 🔐 Certificados SSL

### Generar certificado autofirmado (desarrollo)

```bash
openssl req -x509 -newkey rsa:2048 -nodes -out cert.pem -keyout key.pem -days 365
```

### Let's Encrypt (producción)

```bash
# Instalar certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtener certificado
sudo certbot certonly --standalone -d tudominio.com

# Los certificados estarán en:
# /etc/letsencrypt/live/tudominio.com/fullchain.pem
# /etc/letsencrypt/live/tudominio.com/privkey.pem

# Auto-renovación
sudo certbot renew --dry-run
```

---

## 📊 Control de Acceso

### Límites por IP (Recomendado)

```
API Pública:      100 requests/minuto
API Autenticada:  1000 requests/minuto
Admin:            Sin límite (en VPN)
```

### CORS Configurado

```
Desarrollo:  http://localhost:3000, http://127.0.0.1:8000
Producción:  https://tudominio.com
```

---

## 🛡️ Headers de Seguridad (Automáticos)

```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Referrer-Policy: no-referrer
Permissions-Policy: geolocation=(), microphone=(), camera=()
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'
```

---

## 🔍 Monitoreo de Seguridad

### Logs de Acceso

```
[2026-02-26 14:30:45] [127.0.0.1] GET /hora/españa - 200
[2026-02-26 14:30:51] [192.168.1.100] Rate limit excedido - 429
[2026-02-26 14:31:00] [10.0.0.5] HTTP Exception: 500 - Error interno
```

### Métricas para Monitorear

- Requests exitosos (200)
- Rate limit exceeds (429)
- Errores internos (500)
- Accesos por país
- Accesos por IP

---

## 🚨 Respuesta a Incidentes

### Si detectas una vulnerabilidad:

1. **NO** la publiques en redes sociales
2. Crea un issue PRIVADO
3. Espera confirmación
4. Espera el patch
5. Coordina el disclosure responsable

### Procedimiento:

```
1. Reporta a: seguridad@tudominio.com
2. Incluye: Descripción, pasos para reproducir, impacto
3. Espera: 48 horas de respuesta
4. Seguimiento: Actualizaciones cada 72 horas
5. Publicación: 90 días después del patch
```

---

## ✅ Checklist de Despliegue

- [ ] Certificado SSL válido instalado
- [ ] CORS configurado para dominios específicos
- [ ] Rate limiting activo
- [ ] Headers de seguridad presentes
- [ ] Logging configurado
- [ ] Backups automáticos configurados
- [ ] Monitoreo de disponibilidad activo
- [ ] WAF (Cloudflare/AWS) configurado
- [ ] Actualizaciones de dependencias al día
- [ ] Testing de penetration realizado
- [ ] Incidentes y logs retenidos
- [ ] Plan de recuperación ante desastres

---

## 📚 Recursos de Seguridad

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security Docs](https://fastapi.tiangolo.com/tutorial/security/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [SANS Top 25](https://www.sans.org/top25-software-errors/)

---

**Versión**: 3.0.0  
**Última revisión**: 2026-02-26
