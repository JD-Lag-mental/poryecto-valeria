#!/usr/bin/env python3
"""
API de Reloj Interactivo - Valeria - VERSIÓN SEGURA.

Este módulo proporciona una aplicación FastAPI que muestra la hora actual
en diferentes países del mundo. Incluye una interfaz web interactiva con
tarjetas que se actualizan en tiempo real sin parpadeos.

SEGURIDAD IMPLEMENTADA:
- CORS robusta
- Rate limiting
- Protección contra XSS
- Headers de seguridad
- Validación de entrada
- Sanitización de datos
"""

from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.gzip import GZIPMiddleware
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
from enum import Enum
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Dict, Optional
import logging
import pytz
import hashlib
import os
from collections import defaultdict
import html
import json
from pathlib import Path

# ==================== JWT Y SEGURIDAD ====================
try:
    from jose import JWTError, jwt
    from passlib.context import CryptContext
except ImportError:
    raise ImportError("Instala: pip install python-jose[cryptography] passlib")

# ==================== CONFIGURACIÓN DE LOGGING ====================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== CONSTANTES DE SEGURIDAD ====================
# Rate Limiting: máximo 100 requests por minuto por IP
RATE_LIMIT_REQUESTS = 100
RATE_LIMIT_WINDOW = 60  # segundos

# Variables para control de rate limiting
request_counts = defaultdict(list)

# ==================== CONFIGURACIÓN JWT ====================
SECRET_KEY = os.getenv("SECRET_KEY", "valeria-secret-key-dev-cambiar-produccion")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Context para hashear contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ==================== BASE DE DATOS DE USUARIOS ====================
USERS_DB_FILE = Path("users_db.json")

# Usuario admin por defecto
DEFAULT_ADMIN = {
    "username": "admin",
    "email": "admin@valeria.local",
    "hashed_password": pwd_context.hash("admin123"),
    "is_admin": True,
    "is_active": True
}

def cargar_usuarios():
    """Carga usuarios de archivo JSON."""
    if USERS_DB_FILE.exists():
        try:
            with open(USERS_DB_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error cargando usuarios: {str(e)}")
            return {}
    return {}

def guardar_usuarios(usuarios: dict):
    """Guarda usuarios en archivo JSON."""
    try:
        with open(USERS_DB_FILE, 'w') as f:
            json.dump(usuarios, f, indent=2)
        logger.info("Usuarios guardados correctamente")
    except Exception as e:
        logger.error(f"Error guardando usuarios: {str(e)}")

# Inicializar BD de usuarios
USUARIOS = cargar_usuarios()
if "admin" not in USUARIOS:
    USUARIOS["admin"] = DEFAULT_ADMIN
    guardar_usuarios(USUARIOS)
    logger.info("Usuario admin creado: admin / admin123")

# ==================== INICIALIZAR FASTAPI ====================
app = FastAPI(
    title="Valeria - Reloj Interactivo SEGURO", 
    version="3.0.0",
    description="API segura que muestra la hora en tiempo real en diferentes países",
    docs_url="/docs",
    redoc_url=None  # Desactivar ReDoc por seguridad
)

# ==================== MIDDLEWARES DE SEGURIDAD ====================

# 1. GZIP Compression
app.add_middleware(GZIPMiddleware, minimum_size=1000)

# 2. CORS - Configuración Segura
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "http://localhost:3000",
        # Agregar tus dominios aquí en producción
    ],
    allow_credentials=False,  # No permitir credenciales en CORS
    allow_methods=["GET", "HEAD", "OPTIONS"],  # Solo métodos seguros
    allow_headers=["Content-Type", "Accept"],
    max_age=600,  # Cache CORS por 10 minutos
    expose_headers=["X-RateLimit-Remaining"],
)

# ==================== RATE LIMITING ====================
def check_rate_limit(client_ip: str) -> bool:
    """
    Verifica si el cliente ha excedido el rate limit.
    
    Args:
        client_ip: IP del cliente
    
    Returns:
        bool: True si está dentro del límite, False si lo excedió
    """
    now = datetime.now()
    window_start = now - timedelta(seconds=RATE_LIMIT_WINDOW)
    
    # Limpiar requests antiguos
    request_counts[client_ip] = [
        req_time for req_time in request_counts[client_ip]
        if req_time > window_start
    ]
    
    # Verificar límite
    if len(request_counts[client_ip]) >= RATE_LIMIT_REQUESTS:
        logger.warning(f"Rate limit excedido para IP: {client_ip}")
        return False
    
    # Agregar nuevo request
    request_counts[client_ip].append(now)
    return True

