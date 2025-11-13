import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap
import streamlit.components.v1 as components
import time 
import urllib.parse 
import random
from datetime import datetime, timedelta
import math

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="SECURE MAP HUANCAYO",
    page_icon="🚨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- COORDENADAS DE LA UTP HUANCAYO (UBICACIÓN FIJA) ---
UTP_LAT = -12.022398351778946
UTP_LON = -75.23382979742267

# --- 2. DATOS BASE Y CALLES REALES DE HUANCAYO ---

# Calles y puntos de referencia para simulación realista
HUANCAYO_STREETS = [
    "Av. Mariscal Castilla",
    "Av. Huancavelica",
    "Calle Real",
    "Jr. Piura",
    "Av. Circunvalación",
    "Paradero UTP (Av. Circunvalación)",
    "Parque de la Identidad Huanca",
    "Av. Giráldez",
    "Plaza de Toros (El Tambo)",
    "Cruce Av. 9 de Diciembre y Av. Real"
]

def get_random_location_name():
    """Selecciona un nombre de calle/lugar aleatorio para el log."""
    return random.choice(HUANCAYO_STREETS)

# Plantillas para la simulación dinámica
INCIDENT_TEMPLATES = [
    ("Robo de celular", "Av. Circunvalación - Paradero UTP"),
    ("Acoso verbal", "Cruce Av. Real con Jr. Piura"),
    ("Riña/Pelea", "Cerca a la puerta de la UTP"),
    ("Venta de droga", "Parque La Esperanza"),
    ("Sospechoso siguiendo", "Espalda de la universidad"),
    ("Accidente vehicular menor", "Av. Mariscal Castilla"),
    ("Incendio de basura", "Avenida Huancavelica"),
    ("Hurto de pertenencias", "Terminal Terrestre")
]

safe_locations = [
    (UTP_LAT + 0.001, UTP_LON + 0.003, 'Comisaría El Tambo', '24/7'),
    (UTP_LAT - 0.003, UTP_LON - 0.001, 'Hospital Regional', '24/7'),
    (UTP_LAT + 0.002, UTP_LON - 0.003, 'Banco de la Nación', '8 AM - 6 PM'),
]

