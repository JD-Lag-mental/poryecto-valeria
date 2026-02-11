#!/usr/bin/env python3
"""
API de Reloj Interactivo - Valeria.

Este módulo proporciona una aplicación FastAPI que muestra la hora actual
en diferentes países del mundo. Incluye una interfaz web interactiva con
tarjetas que se actualizan en tiempo real sin parpadeos.
"""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from datetime import datetime
import pytz

# Inicializar la aplicación FastAPI con metadatos
app = FastAPI(title="Valeria - Reloj Interactivo", version="1.0.0")

# Diccionario que mapea nombres de países a sus zonas horarias IANA
# Las claves son nombres de países en minúsculas y los valores son códigos de zona horaria
PAISES = {
    "españa": "Europe/Madrid",
    "mexico": "America/Mexico_City",
    "argentina": "America/Argentina/Buenos_Aires",
    "japon": "Asia/Tokyo",
    "australia": "Australia/Sydney",
    "usa": "America/New_York",
    "reino_unido": "Europe/London",
    "india": "Asia/Kolkata",
    "brasil": "America/Sao_Paulo",
    "singapur": "Asia/Singapore",
}

@app.get("/")
def read_root():
    """
    Endpoint raíz que sirve la página HTML principal.
    
    Retorna:
        HTMLResponse: Página HTML con interfaz interactiva del reloj
    """
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
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
        </style>
    </head>
    <body>
        <div class="container">
            <h1>⏰ Reloj Interactivo</h1>
            
            <div class="input-container">
                <input type="text" id="paisInput" placeholder="Buscar país o zona horaria...">
                <button onclick="buscarPais()">Buscar</button>
            </div>
            
            <div class="reloj-grid" id="relojes"></div>
            
            <div class="paises-disponibles">
                <h3>Países disponibles:</h3>
                <div class="paises-lista" id="paises-lista"></div>
            </div>
        </div>

        <script>
            /**
             * Array con los nombres de los países disponibles.
             * Se usa para iterar y crear tarjetas y botones.
             */
            const paises = ["españa", "mexico", "argentina", "japon", "australia", "usa", "reino_unido", "india", "brasil", "singapur"];
            
            /**
             * Crea las tarjetas de reloj una sola vez al cargar la página.
             * Evita parpadeos al no redibujar elementos innecesariamente.
             */
            function crearTarjetas() {
                const container = document.getElementById('relojes');
                container.innerHTML = '';
                
                // Para cada país, crea una tarjeta con su nombre y un placeholder de hora
                for (const pais of paises) {
                    const card = document.createElement('div');
                    card.className = 'reloj-card';
                    card.id = `tarjeta-${pais}`;
                    card.innerHTML = `
                        <div class="pais">${pais.toUpperCase()}</div>
                        <div class="hora" id="hora-${pais}">--:--:--</div>
                    `;
                    container.appendChild(card);
                }
            }
            
            /**
             * Actualiza solo los números de las horas en las tarjetas existentes.
             * Realiza peticiones fetch a la API para obtener la hora actual de cada país.
             * Solo actualiza si el valor ha cambiado para evitar parpadeos innecesarios.
             */
            async function actualizarHoras() {
                for (const pais of paises) {
                    try {
                        // Realiza petición GET al endpoint /hora/{pais}
                        const response = await fetch(`/hora/${pais}`);
                        const data = await response.json();
                        
                        // Obtiene el elemento HTML que contiene la hora del país
                        const horaElement = document.getElementById(`hora-${pais}`);
                        
                        // Solo actualiza si el contenido ha cambiado
                        if (horaElement && horaElement.textContent !== data.hora) {
                            horaElement.textContent = data.hora;
                        }
                    } catch (error) {
                        console.error(`Error actualizando ${pais}:`, error);
                    }
                }
            }
            
            /**
             * Busca un país específico cuando el usuario lo ingresa en la barra de búsqueda.
             * Muestra un alert con la información completa (hora, fecha, zona horaria).
             */
            async function buscarPais() {
                // Obtiene el valor del input y lo convierte a minúsculas
                const input = document.getElementById('paisInput').value.toLowerCase().trim();
                
                // Valida que el input no esté vacío
                if (!input) {
                    alert('Por favor ingresa un país');
                    return;
                }
                
                try {
                    // Realiza petición GET al endpoint /hora/{pais}
                    const response = await fetch(`/hora/${input}`);
                    const data = await response.json();
                    
                    // Si hay error, muestra los países disponibles
                    if (data.error) {
                        alert('País no encontrado. Países disponibles: ' + paises.join(', '));
                    } else {
                        // Muestra información completa en un alert formateado
                        alert(`${input.toUpperCase()}\nHora: ${data.hora}\nFecha: ${data.fecha}\nZona horaria: ${data.zona_horaria}`);
                    }
                } catch (error) {
                    console.error('Error:', error);
                    alert('Error al buscar el país');
                }
            }
            
            /**
             * Carga la lista de países disponibles como botones clicables.
             * Al hacer clic en un país, se llena el input de búsqueda y se busca automáticamente.
             */
            function cargarPaisesDisponibles() {
                const lista = document.getElementById('paises-lista');
                
                // Para cada país, crea un botón clickeable
                for (const pais of paises) {
                    const tag = document.createElement('span');
                    tag.className = 'pais-tag';
                    tag.textContent = pais.toUpperCase();
                    tag.style.cursor = 'pointer';
                    
                    // Al hacer clic, rellena el input y busca el país
                    tag.onclick = () => {
                        document.getElementById('paisInput').value = pais;
                        buscarPais();
                    };
                    lista.appendChild(tag);
                }
            }
            
            /**
             * INICIALIZACIÓN: Se ejecuta cuando carga la página
             */
            // 1. Crea las tarjetas de reloj (estructura HTML)
            crearTarjetas();
            
            // 2. Carga los botones de países disponibles
            cargarPaisesDisponibles();
            
            // 3. Realiza la primera actualización de horas
            actualizarHoras();
            
            // 4. Actualiza las horas cada 1000 milisegundos (1 segundo)
            // Solo actualiza los números, no redibuja las tarjetas
            setInterval(actualizarHoras, 1000);
            
            // 5. Permite buscar presionando Enter en el input
            document.getElementById('paisInput').addEventListener('keypress', function(event) {
                if (event.key === 'Enter') {
                    buscarPais();
                }
            });
        </script>
    </body>
    </html>
    """)

@app.get("/hora/{pais}")
def obtener_hora(pais: str):
    """
    Obtiene la hora actual en un país específico.
    
    Este endpoint:
    1. Valida que el país exista en el diccionario PAISES
    2. Obtiene la zona horaria correspondiente
    3. Calcula la hora actual en esa zona horaria
    4. Retorna la información formateada
    
    Args:
        pais (str): Nombre del país en minúsculas (ej: "españa", "mexico")
    
    Returns:
        dict: Con las siguientes claves:
            - pais: Nombre del país consultado
            - hora: Hora formateada como HH:MM:SS
            - fecha: Fecha formateada como YYYY-MM-DD
            - zona_horaria: Código de zona horaria IANA
            - hora_completa: Hora y fecha en formato DD/MM/YYYY HH:MM:SS
        
        Si el país no existe, retorna:
            - error: Mensaje de error
            - paises_disponibles: Lista de países disponibles
    """
    # Normaliza el input del país (minúsculas y sin espacios)
    pais = pais.lower().strip()
    
    # Valida que el país exista en el diccionario
    if pais not in PAISES:
        return {"error": "País no encontrado", "paises_disponibles": list(PAISES.keys())}
    
    # Obtiene la zona horaria correspondiente al país
    zona_horaria = PAISES[pais]
    
    # Crea un objeto timezone usando pytz
    tz = pytz.timezone(zona_horaria)
    
    # Obtiene la hora actual en esa zona horaria
    hora_actual = datetime.now(tz)
    
    # Retorna la información formateada
    return {
        "pais": pais,
        "hora": hora_actual.strftime("%H:%M:%S"),
        "fecha": hora_actual.strftime("%Y-%m-%d"),
        "zona_horaria": zona_horaria,
        "hora_completa": hora_actual.strftime("%d/%m/%Y %H:%M:%S")
    }

@app.get("/paises")
def listar_paises():
    """
    Lista todos los países disponibles en la aplicación.
    
    Retorna:
        dict: Con las claves:
            - paises: Lista de nombres de países disponibles
            - total: Cantidad total de países disponibles
    """
    return {"paises": list(PAISES.keys()), "total": len(PAISES)}

@app.get("/todas-horas")
def obtener_todas_horas():
    """
    Obtiene la hora actual en todos los países disponibles simultáneamente.
    
    Retorna:
        dict: Un diccionario donde:
            - Clave: nombre del país
            - Valor: diccionario con "hora", "fecha" y "zona_horaria"
    """
    resultado = {}
    
    # Para cada país, obtiene su hora actual
    for pais in PAISES.keys():
        zona_horaria = PAISES[pais]
        tz = pytz.timezone(zona_horaria)
        hora_actual = datetime.now(tz)
        
        resultado[pais] = {
            "hora": hora_actual.strftime("%H:%M:%S"),
            "fecha": hora_actual.strftime("%Y-%m-%d"),
            "zona_horaria": zona_horaria
        }
    
    return resultado

@app.get("/health")
def health_check():
    """
    Endpoint de verificación de salud de la aplicación.
    
    Se usa para verificar que la API está activa y funcionando correctamente.
    
    Retorna:
        dict: Con el estado de la aplicación y su nombre
    """
    return {"status": "ok", "servicio": "Reloj Interactivo Valeria"}