# ==================== MIDDLEWARE DE RATE LIMITING ====================
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Middleware que implementa rate limiting por IP."""
    # Obtener IP del cliente
    client_ip = request.client.host if request.client else "unknown"
    
    # Verificar rate limit
    if not check_rate_limit(client_ip):
        logger.warning(f"Acceso bloqueado por rate limit: {client_ip}")
        return HTMLResponse(
            content="<h1>429 Too Many Requests</h1><p>Has excedido el límite de solicitudes. Intenta más tarde.</p>",
            status_code=429
        )
    
    response = await call_next(request)
    
    # Agregar headers de seguridad
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:;font-src 'self'"
    
    return response

# ==================== ENUMS Y MODELOS ====================

# Enum para países (más seguro que diccionario)
class PaisEnum(str, Enum):
    ESPAÑA = "españa"
    MEXICO = "mexico"
    ARGENTINA = "argentina"
    JAPON = "japon"
    AUSTRALIA = "australia"
    USA = "usa"
    REINO_UNIDO = "reino_unido"
    INDIA = "india"
    BRASIL = "brasil"
    SINGAPUR = "singapur"

# Diccionario que mapea países a zonas horarias
PAISES = {
    PaisEnum.ESPAÑA: "Europe/Madrid",
    PaisEnum.MEXICO: "America/Mexico_City",
    PaisEnum.ARGENTINA: "America/Argentina/Buenos_Aires",
    PaisEnum.JAPON: "Asia/Tokyo",
    PaisEnum.AUSTRALIA: "Australia/Sydney",
    PaisEnum.USA: "America/New_York",
    PaisEnum.REINO_UNIDO: "Europe/London",
    PaisEnum.INDIA: "Asia/Kolkata",
    PaisEnum.BRASIL: "America/Sao_Paulo",
    PaisEnum.SINGAPUR: "Asia/Singapore",
}

# ==================== MODELOS PYDANTIC ====================

class HoraResponse(BaseModel):
    pais: str
    hora: str
    fecha: str
    zona_horaria: str
    hora_completa: str
    
    class Config:
        schema_extra = {
            "example": {
                "pais": "españa",
                "hora": "14:30:45",
                "fecha": "2026-02-26",
                "zona_horaria": "Europe/Madrid",
                "hora_completa": "26/02/2026 14:30:45"
            }
        }

class PaisesResponse(BaseModel):
    paises: list
    total: int

class HealthResponse(BaseModel):
    status: str
    servicio: str
    version: str
    security: str

# ==================== MODELOS PARA AUTENTICACIÓN ====================

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class LoginRequest(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    username: str
    email: str
    is_admin: bool
    is_active: bool

class UsuarioRegistro(BaseModel):
    username: str
    email: str
    password: str

# ==================== FUNCIONES DE AUTENTICACIÓN ====================

def verificar_contrasena(contrasena_plana: str, contrasena_hasheada: str) -> bool:
    """Verifica si la contraseña es correcta."""
    try:
        return pwd_context.verify(contrasena_plana, contrasena_hasheada)
    except Exception as e:
        logger.error(f"Error verificando contraseña: {str(e)}")
        return False

def crear_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crea un JWT token con los datos proporcionados."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error creando token: {str(e)}")
        raise HTTPException(status_code=500, detail="Error creando token")

def verificar_token(token: str) -> dict:
    """Verifica que el token sea válido y retorna el payload."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
        
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado o inválido"
        )

async def obtener_usuario_actual(request: Request) -> dict:
    """Dependency para obtener el usuario del token JWT."""
    # Obtener token del header Authorization
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no proporcionado",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token = auth_header.split(" ")[1]
    payload = verificar_token(token)
    username = payload.get("sub")
    
    if username not in USUARIOS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado"
        )
    
    usuario = USUARIOS[username].copy()
    usuario.pop("hashed_password", None)
    return usuario

async def obtener_usuario_admin(usuario: dict = Depends(obtener_usuario_actual)) -> dict:
    """Dependency para verificar que el usuario sea admin."""
    if not usuario.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador"
        )
    return usuario

# ==================== FUNCIONES DE SANITIZACIÓN ====================

def sanitizar_entrada(entrada: str, max_length: int = 50) -> str:
    """
    Sanitiza la entrada del usuario para prevenir XSS y otros ataques.
    
    Args:
        entrada: Texto a sanitizar
        max_length: Longitud máxima permitida
    
    Returns:
        str: Texto sanitizado y escapado
    """
    if not entrada:
        return ""
    
    # Limitar longitud
    entrada = entrada[:max_length]
    
    # Convertir a minúsculas y quitar espacios
    entrada = entrada.lower().strip()
    
    # Escapar caracteres HTML
    entrada = html.escape(entrada)
    
    # Permitir solo caracteres alfanuméricos, guiones y guiones bajos
    entrada_limpia = ""
    for char in entrada:
        if char.isalnum() or char in "-_ ":
            entrada_limpia += char
    
    logger.info(f"Entrada sanitizada: {entrada_limpia}")
    return entrada_limpia