# --- 3. ESTILOS CSS (Mejoras en PESTAÑAS y Texto BLANCO) ---
st.markdown("""
<style>
    /* Importar fuente Sci-Fi/Tech */
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');

    /* Keyframes para la animación de pulso (Neon Green) */
    @keyframes pulse {
        0% {
            transform: scale(1);
            box-shadow: 0 0 15px #39ff14, 0 0 25px #39ff14; /* Neon Green Glow */
        }
        50% {
            transform: scale(1.015);
            box-shadow: 0 0 30px #39ff14, 0 0 40px #39ff14;
        }
        100% {
            transform: scale(1);
            box-shadow: 0 0 15px #39ff14, 0 0 25px #39ff14;
        }
    }
    
    /* Keyframes for the Siren Flash (Alerta de Pánico) */
    @keyframes siren-flash {
        0% { background-color: #ff0000; box-shadow: 0 0 20px #ff0000; }
        50% { background-color: #0000ff; box-shadow: 0 0 20px #0000ff; }
        100% { background-color: #ff0000; box-shadow: 0 0 20px #ff0000; }
    }
    .siren-alert {
        padding: 20px;
        margin: 20px 0;
        text-align: center;
        font-size: 28px;
        font-weight: bold;
        color: white;
        border-radius: 10px;
        animation: siren-flash 0.5s infinite alternate;
    }

    /* Estilo base de la App (Simulación Móvil) */
    .stApp {
        background-color: #0a0a0f; /* Negro Cyberpunk */
        color: #ffffff; /* Texto general en BLANCO */
        font-family: 'Share Tech Mono', monospace;
        max-width: 390px; /* Ancho de iPhone Pro */
        min-height: 844px; /* Altura mínima */
        margin: 10px auto;
        padding: 0 !important; 
        border: 1px solid #333;
        border-radius: 20px;
        box-shadow: 0 0 20px rgba(0,0,0,0.5);
        overflow: hidden; 
    }
    
    /* Ocultar footer de Streamlit */
    footer {
        visibility: hidden;
    }
    
    /* Contenedor principal de Streamlit */
    div[data-testid="stAppViewContainer"] {
        padding: 0 1rem 1rem 1rem !important;
    }

    /* --- BOTÓN DE PÁNICO BARRA TÁCTICA (TURQUESA PSICODÉLICO) --- */
    .stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #00A693, #00FFFF); 
        color: #0a0a0f; 
        border-radius: 12px; 
        width: 100%; 
        height: 70px; 
        font-size: 24px; 
        font-weight: bold;
        font-family: 'Share Tech Mono', monospace;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 15px 0 25px 0; 
        border: 4px solid #39ff14; 
        text-shadow: 0 0 10px #ffffff;
        
        animation: pulse 1.5s infinite ease-in-out;
        transition: transform 0.2s;
        box-sizing: border-box; 
    }
    .stButton > button[kind="primary"]:hover {
        transform: scale(1.02) !important;
        background: linear-gradient(90deg, #00E4C9, #00FFFF); 
        color: #0a0a0f;
    }
    
    /* --- PESTAÑAS (TABS) - AJUSTE DE TAMAÑO GRANDE --- */
    .stTabs [data-testid="stTabs"] button {
        font-size: 18px !important; 
        padding: 10px 5px !important; 
        border-radius: 8px !important;
        transition: background-color 0.2s, color 0.2s;
        border: 2px solid #00FFFF !important; 
        color: #00FFFF !important;
        background-color: #0a0a0f !important;
        flex-grow: 1; 
        margin: 0 2px; /* Pequeño margen entre tabs */
    }
    .stTabs [data-testid="stTabs"] button:hover {
        background-color: #00FFFF30 !important;
    }
    .stTabs [data-testid="stTabs"] button[aria-selected="true"] {
        color: #0a0a0f !important;
        background-color: #00FFFF !important; 
        font-weight: bold;
    }

    /* --- Contenedor de LOGS (Live Feed) --- */
    .dynamic-log-container {
        max-height: 250px; 
        overflow-y: auto;
        border: 1px solid #005f5f;
        padding: 5px;
        border-radius: 8px;
        margin-bottom: 20px;
    }
    .dynamic-log-title {
        color: #00f0ff; /* Sigue turquesa para el título */
        font-size: 16px;
        font-weight: bold;
        margin-bottom: 8px;
    }
    .dynamic-log-item {
        background: #0d1b2a;
        padding: 8px;
        border-radius: 4px;
        color: #ffffff; /* BLANCO PURO para el contenido del log */
        font-size: 13px;
        border-left: 3px solid #ff00ff;
        margin-bottom: 5px;
        white-space: nowrap; 
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .dynamic-log-item strong {
        color: #ffffff;
    }

    /* --- Análisis Predictivo (Nuevo estilo) --- */
    .analysis-item {
        background: #112d3c;
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 10px;
        border-left: 4px solid #39ff14; 
        color: #ffffff; /* BLANCO PURO para el contenido del análisis */
        font-size: 14px;
    }
    .analysis-item strong {
        color: #00f0ff; /* Turquesa para el encabezado del análisis */
        display: block;
        margin-bottom: 5px;
    }
    .metric-card {
        padding: 8px;
        border-radius: 8px;
        background-color: #1a1a2a;
        text-align: center;
        border: 1px solid #333;
        font-size: 12px;
        color: #ffffff; /* Asegurar color blanco */
    }

</style>
""", unsafe_allow_html=True)

# --- 4. DATOS DE ESTADO Y SIMULACIÓN DE INCIDENTES ---

if 'panic_active' not in st.session_state:
    st.session_state.panic_active = False
if 'contact_1' not in st.session_state:
    st.session_state.contact_1 = "+51999999999" 
if 'contact_2' not in st.session_state:
    st.session_state.contact_2 = "+51999888777" 
if 'contact_authority' not in st.session_state:
    st.session_state.contact_authority = "+51987654321" 
if 'medical_info' not in st.session_state:
    st.session_state.medical_info = "Tipo de sangre: O+, Alergias: Penicilina." 
if 'user_name' not in st.session_state:
    st.session_state.user_name = "Andrea G."
if 'last_alert_time' not in st.session_state:
    st.session_state.last_alert_time = None 

if 'incident_logs' not in st.session_state:
    st.session_state.incident_logs = [
        f"[{datetime.now().strftime('%H:%M:%S')}] REPORTE: Hurto en Paradero Av. Real (Media)"
    ]
