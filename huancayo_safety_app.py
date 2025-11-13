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

# --- COORDENADAS DE LA UTP HUANCAYO (FALLBACK) ---
UTP_LAT = -12.022398351778946
UTP_LON = -75.23382979742267

# --- 2. DATOS BASE Y CALLES REALES DE HUANCAYO ---
HUANCAYO_STREETS = [
    "Av. Mariscal Castilla", "Av. Huancavelica", "Calle Real", "Jr. Piura", 
    "Av. Circunvalación", "Paradero UTP", "Parque de la Identidad Huanca", 
    "Av. Giráldez", "Plaza de Toros", "Cruce Av. 9 de Diciembre"
]

INCIDENT_TEMPLATES = [
    ("Robo de celular", "Av. Circunvalación - Paradero UTP"),
    ("Acoso verbal", "Cruce Av. Real con Jr. Piura"),
    ("Riña/Pelea", "Cerca a la puerta de la UTP"),
    ("Venta de droga", "Parque La Esperanza"),
    ("Sospechoso siguiendo", "Espalda de la universidad"),
    ("Accidente vehicular menor", "Av. Mariscal Castilla"),
]

safe_locations = [
    (UTP_LAT + 0.001, UTP_LON + 0.003, 'Comisaría El Tambo', '24/7'),
    (UTP_LAT - 0.003, UTP_LON - 0.001, 'Hospital Regional', '24/7'),
    (UTP_LAT + 0.002, UTP_LON - 0.003, 'Banco de la Nación', '8 AM - 6 PM'),
]

# --- 3. COMPONENTE JAVASCRIPT PARA GPS REAL ---
def gps_component():
    """Componente JavaScript para obtener GPS real"""
    html_code = """
    <script>
    function getGPSCooridnates() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                function(position) {
                    const lat = position.coords.latitude;
                    const lon = position.coords.longitude;
                    const acc = position.coords.accuracy;
                    
                    // Enviar a Streamlit
                    window.parent.postMessage({
                        type: 'streamlit:setComponentValue',
                        value: {
                            lat: lat,
                            lon: lon,
                            accuracy: acc,
                            timestamp: new Date().toISOString()
                        }
                    }, '*');
                },
                function(error) {
                    console.error('Error GPS:', error);
                    window.parent.postMessage({
                        type: 'streamlit:setComponentValue',
                        value: {
                            error: true,
                            message: 'No se pudo obtener la ubicación'
                        }
                    }, '*');
                },
                {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 0
                }
            );
        } else {
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: {
                    error: true,
                    message: 'GPS no soportado'
                }
            }, '*');
        }
    }
    
    // Ejecutar inmediatamente
    getGPSCooridnates();
    </script>
    """
    return html_code

# --- 4. ESTILOS CSS (MANTENIENDO EL DISEÑO ORIGINAL) ---
st.markdown("""
<style>
    /* Importar fuente Sci-Fi/Tech */
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');

    /* Keyframes para la animación de pulso (Neon Green) */
    @keyframes pulse {
        0% {
            transform: scale(1);
            box-shadow: 0 0 15px #39ff14, 0 0 25px #39ff14;
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

    /* Estilo base de la App */
    .stApp {
        background-color: #0a0a0f;
        color: #ffffff;
        font-family: 'Share Tech Mono', monospace;
        max-width: 390px;
        min-height: 844px;
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

    /* --- BOTÓN DE PÁNICO BARRA TÁCTICA --- */
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
        margin: 0 2px;
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
        color: #00f0ff;
        font-size: 16px;
        font-weight: bold;
        margin-bottom: 8px;
    }
    .dynamic-log-item {
        background: #0d1b2a;
        padding: 8px;
        border-radius: 4px;
        color: #ffffff;
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

    /* --- Análisis Predictivo --- */
    .analysis-item {
        background: #112d3c;
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 10px;
        border-left: 4px solid #39ff14; 
        color: #ffffff;
        font-size: 14px;
    }
    .analysis-item strong {
        color: #00f0ff;
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
        color: #ffffff;
    }
    
    /* Estado GPS */
    .gps-status-ready {
        background: #00b894;
        color: white;
        padding: 10px;
        border-radius: 8px;
        text-align: center;
        margin: 10px 0;
        font-weight: bold;
    }
    .gps-status-waiting {
        background: #fdcb6e;
        color: black;
        padding: 10px;
        border-radius: 8px;
        text-align: center;
        margin: 10px 0;
        font-weight: bold;
    }

</style>
""", unsafe_allow_html=True)

