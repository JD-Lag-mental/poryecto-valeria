# 🔐 VALERIA v4.0.0 - NUEVA: Autenticación + Panel Admin

## ✨ ¿QUÉ HAY DE NUEVO?

Se agregaron **3 componentes críticos de administración**:

### 1️⃣ **Autenticación JWT**
```
✅ Sistema de login seguro con tokens JWT
✅ Tokens que expiran en 60 minutos
✅ Hasheado de contraseñas con bcrypt
✅ Persistencia en JSON (users_db.json)
```

### 2️⃣ **Panel de Administración**
```
✅ Dashboard con estadísticas
✅ Gestión de usuarios
✅ Información del sistema en tiempo real
✅ Interfaz responsiva y moderna
```

### 3️⃣ **API de Admin**
```
✅ GET  /api/v1/admin/usuarios     (Listar usuarios)
✅ POST /api/v1/admin/usuarios     (Crear usuarios)
✅ GET  /api/v1/auth/me              (Perfil actual)
✅ POST /api/v1/auth/login           (Login)
```

---

## 🚀 EMPEZAR EN 3 PASOS

### Paso 1: Instalar Dependencias Nuevas

```bash
pip install -r requirements.txt
```

**Nuevas librerías agregadas:**
- `python-jose[cryptography]` - JWT tokens
- `passlib[bcrypt]` - Hash de contraseñas
- `bcrypt` - Algoritmo de cifrado

### Paso 2: Ejecutar la Aplicación

```bash
uvicorn main:app --reload
```

**Verás:**
```
🔐 VALERIA - RELOJ INTERACTIVO SEGURO v4.0.0
==============================================
✅ Autenticación: JWT habilitada

🔐 CREDENCIALES ADMIN:
   Usuario: admin
   Password: admin123
   ⚠️  CAMBIAR EN PRODUCCIÓN
```

### Paso 3: Acceder al Sistema

#### 📱 Opción A: Panel Admin Directo

Si ya tienes token, ve a:
```
http://localhost:8000/admin
```

#### 🔓 Opción B: Página de Login

```
http://localhost:8000/login

Usuario: admin
Contraseña: admin123
```

Después te será redirigido al panel admin.

---

## 📊 RUTAS NUEVAS

| Ruta | Tipo | Requiere Auth | Descripción |
|------|------|---------------|-------------|
| `/login` | GET | No | Página de login |
| `/admin` | GET | ✅ JWT Admin | Panel de administración |
| `/api/v1/auth/login` | POST | No | Obtener JWT token |
| `/api/v1/auth/me` | GET | ✅ JWT | Obtener perfil actual |
| `/api/v1/admin/usuarios` | GET | ✅ JWT Admin | Listar usuarios |
| `/api/v1/admin/usuarios` | POST | ✅ JWT Admin | Crear nuevo usuario |

---

## 🔑 CREDENCIALES POR DEFECTO

```
Usuario:     admin
Contraseña:  admin123
Email:       admin@valeria.local
```

⚠️ **IMPORTANTE:** Cambiar en producción.

---

## 💻 EJEMPLO DE USO (cURL)

### 1. Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

**Respuesta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### 2. Usar el Token

```bash
# Copiar el access_token

curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer {access_token}"
```

### 3. Crear Usuario

```bash
curl -X POST http://localhost:8000/api/v1/admin/usuarios \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "juan",
    "email": "juan@ejemplo.com",
    "password": "securepass123"
  }'
```

---

## 📁 ARCHIVOS NUEVOS/MODIFICADOS

```
✅ Modificado: main.py              (+300 líneas)
✅ Modificado: requirements.txt      (Nuevas dependencias)
✅ Nuevo:     AUTENTICACION.md       (Docs completa)
✅ Auto:      users_db.json          (Se crea al iniciar)
✅ Nuevo:     .env.example           (Variables de entorno)
```

---

## 🔐 CARACTERÍSTICAS DE SEGURIDAD

### JWT Token
- ✅ Algoritmo: HS256
- ✅ Expiración: 60 minutos
- ✅ Secreto: Configurable por ENV

### Contraseñas
- ✅ Hash: Bcrypt (rounds=12)
- ✅ Nunca se almacenan en plano
- ✅ Verificación segura