if 'last_log_time' not in st.session_state:
    st.session_state.last_log_time = time.time() # Tiempo inicial

# --- NUEVO ESTADO PARA LOS PUNTOS DEL MAPA DINÁMICO ---
if 'dynamic_map_points' not in st.session_state:
    st.session_state.dynamic_map_points = [
        (UTP_LAT + 0.001, UTP_LON - 0.001, 'Alta', 'Robo de celular', "Av. Mariscal Castilla"),
        (UTP_LAT - 0.001, UTP_LON + 0.002, 'Media', 'Acoso verbal', "Jr. Piura"),
    ]

# Nuevo estado para el análisis (1 segundo)
if 'analysis_last_update' not in st.session_state:
    st.session_state.analysis_last_update = time.time()
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = "🏠" # Track the active tab

# LÓGICA DE UBICACIÓN FIJA 
st.session_state.location = {
    "status": "success",  
    "lat": UTP_LAT,       
    "lon": UTP_LON        
}

# --- INTERVALO DE ACTUALIZACIÓN DINÁMICA DE INCIDENTES (20 SEGUNDOS) ---
MIN_INTERVAL_SECONDS = 20
MAX_INCIDENTS = 20
MIN_INCIDENTS = 5

# --- 5. FUNCIONES PRINCIPALES ---

def generate_random_huancayo_point():
    """Genera una coordenada aleatoria, nivel, tipo de incidente y nombre de calle."""
    random_lat = UTP_LAT + random.uniform(-0.03, 0.03)
    random_lon = UTP_LON + random.uniform(-0.03, 0.03)
    
    nivel = random.choice(['Baja', 'Media', 'Alta', 'Critica'])
    incident_type, _ = random.choice(INCIDENT_TEMPLATES)
    location_name = get_random_location_name()
    
    return (random_lat, random_lon, nivel, incident_type, location_name)

def log_new_incident():
    """Gestiona la simulación dinámica de los puntos del mapa (añadir, mover, eliminar)."""
    CURRENT_TIME = time.time()

    # Solo procede a generar logs si ha pasado el tiempo mínimo
    if CURRENT_TIME > st.session_state.last_log_time + MIN_INTERVAL_SECONDS:
        
        # A. Eliminación (Simula incidentes resueltos)
        if len(st.session_state.dynamic_map_points) > MIN_INCIDENTS and random.random() < 0.3:
            index_to_remove = random.randint(0, len(st.session_state.dynamic_map_points) - 1)
            _, _, _, _, loc_name = st.session_state.dynamic_map_points.pop(index_to_remove)
            
            report_time_str = datetime.now().strftime('%H:%M:%S')
            new_log = f"[{report_time_str}] ✅ RESOLUCIÓN: Incidente cerca de {loc_name} resuelto y retirado del mapa."
            st.session_state.incident_logs.insert(0, new_log)
        
        # B. Actualización de Posición/Tipo (Simula movimiento o cambio de gravedad)
        if st.session_state.dynamic_map_points and random.random() < 0.3:
             index_to_update = random.randint(0, len(st.session_state.dynamic_map_points) - 1)
             
             old_lat, old_lon, old_nivel, old_tipo, old_loc_name = st.session_state.dynamic_map_points[index_to_update]
             new_lat = old_lat + random.uniform(-0.0005, 0.0005)
             new_lon = old_lon + random.uniform(-0.0005, 0.0005)
             
             new_nivel = random.choice(['Baja', 'Media', 'Alta', 'Critica'])
             
             st.session_state.dynamic_map_points[index_to_update] = (new_lat, new_lon, new_nivel, old_tipo, old_loc_name)
             report_time_str = datetime.now().strftime('%H:%M:%S')
             new_log = f"[{report_time_str}] ALERTA LIVE: Movimiento en {old_loc_name}. Nivel: {new_nivel}."
             st.session_state.incident_logs.insert(0, new_log)


        # C. Adición (Simula nuevos reportes)
        if len(st.session_state.dynamic_map_points) < MAX_INCIDENTS:
            lat, lon, nivel, incident, location_name = generate_random_huancayo_point()
            
            # Add to map points
            new_map_point = (lat, lon, nivel, incident, location_name)
            st.session_state.dynamic_map_points.insert(0, new_map_point)
            
            # Add to log text
            report_time_str = (datetime.now() - timedelta(seconds=random.randint(1, 5))).strftime('%H:%M:%S')
            new_log = f"[{report_time_str}] 🆕 REGISTRO {nivel.upper()}: {incident} en {location_name}"
            st.session_state.incident_logs.insert(0, new_log)

        # 2. GESTIÓN DE LOGS TEXTUALES
        if len(st.session_state.incident_logs) > 10: 
            st.session_state.incident_logs.pop()
            
        st.session_state.last_log_time = CURRENT_TIME
        return True 
    return False