# --- 5. INICIALIZACIÓN DE ESTADOS ---
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
if 'gps_location' not in st.session_state:
    st.session_state.gps_location = None
if 'gps_attempted' not in st.session_state:
    st.session_state.gps_attempted = False

if 'incident_logs' not in st.session_state:
    st.session_state.incident_logs = [
        f"[{datetime.now().strftime('%H:%M:%S')}] SISTEMA: Secure Map Huancayo iniciado"
    ]
if 'last_log_time' not in st.session_state:
    st.session_state.last_log_time = time.time()

if 'dynamic_map_points' not in st.session_state:
    st.session_state.dynamic_map_points = [
        (UTP_LAT + 0.001, UTP_LON - 0.001, 'Alta', 'Robo de celular', "Av. Mariscal Castilla"),
        (UTP_LAT - 0.001, UTP_LON + 0.002, 'Media', 'Acoso verbal', "Jr. Piura"),
    ]

if 'analysis_last_update' not in st.session_state:
    st.session_state.analysis_last_update = time.time()

# --- 6. FUNCIONES PRINCIPALES ---
def get_random_location_name():
    return random.choice(HUANCAYO_STREETS)

def generate_random_huancayo_point():
    random_lat = UTP_LAT + random.uniform(-0.03, 0.03)
    random_lon = UTP_LON + random.uniform(-0.03, 0.03)
    nivel = random.choice(['Baja', 'Media', 'Alta', 'Critica'])
    incident_type, _ = random.choice(INCIDENT_TEMPLATES)
    location_name = get_random_location_name()
    return (random_lat, random_lon, nivel, incident_type, location_name)

def log_new_incident():
    CURRENT_TIME = time.time()
    MIN_INTERVAL_SECONDS = 20
    MAX_INCIDENTS = 20
    MIN_INCIDENTS = 5

    if CURRENT_TIME > st.session_state.last_log_time + MIN_INTERVAL_SECONDS:
        # Lógica de simulación de incidentes (se mantiene igual)
        if len(st.session_state.dynamic_map_points) > MIN_INCIDENTS and random.random() < 0.3:
            index_to_remove = random.randint(0, len(st.session_state.dynamic_map_points) - 1)
            _, _, _, _, loc_name = st.session_state.dynamic_map_points.pop(index_to_remove)
            report_time_str = datetime.now().strftime('%H:%M:%S')
            new_log = f"[{report_time_str}] ✅ RESOLUCIÓN: Incidente cerca de {loc_name} resuelto"
            st.session_state.incident_logs.insert(0, new_log)
        
        if st.session_state.dynamic_map_points and random.random() < 0.3:
            index_to_update = random.randint(0, len(st.session_state.dynamic_map_points) - 1)
            old_lat, old_lon, old_nivel, old_tipo, old_loc_name = st.session_state.dynamic_map_points[index_to_update]
            new_lat = old_lat + random.uniform(-0.0005, 0.0005)
            new_lon = old_lon + random.uniform(-0.0005, 0.0005)
            new_nivel = random.choice(['Baja', 'Media', 'Alta', 'Critica'])
            st.session_state.dynamic_map_points[index_to_update] = (new_lat, new_lon, new_nivel, old_tipo, old_loc_name)

        if len(st.session_state.dynamic_map_points) < MAX_INCIDENTS:
            lat, lon, nivel, incident, location_name = generate_random_huancayo_point()
            st.session_state.dynamic_map_points.insert(0, (lat, lon, nivel, incident, location_name))
            report_time_str = (datetime.now() - timedelta(seconds=random.randint(1, 5))).strftime('%H:%M:%S')
            new_log = f"[{report_time_str}] 🆕 REGISTRO {nivel.upper()}: {incident} en {location_name}"
            st.session_state.incident_logs.insert(0, new_log)

        if len(st.session_state.incident_logs) > 10:
            st.session_state.incident_logs.pop()
            
        st.session_state.last_log_time = CURRENT_TIME
        return True
    return False