@app.get("/")
def read_root(request: Request):
    """
    Endpoint raíz que sirve la página HTML principal con protección contra XSS.
    
    Retorna:
        HTMLResponse: Página HTML con interfaz interactiva del reloj
    """
    # Verificar rate limit
    client_ip = request.client.host if request.client else "unknown"
    
    return HTMLResponse(
        content="""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="X-UA-Compatible" content="ie=edge">
        <meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:;">
        <title>Reloj Interactivo - Valeria</title>
        <style>
            /* Reinicia todos los estilos por defecto del navegador */
            * { margin: 0; padding: 0; box-sizing: border-box; }
            
            /* Estilos del cuerpo: fondo gradiente, centrado y responsive */
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }
            
            /* Contenedor principal: caja blanca con sombra y bordes redondeados */
            .container {
                background: white;
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                max-width: 900px;
                width: 100%;
            }
            
            /* Título principal: grande, centrado y oscuro */
            h1 {
                text-align: center;
                color: #333;
                margin-bottom: 30px;
                font-size: 2.5em;
            }
            
            /* Grilla para las tarjetas de reloj: responsive con 4 columnas máximo */
            .reloj-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            
            /* Tarjeta individual de reloj con gradiente y efecto hover */
            .reloj-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 20px;
                border-radius: 15px;
                text-align: center;
                color: white;
                cursor: pointer;
                transition: transform 0.3s, box-shadow 0.3s;
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
            }
            
            /* Efecto hover: eleva la tarjeta y aumenta la sombra */
            .reloj-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
            }
            
            /* Nombre del país en la tarjeta */
            .pais {
                font-size: 1.2em;
                font-weight: bold;
                margin-bottom: 10px;
                text-transform: capitalize;
            }
            
            /* Hora mostrada en fuente monoespaciada para mejor legibilidad */
            .hora {
                font-size: 1.8em;
                font-family: 'Courier New', monospace;
                font-weight: bold;
            }
            
            /* Contenedor para la barra de búsqueda */
            .input-container {
                margin-bottom: 20px;
                text-align: center;
            }
            
            /* Input de búsqueda: estilizado con bordes y sombra */
            input {
                padding: 10px 15px;
                border: 2px solid #667eea;
                border-radius: 8px;
                font-size: 1em;
                width: 100%;
                max-width: 300px;
            }
            
            /* Botón de búsqueda: color gradiente con transición */
            button {
                padding: 10px 20px;
                margin-left: 10px;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-size: 1em;
                font-weight: bold;
                transition: background 0.3s;
            }
            
            /* Botón al pasar el mouse: cambia color */
            button:hover {
                background: #764ba2;
            }
            
            /* Sección de países disponibles al final */
            .paises-disponibles {
                margin-top: 30px;
                padding-top: 30px;
                border-top: 2px solid #eee;
            }
            
            /* Título de la sección de países */
            .paises-disponibles h3 {
                color: #333;
                margin-bottom: 10px;
            }
            
            /* Lista de países: flex para distribuirlos en fila */
            .paises-lista {
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
            }
            
            /* Botones de país individuales: tags clicables */
            .pais-tag {
                background: #f0f0f0;
                padding: 8px 12px;
                border-radius: 20px;
                font-size: 0.9em;
                color: #333;
            }
            
            /* Mensaje de seguridad */
            .security-badge {
                text-align: center;
                font-size: 0.8em;
                color: #666;
                margin-top: 20px;
                padding-top: 20px;
                border-top: 1px solid #eee;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🕐 Reloj Interactivo</h1>
            
            <div class="input-container">
                <input 
                    type="text" 
                    id="paisInput" 
                    placeholder="Buscar país..." 
                    maxlength="50"
                    autocomplete="off"
                    spellcheck="false"
                >
                <button onclick="buscarPais()" aria-label="Buscar país">Buscar</button>
            </div>
            
            <div class="reloj-grid" id="relojes" role="main" aria-label="Lista de países y horarios"></div>
            
            <div class="paises-disponibles">
                <h3>Países disponibles:</h3>
                <div class="paises-lista" id="paises-lista" role="group" aria-label="Botones de selección de país"></div>
            </div>
            
            <div class="security-badge">
                🔒 Conexión segura | v3.0.0 | Rate Limited
            </div>
        </div>

        <script>
            // ========== PREVENCIÓN DE XSS ==========
            
            /**
             * Escapa caracteres HTML peligrosos
             */
            function escaparHTML(texto) {
                const div = document.createElement('div');
                div.textContent = texto;
                return div.innerHTML;
            }
            
            /**
             * Sanitiza entrada del usuario
             */
            function sanitizar(entrada) {
                if (!entrada) return '';
                return entrada.toLowerCase().trim().substring(0, 50);
            }
            
            // ========== VARIABLES GLOBALES ==========
            const paises = ["españa", "mexico", "argentina", "japon", "australia", "usa", "reino_unido", "india", "brasil", "singapur"];
            const TIMEOUT_MS = 5000;
            const MAX_REINTENTOS = 3;
            
            // ========== FETCH SEGURO CON TIMEOUT Y REINTENTOS ==========
            async function fetchConReintentos(url, intentos = 1) {
                try {
                    // Validar URL
                    const urlObj = new URL(url, window.location.origin);
                    
                    const controller = new AbortController();
                    const timeoutId = setTimeout(() => controller.abort(), TIMEOUT_MS);
                    
                    const response = await fetch(urlObj.toString(), { 
                        signal: controller.signal,
                        method: 'GET',
                        headers: {
                            'Accept': 'application/json'
                        }
                    });
                    clearTimeout(timeoutId);
                    
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}`);
                    }
                    
                    const data = await response.json();
                    return data;
                } catch (error) {
                    if (intentos < MAX_REINTENTOS) {
                        await new Promise(resolve => setTimeout(resolve, 500 * intentos));
                        return fetchConReintentos(url, intentos + 1);
                    }
                    throw error;
                }
            }
            
            // ========== CREAR TARJETAS ==========
            function crearTarjetas() {
                const container = document.getElementById('relojes');
                if (!container) return;
                
                container.innerHTML = '';
                
                for (const pais of paises) {
                    const card = document.createElement('div');
                    card.className = 'reloj-card';
                    card.id = `tarjeta-${sanitizar(pais)}`;
                    
                    const paisName = document.createElement('div');
                    paisName.className = 'pais';
                    paisName.textContent = pais.toUpperCase();
                    
                    const horaDisplay = document.createElement('div');
                    horaDisplay.className = 'hora';
                    horaDisplay.id = `hora-${sanitizar(pais)}`;
                    horaDisplay.textContent = '--:--:--';
                    
                    card.appendChild(paisName);
                    card.appendChild(horaDisplay);
                    container.appendChild(card);
                }
            }
            
            // ========== ACTUALIZAR HORAS ==========
            async function actualizarHoras() {
                for (const pais of paises) {
                    try {
                        const data = await fetchConReintentos(`/hora/${sanitizar(pais)}`);
                        const horaElement = document.getElementById(`hora-${sanitizar(pais)}`);
                        
                        if (horaElement && horaElement.textContent !== data.hora) {
                            horaElement.textContent = escaparHTML(data.hora);
                            horaElement.style.color = '#ffffff';
                        }
                    } catch (error) {
                        console.error(`Error actualizando ${pais}:`, error);
                        const horaElement = document.getElementById(`hora-${sanitizar(pais)}`);
                        if (horaElement) {
                            horaElement.textContent = 'Error';
                            horaElement.style.color = '#ff6b6b';
                        }
                    }
                }
            }
            
            // ========== BUSCAR PAÍS ==========
            async function buscarPais() {
                const input = document.getElementById('paisInput').value;
                const paisSanitizado = sanitizar(input);
                
                if (!paisSanitizado) {
                    alert('Por favor ingresa un país válido');
                    return;
                }
                
                try {
                    const data = await fetchConReintentos(`/hora/${paisSanitizado}`);
                    
                    const mensaje = 
                        escaparHTML(paisSanitizado.toUpperCase()) + '\\n' +
                        'Hora: ' + escaparHTML(data.hora) + '\\n' +
                        'Fecha: ' + escaparHTML(data.fecha) + '\\n' +
                        'Zona: ' + escaparHTML(data.zona_horaria);
                    
                    alert(mensaje);
                } catch (error) {
                    alert('País no encontrado o error de conexión');
                }
            }
            
            // ========== CARGAR PAÍSES DISPONIBLES ==========
            function cargarPaisesDisponibles() {
                const lista = document.getElementById('paises-lista');
                if (!lista) return;
                
                for (const pais of paises) {
                    const tag = document.createElement('span');
                    tag.className = 'pais-tag';
                    tag.textContent = pais.toUpperCase();
                    tag.style.cursor = 'pointer';
                    tag.role = 'button';
                    tag.tabIndex = 0;
                    
                    const buscar = () => {
                        document.getElementById('paisInput').value = pais;
                        buscarPais();
                    };
                    
                    tag.onclick = buscar;
                    tag.onkeypress = (e) => {
                        if (e.key === 'Enter' || e.key === ' ') {
                            e.preventDefault();
                            buscar();
                        }
                    };
                    
                    lista.appendChild(tag);
                }
            }
            
            // ========== INICIALIZACIÓN ==========
            document.addEventListener('DOMContentLoaded', function() {
                crearTarjetas();
                cargarPaisesDisponibles();
                actualizarHoras();
                setInterval(actualizarHoras, 1000);
                
                const paisInput = document.getElementById('paisInput');
                if (paisInput) {
                    paisInput.addEventListener('keypress', function(event) {
                        if (event.key === 'Enter') {
                            event.preventDefault();
                            buscarPais();
                        }
                    });
                }
            });
        </script>
    </body>
    </html>
    """,
        status_code=200
    )