def generate_live_analysis():
    """Genera un análisis y recomendaciones ultradinámicas para el tab 🧠."""
    now = datetime.now()
    hour = now.hour
    
    analysis = []
    
    # 1. ANÁLISIS CLIMÁTICO (Simulado)
    weather_options = [
        ("Cielo despejado", "Baja", "Ideal para movilidad"),
        ("Nubosidad densa", "Media", "Baja visibilidad. Mayor precaución nocturna."),
        ("Lluvia ligera", "Alta", "Riesgo de accidentes vehiculares 75% más alto."),
        ("Tormenta eléctrica", "Crítica", "Alerta máxima. Refúgiese en zona segura."),
    ]
    
    # Simular cambio de clima basado en la hora (más lluvia/nubes en la mañana)
    if 6 <= hour < 12:
        current_weather = random.choice([weather_options[1], weather_options[1], weather_options[2], weather_options[0]])
    elif 18 <= hour < 22:
        current_weather = random.choice([weather_options[1], weather_options[2], weather_options[3], weather_options[0]])
    else:
        current_weather = random.choice(weather_options)

    analysis.append({
        "title": "ANÁLISIS CLIMÁTICO",
        "icon": "🌦️",
        "detail": f"Situación: {current_weather[0]}. Nivel de Impacto: {current_weather[1]}. Recomendación: {current_weather[2]}"
    })
    
    # 2. ANÁLISIS DE PUNTOS SEGUROS (Simulado)
    safe_status_options = [
        ("Comisaría El Tambo", "Operacional", "Protocolo Activo"),
        ("Hospital Regional", "Alta Demanda", "Evitar si no es emergencia médica."),
        ("Banco de la Nación", "Apertura en 2h", "Cerrado hasta las 8:00 AM"),
    ]
    
    # Simular estado de zona segura
    selected_safe_zone = random.choice(safe_status_options)
    
    analysis.append({
        "title": "ESTADO ZONA SEGURA",
        "icon": "🛡️",
        "detail": f"Punto: {selected_safe_zone[0]}. Estado: {selected_safe_zone[1]}. Nota: {selected_safe_zone[2]}"
    })

    # 3. ANÁLISIS DE RIESGO POR ZONA
    high_risk_locs = [loc for _, _, nivel, _, loc in st.session_state.dynamic_map_points if nivel in ['Alta', 'Critica']]
    if high_risk_locs:
         analysis.append({
            "title": "RIESGO PERIMETRAL",
            "icon": "🚨",
            "detail": f"Alto riesgo detectado cerca de: {high_risk_locs[0]}. Mantenga distancia o cambie de ruta."
        })
    else:
         analysis.append({
            "title": "RIESGO PERIMETRAL",
            "icon": "✅",
            "detail": "Nivel de riesgo bajo en el perímetro inmediato. Mantener conciencia situacional."
        })

    
    return analysis

def generate_whatsapp_url(number, lat, lon, user_name, medical_info):
    """Genera la URL de WhatsApp con un mensaje de emergencia URGENTE y CLARO."""
    if not number or len(number) < 5:
        return None 
        
    # --- MENSAJE DE EMERGENCIA MEJORADO ---
    message = (
        f"🚨 *EMERGENCIA - {user_name.upper()} NECESITA AYUDA INMEDIATA* 🚨\n\n"
        
        f"*👤 PERSONA EN RIESGO:* {user_name}\n"
        f"*📍 UBICACIÓN ACTUAL:* https://maps.google.com/?q={lat},{lon}\n"
        f"*📌 COORDENADAS:* {lat:.6f}, {lon:.6f}\n\n"
        
        f"*⚕️ INFORMACIÓN MÉDICA CRÍTICA:*\n"
        f"{medical_info}\n\n"
        
        "*⚠️ ESTA PERSONA ACTIVÓ LA ALERTA DE PÁNICO* \n"
        "*🚨 NECESITA ASISTENCIA URGENTE* \n"
        "*📞 CONTÁCTALA INMEDIATAMENTE* \n\n"
        
        "_Sistema de Alerta SECURE MAP HUANCAYO_"
    )
    
    message_encoded = urllib.parse.quote(message)
    number_cleaned = number.replace('+', '').replace(' ', '')
    url = f"https://wa.me/{number_cleaned}?text={message_encoded}" 
    return url