def generate_live_analysis():
    """Genera análisis en tiempo real"""
    now = datetime.now()
    hour = now.hour
    
    analysis = []
    
    # Análisis climático
    weather_options = [
        ("Cielo despejado", "Baja", "Ideal para movilidad"),
        ("Nubosidad densa", "Media", "Baja visibilidad. Mayor precaución nocturna."),
        ("Lluvia ligera", "Alta", "Riesgo de accidentes vehiculares 75% más alto."),
    ]
    
    current_weather = random.choice(weather_options)
    analysis.append({
        "title": "ANÁLISIS CLIMÁTICO",
        "icon": "🌦️",
        "detail": f"Situación: {current_weather[0]}. Nivel de Impacto: {current_weather[1]}. Recomendación: {current_weather[2]}"
    })
    
    # Análisis de riesgo
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
    """Genera URL de WhatsApp con ubicación REAL"""
    if not number or len(number) < 5:
        return None 
        
    message = (
        f"🚨 *EMERGENCIA - {user_name.upper()} NECESITA AYUDA INMEDIATA* 🚨\n\n"
        
        f"*👤 PERSONA EN RIESGO:* {user_name}\n"
        f"*📍 UBICACIÓN ACTUAL (GPS REAL):* https://maps.google.com/?q={lat},{lon}\n"
        f"*📌 COORDENADAS EXACTAS:* {lat:.6f}, {lon:.6f}\n"
        f"*🕒 HORA DEL INCIDENTE:* {datetime.now().strftime('%H:%M:%S')}\n\n"
        
        f"*⚕️ INFORMACIÓN MÉDICA CRÍTICA:*\n"
        f"{medical_info}\n\n"
        
        "*⚠️ ESTA PERSONA ACTIVÓ LA ALERTA DE PÁNICO* \n"
        "*🚨 NECESITA ASISTENCIA URGENTE* \n"
        "*📞 CONTÁCTALA INMEDIATAMENTE* \n\n"
        
        "_Sistema de Alerta SECURE MAP HUANCAYO - UBICACIÓN GPS EN VIVO_"
    )
    
    message_encoded = urllib.parse.quote(message)
    number_cleaned = number.replace('+', '').replace(' ', '')
    url = f"https://wa.me/{number_cleaned}?text={message_encoded}" 
    return url

def cancel_alert():
    st.session_state.panic_active = False
    st.session_state.last_alert_time = None

# --- 7. COMPONENTE GPS ---
def request_gps_location():
    """Solicita la ubicación GPS del usuario"""
    st.markdown("### 📍 OBTENIENDO UBICACIÓN GPS...")
    st.info("Por favor, permite el acceso a tu ubicación cuando el navegador lo solicite")
    
    # Componente JavaScript para GPS
    gps_html = gps_component()
    components.html(gps_html, height=0)
    
    # Input para recibir las coordenadas
    gps_data = st.text_input("Coordenadas GPS (automático)", key="gps_input", label_visibility="collapsed")
    
    if gps_data:
        try:
            import json
            data = json.loads(gps_data)
            if 'lat' in data and 'lon' in data:
                st.session_state.gps_location = {
                    'lat': data['lat'],
                    'lon': data['lon'],
                    'accuracy': data.get('accuracy', 0),
                    'timestamp': datetime.now()
                }
                st.session_state.gps_attempted = True
                st.success("✅ Ubicación GPS obtenida correctamente!")
                return True
        except:
            st.error("Error al procesar ubicación GPS")
    
    return False

# --- 8. PESTAÑAS PRINCIPALES (MANTENIENDO ESTRUCTURA ORIGINAL) ---
tabs = st.tabs(["🏠", "🗺️", "📢", "🏪", "👤", "🧠"])

