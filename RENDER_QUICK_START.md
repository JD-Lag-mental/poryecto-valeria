# 🚀 GUÍA RÁPIDA RENDER (5 MINUTOS)

## PASO 1️⃣: Crear repositorio GitHub

### Opción A: CLI (Recomendado si tienes Git)
```bash
cd "c:\Users\JHON\OneDrive\Desktop\poryecto valeria"
git init
git add .
git commit -m "Initial commit - Valeria API v4.0.0"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/valeria.git
git push -u origin main
```

### Opción B: GitHub Web
1. Ve a https://github.com/new
2. Crea repo llamado `valeria`
3. Copia los comandos que te da GitHub
4. Pega en PowerShell

---

## PASO 2️⃣: Ir a Render.com

1. Ve a https://render.com
2. Sign up (puedes usar GitHub)
3. Autoriza a Render acceder a GitHub

---

## PASO 3️⃣: Crear Web Service

1. Dashboard → **New +** (arriba derecha)
2. Selecciona **Web Service**
3. Selecciona tu repo `valeria`
4. Configura:

```
Name:                valeria-api
Environment:         Python 3.11
Region:              Oregon (o tu región)
Branch:              main
Build Command:       pip install -r requirements.txt
Start Command:       uvicorn main:app --host 0.0.0.0 --port $PORT
Plan:                Starter ($7/mes - recomendado)
```

---

## PASO 4️⃣: Configurar Variables de Entorno

En el panel de Render:
1. Settings → Environment
2. Add Environment Variable

Agregar 3 variables:

### Variable 1: SECRET_KEY
```
KEY:   SECRET_KEY
VALUE: (copiar output de esto)
```

Genera una clave segura en terminal:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Salida ejemplo: `Z7_K9x2nPq5mL8wT4j6vH3yB1cF0a9X2Y5`

### Variable 2: CORS_ORIGINS
```
KEY:   CORS_ORIGINS
VALUE: https://valeria-api.onrender.com
```

### Variable 3: ENVIRONMENT
```
KEY:   ENVIRONMENT
VALUE: production
```

---

## PASO 5️⃣: Deploy

1. Click en **Create Web Service**
2. Espera a que compile (2-3 minutos)
3. Ver progreso en **Logs**

---

## ✅ VERIFICAR QUE FUNCIONA

Una vez que diga "Live", prueba:

```bash
# Test 1: Health check
curl https://valeria-api.onrender.com/health

# Test 2: Ver países
curl https://valeria-api.onrender.com/paises

# Test 3: Login
curl https://valeria-api.onrender.com/login
```

O abre en navegador:
- Página principal: https://valeria-api.onrender.com
- Login: https://valeria-api.onrender.com/login
- Admin: https://valeria-api.onrender.com/admin
- Docs: https://valeria-api.onrender.com/docs

---

## 🔒 CAMBIAR CONTRASEÑA ADMIN

Después del first deploy:

### Opción 1: Eliminar BD (recrea con admin123)
```bash
rm users_db.json
# Restart en Render dashboard
```

### Opción 2: Crear usuario nuevo
```bash
curl -X POST https://valeria-api.onrender.com/api/v1/admin/usuarios \
  -H "Authorization: Bearer <TOKEN_DE_ADMIN>" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "tuusuario",
    "email": "tuemail@example.com",
    "password": "tu-nueva-contrasena"
  }'
```

---

## 🛠️ SOLUCIÓN RÁPIDA DE PROBLEMAS

### ❌ "Build Error"
```
1. Click en "Logs"
2. Ver error específico
3. Generalmente es requirements.txt corrupto
```

### ❌ "Service keeps crashing"
```
1. Logs → ver error
2. Probable causa: SECRET_KEY no configurada
3. Verificar variables de entorno están seteadas
```

### ❌ "CORS error en login"
```
1. Verificar CORS_ORIGINS en env vars
2. Debe incluir tu dominio
3. Restart servicio después de cambiar
```

### ❌ "users_db.json desaparece"
```
Render no persiste archivos en free tier
→ Necesitas Starter plan ($7/mes)
```

---

## 📊 DESPUÉS DE DEPLOYAR

### Monitorear Logs
```
Dashboard → Valeria → Logs
Ver requests en tiempo real
Ver errores automáticamente
```

### Ver Métricas
```
Dashboard → Valeria → Metrics
CPU usage
Memory usage
Requests/sec
```

### Auto-Restart
Por defecto Render reinicia si hay error.

---

## 🎯 URLS FINALES

```
API:    https://valeria-api.onrender.com
Home:   https://valeria-api.onrender.com/
Login:  https://valeria-api.onrender.com/login
Admin:  https://valeria-api.onrender.com/admin
Docs:   https://valeria-api.onrender.com/docs
Health: https://valeria-api.onrender.com/health
```

---

## 💰 COSTOS EN RENDER

- **Free**: $0/mes
  - Auto-sleep después de 15 min
  - Perfecto para prototipos
  
- **Starter**: $7/mes (RECOMENDADO)
  - No duerme
  - 0.5 CPU
  - 512 MB RAM
  - Persiste archivos
  - ¡Worth it!

---

## 🎉 ¡LISTO!

Tu API está online en: https://valeria-api.onrender.com

Puedes:
- ✅ Ver hora en todos los países
- ✅ Login con admin/admin123
- ✅ Panel de admin para gestionar usuarios
- ✅ API REST completa

¿Preguntas? Revisa los logs en Render dashboard.

