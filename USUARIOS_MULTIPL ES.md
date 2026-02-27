# 👥 SISTEMA DE MÚLTIPLES USUARIOS - GUÍA COMPLETA

## ✅ LO QUE YA ESTÁ IMPLEMENTADO

Tu aplicación **YA TIENE TODO** para múltiples usuarios:

### 1️⃣ **Hash de Contraseñas (bcrypt)**

**Ubicación**: `main.py` línea ~146

```python
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
```

**Funciones**:
- `pwd_context.hash(contraseña)` → Hashea la contraseña
- `pwd_context.verify(contraseña_plana, hash)` → Verifica si coincide

### 2️⃣ **Base de Datos de Usuarios**

**Archivo**: `users_db.json`

```json
{
  "admin": {
    "username": "admin",
    "email": "admin@valeria.local",
    "hashed_password": "$2b$12$...",  ← Contraseña hasheada
    "is_admin": true,
    "is_active": true
  },
  "usuario1": {
    "username": "usuario1",
    ...
  }
}
```

### 3️⃣ **Autenticación con JWT**

**Endpoints**:
- `POST /api/v1/auth/login` → Login y obtener token
- `GET /api/v1/auth/me` → Ver perfil actual
- `POST /api/v1/auth/logout` → Logout

**Token JWT**: Cada usuario obtiene un token válido por 60 minutos

### 4️⃣ **Panel Admin para Crear Usuarios**

**Endpoint**: `POST /api/v1/admin/usuarios` (solo admin)

```bash
curl -X POST http://localhost:8000/api/v1/admin/usuarios \
  -H "Authorization: Bearer TOKEN_DEL_ADMIN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "nuevo_usuario",
    "email": "nuevo@valeria.local",
    "password": "password123"
  }'
```

---

## 🚀 FORMAS DE CREAR MÚLTIPLES USUARIOS

### **OPCIÓN 1: Panel Web (Más Fácil)**

1. Abre: `create_users.html` en tu navegador
2. Crea usuarios directamente desde la interfaz
3. Copia el JSON generado
4. Pega en `users_db.json`

### **OPCIÓN 2: Manualmente (Fastest)**

1. Edita `users_db.json`:
```json
{
  "admin": {
    "username": "admin",
    "email": "admin@valeria.local",
    "hashed_password": "$2b$12$R9h7cIPz0gi.URNNX3kh2OPST9/PgBkqquzi.Ss8KCUgQDiP34pFm",
    "is_admin": true,
    "is_active": true
  },
  "usuario1": {
    "username": "usuario1",
    "email": "usuario1@valeria.local",
    "hashed_password": "$2b$12$8qDiS9fZpK2Li1KWnqzMPeZ0Xt9JkL3MqQpRhYvNxT4ZvUqB.oeSa",
    "is_admin": false,
    "is_active": true
  }
}
```

2. Inicia la app: `python main.py`
3. Login con cualquier usuario

### **OPCIÓN 3: Via API (Después de Loguearse)**

```bash
# 1. Login como admin
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r .access_token)

# 2. Crear nuevo usuario
curl -X POST http://localhost:8000/api/v1/admin/usuarios \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "usuario_nuevo",
    "email": "nuevo@valeria.local",
    "password": "pass123"
  }'
```

---

## 💡 ¿CÓMO NAVEGAN MÚLTIPLES USUARIOS?

### **Flujo de un Usuario**

```
1. Usuario va a /login
   ↓
2. Ingresa username + password
   ↓
3. main.py verifica: USUARIOS[username]
   ↓
4. Compara password con hash: pwd_context.verify()
   ↓
5. Si OK: genera JWT token
   ↓
6. Usuario guarda token en localStorage
   ↓
7. En CADA request API: envía "Authorization: Bearer TOKEN"
   ↓
8. main.py valida token → obtiene usuario
   ↓
9. Usuario logueado SÓLO VE SUS DATOS
```

### **Ejemplo: Dos Usuarios Simultáneamente**