# ---------------- PESTAÑA INICIO ----------------
with tabs[0]:
    # Estado GPS
    if not st.session_state.gps_attempted:
        st.markdown('<div class="gps-status-waiting">📍 ESPERANDO ACCESO A GPS</div>', unsafe_allow_html=True)
        if st.button("🎯 OBTENER MI UBICACIÓN ACTUAL"):
            if request_gps_location():
                st.rerun()
    else:
        if st.session_state.gps_location:
            st.markdown(f'<div class="gps-status-ready">📍 GPS ACTIVO | Lat: {st.session_state.gps_location["lat"]:.4f}, Lon: {st.session_state.gps_location["lon"]:.4f}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="gps-status-waiting">📍 GPS NO DISPONIBLE - Usando ubicación UTP</div>', unsafe_allow_html=True)

    # BOTÓN DE PÁNICO
    panic_placeholder = st.empty()
    message_placeholder = st.empty()

    # Usar ubicación GPS si está disponible, sino UTP
    current_lat = st.session_state.gps_location['lat'] if st.session_state.gps_location else UTP_LAT
    current_lon = st.session_state.gps_location['lon'] if st.session_state.gps_location else UTP_LON
    
    if panic_placeholder.button("🚨 ACTIVAR PROTOCOLO TÁCTICO", key="panic_main", type="primary"):
        contacts_to_alert = []
        if st.session_state.contact_1 and len(st.session_state.contact_1) > 5:
            contacts_to_alert.append(st.session_state.contact_1)
        if st.session_state.contact_2 and len(st.session_state.contact_2) > 5:
            contacts_to_alert.append(st.session_state.contact_2)
        if st.session_state.contact_authority and len(st.session_state.contact_authority) > 5:
            contacts_to_alert.append(st.session_state.contact_authority)

        if not contacts_to_alert:
            message_placeholder.error("¡No hay contactos de emergencia! Ve a PERFIL para agregarlos.")
        else:
            try:
                st.session_state.last_alert_time = time.time()
                message_placeholder.markdown('<div class="siren-alert">🚨 ¡ALERTA TÁCTICA ACTIVADA! 🚨</div>', unsafe_allow_html=True)
                
                with st.expander("🔗 ENLACES DE EMERGENCIA (UBICACIÓN REAL)", expanded=True):
                    st.success("Presiona los botones para enviar tu ubicación EXACTA por WhatsApp")
                    
                    url_1 = generate_whatsapp_url(st.session_state.contact_1, current_lat, current_lon, st.session_state.user_name, st.session_state.medical_info)
                    if url_1 and st.session_state.contact_1 in contacts_to_alert:
                        st.link_button(f"🔴 ENVIAR A CONTACTO 1", url_1, use_container_width=True)

                    url_2 = generate_whatsapp_url(st.session_state.contact_2, current_lat, current_lon, st.session_state.user_name, st.session_state.medical_info)
                    if url_2 and st.session_state.contact_2 in contacts_to_alert:
                        st.link_button(f"🟡 ENVIAR A CONTACTO 2", url_2, use_container_width=True)

                    url_3 = generate_whatsapp_url(st.session_state.contact_authority, current_lat, current_lon, st.session_state.user_name, st.session_state.medical_info)
                    if url_3 and st.session_state.contact_authority in contacts_to_alert:
                        st.link_button(f"🚔 ENVIAR A AUTORIDADES", url_3, use_container_width=True)
                    
                    # Botón cancelar
                    if st.button("✅ CANCELAR ALERTA", type="secondary", use_container_width=True):
                        cancel_alert()
                        st.rerun()
                
            except Exception as e:
                message_placeholder.error(f"Error: {e}")

    # LIVE FEED (se mantiene igual)
    st.markdown('<div class="dynamic-log-title">⚠️ REGISTRO DE INCIDENTES (LIVE FEED)</div>', unsafe_allow_html=True)
    st.caption(f"Actualización cada 20 segundos. Último: {datetime.now().strftime('%H:%M:%S')}")
    st.markdown('<div class="dynamic-log-container">', unsafe_allow_html=True)
    for log in st.session_state.incident_logs:
        st.markdown(f'<div class="dynamic-log-item">{log}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # HUD METRICS
    high_risk_count = sum(1 for _, _, nivel, _, _ in st.session_state.dynamic_map_points if nivel in ['Alta', 'Critica'])
    incident_count = len(st.session_state.dynamic_map_points)
    risk_level = "CRÍTICO" if high_risk_count > 5 else "ALTO" if high_risk_count > 2 else "MODERADO"

    col1, col2, col3 = st.columns(3)
    with col1: 
        st.markdown(f'<div class="metric-card">📊<br><strong>{incident_count}</strong><br>Incidentes Activos</div>', unsafe_allow_html=True)
    with col2: 
        st.markdown(f'<div class="metric-card">🛡️<br><strong>{len(safe_locations)}</strong><br>Zonas Seguras</div>', unsafe_allow_html=True)
    with col3: 
        st.markdown(f'<div class="metric-card">⚠️<br><strong>{risk_level}</strong><br>Riesgo Local</div>', unsafe_allow_html=True)

# ---------------- PESTAÑA MAPA ----------------
with tabs[1]:
    st.title("🗺️ MAPA DE SEGURIDAD (LIVE)")
    
    # Usar ubicación actual (GPS o UTP)
    map_center = [current_lat, current_lon]
    
    show_heatmap = st.checkbox("Ver Mapa de Calor", value=True)
    show_safe_zones = st.checkbox("Ver Puntos Seguros", value=True)
    
    m = folium.Map(location=map_center, zoom_start=15, tiles="CartoDB dark_matter")
    
    # Marcador del USUARIO (ubicación real)
    user_icon = folium.Icon(color="blue", icon="user", prefix='fa')
    if st.session_state.gps_location:
        user_popup = "¡TÚ ESTÁS AQUÍ! (GPS REAL)"
    else:
        user_popup = "¡TÚ ESTÁS AQUÍ! (UBICACIÓN UTP)"
    
    folium.Marker(
        map_center,
        popup=user_popup,
        icon=user_icon
    ).add_to(m)

    # Heatmap y puntos de incidentes (se mantiene igual)
    if show_heatmap:
        heat_data = [[lat, lon, 1.0 if nivel=='Critica' else 0.8 if nivel=='Alta' else 0.5 if nivel=='Media' else 0.2] 
                    for lat, lon, nivel, _, _ in st.session_state.dynamic_map_points]
        HeatMap(heat_data, radius=18, blur=10).add_to(m)
    
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
    
    if show_safe_zones:
        for lat, lon, nombre, horario in safe_locations:
            folium.Marker([lat, lon], popup=f"🏪 {nombre} ({horario})", 
                         icon=folium.Icon(color="green", icon="shield", prefix='fa')).add_to(m)
    
    st_folium(m, width=360, height=400)
    st.caption("Mapa muestra tu ubicación actual y incidentes en tiempo real")

# ---------------- PESTAÑAS RESTANTES (SE MANTIENEN IGUAL) ----------------
with tabs[2]:
    st.title("📢 REPORTAR INCIDENTE")
    st.info("Tu reporte ayudará a otros usuarios")
    with st.form("report_form"):
        tipo_incidente = st.selectbox("Tipo de Incidente", ["Robo","Acoso","Persona Sospechosa","Asalto","Accidente","Otro"])
        ubicacion_default = f"GPS: {current_lat:.5f}, {current_lon:.5f}" if st.session_state.gps_location else "UTP Huancayo"
        ubicacion = st.text_input("Ubicación", ubicacion_default, disabled=True)
        descripcion = st.text_area("Descripción del incidente")
        submitted = st.form_submit_button("📤 ENVIAR REPORTE")
        if submitted:
            report_time_str = datetime.now().strftime('%H:%M:%S')
            new_log = f"[{report_time_str}] TU REPORTE: {tipo_incidente} en {ubicacion} (PENDIENTE)"
            st.session_state.incident_logs.insert(0, new_log)
            st.success("Reporte enviado. Gracias por tu colaboración.")

with tabs[3]:
    st.title("🏪 PUNTOS CLAVE SEGUROS")
    st.caption("Ubicaciones seguras verificadas en Huancayo")
    for lat, lon, nombre, horario in safe_locations:
        st.markdown(f"**{nombre}**")
        st.caption(f"⏰ {horario} | 📍 Aprox. {random.randint(100, 500)}m")
        st.divider()

with tabs[4]:
    st.title("👤 PERFIL DE USUARIO")
    st.info("Tu información se incluye en las alertas de emergencia")
    with st.form("profile_form"):
        nombre = st.text_input("Tu Nombre", st.session_state.user_name) 
        st.subheader("Contactos de Emergencia")
        contact_1 = st.text_input("Contacto 1 (WhatsApp)", st.session_state.contact_1)
        contact_2 = st.text_input("Contacto 2 (WhatsApp)", st.session_state.contact_2)
        contact_authority = st.text_input("Autoridad (Policía, etc.)", st.session_state.contact_authority)
        st.subheader("Información Médica")
        medical_info = st.text_area("Condiciones Médicas", st.session_state.medical_info)
        if st.form_submit_button("💾 GUARDAR PERFIL"):
            st.session_state.user_name = nombre
            st.session_state.contact_1 = contact_1
            st.session_state.contact_2 = contact_2
            st.session_state.contact_authority = contact_authority
            st.session_state.medical_info = medical_info
            st.success("Perfil actualizado correctamente")

with tabs[5]:
    st.title("🧠 ANÁLISIS PREDICTIVO (LIVE)")
    analysis_data = generate_live_analysis()
    st.caption(f"Última actualización: {datetime.now().strftime('%H:%M:%S')}")
    for item in analysis_data:
        st.markdown(
            f'<div class="analysis-item">{item["icon"]} <strong>{item["title"]}</strong>{item["detail"]}</div>', 
            unsafe_allow_html=True
        )

# --- ACTUALIZACIÓN AUTOMÁTICA ---
log_new_incident()

# Actualizar análisis cada 5 segundos si está en esa pestaña
if time.time() - st.session_state.analysis_last_update > 5:
    st.session_state.analysis_last_update = time.time()
    st.rerun()