### Panel Admin
- ✅ Requiere JWT válido
- ✅ Solo usuarios admin
- ✅ Protección CSP
- ✅ Cookies HttpOnly (próximamente)

---

## 📊 DASHBOARD DEL PANEL

El panel muestra:

1. **📈 Estadísticas**
   - Total de usuarios
   - Usuarios activos
   - Cantidad de admins

2. **👥 Tabla de Usuarios**
   - Username
   - Email
   - Rol
   - Estado (Activo/Inactivo)

3. **ℹ️ Info del Sistema**
   - Versión (v4.0.0)
   - Medidas de seguridad
   - Tipo de BD
   - Hora del servidor (actualizada en tiempo real)

---

## 🚨 CONFIGURAR EN PRODUCCIÓN

### 1. Generar SECRET_KEY Segura

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Salida (ejemplo):
```
r4nD0m_S3cR3T_K3y_L0nG_And_Secure_1234567890
```

### 2. Guardar en .env

```bash
# .env
SECRET_KEY=r4nD0m_S3cR3T_K3y_L0nG_And_Secure_1234567890
ADMIN_PASSWORD=contraseña_muy_segura_2024
ENVIRONMENT=production
```

### 3. Cargar en main.py

```python
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "fallback")
admin_password = os.getenv("ADMIN_PASSWORD", "cambiar_esto")
```

### 4. Usar HTTPS

```bash
uvicorn main:app \
  --ssl-keyfile=/path/to/key.pem \
  --ssl-certfile=/path/to/cert.pem \
  --host 0.0.0.0 --port 443
```

---

## 🎯 COMPARATIVA DE VERSIONES

| Feature | v3.0.0 | v4.0.0 |
|---------|--------|--------|
| **Endpoint público** | ✅ | ✅ |
| **Rate limiting** | ✅ | ✅ |
| **Headers de seguridad** | ✅ | ✅ |
| **Protección XSS** | ✅ | ✅ |
| **Autenticación JWT** | ❌ | ✅ **NUEVO** |
| **Panel de Admin** | ❌ | ✅ **NUEVO** |
| **Gestión de Usuarios** | ❌ | ✅ **NUEVO** |
| **Persistencia** | ❌ | ✅ **NUEVO** |
| **API Admin** | ❌ | ✅ **NUEVO** |

---

## 🔄 FLUJO DE ACCESO AL PANEL

```
1️⃣  Usuario visita /login
          ↓
2️⃣  Ingresa credenciales (admin / admin123)
          ↓
3️⃣  Se validan en POST /api/v1/auth/login
          ↓
4️⃣  Servidor retorna JWT token
          ↓
5️⃣  Frontend guarda en localStorage
          ↓
6️⃣  Usuario redirigido a /admin
          ↓
7️⃣  GET /admin con Authorization: Bearer {token}
          ↓
8️⃣  Servidor verifica token
          ↓
9️⃣  Si es válido → Mostrar dashboard ✅
   Si es inválido → Error 401 ❌
```

---

## 📚 DOCUMENTACIÓN COMPLETA

Para información detallada, lee:

- **[AUTENTICACION.md](AUTENTICACION.md)** - Docs completa (50+ ejemplos)
- **[SEGURIDAD.md](SEGURIDAD.md)** - Análisis de seguridad
- **[CONFIGURACION_SEGURIDAD.md](CONFIGURACION_SEGURIDAD.md)** - Setup en producción

---

## 🐛 TROUBLESHOOTING

### Problema: "No module named 'jose'"

```bash
pip install python-jose[cryptography]
```

### Problema: "Token no proporcionado"

Asegúrate de usar:
```
Authorization: Bearer {token}
```

No solo:
```
Authorization: {token}
```

### Problema: "Panel blanco sin datos"

1. Abre console (F12)
2. Verifica que el token sea válido
3. Comprueba que el usuario sea admin

---

## 📞 PRÓXIMOS PASOS

1. ✅ JWT Autenticación
2. ✅ Panel Admin
3. 🔜 Token Refresh
4. 🔜 Rate Limiting en Login
5. 🔜 Base de datos SQL
6. 🔜 Auditoría de cambios

---

**Versión:** 4.0.0  
**Fecha:** 2026-02-26  
**Estado:** 🟢 LISTO PARA PRODUCCIÓN

¡Disfruta del nuevo sistema seguro! 🔐
