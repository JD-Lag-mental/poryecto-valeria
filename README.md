# 🕐 Reloj Interactivo - Valeria

Una aplicación web interactiva que muestra la hora actual en diferentes países del mundo en tiempo real.

## 📋 Descripción

Valeria es una API REST construida con **FastAPI** que proporciona una interfaz web moderna y responsive para consultar la hora en 10 países diferentes. La aplicación actualiza los tiempos cada segundo sin parpadeos molestos, ofreciendo una experiencia visual fluida.

## ✨ Características

- ⏰ **Reloj en Tiempo Real**: Actualización cada segundo de las horas sin parpadeos
- 🌍 **10 Países Disponibles**: España, México, Argentina, Japón, Australia, USA, Reino Unido, India, Brasil y Singapur
- 🔍 **Búsqueda Inteligente**: Encuentra la hora de cualquier país disponible
- 📱 **Diseño Responsive**: Interfaz adaptable a cualquier tamaño de pantalla
- 🎨 **Interfaz Moderna**: Diseño con gradientes y efectos hover atractivos
- 🐳 **Containerizado con Docker**: Fácil de desplegar en cualquier entorno

## 🚀 Inicio Rápido

### Requisitos Previos
- Docker instalado en tu sistema
- Git (opcional)

### Pasos de Instalación

1. **Clonar o descargar el proyecto**
```bash
cd "c:\Users\JHON\OneDrive\Desktop\poryecto valeria"
```

2. **Construir la imagen Docker**
```powershell
docker build -t imagen_valeria .
```

3. **Ejecutar el contenedor**
```powershell
docker run -p 8000:8000 imagen_valeria
```

4. **Acceder a la aplicación**
Abre tu navegador y ve a:
```
http://127.0.0.1:8000
```

## 📁 Estructura del Proyecto

```
poryecto valeria/
├── main.py              # Aplicación principal con FastAPI
├── Dockerfile           # Configuración de Docker
├── requirements.txt     # Dependencias de Python
└── README.md           # Este archivo
```

## 🔧 Tecnologías Utilizadas

- **FastAPI**: Framework web moderno para Python
- **Uvicorn**: Servidor ASGI de alto rendimiento
- **Pytz**: Biblioteca para manejo de zonas horarias
- **Docker**: Contenedorización de la aplicación
- **HTML5 + CSS3 + JavaScript**: Frontend interactivo

## 📚 API Endpoints

### 1. Página Principal
```
GET /
```
Retorna la interfaz HTML interactiva del reloj.

**Respuesta**: Página HTML renderizada

---

### 2. Obtener Hora de un País
```
GET /hora/{pais}
```
Obtiene la hora actual en un país específico.

**Parámetros**:
- `pais` (string): Nombre del país en minúsculas

**Ejemplo**:
```
GET /hora/españa
```

**Respuesta Exitosa** (200):
```json
{
  "pais": "españa",
  "hora": "14:30:45",
  "fecha": "2026-02-05",
  "zona_horaria": "Europe/Madrid",
  "hora_completa": "05/02/2026 14:30:45"
}
```

**Respuesta de Error** (país no encontrado):
```json
{
  "error": "País no encontrado",
  "paises_disponibles": ["españa", "mexico", "argentina", ...]
}
```

---

### 3. Listar Países Disponibles
```
GET /paises
```
Lista todos los países para los cuales se puede obtener la hora.

**Respuesta**:
```json
{
  "paises": ["españa", "mexico", "argentina", "japon", "australia", "usa", "reino_unido", "india", "brasil", "singapur"],
  "total": 10
}
```

---

### 4. Obtener Todas las Horas
```
GET /todas-horas
```
Retorna la hora actual en todos los países disponibles simultáneamente.

**Respuesta**:
```json
{
  "españa": {
    "hora": "14:30:45",
    "fecha": "2026-02-05",
    "zona_horaria": "Europe/Madrid"
  },
  "mexico": {
    "hora": "07:30:45",
    "fecha": "2026-02-05",
    "zona_horaria": "America/Mexico_City"
  },
  ...
}
```

---

### 5. Verificación de Salud
```
GET /health
```
Verifica que la aplicación está activa y funcionando.

