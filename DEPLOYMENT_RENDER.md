# Guía de Deployment en Render.com

## 🚀 PASOS PARA DEPLOYAR EN RENDER

### PASO 1: Preparar el Repositorio Git
```bash
cd "c:\Users\JHON\OneDrive\Desktop\poryecto valeria"
git init
git add .
git commit -m "Initial commit - Production ready"
git remote add origin https://github.com/tu-usuario/valeria.git
git push -u origin main
```

Si aún no tienes Git instalado, descargalo desde https://git-scm.com/

---

### PASO 2: Crear Cuenta en Render
1. Ve a https://render.com
2. Sign up (puedes usar GitHub)
3. Conecta tu cuenta de GitHub

---

### PASO 3: Crear Nuevo Servicio Web

1. Dashboard → New +
2. Selecciona "Web Service"
3. Conecta tu repositorio GitHub (valeria)
4. Configura:
   - **Name**: valeria-api
   - **Environment**: Python 3
   - **Region**: Choose a region (ej: Oregon)
   - **Branch**: main
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

---

### PASO 4: Configurar Variables de Entorno

En el dashboard de Render, ve a Environment:

```
SECRET_KEY=<tu-clave-generada-con-secrets.token_urlsafe(32)>
CORS_ORIGINS=https://valeria-api.onrender.com,https://tudominio.com
ENVIRONMENT=production
```

**IMPORTANTE**: Nunca hardcodees SECRET_KEY. Solo en variables de entorno.

---

### PASO 5: Configurar Plan

- **Free**: 0.50 USD/mes (con limitaciones)
- **Starter**: 7 USD/mes (recomendado)
  - 0.5 CPU
  - 512 MB RAM
  - Auto-sleep después de 15 min de inactividad
  - Pero NO duerme si tienes paid plan

---

### PASO 6: Deploy

Render auto-deploya cuando haces push a main:
```bash
git add .
git commit -m "Changes"
git push origin main
```

Para ver logs:
- Dashboard → Logs
- En tiempo real ves que sucede

---

## ✅ CHECKLIST PRE-DEPLOY

### Código
- [ ] `requirements.txt` updated y correcto
- [ ] `start.sh` existe
- [ ] `.env.example` documentado
- [ ] SECRET_KEY NO está en código
- [ ] CORS_ORIGINS NO está hardcodeado
- [ ] Repositorio Git creado y pusheado

### Variables de Entorno en Render
- [ ] SECRET_KEY configurada
- [ ] CORS_ORIGINS configurada
- [ ] ENVIRONMENT=production

### Testing
- [ ] LOGIN funciona
- [ ] Endpoints públicos responden
- [ ] Admin panel accesible
- [ ] BD JSON persiste

---

## 🔧 SOLUCIÓN DE PROBLEMAS EN RENDER

### "Build failed"
```
Solución:
1. Revisar logs en Render dashboard
2. Verificar que requirements.txt es válido (sin caracteres raros)
3. Asegurar que Python 3.10+ está seleccionado
```

### "Port already in use"
```
Solución:
Usar $PORT en el comando de start:
✓ uvicorn main:app --host 0.0.0.0 --port $PORT
✗ uvicorn main:app --host 0.0.0.0 --port 8000
```

### "Service is restarting"
```
Causas frecuentes:
1. Error en main.py al iniciar
2. Módulo faltante en requirements.txt
3. SECRET_KEY no configurada (RuntimeError)

Solución: Ver logs en dashboard para error específico
```

### "CORS Blocked"
```
Solución:
Verificar que CORS_ORIGINS contiene tu dominio:
CORS_ORIGINS=https://tudominio.com,https://valeria-api.onrender.com

Restart el servicio después de cambiar env vars
```

### "users_db.json desaparece"
```
Problema: Render no persiste archivos en free tier
Solución: 
- Cambiar a Starter plan ($7/mes)
- O usar PostgreSQL (requiere cambios de código)
- O usar otra BD en la nube
```

---

## 📊 MONITOREO EN RENDER

### Ver Logs
```
Dashboard → Valeria → Logs
Ver en tiempo real los requests y errores
```

### Métrica de Uptime
```
Dashboard → Settings → Uptime
Monitorea disponibilidad 24/7
```

### Auto-Restart
Por defecto Render reinicia servicios si fallan.

---

## 🔒 SEGURIDAD EN RENDER

1. **HTTPS Automático**: Render da SSL/TLS gratis
2. **Variables Encriptadas**: Env vars cifradas en reposo
3. **Firewall**: DDoS protection incluido

---

## 🎯 URL FINAL

Una vez deployado:
```
API: https://valeria-api.onrender.com
Docs: https://valeria-api.onrender.com/docs
Login: https://valeria-api.onrender.com/login
Admin: https://valeria-api.onrender.com/admin
```

---

## 📝 NEXT STEPS

1. Crear repositorio GitHub
2. Pushear código a GitHub
3. Conectar Render a GitHub
4. Configurar variables de entorno
5. Deploy automático
6. Monitorear logs
7. ¡Listo! 🎉

