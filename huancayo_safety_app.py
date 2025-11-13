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
import json

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="SECURE MAP HUANCAYO",
    page_icon="🚨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 2. COMPONENTE JAVASCRIPT PARA GPS Y HORA REAL ---
def gps_component():
    """Componente JavaScript para obtener GPS y hora real"""
    html_code = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Secure Map Huancayo - GPS</title>
        <style>
            body { 
                margin: 0; 
                padding: 20px; 
                font-family: Arial, sans-serif; 
                background: #0a0a0f;
                color: white;
            }
            .status { 
                padding: 15px; 
                border-radius: 10px; 
                margin: 10px 0; 
                text-align: center;
                font-weight: bold;
            }
            .success { background: #00b894; }
            .warning { background: #fdcb6e; color: black; }
            .error { background: #d63031; }
            button { 
                background: #00A693; 
                color: white; 
                border: none; 
                padding: 15px 30px; 
                border-radius: 25px; 
                font-size: 16px; 
                cursor: pointer;
                margin: 10px;
                width: 100%;
            }
            button:hover { background: #00E4C9; }
        </style>
    </head>
    <body>
        <div id="status"></div>
        <button onclick="getLocation()">📍 OBTENER MI UBICACIÓN Y HORA ACTUAL</button>
        
        <script>
        function updateStatus(message, type) {
            const status = document.getElementById('status');
            status.innerHTML = message;
            status.className = 'status ' + type;
        }
        
        function getLocation() {
            updateStatus('🕐 Solicitando permisos de ubicación y hora...', 'warning');
            
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    function(position) {
                        const lat = position.coords.latitude;
                        const lon = position.coords.longitude;
                        const acc = position.coords.accuracy;
                        const timestamp = new Date().toISOString();
                        const localTime = new Date().toLocaleString();
                        
                        // Enviar datos a Streamlit
                        window.parent.postMessage({
                            type: 'streamlit:setComponentValue',
                            value: JSON.stringify({
                                lat: lat,
                                lon: lon,
                                accuracy: acc,
                                timestamp: timestamp,
                                localTime: localTime,
                                success: true
                            })
                        }, '*');
                        
                        updateStatus('✅ Ubicación y hora obtenidas correctamente!', 'success');
                    },
                    function(error) {
                        let errorMessage = '❌ Error al obtener ubicación: ';
                        switch(error.code) {
                            case error.PERMISSION_DENIED:
                                errorMessage += 'Permiso denegado por el usuario';
                                break;
                            case error.POSITION_UNAVAILABLE:
                                errorMessage += 'Ubicación no disponible';
                                break;
                            case error.TIMEOUT:
                                errorMessage += 'Tiempo de espera agotado';
                                break;
                            default:
                                errorMessage += 'Error desconocido';
                        }
                        
                        window.parent.postMessage({
                            type: 'streamlit:setComponentValue',
                            value: JSON.stringify({
                                error: true,
                                message: errorMessage
                            })
                        }, '*');
                        
                        updateStatus(errorMessage, 'error');
                    },
                    {
                        enableHighAccuracy: true,
                        timeout: 15000,
                        maximumAge: 0
                    }
                );
            } else {
                const errorMsg = '❌ Geolocalización no soportada por este navegador';
                updateStatus(errorMsg, 'error');
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    value: JSON.stringify({
                        error: true,
                        message: errorMsg
                    })
                }, '*');
            }
        }
        
        // Solicitar automáticamente al cargar
        setTimeout(getLocation, 1000);
        </script>
    </body>
    </html>
    """
    return html_code

# --- 3. DATOS BASE Y CALLES REALES DE HUANCAYO ---
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
    (-12.021, -75.236, 'Comisaría El Tambo', '24/7'),
    (-12.025, -75.230, 'Hospital Regional', '24/7'),
    (-12.019, -75.238, 'Banco de la Nación', '8 AM - 6 PM'),
]

# --- 4. ESTILOS CSS MEJORADOS ---
st.markdown("""
<style>
    /* Importar fuente moderna */
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&display=swap');
    
    /* ESTILOS GENERALES MEJORADOS */
    .stApp {
        background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 50%, #16213e 100%);
        color: #ffffff;
        font-family: 'Share Tech Mono', monospace;
        max-width: 390px;
        min-height: 844px;
        margin: 10px auto;
        padding: 0 !important; 
        border: 1px solid #333;
        border-radius: 20px;
        box-shadow: 0 0 30px rgba(0,0,0,0.8);
        overflow: hidden; 
        position: relative;
    }
    
    /* HEADER PERSONALIZADO CON NOMBRE DEL PROYECTO */
    .main-header {
        background: linear-gradient(90deg, #ff0000, #ff6b6b, #ff0000);
        padding: 20px 0;
        text-align: center;
        margin-bottom: 15px;
        border-bottom: 3px solid #39ff14;
        animation: header-glow 2s infinite alternate;
    }
    
    @keyframes header-glow {
        0% { box-shadow: 0 0 20px #ff0000; }
        100% { box-shadow: 0 0 40px #ff6b6b; }
    }
    
    .app-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 1.8rem !important;
        font-weight: 900;
        color: white;
        text-shadow: 0 0 10px #39ff14, 0 0 20px #39ff14;
        margin: 0;
        padding: 0;
        letter-spacing: 1px;
    }
    
    /* BOTÓN DE PÁNICO MEJORADO */
    .panic-button-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 25px 0;
        padding: 0 15px;
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(45deg, #ff0000, #ff6b6b, #ff0000);
        color: white;
        border: none;
        border-radius: 50px;
        width: 100%;
        height: 80px;
        font-size: 1.4rem;
        font-weight: bold;
        font-family: 'Orbitron', sans-serif;
        margin: 0 auto;
        display: block;
        animation: panic-pulse 1.5s infinite;
        box-shadow: 0 0 30px rgba(255, 0, 0, 0.6);
        transition: all 0.3s ease;
        text-shadow: 0 0 10px white;
    }
    
    @keyframes panic-pulse {
        0% { transform: scale(1); box-shadow: 0 0 30px rgba(255, 0, 0, 0.6); }
        50% { transform: scale(1.05); box-shadow: 0 0 50px rgba(255, 0, 0, 0.9); }
        100% { transform: scale(1); box-shadow: 0 0 30px rgba(255, 0, 0, 0.6); }
    }
    
    .stButton > button[kind="primary"]:hover {
        transform: scale(1.08);
        background: linear-gradient(45deg, #ff0000, #ff4444, #ff0000);
        animation: none;
    }
    
    /* PESTAÑAS MEJORADAS */
    .stTabs [data-testid="stTabs"] {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 5px;
        margin: 10px 0;
    }
    
    .stTabs [data-testid="stTabs"] button {
        font-size: 16px !important;
        padding: 12px 8px !important;
        border-radius: 12px !important;
        transition: all 0.3s ease;
        border: 2px solid #00FFFF !important;
        color: #00FFFF !important;
        background: rgba(0, 255, 255, 0.1) !important;
        flex-grow: 1;
        margin: 0 3px;
        font-weight: bold;
    }
    
    .stTabs [data-testid="stTabs"] button:hover {
        background: rgba(0, 255, 255, 0.3) !important;
        transform: translateY(-2px);
    }
    
    .stTabs [data-testid="stTabs"] button[aria-selected="true"] {
        color: #0a0a0f !important;
        background: linear-gradient(45deg, #00FFFF, #00E4C9) !important;
        font-weight: bold;
        box-shadow: 0 0 15px #00FFFF;
    }
    
    /* CONTENEDORES MEJORADOS */
    .dynamic-log-container {
        max-height: 250px;
        overflow-y: auto;
        border: 1px solid #005f5f;
        padding: 10px;
        border-radius: 12px;
        margin-bottom: 20px;
        background: rgba(13, 27, 42, 0.8);
    }
    
    .dynamic-log-title {
        color: #00f0ff;
        font-size: 16px;
        font-weight: bold;
        margin-bottom: 10px;
        text-align: center;
    }
    
    .dynamic-log-item {
        background: rgba(255, 255, 255, 0.1);
        padding: 10px;
        border-radius: 8px;
        color: #ffffff;
        font-size: 13px;
        border-left: 4px solid #ff00ff;
        margin-bottom: 8px;
        backdrop-filter: blur(10px);
    }
    
    .metric-card {
        padding: 12px;
        border-radius: 12px;
        background: rgba(255, 255, 255, 0.1);
        text-align: center;
        border: 1px solid rgba(57, 255, 20, 0.4);
        font-size: 12px;
        color: #ffffff;
        backdrop-filter: blur(10px);
    }
    
    .analysis-item {
        background: rgba(17, 45, 60, 0.8);
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 12px;
        border-left: 5px solid #39ff14;
        color: #ffffff;
        font-size: 14px;
        backdrop-filter: blur(5px);
    }
    
    /* ESTADOS GPS */
    .gps-status-ready {
        background: linear-gradient(45deg, #00b894, #55efc4);
        color: #2d3436;
        padding: 12px;
        border-radius: 10px;
        text-align: center;
        margin: 10px 0;
        font-weight: bold;
        border: 2px solid #39ff14;
    }
    
    .gps-status-waiting {
        background: linear-gradient(45deg, #fdcb6e, #ffeaa7);
        color: #2d3436;
        padding: 12px;
        border-radius: 10px;
        text-align: center;
        margin: 10px 0;
        font-weight: bold;
        border: 2px solid #fdcb6e;
    }
    
    /* ALERTA DE SIRENA MEJORADA */
    .siren-alert {
        padding: 25px;
        margin: 20px 0;
        text-align: center;
        font-size: 1.8rem;
        font-weight: bold;
        color: white;
        border-radius: 15px;
        animation: siren-flash 0.5s infinite alternate;
        font-family: 'Orbitron', sans-serif;
        text-shadow: 0 0 10px white;
        border: 3px solid #ff0000;
    }
    
    @keyframes siren-flash {
        0% { 
            background-color: #ff0000; 
            box-shadow: 0 0 30px #ff0000; 
        }
        50% { 
            background-color: #0000ff; 
            box-shadow: 0 0 30px #0000ff; 
        }
        100% { 
            background-color: #ff0000; 
            box-shadow: 0 0 30px #ff0000; 
        }
    }
    
    /* OCULTAR ELEMENTOS NO DESEADOS */
    footer { visibility: hidden; }
    .stDeployButton { display: none; }
    #MainMenu { visibility: hidden; }
    
    /* Contenedor principal de Streamlit */
    div[data-testid="stAppViewContainer"] {
        padding: 0 1rem 1rem 1rem !important;
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
        f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 SECURE MAP HUANCAYO INICIADO",
        f"[{datetime.now().strftime('%H:%M:%S')}] 📍 Esperando acceso a GPS..."
    ]
if 'last_log_time' not in st.session_state:
    st.session_state.last_log_time = time.time()

if 'dynamic_map_points' not in st.session_state:
    st.session_state.dynamic_map_points = []

if 'analysis_last_update' not in st.session_state:
    st.session_state.analysis_last_update = time.time()

# --- 6. FUNCIONES PRINCIPALES ---
def get_random_location_name():
    return random.choice(HUANCAYO_STREETS)

def generate_random_huancayo_point():
    # Generar puntos alrededor del centro de Huancayo
    center_lat = -12.022
    center_lon = -75.233
    random_lat = center_lat + random.uniform(-0.03, 0.03)
    random_lon = center_lon + random.uniform(-0.03, 0.03)
    nivel = random.choice(['Baja', 'Media', 'Alta', 'Critica'])
    incident_type, _ = random.choice(INCIDENT_TEMPLATES)
    location_name = get_random_location_name()
    return (random_lat, random_lon, nivel, incident_type, location_name)

def log_new_incident():
    CURRENT_TIME = time.time()
    MIN_INTERVAL_SECONDS = 20
    MAX_INCIDENTS = 15
    MIN_INCIDENTS = 3

    if CURRENT_TIME > st.session_state.last_log_time + MIN_INTERVAL_SECONDS:
        # Lógica de simulación de incidentes
        if len(st.session_state.dynamic_map_points) > MIN_INCIDENTS and random.random() < 0.3:
            index_to_remove = random.randint(0, len(st.session_state.dynamic_map_points) - 1)
            _, _, _, _, loc_name = st.session_state.dynamic_map_points.pop(index_to_remove)
            report_time_str = datetime.now().strftime('%H:%M:%S')
            new_log = f"[{report_time_str}] ✅ RESOLUCIÓN: Incidente cerca de {loc_name} resuelto"
            st.session_state.incident_logs.insert(0, new_log)
        
        if st.session_state.dynamic_map_points and random.random() < 0.4:
            index_to_update = random.randint(0, len(st.session_state.dynamic_map_points) - 1)
            old_lat, old_lon, old_nivel, old_tipo, old_loc_name = st.session_state.dynamic_map_points[index_to_update]
            new_lat = old_lat + random.uniform(-0.001, 0.001)
            new_lon = old_lon + random.uniform(-0.001, 0.001)
            new_nivel = random.choice(['Baja', 'Media', 'Alta', 'Critica'])
            st.session_state.dynamic_map_points[index_to_update] = (new_lat, new_lon, new_nivel, old_tipo, old_loc_name)

        if len(st.session_state.dynamic_map_points) < MAX_INCIDENTS:
            lat, lon, nivel, incident, location_name = generate_random_huancayo_point()
            st.session_state.dynamic_map_points.insert(0, (lat, lon, nivel, incident, location_name))
            report_time_str = (datetime.now() - timedelta(seconds=random.randint(1, 5))).strftime('%H:%M:%S')
            new_log = f"[{report_time_str}] 🆕 REGISTRO {nivel.upper()}: {incident} en {location_name}"
            st.session_state.incident_logs.insert(0, new_log)

        if len(st.session_state.incident_logs) > 8:
            st.session_state.incident_logs.pop()
            
        st.session_state.last_log_time = CURRENT_TIME
        return True
    return False

def generate_live_analysis():
    now = datetime.now()
    hour = now.hour
    
    analysis = []
    
    # Análisis basado en hora actual
    if 18 <= hour < 24 or 0 <= hour < 6:
        analysis.append({
            "title": "ANÁLISIS NOCTURNO",
            "icon": "🌙",
            "detail": f"Hora: {hour}:00. Riesgo incrementado 65%. Evitar calles solitarias."
        })
    else:
        analysis.append({
            "title": "ANÁLISIS DIURNO",
            "icon": "☀️",
            "detail": f"Hora: {hour}:00. Condiciones normales. Mantener precauciones básicas."
        })
    
    # Análisis de incidentes activos
    high_risk_count = sum(1 for _, _, nivel, _, _ in st.session_state.dynamic_map_points if nivel in ['Alta', 'Critica'])
    if high_risk_count > 0:
        analysis.append({
            "title": "ALERTAS ACTIVAS",
            "icon": "🚨",
            "detail": f"{high_risk_count} zonas de alto riesgo identificadas. Navegar con precaución."
        })
    
    return analysis

def generate_whatsapp_url(number, lat, lon, user_name, medical_info, local_time):
    if not number or len(number) < 5:
        return None 
        
    message = (
        f"🚨 *EMERGENCIA - {user_name.upper()} NECESITA AYUDA INMEDIATA* 🚨\n\n"
        
        f"*👤 PERSONA EN RIESGO:* {user_name}\n"
        f"*📍 UBICACIÓN EXACTA (GPS):* https://maps.google.com/?q={lat},{lon}\n"
        f"*📌 COORDENADAS:* {lat:.6f}, {lon:.6f}\n"
        f"*🕒 HORA EXACTA:* {local_time}\n\n"
        
        f"*⚕️ INFORMACIÓN MÉDICA:*\n"
        f"{medical_info}\n\n"
        
        "*⚠️ ALERTA DE PÁNICO ACTIVADA - ASISTENCIA URGENTE REQUERIDA* \n"
        "*🚨 PROCEDER A LA UBICACIÓN INMEDIATAMENTE* \n\n"
        
        "_Sistema de Alerta SECURE MAP HUANCAYO - GPS EN VIVO_"
    )
    
    message_encoded = urllib.parse.quote(message)
    number_cleaned = number.replace('+', '').replace(' ', '')
    return f"https://wa.me/{number_cleaned}?text={message_encoded}"

def cancel_alert():
    st.session_state.panic_active = False
    st.session_state.last_alert_time = None

# --- 7. COMPONENTE GPS AUTOMÁTICO ---
def auto_request_gps():
    """Solicita automáticamente la ubicación GPS"""
    if not st.session_state.gps_attempted:
        st.session_state.gps_attempted = True
        gps_html = gps_component()
        components.html(gps_html, height=300)
        
        # Input para recibir datos del GPS
        gps_data = st.text_input("Datos GPS", key="gps_data_input", label_visibility="collapsed")
        
        if gps_data:
            try:
                data = json.loads(gps_data)
                if data.get('success'):
                    st.session_state.gps_location = {
                        'lat': data['lat'],
                        'lon': data['lon'],
                        'accuracy': data.get('accuracy', 0),
                        'timestamp': data.get('timestamp'),
                        'localTime': data.get('localTime', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    }
                    st.session_state.incident_logs.insert(0, 
                        f"[{datetime.now().strftime('%H:%M:%S')}] ✅ GPS ACTIVO: Ubicación obtenida"
                    )
                    st.rerun()
                elif data.get('error'):
                    st.session_state.incident_logs.insert(0, 
                        f"[{datetime.now().strftime('%H:%M:%S')}] ❌ GPS: {data.get('message', 'Error desconocido')}"
                    )
            except Exception as e:
                st.session_state.incident_logs.insert(0, 
                    f"[{datetime.now().strftime('%H:%M:%S')}] ❌ GPS: Error procesando datos"
                )

# --- 8. INTERFAZ PRINCIPAL ---

# HEADER CON NOMBRE DEL PROYECTO
st.markdown("""
<div class="main-header">
    <h1 class="app-title">🚨 SECURE MAP HUANCAYO</h1>
</div>
""", unsafe_allow_html=True)

# SOLICITUD AUTOMÁTICA DE GPS
auto_request_gps()

# PESTAÑAS MEJORADAS
tabs = st.tabs(["🏠 INICIO", "🗺️ MAPA", "📢 REPORTAR", "🏪 ZONAS", "👤 PERFIL", "🧠 ANÁLISIS"])

# ---------------- PESTAÑA INICIO ----------------
with tabs[0]:
    # Estado GPS
    if st.session_state.gps_location:
        local_time = st.session_state.gps_location.get('localTime', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        st.markdown(f'''
        <div class="gps-status-ready">
            📍 GPS ACTIVO | 🕒 {local_time}<br>
            <small>Lat: {st.session_state.gps_location["lat"]:.4f} | Lon: {st.session_state.gps_location["lon"]:.4f}</small>
        </div>
        ''', unsafe_allow_html=True)
        current_lat = st.session_state.gps_location['lat']
        current_lon = st.session_state.gps_location['lon']
    else:
        st.markdown('<div class="gps-status-waiting">📍 SOLICITANDO ACCESO A GPS Y HORA...</div>', unsafe_allow_html=True)
        # Usar centro de Huancayo como fallback
        current_lat = -12.022
        current_lon = -75.233

    # BOTÓN DE PÁNICO MEJORADO
    panic_placeholder = st.empty()
    message_placeholder = st.empty()

    if panic_placeholder.button("🚨 ACTIVAR ALERTA TÁCTICA", key="panic_main", type="primary"):
        contacts_to_alert = []
        if st.session_state.contact_1 and len(st.session_state.contact_1) > 5:
            contacts_to_alert.append(st.session_state.contact_1)
        if st.session_state.contact_2 and len(st.session_state.contact_2) > 5:
            contacts_to_alert.append(st.session_state.contact_2)
        if st.session_state.contact_authority and len(st.session_state.contact_authority) > 5:
            contacts_to_alert.append(st.session_state.contact_authority)

        if not contacts_to_alert:
            message_placeholder.error("¡Agrega contactos de emergencia en PERFIL!")
        else:
            try:
                st.session_state.last_alert_time = time.time()
                message_placeholder.markdown('<div class="siren-alert">🚨 ¡ALERTA TÁCTICA ACTIVADA! 🚨</div>', unsafe_allow_html=True)
                
                local_time_display = st.session_state.gps_location.get('localTime', datetime.now().strftime('%Y-%m-%d %H:%M:%S')) if st.session_state.gps_location else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                with st.expander("🔗 ENLACES DE EMERGENCIA - UBICACIÓN EXACTA", expanded=True):
                    st.warning("Los contactos recibirán tu ubicación GPS exacta y hora actual")
                    
                    url_1 = generate_whatsapp_url(st.session_state.contact_1, current_lat, current_lon, st.session_state.user_name, st.session_state.medical_info, local_time_display)
                    if url_1:
                        st.link_button(f"🔴 CONTACTO 1", url_1, use_container_width=True)

                    url_2 = generate_whatsapp_url(st.session_state.contact_2, current_lat, current_lon, st.session_state.user_name, st.session_state.medical_info, local_time_display)
                    if url_2:
                        st.link_button(f"🟡 CONTACTO 2", url_2, use_container_width=True)

                    url_3 = generate_whatsapp_url(st.session_state.contact_authority, current_lat, current_lon, st.session_state.user_name, st.session_state.medical_info, local_time_display)
                    if url_3:
                        st.link_button(f"🚔 AUTORIDADES", url_3, use_container_width=True)
                    
                    if st.button("✅ CANCELAR ALERTA", type="secondary", use_container_width=True):
                        cancel_alert()
                        st.rerun()
                
            except Exception as e:
                message_placeholder.error(f"Error: {e}")

    # LIVE FEED
    st.markdown('<div class="dynamic-log-title">📡 ACTIVIDAD EN TIEMPO REAL</div>', unsafe_allow_html=True)
    st.markdown('<div class="dynamic-log-container">', unsafe_allow_html=True)
    for log in st.session_state.incident_logs:
        st.markdown(f'<div class="dynamic-log-item">{log}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # MÉTRICAS
    high_risk_count = sum(1 for _, _, nivel, _, _ in st.session_state.dynamic_map_points if nivel in ['Alta', 'Critica'])
    incident_count = len(st.session_state.dynamic_map_points)
    risk_level = "CRÍTICO" if high_risk_count > 3 else "ALTO" if high_risk_count > 1 else "MODERADO"

    col1, col2, col3 = st.columns(3)
    with col1: 
        st.markdown(f'<div class="metric-card">📊<br><strong>{incident_count}</strong><br>Incidentes</div>', unsafe_allow_html=True)
    with col2: 
        st.markdown(f'<div class="metric-card">🛡️<br><strong>{len(safe_locations)}</strong><br>Zonas Seguras</div>', unsafe_allow_html=True)
    with col3: 
        st.markdown(f'<div class="metric-card">⚠️<br><strong>{risk_level}</strong><br>Riesgo</div>', unsafe_allow_html=True)

# ---------------- PESTAÑA MAPA ----------------
with tabs[1]:
    st.title("🗺️ MAPA DE SEGURIDAD")
    
    map_center = [current_lat, current_lon]
    
    show_heatmap = st.checkbox("Mapa de Calor", value=True)
    show_safe_zones = st.checkbox("Zonas Seguras", value=True)
    
    m = folium.Map(location=map_center, zoom_start=15, tiles="CartoDB dark_matter")
    
    # Marcador del usuario
    user_popup = "¡TÚ ESTÁS AQUÍ! (GPS ACTIVO)" if st.session_state.gps_location else "¡TÚ ESTÁS AQUÍ! (CENTRO HUANCAYO)"
    folium.Marker(
        map_center,
        popup=user_popup,
        icon=folium.Icon(color="blue", icon="user", prefix='fa')
    ).add_to(m)

    # Heatmap
    if show_heatmap and st.session_state.dynamic_map_points:
        heat_data = [[lat, lon, 1.0 if nivel=='Critica' else 0.8 if nivel=='Alta' else 0.5 if nivel=='Media' else 0.2] 
                    for lat, lon, nivel, _, _ in st.session_state.dynamic_map_points]
        HeatMap(heat_data, radius=20, blur=15).add_to(m)
    
    # Incidentes
    for lat, lon, nivel, tipo, location_name in st.session_state.dynamic_map_points:
        color = "darkred" if nivel=="Critica" else "red" if nivel=="Alta" else "orange" if nivel=="Media" else "yellow"
        folium.CircleMarker(
            [lat, lon], 
            radius=8 if nivel=="Critica" else 6, 
            popup=f"⚠️ {tipo} ({nivel})", 
            color=color, 
            fill=True, 
            fill_color=color
        ).add_to(m)
    
    # Zonas seguras
    if show_safe_zones:
        for lat, lon, nombre, horario in safe_locations:
            folium.Marker([lat, lon], popup=f"🏪 {nombre}", 
                         icon=folium.Icon(color="green", icon="shield", prefix='fa')).add_to(m)
    
    st_folium(m, width=360, height=400)

# ---------------- PESTAÑAS RESTANTES ----------------
with tabs[2]:
    st.title("📢 REPORTAR INCIDENTE")
    with st.form("report_form"):
        tipo_incidente = st.selectbox("Tipo", ["Robo","Acoso","Persona Sospechosa","Asalto","Accidente","Otro"])
        ubicacion = st.text_input("Ubicación", f"GPS: {current_lat:.4f}, {current_lon:.4f}", disabled=True)
        descripcion = st.text_area("Descripción")
        if st.form_submit_button("📤 ENVIAR REPORTE"):
            report_time = datetime.now().strftime('%H:%M:%S')
            st.session_state.incident_logs.insert(0, f"[{report_time}] 📋 TU REPORTE: {tipo_incidente}")
            st.success("Reporte enviado correctamente")

with tabs[3]:
    st.title("🏪 ZONAS SEGURAS")
    for lat, lon, nombre, horario in safe_locations:
        with st.container():
            st.markdown(f"**{nombre}**")
            st.caption(f"⏰ {horario} | 📍 {random.randint(200, 800)}m")
            st.divider()

with tabs[4]:
    st.title("👤 PERFIL")
    with st.form("profile_form"):
        st.session_state.user_name = st.text_input("Nombre", st.session_state.user_name) 
        st.subheader("Contactos Emergencia")
        st.session_state.contact_1 = st.text_input("Contacto 1", st.session_state.contact_1)
        st.session_state.contact_2 = st.text_input("Contacto 2", st.session_state.contact_2)
        st.session_state.contact_authority = st.text_input("Autoridades", st.session_state.contact_authority)
        st.subheader("Info Médica")
        st.session_state.medical_info = st.text_area("Información", st.session_state.medical_info)
        if st.form_submit_button("💾 GUARDAR"):
            st.success("Perfil actualizado")

with tabs[5]:
    st.title("🧠 ANÁLISIS PREDICTIVO")
    analysis_data = generate_live_analysis()
    for item in analysis_data:
        st.markdown(
            f'<div class="analysis-item">{item["icon"]} <strong>{item["title"]}</strong>{item["detail"]}</div>', 
            unsafe_allow_html=True
        )

# --- ACTUALIZACIÓN AUTOMÁTICA ---
log_new_incident()

if time.time() - st.session_state.analysis_last_update > 10:
    st.session_state.analysis_last_update = time.time()
    st.rerun()