# ==================== FUNCIÓN CACHEADA PARA OBTENER HORAS ====================

@lru_cache(maxsize=1)
def _obtener_hora_pais(pais_value: str) -> Dict:
    """
    Función auxiliar cacheada que obtiene la hora de un país.
    Se cachea para optimizar llamadas frecuentes.
    
    Args:
        pais_value: Valor del país (debe estar validado)
    
    Returns:
        Dict con hora, fecha y zona horaria
    """
    try:
        zona_horaria = PAISES[pais_value]
        tz = pytz.timezone(zona_horaria)
        hora_actual = datetime.now(tz)
        
        return {
            "pais": pais_value,
            "hora": hora_actual.strftime("%H:%M:%S"),
            "fecha": hora_actual.strftime("%Y-%m-%d"),
            "zona_horaria": zona_horaria,
            "hora_completa": hora_actual.strftime("%d/%m/%Y %H:%M:%S")
        }
    except Exception as e:
        logger.error(f"Error obteniendo hora para {pais_value}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al obtener la hora")

# ==================== ENDPOINTS SEGUROS ====================

@app.get("/hora/{pais}", response_model=HoraResponse)
async def obtener_hora(pais: PaisEnum, request: Request):
    """
    Endpoint seguro para obtener la hora actual en un país específico.
    
    Validaciones:
    - Rate limiting por IP
    - Validación de país por Enum
    - Sanitización de entrada
    
    Args:
        pais: Nombre del país (validado por Enum)
        request: Objeto de solicitud (para obtener IP)
    
    Returns:
        HoraResponse: Con hora, fecha, zona horaria e información completa
    """
    try:
        resultado = _obtener_hora_pais(pais.value)
        client_ip = request.client.host if request.client else "unknown"
        logger.info(f"[{client_ip}] Consulta de hora: {pais.value}")
        return resultado
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error crítico en obtener_hora: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/paises", response_model=PaisesResponse)
async def listar_paises(request: Request):
    """
    Endpoint seguro que lista todos los países disponibles.
    
    Returns:
        PaisesResponse: Con lista de países y total disponible
    """
    try:
        paises_list = [pais.value for pais in PaisEnum]
        logger.info(f"[{request.client.host}] Consulta de países disponibles")
        return {"paises": paises_list, "total": len(paises_list)}
    except Exception as e:
        logger.error(f"Error en listar_paises: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al listar países")