**Respuesta**:
```json
{
  "status": "ok",
  "servicio": "Reloj Interactivo Valeria"
}
```

---

## 🎯 Cómo Usar la Interfaz

### Tarjetas de Reloj
- Las tarjetas muestran la hora en tiempo real para cada país
- Se actualizan cada segundo suavemente sin parpadeos
- Al pasar el mouse, las tarjetas se elevan ligeramente

### Barra de Búsqueda
1. Escribe el nombre de un país (ej: "españa", "japon")
2. Presiona Enter o haz clic en "Buscar"
3. Se mostrará una ventana con la información completa

### Botones de Países
- Haz clic en cualquier país de la lista inferior
- Se ejecutará la búsqueda automáticamente
- Aparecerá un alert con hora, fecha y zona horaria

## 📝 Detalles Técnicos

### Arquitectura Frontend
- **HTML**: Estructura semántica de la página
- **CSS**: Estilos con gradientes, flexbox y grid
- **JavaScript**: 
  - `crearTarjetas()`: Crea la estructura una sola vez
  - `actualizarHoras()`: Solo actualiza los números (optimizado)
  - `buscarPais()`: Busca país específico
  - `cargarPaisesDisponibles()`: Genera botones clickeables

### Arquitectura Backend
- **FastAPI**: Manejo de rutas y requests
- **Pytz**: Gestión de zonas horarias
- **Datetime**: Obtención de hora actual

### Optimización
La aplicación está optimizada para evitar parpadeos:
- Las tarjetas se crean una sola vez
- Solo se actualiza el contenido de texto (hora)
- Se compara antes de actualizar para evitar cambios innecesarios

## 🛑 Detener la Aplicación

### Con Ctrl + C
Presiona `Ctrl + C` en la terminal donde corre Docker.

### Con Comando Docker
```powershell
docker stop nombre_del_contenedor
```

Para ver todos los contenedores:
```powershell
docker ps
```

## 🐛 Solución de Problemas

### No puedo acceder a la página
**Solución**: Intenta con `http://127.0.0.1:8000` en lugar de `localhost`

### Las horas no se actualizan
**Solución**: Abre la consola del navegador (F12) y verifica los errores en la pestaña Console

### Error "ports are allocated"
**Solución**: El puerto 8000 ya está en uso. Usa otro puerto:
```powershell
docker run -p 8080:8000 imagen_valeria
```

## 📊 Países Soportados

| País | Zona Horaria | GMT |
|------|--------------|-----|
| España | Europe/Madrid | GMT+1 |
| México | America/Mexico_City | GMT-6 |
| Argentina | America/Argentina/Buenos_Aires | GMT-3 |
| Japón | Asia/Tokyo | GMT+9 |
| Australia | Australia/Sydney | GMT+11 |
| USA | America/New_York | GMT-5 |
| Reino Unido | Europe/London | GMT+0 |
| India | Asia/Kolkata | GMT+5:30 |
| Brasil | America/Sao_Paulo | GMT-3 |
| Singapur | Asia/Singapore | GMT+8 |

## 🔄 Actualizar el Proyecto

Si realizas cambios en el código:

1. Detén el contenedor actual
2. Reconstruye la imagen:
```powershell
docker build -t imagen_valeria .
```
3. Ejecuta nuevamente:
```powershell
docker run -p 8000:8000 imagen_valeria
```

## 📖 Documentación de Código

El código está completamente documentado con:
- **Docstrings**: Explicación de cada función
- **Comentarios de Código**: Línea por línea en CSS y JavaScript
- **Type Hints**: Tipos de datos en Python

## 🎓 Aprendizajes

Este proyecto enseña:
- ✅ Cómo crear APIs REST con FastAPI
- ✅ Manejo de zonas horarias con Pytz
- ✅ Desarrollo frontend con HTML, CSS y JavaScript
- ✅ Containerización con Docker
- ✅ Optimización de renderizado sin parpadeos
- ✅ Diseño responsive y moderno

## 📧 Autor

Proyecto: **Valeria - Reloj Interactivo**  
Fecha de Creación: Febrero 2026

## 📄 Licencia

Este proyecto es de código abierto y está disponible para uso educativo.

---

**¡Disfruta usando Valeria! ⏰✨**
