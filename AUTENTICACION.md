# 🔐 GUÍA DE AUTENTICACIÓN Y ADMIN - Valeria v4.0.0

## 📋 Tabla de Contenidos

1. [Sistema JWT](#sistema-jwt)
2. [Primeros pasos](#primeros-pasos)
3. [API de Autenticación](#api-de-autenticación)
4. [Panel de Administración](#panel-de-administración)
5. [Ejemplos de Uso](#ejemplos-de-uso)
6. [Seguridad](#seguridad)

---

## Sistema JWT

### ¿Qué es JWT?

JWT (JSON Web Token) es un estándar seguro para transmitir información entre partes. Consta de 3 partes:

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTY0NTA4MzIwMH0.signature
├─ HEADER ────────────────────────────────────────────┤
├─ PAYLOAD ────────────────────────────────────────────┤
└─ SIGNATURE ──────────────────────────────────────────┘
```

**Ventajas**:
- ✅ No requiere sesiones en servidor
- ✅ Escalable (sin estado)
- ✅ Seguro criptográficamente
- ✅ Estándar de industria

---

## Primeros Pasos

### 1. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 2. Ejecutar la Aplicación

```bash
uvicorn main:app --reload
```

**Salida esperada:**

```
🔒 VALERIA - RELOJ INTERACTIVO SEGURO v4.0.0
================================================
✅ CORS: Habilitado
✅ Rate Limiting: 100 requests/minuto por IP
✅ Protección XSS: Habilitada
✅ Autenticación: JWT habilitada

🔐 CREDENCIALES ADMIN:
   Usuario: admin
   Password: admin123
   ⚠️  CAMBIAR EN PRODUCCIÓN
```

### 3. Acceder al Panel

```
http://localhost:8000/admin
```

⚠️ Te redireccionará al login automáticamente.

---

## API de Autenticación

### 📨 POST /api/v1/auth/login

**Descripción:** Obtiene un JWT token para autenticarse.

**Solicitud:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

**Respuesta (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTY0NTA4MzIwMH0.signature",
  "token_type": "bearer",
  "expires_in": 3600
}
```

**Respuesta (401 Unauthorized):**
```json
{
  "detail": "Credenciales incorrectas"
}
```

---

### ✅ GET /api/v1/auth/me

**Descripción:** Obtiene información del usuario autenticado.

**Solicitud:**
```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Respuesta (200 OK):**
```json
{
  "username": "admin",
  "email": "admin@valeria.local",
  "is_admin": true,
  "is_active": true
}
```

**Respuesta (401 Unauthorized):**
```json
{
  "detail": "Token no proporcionado"
}
```

---

### 🚪 POST /api/v1/auth/logout

**Descripción:** Cierra sesión (principalmente para frontend).

**Solicitud:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/logout \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Respuesta (200 OK):**
```json
{
  "message": "Logout exitoso"
}
```

---

## Panel de Administración

### Acceso

```
URL: http://localhost:8000/admin
Requiere: Login como administrador
```

### Características

#### 1. 📊 Estadísticas del Sistema

- Total de usuarios
- Usuarios activos
- Administradores
- Hora del servidor en tiempo real

#### 2. 👥 Gestión de Usuarios

Tabla con información de todos los usuarios:
- Username
- Email
- Rol (Admin / Usuario)
- Estado (Activo / Inactivo)

#### 3. ℹ️ Información del Sistema

- Versión de la aplicación
- Medidas de seguridad activas
- Tipo de base de datos
- Hora del servidor

---

## API de Administración

### 📋 GET /api/v1/admin/usuarios

**Descripción:** Lista todos los usuarios del sistema.

**Requisito:** Ser administrador

**Solicitud:**
```bash
curl -X GET http://localhost:8000/api/v1/admin/usuarios \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

**Respuesta (200 OK):**
```json
{
  "usuarios": [
    {
      "username": "admin",
      "email": "admin@valeria.local",
      "is_admin": true,
      "is_active": true
    },
    {
      "username": "usuario1",
      "email": "user1@ejemplo.com",
      "is_admin": false,
      "is_active": true
    }
  ],
  "total": 2
}
```

---

### ➕ POST /api/v1/admin/usuarios

**Descripción:** Crea un nuevo usuario.

**Requisito:** Ser administrador

**Solicitud:**
```bash
curl -X POST http://localhost:8000/api/v1/admin/usuarios \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "nuevo_usuario",
    "email": "nuevo@ejemplo.com",
    "password": "contraseña123"
  }'
```

**Respuesta (200 OK):**
```json
{
  "message": "Usuario nuevo_usuario creado exitosamente"
}
```

**Respuesta (400 Bad Request):**
```json
{
  "detail": "El usuario ya existe"
}
```

---

## Ejemplos de Uso

### Ejemplo 1: Flujo Completo de Autenticación

```bash
# 1. Login
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }' | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

echo "Token: $TOKEN"

# 2. Obtener perfil
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"

# 3. Listar usuarios
curl -X GET http://localhost:8000/api/v1/admin/usuarios \
  -H "Authorization: Bearer $TOKEN"
```

### Ejemplo 2: Crear Nuevo Usuario

```javascript
// JavaScript - Frontend

async function crearUsuario() {
  const token = localStorage.getItem('auth_token');
  
  const response = await fetch('http://localhost:8000/api/v1/admin/usuarios', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      username: 'juan',
      email: 'juan@ejemplo.com',
      password: 'securepwd123'
    })
  });
  
  const data = await response.json();
  console.log(data);
}
```

### Ejemplo 3: Guardar Token en LocalStorage

```javascript
// Login y guardar token
async function login() {
  const response = await fetch('/api/v1/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      username: document.getElementById('username').value,
      password: document.getElementById('password').value
    })
  });
  
  const data = await response.json();
  
  if (response.ok) {
    // Guardar token
    localStorage.setItem('auth_token', data.access_token);
    
    // Redirigir al panel
    window.location.href = '/admin?token=' + data.access_token;
  }
}

// Usar token en solicitudes
function fetchConToken(url, options = {}) {
  const token = localStorage.getItem('auth_token');
  
  return fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${token}`
    }
  });
}
```

---

## Seguridad

### 🔒 Buenas Prácticas

#### 1. **Cambiar Credenciales por Defecto**

```python
# .env
ADMIN_PASSWORD=cambiar_esto_en_produccion!

# main.py
DEFAULT_ADMIN = {
    "username": "admin",
    "email": "admin@produccion.com",
    "hashed_password": pwd_context.hash(os.getenv("ADMIN_PASSWORD")),
    ...
}
```

#### 2. **Cambiar SECRET_KEY**

```bash
# Generar una clave segura en producción
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Guardar en .env
SECRET_KEY=tu_clave_segura_aqui
```

#### 3. **Usar HTTPS en Producción**

```bash
# Ejecutar con SSL
uvicorn main:app \
  --ssl-keyfile=/path/to/key.pem \
  --ssl-certfile=/path/to/cert.pem \
  --host 0.0.0.0 \
  --port 443
```

#### 4. **Implementar Token Refresh**

Para sesiones largas, es recomendable:

```python
# Token corta duración: 15 minutos
ACCESS_TOKEN_EXPIRE_MINUTES = 15

# Token de refresco: 7 días
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Endpoint para refrescar
@app.post("/api/v1/auth/refresh")
async def refresh_token(refresh_token: str):
    # Verificar refresh token y generar nuevo access token
    ...
```

#### 5. **Guardar Logs de Acceso**

```python
# Log de intentos fallidos
logger.warning(f"[{client_ip}] Intento de login fallido: {username}")

# Log de acciones admin
logger.info(f"Admin {admin['username']} creó usuario: {new_user.username}")
```

#### 6. **Rate Limiting en Login**

```python
# Limitar intentos de login
MAX_LOGIN_ATTEMPTS = 5
LOGIN_ATTEMPT_WINDOW = 900  # 15 minutos

# Implementar en endpoint de login
if login_attempts[client_ip] >= MAX_LOGIN_ATTEMPTS:
    raise HTTPException(status_code=429, detail="Demasiados intentos")
```

---

### 🚀 Token Expiration (Expiración de Tokens)

Los tokens JWT expiran automáticamente:

```
Tiempo de expiración: 60 minutos
Después: RequiereNuevo login

Token Expirado Response:
{
  "detail": "Token expirado o inválido"
}
```

---

### 🔑 Flujo de Autenticación

```
┌─────────────┐
│   Cliente   │
└──────┬──────┘
       │
       │ 1. POST /auth/login
       │    (username, password)
       ↓
┌─────────────────────────────────┐
│   Servidor                      │
│  ✓ Verificar usuario existe    │
│  ✓ Verificar contraseña        │
│  ✓ Generar JWT token           │
└──────┬──────────────────────────┘
       │
       │ 2. Response: {access_token, expires_in}
       ↓
┌──────────────────────────┐
│   Cliente LocalStorage   │
│   Guardar: auth_token    │
└─────────────┬────────────┘
              │
              │ 3. GET /admin
              │    Header: Authorization: Bearer {token}
              ↓
       ┌──────────────┐
       │   Servidor   │
       │  ✓ Verificar │
       │    token    │
       │  ✓ Retornar │
       │    datos    │
       └──────────────┘
```

---

## 📚 Tabla de Referencia

| Endpoint | Método | Requiere Auth | Admin | Descripción |
|----------|--------|---------------|-------|-------------|
| `/` | GET | No | - | Página principal |
| `/health` | GET | No | - | Health check |
| `/api/v1/auth/login` | POST | No | - | Login |
| `/api/v1/auth/me` | GET | **Sí** | No | Perfil actual |
| `/api/v1/auth/logout` | POST | **Sí** | No | Logout |
| `/api/v1/admin/usuarios` | GET | **Sí** | **Sí** | Listar usuarios |
| `/api/v1/admin/usuarios` | POST | **Sí** | **Sí** | Crear usuario |
| `/admin` | GET | **Sí** | **Sí** | Panel admin |

---

## 🔍 Troubleshooting

### Problema: "Token no proporcionado"

**Solución:** Asegúrate de incluir el header correcto:

```bash
# ❌ Incorrecto
curl -H "Authorization: YOUR_TOKEN"

# ✅ Correcto
curl -H "Authorization: Bearer YOUR_TOKEN"
```

### Problema: "Token expirado"

**Solución:** Haz login nuevamente para obtener un nuevo token.

### Problema: "Se requieren permisos de administrador"

**Solución:** Solo usuarios admin pueden acceder. Contacta al administrador.

---

## 📝 Cambios Respecto a v3.0.0

| Feature | v3.0.0 | v4.0.0 |
|---------|--------|--------|
| Autenticación | ❌ No | ✅ JWT |
| Panel Admin | ❌ No | ✅ Sí |
| Gestión Usuarios | ❌ No | ✅ Sí |
| Persistencia | ❌ No | ✅ JSON |
| Rate Limiting | ✅ Sí | ✅ Sí |
| CORS | ✅ Sí | ✅ Sí |
| CSP | ✅ Sí | ✅ Sí |

---

**Versión:** 4.0.0  
**Última actualización:** 2026-02-26  
**Estado:** 🟢 Listo para producción