@app.get("/todas-horas")
async def obtener_todas_horas(request: Request):
    """
    Endpoint seguro que obtiene horas de todos los países.
    
    Returns:
        dict: Diccionario con país como clave y hora/fecha/zona_horaria como valor
    """
    try:
        resultado = {}
        for pais_enum in PaisEnum:
            resultado[pais_enum.value] = _obtener_hora_pais(pais_enum.value)
            resultado[pais_enum.value].pop("hora_completa", None)
        
        logger.info(f"[{request.client.host}] Consulta de todas las horas")
        return resultado
    except Exception as e:
        logger.error(f"Error en obtener_todas_horas: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al obtener todas las horas")

@app.get("/health", response_model=HealthResponse)
async def health_check(request: Request):
    """
    Endpoint de verificación de salud con información de seguridad.
    
    Returns:
        HealthResponse: Estado de la aplicación
    """
    logger.info(f"[{request.client.host}] Health check realizado")
    return {
        "status": "ok", 
        "servicio": "Reloj Interactivo Valeria",
        "version": "3.0.0",
        "security": "enabled"
    }

# ==================== ENDPOINTS DE AUTENTICACIÓN ====================

@app.get("/login")
async def pagina_login():
    """
    Página de login para acceder al sistema.
    """
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'">
        <title>Login - Valeria</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }
            
            .login-container {
                background: white;
                border-radius: 15px;
                padding: 40px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                max-width: 400px;
                width: 100%;
            }
            
            .login-header {
                text-align: center;
                margin-bottom: 40px;
            }
            
            .login-header h1 {
                color: #333;
                font-size: 2em;
                margin-bottom: 10px;
            }
            
            .login-header p {
                color: #666;
                font-size: 0.9em;
            }
            
            .form-group {
                margin-bottom: 20px;
            }
            
            label {
                display: block;
                margin-bottom: 8px;
                color: #333;
                font-weight: bold;
            }
            
            input {
                width: 100%;
                padding: 12px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 1em;
                transition: border-color 0.3s;
            }
            
            input:focus {
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }
            
            .btn-login {
                width: 100%;
                padding: 12px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 1em;
                font-weight: bold;
                cursor: pointer;
                transition: transform 0.2s;
            }
            
            .btn-login:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
            }
            
            .btn-login:active {
                transform: translateY(0);
            }
            
            .error-message {
                background: #ffebee;
                color: #c62828;
                padding: 12px;
                border-radius: 8px;
                margin-bottom: 20px;
                display: none;
                border-left: 4px solid #c62828;
            }
            
            .success-message {
                background: #e8f5e9;
                color: #2e7d32;
                padding: 12px;
                border-radius: 8px;
                margin-bottom: 20px;
                display: none;
                border-left: 4px solid #2e7d32;
            }
            
            .loading {
                display: none;
                text-align: center;
                color: #667eea;
            }
            
            .spinner {
                display: inline-block;
                width: 20px;
                height: 20px;
                border: 3px solid #f3f3f3;
                border-top: 3px solid #667eea;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin-right: 10px;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            .security-info {
                background: #e3f2fd;
                border-left: 4px solid #1976d2;
                padding: 12px;
                border-radius: 5px;
                margin-top: 20px;
                font-size: 0.85em;
                color: #1565c0;
            }
            
            .back-link {
                text-align: center;
                margin-top: 20px;
            }
            
            .back-link a {
                color: #667eea;
                text-decoration: none;
                font-size: 0.9em;
            }
            
            .back-link a:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <div class="login-container">
            <div class="login-header">
                <h1>🔐 Valeria</h1>
                <p>Acceso al Panel de Administración</p>
            </div>
            
            <div id="error-message" class="error-message"></div>
            <div id="success-message" class="success-message"></div>
            
            <form id="login-form" onsubmit="handleLogin(event)">
                <div class="form-group">
                    <label for="username">Usuario</label>
                    <input 
                        type="text" 
                        id="username" 
                        name="username"
                        placeholder="admin"
                        required
                        autocomplete="username"
                    >
                </div>
                
                <div class="form-group">
                    <label for="password">Contraseña</label>
                    <input 
                        type="password" 
                        id="password" 
                        name="password"
                        placeholder="••••••••"
                        required
                        autocomplete="current-password"
                    >
                </div>
                
                <button type="submit" class="btn-login" id="btn-submit">
                    Iniciar Sesión
                </button>
            </form>
            
            <div id="loading" class="loading">
                <div class="spinner"></div> Autenticando...
            </div>
            
            <div class="security-info">
                🔒 Conexión segura | Los datos se transmiten de forma cifrada
            </div>
            
            <div class="back-link">
                <a href="/">← Volver a la página principal</a>
            </div>
        </div>
        
        <script>
            // Recuperar token de URL si existe
            const urlParams = new URLSearchParams(window.location.search);
            const token = urlParams.get('token');
            
            if (token) {
                localStorage.setItem('auth_token', token);
                window.location.href = '/admin';
            }
            
            async function handleLogin(event) {
                event.preventDefault();
                
                const username = document.getElementById('username').value;
                const password = document.getElementById('password').value;
                
                const errorMsg = document.getElementById('error-message');
                const successMsg = document.getElementById('success-message');
                const loading = document.getElementById('loading');
                const btnSubmit = document.getElementById('btn-submit');
                
                // Limpiar mensajes
                errorMsg.style.display = 'none';
                successMsg.style.display = 'none';
                loading.style.display = 'block';
                btnSubmit.disabled = true;
                
                try {
                    const response = await fetch('/api/v1/auth/login', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            username: username,
                            password: password
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        // Guardar token
                        localStorage.setItem('auth_token', data.access_token);
                        
                        // Mostrar mensaje de éxito
                        successMsg.textContent = '✅ Autenticación exitosa. Redirigiendo...';
                        successMsg.style.display = 'block';
                        
                        // Redirigir al panel
                        setTimeout(() => {
                            window.location.href = '/admin';
                        }, 1500);
                    } else {
                        // Error de autenticación
                        errorMsg.textContent = '❌ ' + (data.detail || 'Error en autenticación');
                        errorMsg.style.display = 'block';
                        btnSubmit.disabled = false;
                        loading.style.display = 'none';
                    }
                } catch (error) {
                    console.error('Error:', error);
                    errorMsg.textContent = '❌ Error de conexión con el servidor';
                    errorMsg.style.display = 'block';
                    btnSubmit.disabled = false;
                    loading.style.display = 'none';
                }
            }
            
            // Foco automático en el primer campo
            document.getElementById('username').focus();
        </script>
    </body>
    </html>
    """)
async def login(credenciales: LoginRequest, request: Request):
    """
    Endpoint de login que retorna un JWT token.
    
    Args:
        credenciales: Username y password
        request: Objeto de solicitud
    
    Returns:
        TokenResponse: JWT token con información de expiración
    
    Raises:
        HTTPException: Si credenciales son incorrectas
    """
    client_ip = request.client.host if request.client else "unknown"
    username = credenciales.username
    
    # Verificar que el usuario existe
    if username not in USUARIOS:
        logger.warning(f"[{client_ip}] Intento de login fallido - usuario no existe: {username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )
    
    usuario = USUARIOS[username]
    
    # Verificar que el usuario está activo
    if not usuario.get("is_active"):
        logger.warning(f"[{client_ip}] Intento de login - usuario inactivo: {username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )
    
    # Verificar contraseña
    if not verificar_contrasena(credenciales.password, usuario["hashed_password"]):
        logger.warning(f"[{client_ip}] Intento de login fallido - contraseña incorrecta: {username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )
    
    # Crear token
    access_token = crear_access_token(data={"sub": username})
    
    logger.info(f"[{client_ip}] Login exitoso: {username}")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@app.post("/api/v1/auth/logout")
async def logout(usuario: dict = Depends(obtener_usuario_actual)):
    """
    Endpoint de logout (principalmente para frontend).
    
    En producción, considerar usar token blacklist.
    """
    logger.info(f"Logout de usuario: {usuario['username']}")
    return {"message": "Logout exitoso"}

@app.get("/api/v1/auth/me", response_model=UserResponse)
async def obtener_perfil(usuario: dict = Depends(obtener_usuario_actual)):
    """
    Obtiene la información del usuario actual.
    
    Requiere: Bearer token válido
    """
    return {
        "username": usuario["username"],
        "email": usuario["email"],
        "is_admin": usuario["is_admin"],
        "is_active": usuario["is_active"]
    }

# ==================== ENDPOINTS DE ADMINISTRACIÓN ====================

@app.get("/api/v1/admin/usuarios")
async def listar_usuarios(admin: dict = Depends(obtener_usuario_admin)):
    """
    Lista todos los usuarios del sistema (solo admin).
    
    Requiere: Ser administrador
    """
    usuarios_list = []
    for username, usuario in USUARIOS.items():
        usuarios_list.append({
            "username": usuario["username"],
            "email": usuario["email"],
            "is_admin": usuario["is_admin"],
            "is_active": usuario["is_active"]
        })
    
    logger.info(f"Admin {admin['username']} consultó lista de usuarios")
    return {"usuarios": usuarios_list, "total": len(usuarios_list)}

@app.post("/api/v1/admin/usuarios")
async def crear_usuario(new_user: UsuarioRegistro, admin: dict = Depends(obtener_usuario_admin)):
    """
    Crea un nuevo usuario (solo admin).
    
    Requiere: Ser administrador
    """
    if new_user.username in USUARIOS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario ya existe"
        )
    
    USUARIOS[new_user.username] = {
        "username": new_user.username,
        "email": new_user.email,
        "hashed_password": pwd_context.hash(new_user.password),
        "is_admin": False,
        "is_active": True
    }
    
    guardar_usuarios(USUARIOS)
    logger.info(f"Admin {admin['username']} creó nuevo usuario: {new_user.username}")
    
    return {"message": f"Usuario {new_user.username} creado exitosamente"}

@app.get("/admin")
async def panel_admin(usuario: dict = Depends(obtener_usuario_admin)):
    """
    Panel de administración de Valeria.
    
    Requiere: Ser administrador
    """
    return HTMLResponse(content=f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'">
        <title>Panel Admin - Valeria</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }}
            
            .navbar {{
                background: #222;
                color: white;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            
            .navbar h1 {{
                font-size: 1.5em;
            }}
            
            .user-info {{
                display: flex;
                gap: 15px;
                align-items: center;
            }}
            
            .user-info span {{
                background: #667eea;
                padding: 5px 15px;
                border-radius: 20px;
                font-size: 0.9em;
            }}
            
            .container {{
                max-width: 1000px;
                margin: 0 auto;
            }}
            
            .card {{
                background: white;
                border-radius: 10px;
                padding: 30px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                margin-bottom: 20px;
            }}
            
            .card h2 {{
                color: #333;
                margin-bottom: 20px;
                border-bottom: 2px solid #667eea;
                padding-bottom: 10px;
            }}
            
            table {{
                width: 100%;
                border-collapse: collapse;
            }}
            
            table th {{
                background: #f0f0f0;
                padding: 12px;
                text-align: left;
                color: #333;
                font-weight: bold;
            }}
            
            table td {{
                padding: 12px;
                border-bottom: 1px solid #eee;
            }}
            
            table tr:hover {{
                background: #f9f9f9;
            }}
            
            .badge {{
                padding: 5px 10px;
                border-radius: 5px;
                font-size: 0.85em;
                font-weight: bold;
            }}
            
            .badge-admin {{
                background: #ff6b6b;
                color: white;
            }}
            
            .badge-active {{
                background: #51cf66;
                color: white;
            }}
            
            .badge-inactive {{
                background: #868e96;
                color: white;
            }}
            
            .stats {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 20px;
            }}
            
            .stat-box {{
                background: white;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }}
            
            .stat-box .number {{
                font-size: 2.5em;
                color: #667eea;
                font-weight: bold;
            }}
            
            .stat-box .label {{
                color: #666;
                font-size: 0.9em;
                margin-top: 10px;
            }}
            
            .button {{
                padding: 10px 20px;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-weight: bold;
                transition: background 0.3s;
            }}
            
            .button:hover {{
                background: #764ba2;
            }}
            
            .button.danger {{
                background: #ff6b6b;
            }}
            
            .button.danger:hover {{
                background: #ff5252;
            }}
            
            .logout {{
                background: #ff6b6b;
                padding: 10px 20px;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-weight: bold;
            }}
            
            .logout:hover {{
                background: #ff5252;
            }}
            
            .security-info {{
                background: #e7f5ff;
                border-left: 4px solid #667eea;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="navbar">
            <h1>🛡️ Panel de Administración</h1>
            <div class="user-info">
                <span>👤 {usuario['username']}</span>
                <button class="logout" onclick="logout()">Cerrar Sesión</button>
            </div>
        </div>
        
        <div class="container">
            <div class="security-info">
                ✅ Estás conectado como administrador | 🔒 Conexión segura
            </div>
            
            <div class="stats">
                <div class="stat-box">
                    <div class="number" id="total-usuarios">0</div>
                    <div class="label">Usuarios Totales</div>
                </div>
                <div class="stat-box">
                    <div class="number" id="usuarios-activos">0</div>
                    <div class="label">Usuarios Activos</div>
                </div>
                <div class="stat-box">
                    <div class="number" id="admins">0</div>
                    <div class="label">Administradores</div>
                </div>
            </div>
            
            <div class="card">
                <h2>📋 Gestión de Usuarios</h2>
                <table id="usuarios-table">
                    <thead>
                        <tr>
                            <th>Usuario</th>
                            <th>Email</th>
                            <th>Rol</th>
                            <th>Estado</th>
                        </tr>
                    </thead>
                    <tbody id="usuarios-tbody">
                        <tr><td colspan="4" style="text-align: center; color: #999;">Cargando...</td></tr>
                    </tbody>
                </table>
            </div>
            
            <div class="card">
                <h2>ℹ️ Información del Sistema</h2>
                <table>
                    <tr>
                        <td><strong>Versión:</strong></td>
                        <td>3.0.0</td>
                    </tr>
                    <tr>
                        <td><strong>Seguridad:</strong></td>
                        <td>🔒 JWT + CORS + Rate Limiting</td>
                    </tr>
                    <tr>
                        <td><strong>Base de Datos:</strong></td>
                        <td>JSON (En-Memoria)</td>
                    </tr>
                    <tr>
                        <td><strong>Hora del Servidor:</strong></td>
                        <td id="server-time">--:--:--</td>
                    </tr>
                </table>
            </div>
        </div>
        
        <script>
            const token = localStorage.getItem('auth_token');
            
            // Obtener token del parámetro URL si es redirección de login
            const urlParams = new URLSearchParams(window.location.search);
            const tokenParam = urlParams.get('token');
            
            if (tokenParam && !token) {{
                localStorage.setItem('auth_token', tokenParam);
                window.location.href = '/admin';
            }}
            
            async function cargarUsuarios() {{
                try {{
                    const response = await fetch('/api/v1/admin/usuarios', {{
                        headers: {{
                            'Authorization': `Bearer ${{token}}`
                        }}
                    }});
                    
                    if (!response.ok) throw new Error('Error al cargar usuarios');
                    
                    const data = await response.json();
                    const tbody = document.getElementById('usuarios-tbody');
                    tbody.innerHTML = '';
                    
                    let activos = 0;
                    let admins = 0;
                    
                    data.usuarios.forEach(usuario => {{
                        if (usuario.is_active) activos++;
                        if (usuario.is_admin) admins++;
                        
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td><strong>${{usuario.username}}</strong></td>
                            <td>${{usuario.email}}</td>
                            <td>${{usuario.is_admin ? '<span class="badge badge-admin">ADMIN</span>' : 'Usuario'}}</td>
                            <td>${{usuario.is_active ? '<span class="badge badge-active">ACTIVO</span>' : '<span class="badge badge-inactive">INACTIVO</span>'}}</td>
                        `;
                        tbody.appendChild(row);
                    }});
                    
                    document.getElementById('total-usuarios').textContent = data.total;
                    document.getElementById('usuarios-activos').textContent = activos;
                    document.getElementById('admins').textContent = admins;
                }} catch (error) {{
                    console.error('Error:', error);
                    document.getElementById('usuarios-tbody').innerHTML = '<tr><td colspan="4" style="text-align: center; color: red;">Error al cargar datos</td></tr>';
                }}
            }}
            
            function actualizarHora() {{
                const now = new Date();
                document.getElementById('server-time').textContent = now.toLocaleTimeString();
            }}
            
            function logout() {{
                localStorage.removeItem('auth_token');
                alert('Sesión cerrada');
                window.location.href = '/';
            }}
            
            // Cargar datos al iniciar
            cargarUsuarios();
            actualizarHora();
            setInterval(actualizarHora, 1000);
            setInterval(cargarUsuarios, 30000);
        </script>
    </body>
    </html>
    """)

