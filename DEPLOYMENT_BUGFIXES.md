# 🚀 DEPLOYMENT CHECKLIST - BUGFIXES APLICADOS

## ✅ BUGS REPARADOS EN v4.0.1

### 1. **CRÍTICO: Endpoint de Login No Registrado** ✓
- **Problema**: Faltaba `@app.post("/api/v1/auth/login")` en la función login
- **Impacto**: El login NO funcionaba en absoluto
- **Solución**: Agregado decorador correcto
- **Línea**: ~1655

### 2. **Deprecado: datetime.utcnow()** ✓
- **Problema**: `datetime.utcnow()` removido en Python 3.12+
- **Error**: `AttributeError: datetime.datetime has no attribute 'utcnow'`
- **Solución**: Reemplazado con `datetime.now(timezone.utc)`
- **Líneas**: 265, 313
- **Requisito**: Actualizar imports a incluir `timezone`

### 3. **Seguridad: Validación de Usuario Insuficiente** ✓
- **Problema**: Modelo `UsuarioRegistro` sin validadores
- **Riesgo**: Usuarios con datos inválidos (username vacío, email sin @)
- **Solución**: Añadidos validadores en modelo:
  - Username: 3-20 caracteres, alfanumérico + guiones
  - Email: Validación de formato
  - Password: 6-50 caracteres
- **Línea**: ~410

### 4. **Race Condition: Base de Datos JSON** ✓
- **Problema**: Sin thread-safety en lectura/escritura de `users_db.json`
- **Riesgo**: Corrupción de datos con múltiples requests simultáneos
- **Solución**: Implementado `threading.Lock()` en:
  - `cargar_usuarios()` 
  - `guardar_usuarios()`
- **Línea**: ~125

### 5. **Seguridad: SECRET_KEY Hardcodeada** ✓
- **Problema**: Default value para SECRET_KEY en código
- **Riesgo**: Tokens predecibles si no se configura env var
- **Solución**: 
  - SECRET_KEY obligatoria en ENVIRONMENT=production
  - Lanza RuntimeError si no está definida
  - Warning en desarrollo
- **Línea**: ~128

### 6. **CORS Incompleto para Producción** ✓
- **Problema**: Dominios hardcodeados, falta POST, falta Authorization header
- **Solución**:
  - CORS_ORIGINS configurable via variable de entorno
  - POST method agregado para autenticación
  - Authorization header soportado
- **Línea**: ~208

---

## 📋 CHECKLIST PRE-DEPLOY

### Configuración de Entorno
- [ ] Crear archivo `.env` en raíz del proyecto
- [ ] Generar SECRET_KEY segura: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- [ ] Configurar CORS_ORIGINS con tus dominios (HTTPS en producción)
- [ ] Establecer ENVIRONMENT=production
- [ ] Cambiar contraseña admin:
  ```bash
  # Opción 1: Eliminar users_db.json (se recrea con admin123)
  # Opción 2: Hashear nueva contraseña y actualizar JSON
  python -c "from passlib.context import CryptContext; ctx = CryptContext(schemes=['bcrypt']); print(ctx.hash('tu-nueva-contrasena'))"
  ```

### Dependencias
- [ ] Instalar dependencias: `pip install -r requirements.txt`
- [ ] Verificar que `python-jose[cryptography]` está instalado
- [ ] Verificar que `passlib[bcrypt]` está instalado

### Seguridad
- [ ] [ ] Rate limiting configurado (100 req/min por IP)
- [ ] [ ] HTTPS habilitado en servidor (nginx/Apache)
- [ ] [ ] Headers de seguridad activos (HSTS, CSP, etc)
- [ ] [ ] Logging habilitado (revisar logs de errores)
- [ ] [ ] Credenciales de admin cambiadas

### Testing Pre-Deploy
```bash
# Test de endpoints públicos
curl http://localhost:8000/health
curl http://localhost:8000/paises
curl http://localhost:8000/hora/españa

# Test de login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Test de endpoint protegido (reemplazar TOKEN)
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer TOKEN"
```

### Docker (si aplica)
- [ ] Dockerfile actualizado con Python 3.10+
- [ ] docker-compose.yml configurable con env vars
- [ ] volúmenes para `users_db.json` (persistencia)

### Monitoreo en Producción
- [ ] Logging centralizado (syslog, CloudWatch, etc)
- [ ] Alertas para errores de autenticación
- [ ] Alertas para cambios en users_db.json
- [ ] Respaldo automático de users_db.json

---

## 🔍 VERIFICACIÓN DE CAMBIOS

Para confirmar que todos los cambios están en place:

```python
# 1. Check decorador de login
grep -n "@app.post(\"/api/v1/auth/login\")" main.py

# 2. Check timezone.utc
grep -n "datetime.now(timezone.utc)" main.py

# 3. Check validadores
grep -n "@validator('username')" main.py

# 4. Check thread-safety
grep -n "users_db_lock" main.py

# 5. Check SECRET_KEY obligatoria
grep -n "ENVIRONMENT.*production" main.py
```

---

## ⚠️ CAMBIOS DE COMPORTAMIENTO

### Breaking Changes
- Ninguno para endpoints públicos
- Login ahora requiere POST a `/api/v1/auth/login`
- SECRET_KEY ahora obligatoria en producción

### Mejoras de Seguridad
- Validación más estricta de usuarios
- Thread-safety para BD
- SECRET_KEY no puede ser predecible

---

## 📞 SOPORTE

Si encuentras problemas en producción:

1. Revisa los logs: `tail -f /var/log/valeria.log`
2. Verifica variables de entorno: `env | grep SECRET_KEY`
3. Prueba el login manualmente con curl
4. Revisa que `users_db.json` no esté corrupto (JSON válido)