# Ejecutar la lógica de log dinámico en cada carga/interacción para sincronizar (20s)
log_new_incident()

# --- 7. PESTAÑAS (TABS) ---
tabs = st.tabs(["🏠", "🗺️", "📢", "🏪", "👤", "🧠"])

# ---------------- PESTAÑA INICIO ----------------
with tabs[0]:
    # Placeholder para el botón de pánico
    panic_placeholder = st.empty()
    
    # Placeholder para el contador y los mensajes
    message_placeholder = st.empty()

    gps_ready = True 
    
    # --- 1. BOTÓN DE PÁNICO BARRA TÁCTICA ---
    if panic_placeholder.button("🚨 ACTIVAR PROTOCOLO TÁCTICO", key="panic_main", type="primary", disabled=not gps_ready):
        
        # --- CONSTRUIR LISTA DE CONTACTOS VÁLIDOS ---
        contacts_to_alert = []
        if st.session_state.contact_1 and len(st.session_state.contact_1) > 5:
            contacts_to_alert.append(st.session_state.contact_1)
        if st.session_state.contact_2 and len(st.session_state.contact_2) > 5:
            contacts_to_alert.append(st.session_state.contact_2)
        if st.session_state.contact_authority and len(st.session_state.contact_authority) > 5:
            contacts_to_alert.append(st.session_state.contact_authority)

        # --- VERIFICAR SI HAY CONTACTOS ---
        if not contacts_to_alert:
            message_placeholder.error("¡No hay contactos de emergencia! Ve a PERFIL para agregarlos.")
            
        else:
            # --- INICIO: LÓGICA DE ENVÍO INMEDIATO (SIN SLEEP) ---
            try:
                st.session_state.last_alert_time = time.time()
                
                # 1. Visual Siren Feedback (Reemplaza los globos)
                message_placeholder.markdown('<div class="siren-alert">🚨 ¡ALERTA TÁCTICA ACTIVADA! 🚨</div>', unsafe_allow_html=True)
                
                # --- OBTENER DATOS PARA MENSAJES ---
                lat = st.session_state.location['lat']
                lon = st.session_state.location['lon']
                user_name = st.session_state.user_name
                medical_info = st.session_state.medical_info
                
                # 2. Renderizar Enlaces Inmediatamente
                with st.expander("🔗 ENLACES DE EMERGENCIA GENERADOS (Abrir en WhatsApp)", expanded=True):
                    st.success("Presiona los botones a continuación para enviar el mensaje de emergencia pre-escrito con tu ubicación.")
                    
                    url_1 = generate_whatsapp_url(st.session_state.contact_1, lat, lon, user_name, medical_info)
                    if url_1 and st.session_state.contact_1 in contacts_to_alert:
                        st.link_button(f"🔴 ENVIAR A CONTACTO 1: {st.session_state.contact_1}", url_1, use_container_width=True, type="primary")

                    url_2 = generate_whatsapp_url(st.session_state.contact_2, lat, lon, user_name, medical_info)
                    if url_2 and st.session_state.contact_2 in contacts_to_alert:
                        st.link_button(f"🟡 ENVIAR A CONTACTO 2: {st.session_state.contact_2}", url_2, use_container_width=True, type="secondary")

                    url_3 = generate_whatsapp_url(st.session_state.contact_authority, lat, lon, user_name, medical_info)
                    if url_3 and st.session_state.contact_authority in contacts_to_alert:
                        st.link_button(f"🚔 ENVIAR A AUTORIDAD/EMERGENCIA: {st.session_state.contact_authority}", url_3, use_container_width=True, type="secondary")
                
            except Exception as e:
                message_placeholder.error(f"Error al preparar envío: {e}")
            # --- FIN: LÓGICA DE ENVÍO INMEDIATO ---

    # --- 2. LIVE FEED DE INCIDENTES (Inmediatamente después del botón) ---
    st.markdown('<div class="dynamic-log-title">⚠️ REGISTRO DE INCIDENTES (LIVE FEED)</div>', unsafe_allow_html=True)
    st.caption(f"Actualización del mapa cada {MIN_INTERVAL_SECONDS} segundos. Último log: {datetime.now().strftime('%H:%M:%S')}")
    st.markdown('<div class="dynamic-log-container">', unsafe_allow_html=True)
    for log in st.session_state.incident_logs:
        st.markdown(f'<div class="dynamic-log-item"><strong>ALERTA</strong> - {log}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # --- 3. HUD METRICS (Al final del Home) ---
    st.markdown(f'<div class="gps-status-ready">📡 GPS CONECTADO | ESTADO: FIJO UTP</div>', unsafe_allow_html=True)

    high_risk_count = sum(1 for _, _, nivel, _, _ in st.session_state.dynamic_map_points if nivel in ['Alta', 'Critica'])
    incident_count = len(st.session_state.dynamic_map_points)
    risk_level = "CRÍTICO" if high_risk_count > 5 else "ALTO" if high_risk_count > 2 else "MODERADO"

    col1, col2, col3 = st.columns(3)
    with col1: st.markdown(f'<div class="metric-card">📊<br><strong>{incident_count}</strong><br>Incidentes Activos</div>', unsafe_allow_html=True)
    with col2: st.markdown(f'<div class="metric-card">🛡️<br><strong>{len(safe_locations)}</strong><br>Zonas Seguras</div>', unsafe_allow_html=True)
    with col3: st.markdown(f'<div class="metric-card">⚠️<br><strong>{risk_level}</strong><br>Riesgo Local</div>', unsafe_allow_html=True)


# ---------------- PESTAÑA MAPA ----------------
with tabs[1]:
    st.title("🗺️ MAPA DE SEGURIDAD (LIVE)")
    
    # Centrar el mapa en la ubicación del usuario (UTP)
    map_center = [st.session_state.location['lat'], st.session_state.location['lon']]
    zoom = 15

    show_heatmap = st.checkbox("Ver Mapa de Calor", value=True)
    show_safe_zones = st.checkbox("Ver Puntos Seguros", value=True)
    
    m = folium.Map(location=map_center, zoom_start=zoom, tiles="CartoDB dark_matter")
    
    # Marcador del Usuario (Ubicación Fija)
    folium.Marker(
        [st.session_state.location['lat'], st.session_state.location['lon']],
        popup="¡TÚ ESTÁS AQUÍ! (UTP)",
        icon=folium.Icon(color="blue", icon="person", prefix='fa')
    ).add_to(m)

    # Marcadores de Riesgo DINÁMICOS y Heatmap
    if show_heatmap:
        heat_data = [[lat, lon, 1.0 if nivel=='Critica' else 0.8 if nivel=='Alta' else 0.5 if nivel=='Media' else 0.2] for lat, lon, nivel, _, _ in st.session_state.dynamic_map_points]
        HeatMap(heat_data, radius=18, blur=10).add_to(m)
    
    # Puntos individuales
    for lat, lon, nivel, tipo, location_name in st.session_state.dynamic_map_points:
        color = "darkred" if nivel=="Critica" else "red" if nivel=="Alta" else "orange" if nivel=="Media" else "yellow"
        folium.CircleMarker(
            [lat, lon], 
            radius=6 if nivel=="Critica" else 5, 
            popup=f"⚠️ {tipo} ({nivel}) - {location_name}", 
            color=color, 
            fill=True, 
            fill_color=color, 
            fill_opacity=0.9
        ).add_to(m)
    
    # Zonas Seguras
    if show_safe_zones:
        for lat, lon, nombre, horario in safe_locations:
            folium.Marker([lat, lon], popup=f"🏪 {nombre} ({horario})", icon=folium.Icon(color="green", icon="shield", prefix='fa')).add_to(m)
    
    st_folium(m, width=360, height=400)
    st.caption("Puntos en el mapa aumentan/disminuyen y cambian de posición simulando incidentes reales.")

# ---------------- PESTAÑA REPORTAR ----------------
with tabs[2]:
    st.title("📢 REPORTAR INCIDENTE")
    
    st.info("Tu ubicación de reporte es la coordenada GPS fija UTP.")
    
    with st.form("report_form"):
        tipo_incidente = st.selectbox("Tipo de Incidente", ["Robo","Acoso","Persona Sospechosa","Asalto","Accidente","Otro"])
        
        ubicacion_default = f"GPS UTP: {st.session_state.location['lat']:.5f}, {st.session_state.location['lon']:.5f}"
        
        ubicacion = st.text_input("Ubicación aproximada (automática)", ubicacion_default, disabled=True)
        descripcion = st.text_area("Descripción del incidente", "Describa lo que sucedió...")
        
        submitted = st.form_submit_button("📤 ENVIAR REPORTE")
        if submitted:
            report_time_str = datetime.now().strftime('%H:%M:%S')
            new_log = f"[{report_time_str}] TU REPORTE: {tipo_incidente} en Zona UTP (PENDIENTE)"
            st.session_state.incident_logs.insert(0, new_log)
            
            st.success("Reporte enviado. Gracias por tu colaboración.")

# ---------------- PESTAÑA ZONAS ----------------
with tabs[3]:
    st.title("🏪 PUNTOS CLAVE SEGUROS")
    st.caption("Ubicaciones cercanas verificadas por el sistema.")
    for lat, lon, nombre, horario in safe_locations:
        st.markdown(f'<div class="safe-zone"><strong>{nombre}</strong><br>⏰ Horario: {horario}</div>', unsafe_allow_html=True)
        st.caption(f"Distancia estimada: {random.randint(100, 500)} metros.")


# ---------------- PESTAÑA PERFIL ----------------
with tabs[4]:
    st.title("👤 PERFIL DE USUARIO")
    st.info("Tu nombre e info médica se incluirán en las alertas de pánico. Usa el código de país (Ej: +51).")
    
    with st.form("profile_form"):
        nombre = st.text_input("Tu Nombre", st.session_state.user_name) 
        
        st.subheader("Contactos de Emergencia")
        st.caption("Añade el número con el código de país (Ej: +51999888777).")
        contact_1 = st.text_input("Contacto 1 (Principal)", st.session_state.contact_1)
        contact_2 = st.text_input("Contacto 2 (Opcional)", st.session_state.contact_2)
        contact_authority = st.text_input("Autoridad (Policía, Bomberos, etc. Opcional)", st.session_state.contact_authority)

        st.subheader("Información Médica")
        medical_info = st.text_area("Condiciones Médicas (Alergias, Tipo de Sangre, etc.)", st.session_state.medical_info)
        
        if st.form_submit_button("💾 GUARDAR PERFIL"):
            st.session_state.user_name = nombre
            st.session_state.contact_1 = contact_1
            st.session_state.contact_2 = contact_2
            st.session_state.contact_authority = contact_authority
            st.session_state.medical_info = medical_info
            st.success("Perfil actualizado correctamente")

# ---------------- PESTAÑA ANÁLISIS PREDICTIVO (LIVE 1 SEGUNDO) ----------------
with tabs[5]:
    st.title("🧠 ANÁLISIS PREDICTIVO (LIVE)")
    
    # --- LÓGICA DE ACTUALIZACIÓN DE 1 SEGUNDO ---
    CURRENT_TIME = time.time()
    
    # Forzar la actualización del contenido del análisis en cada ciclo
    analysis_data = generate_live_analysis()
    
    st.caption(f"Última Transmisión Táctica: {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
    
    for item in analysis_data:
        st.markdown(
            f'<div class="analysis-item">{item["icon"]} <strong>{item["title"]}</strong>{item["detail"]}</div>', 
            unsafe_allow_html=True
        )

# --- 8. ACTUALIZACIÓN SIMPLIFICADA ---
# Solo actualizar cuando sea necesario, sin bucles infinitos

current_time = time.time()

# Actualizar incidentes cada 20 segundos
if current_time - st.session_state.last_log_time > MIN_INTERVAL_SECONDS:
    log_new_incident()

# Actualizar análisis cada 1 segundo si está en esa pestaña
if st.session_state.current_tab == "🧠":
    if current_time - st.session_state.analysis_last_update > 1:
        st.session_state.analysis_last_update = current_time