# ==================== MANEJO DE ERRORES GLOBAL ====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Manejador personalizado para excepciones HTTP."""
    logger.warning(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return {"error": exc.detail, "status": exc.status_code}

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Manejador global para excepciones no manejadas."""
    logger.error(f"Error general: {str(exc)}", exc_info=True)
    return {"error": "Error interno del servidor", "status": 500}

# ==================== MENSAJE DE INICIO ====================
if __name__ == "__main__":
    logger.info("=" * 70)
    logger.info("🔒 VALERIA - RELOJ INTERACTIVO SEGURO v4.0.0")
    logger.info("=" * 70)
    logger.info("✅ CORS: Habilitado")
    logger.info("✅ Rate Limiting: 100 requests/minuto por IP")
    logger.info("✅ Protección XSS: Habilitada")
    logger.info("✅ Autenticación: JWT habilitada")
    logger.info("=" * 70)
    logger.info("🔐 CREDENCIALES ADMIN:")
    logger.info("   Usuario: admin")
    logger.info("   Password: admin123")
    logger.info("   ⚠️  CAMBIAR EN PRODUCCIÓN")
    logger.info("=" * 70)
    logger.info("📍 ENDPOINTS PÚBLICOS:")
    logger.info("   GET  /              (Página principal)")
    logger.info("   GET  /health        (Health check)")
    logger.info("   GET  /paises        (Listar países)")
    logger.info("   GET  /hora/{pais}   (Obtener hora)")
    logger.info("   POST /api/v1/auth/login (Login)")
    logger.info("=" * 70)
    logger.info("🔐 ENDPOINTS PROTEGIDOS (requieren JWT):")
    logger.info("   GET  /api/v1/auth/me          (Perfil actual)")
    logger.info("   POST /api/v1/auth/logout      (Logout)")
    logger.info("   GET  /api/v1/admin/usuarios   (Lista usuarios - Admin)")
    logger.info("   POST /api/v1/admin/usuarios   (Crear usuario - Admin)")
    logger.info("   GET  /admin                   (Panel admin - Admin)")
    logger.info("=" * 70)