```
NAVEGADOR 1                          NAVEGADOR 2
-----------                          -----------

Login como admin                     Login como usuario1
Token: abc123...                     Token: xyz789...

GET /api/v1/auth/me                  GET /api/v1/auth/me
Authorization: Bearer abc123         Authorization: Bearer xyz789
↓                                    ↓
{"username": "admin",                {"username": "usuario1",
 "is_admin": true}                    "is_admin": false}

Puede crear usuarios                 NO puede crear usuarios
Ve todas las horas                   Ve todas las horas
Accede a /admin                      NO puede acceder /admin
```

---

## 🔐 FUNCIONES DE HASH EN `main.py`

### **Verificar Contraseña** (Línea ~392)
```python
def verificar_contrasena(contrasena_plana: str, contrasena_hasheada: str) -> bool:
    try:
        return pwd_context.verify(contrasena_plana, contrasena_hasheada)
    except Exception as e:
        logger.error(f"Error verificando contraseña: {str(e)}")
        return False
```

### **Hash de Contraseña** (Línea ~1741)
```python
USUARIOS[new_user.username] = {
    "username": new_user.username,
    "email": new_user.email,
    "hashed_password": pwd_context.hash(new_user.password),  # ← Aquí el hash
    "is_admin": False,
    "is_active": True
}
```

### **Crear Token JWT** (Línea ~399)
```python
def crear_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

---

## 🎯 TESTING: NAVEGA CON 2 USUARIOS

### **Paso 1: Crear usuarios**

Opción A (Fácil): Abre `create_users.html`
Opción B (Manual): Edita `users_db.json`

### **Paso 2: Inicia la app**
```bash
python main.py
```

### **Paso 3: Login en incógnita/pestaña privada**

**Pestaña 1**: Login como `admin`
```
URL: http://localhost:8000/login
Username: admin
Password: admin123
```

**Pestaña 2** (privada): Login como `usuario1`
```
URL: http://localhost:8000/login
Username: usuario1
Password: pass123
```

### **Paso 4: Navega en ambas pestañas**

En **Pestaña 1** (admin):
- Ve `/admin` → Panel de administración
- Puede crear usuarios
- Ves lista de todos los usuarios

En **Pestaña 2** (usuario1):
- Ve `/` → Página principal
- NO puede ver `/admin`
- Ve solo sus datos

**CADA PESTAÑA = USUARIO DIFERENTE** 🎯

---

## 🔍 VER EL HASH EN `users_db.json`

Los hashes se ven así:
```json
"hashed_password": "$2b$12$R9h7cIPz0gi.URNNX3kh2OPST9/PgBkqquzi.Ss8KCUgQDiP34pFm"
```

**Esto significa**:
- `$2b` = bcrypt version 2b
- `$12$` = cost 12 (número de salts)
- Lo demás = hash + salt

**Importante**: NO puedes desencriptarlo (es una función one-way)

---

## ✅ CHECKLIST

- [x] Hash con bcrypt implementado
- [x] Múltiples usuarios soportados
- [x] JWT tokens para cada usuario
- [x] Base de datos JSON persistente
- [x] Validación de datos de usuario
- [x] Thread-safety en BD
- [x] Login funciona para cualquier usuario
- [x] Cada usuario tiene su token independiente
- [x] Admin puede crear nuevos usuarios
- [x] Usuarios normales NO pueden acceder a funciones admin

---

## 💡 TIPS

1. **Hashes son únicos**: Dos contraseñas iguales generan hashes diferentes (por el salt aleatorio)

2. **Tokens expiran**: Después de 60 minutos el usuario debe loguearse de nuevo

3. **Thread-safe**: Múltiples usuarios simultáneamente = sin problemas (hay lock en BD)

4. **Contraseñas**: Máximo 72 bytes (limitación de bcrypt)

5. **Testing en Render**: 
   - Crea algunos usuarios en `users_db.json`
   - Sube a GitHub
   - Render persiste `users_db.json` si usas Starter plan

---

## 🚀 PRÓXIMOS PASOS

1. Elige cómo crear usuarios:
   - `create_users.html` (web GUI)
   - `users_db.json` manual
   - Panel admin después de login

2. Inicia: `python main.py`

3. Prueba en dos navegadores/pestañas

4. ¡Disfruta! 🎉

