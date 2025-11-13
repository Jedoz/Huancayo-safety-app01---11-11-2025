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

# --- 1. CONFIGURACIÓN DE PÁGINA MEJORADA ---
st.set_page_config(
    page_title="SECURE MAP HUANCAYO",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- COORDENADAS DE LA UTP HUANCAYO (UBICACIÓN FIJA) ---
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

# --- 3. ESTILOS CSS MEJORADOS (SIN MARCOS DE CELULAR) ---
st.markdown("""
<style>
    /* Importar fuente moderna */
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&display=swap');
    
    /* ESTILOS GENERALES MEJORADOS */
    .stApp {
        background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 50%, #16213e 100%);
        color: #ffffff;
        font-family: 'Share Tech Mono', monospace;
        min-height: 100vh;
        margin: 0;
        padding: 0;
    }
    
    /* HEADER PERSONALIZADO */
    .main-header {
        background: linear-gradient(90deg, #ff0000, #ff6b6b, #ff0000);
        padding: 15px 0;
        text-align: center;
        margin-bottom: 20px;
        border-bottom: 3px solid #39ff14;
        animation: header-glow 2s infinite alternate;
    }
    
    @keyframes header-glow {
        0% { box-shadow: 0 0 20px #ff0000; }
        100% { box-shadow: 0 0 40px #ff6b6b; }
    }
    
    .app-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 2.5rem !important;
        font-weight: 900;
        color: white;
        text-shadow: 0 0 10px #39ff14, 0 0 20px #39ff14;
        margin: 0;
        padding: 0;
    }
    
    /* BOTÓN DE PÁNICO MEJORADO Y CENTRADO */
    .panic-button-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 30px 0;
        padding: 0 20px;
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(45deg, #ff0000, #ff6b6b, #ff0000);
        color: white;
        border: none;
        border-radius: 50px;
        width: 300px;
        height: 80px;
        font-size: 1.5rem;
        font-weight: bold;
        font-family: 'Orbitron', sans-serif;
        margin: 0 auto;
        display: block;
        animation: panic-pulse 1.5s infinite;
        box-shadow: 0 0 30px rgba(255, 0, 0, 0.5);
        transition: all 0.3s ease;
    }
    
    @keyframes panic-pulse {
        0% { transform: scale(1); box-shadow: 0 0 30px rgba(255, 0, 0, 0.5); }
        50% { transform: scale(1.05); box-shadow: 0 0 50px rgba(255, 0, 0, 0.8); }
        100% { transform: scale(1); box-shadow: 0 0 30px rgba(255, 0, 0, 0.5); }
    }
    
    .stButton > button[kind="primary"]:hover {
        transform: scale(1.1);
        background: linear-gradient(45deg, #ff0000, #ff4444, #ff0000);
        animation: none;
    }
    
    /* BOTÓN CANCELAR ALERTA */
    .stButton > button[kind="secondary"] {
        background: linear-gradient(45deg, #00b894, #55efc4);
        color: #2d3436;
        border: none;
        border-radius: 25px;
        width: 200px;
        height: 50px;
        font-size: 1.1rem;
        font-weight: bold;
        margin: 10px auto;
        display: block;
        transition: all 0.3s ease;
    }
    
    .stButton > button[kind="secondary"]:hover {
        transform: scale(1.05);
        background: linear-gradient(45deg, #00a085, #00b894);
    }
    
    /* CONTENEDOR RESPONSIVE */
    .responsive-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 0 20px;
    }
    
    /* TARJETAS MEJORADAS */
    .metric-card {
        background: rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 15px;
        text-align: center;
        border: 1px solid rgba(57, 255, 20, 0.3);
        backdrop-filter: blur(10px);
        margin: 5px;
    }
    
    .dynamic-log-item {
        background: rgba(13, 27, 42, 0.8);
        padding: 10px;
        border-radius: 8px;
        color: #ffffff;
        font-size: 14px;
        border-left: 4px solid #ff00ff;
        margin-bottom: 8px;
        backdrop-filter: blur(5px);
    }
    
    .analysis-item {
        background: rgba(17, 45, 60, 0.8);
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
        border-left: 5px solid #39ff14;
        color: #ffffff;
        backdrop-filter: blur(5px);
    }
    
    /* MAPA CON TAMAÑO FIJO */
    .folium-map {
        border-radius: 15px;
        border: 2px solid #39ff14;
        box-shadow: 0 0 20px rgba(57, 255, 20, 0.3);
    }
    
    /* OCULTAR ELEMENTOS NO DESEADOS */
    footer { visibility: hidden; }
    .stDeployButton { display: none; }
    
    /* ALERTA DE SIRENA */
    .siren-alert {
        padding: 25px;
        margin: 20px 0;
        text-align: center;
        font-size: 2rem;
        font-weight: bold;
        color: white;
        border-radius: 15px;
        animation: siren-flash 0.5s infinite alternate;
        font-family: 'Orbitron', sans-serif;
    }
    
    @keyframes siren-flash {
        0% { background-color: #ff0000; box-shadow: 0 0 30px #ff0000; }
        50% { background-color: #0000ff; box-shadow: 0 0 30px #0000ff; }
        100% { background-color: #ff0000; box-shadow: 0 0 30px #ff0000; }
    }
</style>
""", unsafe_allow_html=True)

# --- 4. INICIALIZACIÓN DE ESTADOS ---
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
        f"[{datetime.now().strftime('%H:%M:%S')}] SISTEMA: Secure Map Huancayo activado"
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
if 'map_key' not in st.session_state:
    st.session_state.map_key = str(time.time())  # Key único para el mapa

# Ubicación fija UTP
st.session_state.location = {"status": "success", "lat": UTP_LAT, "lon": UTP_LON}

# --- 5. FUNCIONES PRINCIPALES ---
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
        # Lógica de simulación de incidentes
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
        st.session_state.map_key = str(time.time())  # Actualizar key del mapa
        return True
    return False

def generate_whatsapp_url(number, lat, lon, user_name, medical_info):
    if not number or len(number) < 5:
        return None
        
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
    return f"https://wa.me/{number_cleaned}?text={message_encoded}"

def cancel_alert():
    st.session_state.panic_active = False
    st.session_state.last_alert_time = None
    st.success("✅ Alerta cancelada correctamente")

# --- 6. HEADER PERSONALIZADO ---
st.markdown("""
<div class="main-header">
    <h1 class="app-title">🚨 SECURE MAP HUANCAYO</h1>
</div>
""", unsafe_allow_html=True)

# --- 7. CONTENEDOR PRINCIPAL RESPONSIVE ---
with st.container():
    st.markdown('<div class="responsive-container">', unsafe_allow_html=True)
    
    # Ejecutar simulación de incidentes
    log_new_incident()
    
    # --- PESTAÑAS PRINCIPALES ---
    tabs = st.tabs(["🏠 INICIO", "🗺️ MAPA", "📢 REPORTAR", "🏪 ZONAS SEGURAS", "👤 PERFIL", "🧠 ANÁLISIS"])
    
    with tabs[0]:
        # --- BOTÓN DE PÁNICO CENTRADO ---
        st.markdown('<div class="panic-button-container">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚨 ACTIVAR ALERTA DE PÁNICO", key="panic_main", type="primary", use_container_width=True):
                st.session_state.panic_active = True
                st.session_state.last_alert_time = time.time()
                
                # Mostrar alerta inmediatamente
                st.markdown('<div class="siren-alert">🚨 ¡ALERTA ACTIVADA! 🚨</div>', unsafe_allow_html=True)
                
                # Mostrar enlaces de WhatsApp
                lat = st.session_state.location['lat']
                lon = st.session_state.location['lon']
                user_name = st.session_state.user_name
                medical_info = st.session_state.medical_info
                
                with st.expander("🔗 ENLACES DE EMERGENCIA", expanded=True):
                    st.warning("Presiona los botones para enviar alerta por WhatsApp")
                    
                    contacts_to_alert = []
                    if st.session_state.contact_1 and len(st.session_state.contact_1) > 5:
                        contacts_to_alert.append(st.session_state.contact_1)
                    if st.session_state.contact_2 and len(st.session_state.contact_2) > 5:
                        contacts_to_alert.append(st.session_state.contact_2)
                    if st.session_state.contact_authority and len(st.session_state.contact_authority) > 5:
                        contacts_to_alert.append(st.session_state.contact_authority)
                    
                    if contacts_to_alert:
                        url_1 = generate_whatsapp_url(st.session_state.contact_1, lat, lon, user_name, medical_info)
                        if url_1: st.link_button(f"📱 Contacto 1", url_1, use_container_width=True)
                        
                        url_2 = generate_whatsapp_url(st.session_state.contact_2, lat, lon, user_name, medical_info)
                        if url_2: st.link_button(f"📱 Contacto 2", url_2, use_container_width=True)
                        
                        url_3 = generate_whatsapp_url(st.session_state.contact_authority, lat, lon, user_name, medical_info)
                        if url_3: st.link_button(f"🚔 Autoridades", url_3, use_container_width=True)
                    
                    # BOTÓN CANCELAR ALERTA
                    if st.button("✅ CANCELAR ALERTA", type="secondary", use_container_width=True):
                        cancel_alert()
                        st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # --- LIVE FEED Y MÉTRICAS ---
        st.subheader("📡 LIVE FEED - ACTIVIDAD EN TIEMPO REAL")
        
        col1, col2, col3 = st.columns(3)
        high_risk_count = sum(1 for _, _, nivel, _, _ in st.session_state.dynamic_map_points if nivel in ['Alta', 'Critica'])
        incident_count = len(st.session_state.dynamic_map_points)
        
        with col1:
            st.markdown(f'<div class="metric-card">📊<br><strong>{incident_count}</strong><br>Incidentes Activos</div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-card">🛡️<br><strong>{len(safe_locations)}</strong><br>Zonas Seguras</div>', unsafe_allow_html=True)
        with col3:
            risk_level = "CRÍTICO" if high_risk_count > 5 else "ALTO" if high_risk_count > 2 else "MODERADO"
            st.markdown(f'<div class="metric-card">⚠️<br><strong>{risk_level}</strong><br>Riesgo Local</div>', unsafe_allow_html=True)
        
        # Logs de incidentes
        st.subheader("📋 REGISTRO DE ACTIVIDAD")
        for log in st.session_state.incident_logs[:8]:
            st.markdown(f'<div class="dynamic-log-item">{log}</div>', unsafe_allow_html=True)
    
    # --- PESTAÑA MAPA CORREGIDA ---
    with tabs[1]:
        st.subheader("🗺️ MAPA DE SEGURIDAD EN TIEMPO REAL")
        
        # Controles del mapa
        col1, col2 = st.columns(2)
        with col1:
            show_heatmap = st.checkbox("Mostrar Mapa de Calor", value=True)
        with col2:
            show_safe_zones = st.checkbox("Mostrar Zonas Seguras", value=True)
        
        # CREAR EL MAPA CON KEY ÚNICO
        map_center = [st.session_state.location['lat'], st.session_state.location['lon']]
        m = folium.Map(
            location=map_center, 
            zoom_start=15, 
            tiles="CartoDB dark_matter",
            width='100%', 
            height='100%'
        )
        
        # Marcador del usuario (posición fija UTP)
        folium.Marker(
            map_center,
            popup="""
                <div style="font-family: Arial; text-align: center;">
                    <strong>¡TÚ ESTÁS AQUÍ!</strong><br>
                    📍 UTP Huancayo<br>
                    🕒 Hora: """ + datetime.now().strftime('%H:%M:%S') + """<br>
                    🔒 Estado: Seguro
                </div>
            """,
            tooltip="Tu ubicación actual",
            icon=folium.Icon(color="blue", icon="user", prefix='fa')
        ).add_to(m)
        
        # Heatmap de incidentes
        if show_heatmap and st.session_state.dynamic_map_points:
            heat_data = []
            for lat, lon, nivel, _, _ in st.session_state.dynamic_map_points:
                intensity = 1.0 if nivel == 'Critica' else 0.8 if nivel == 'Alta' else 0.5 if nivel == 'Media' else 0.2
                heat_data.append([lat, lon, intensity])
            
            HeatMap(heat_data, radius=20, blur=15, gradient={
                0.2: 'blue',
                0.4: 'cyan',
                0.6: 'lime',
                0.8: 'yellow',
                1.0: 'red'
            }).add_to(m)
        
        # Puntos de incidentes individuales
        for lat, lon, nivel, tipo, location_name in st.session_state.dynamic_map_points:
            color = "darkred" if nivel == "Critica" else "red" if nivel == "Alta" else "orange" if nivel == "Media" else "yellow"
            
            folium.CircleMarker(
                [lat, lon],
                radius=10 if nivel == "Critica" else 8 if nivel == "Alta" else 6 if nivel == "Media" else 4,
                popup=f"""
                    <div style="font-family: Arial;">
                        <strong>⚠️ {tipo}</strong><br>
                        Nivel: <b>{nivel}</b><br>
                        Ubicación: {location_name}<br>
                        Hora: {datetime.now().strftime('%H:%M')}
                    </div>
                """,
                tooltip=f"{tipo} - {nivel}",
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.7,
                weight=2
            ).add_to(m)
        
        # Zonas seguras
        if show_safe_zones:
            for lat, lon, nombre, horario in safe_locations:
                folium.Marker(
                    [lat, lon],
                    popup=f"""
                        <div style="font-family: Arial; text-align: center;">
                            <strong>🏪 {nombre}</strong><br>
                            ⏰ {horario}<br>
                            📍 Zona Segura Verificada
                        </div>
                    """,
                    tooltip=f"Zona Segura: {nombre}",
                    icon=folium.Icon(color="green", icon="shield", prefix='fa')
                ).add_to(m)
        
        # MOSTRAR EL MAPA CON KEY ÚNICO PARA ACTUALIZACIÓN
        map_data = st_folium(
            m, 
            width=700, 
            height=500, 
            key=st.session_state.map_key  # KEY ÚNICO PARA ACTUALIZACIÓN
        )
        
        # Información del mapa
        st.caption(f"📍 **Ubicación central:** UTP Huancayo | 📊 **Incidentes activos:** {len(st.session_state.dynamic_map_points)} | 🕒 **Actualizado:** {datetime.now().strftime('%H:%M:%S')}")
    
    # --- OTRAS PESTAÑAS ---
    with tabs[2]:
        st.subheader("📢 REPORTAR INCIDENTE")
        with st.form("report_form"):
            tipo_incidente = st.selectbox("Tipo de Incidente", ["Robo","Acoso","Persona Sospechosa","Asalto","Accidente","Otro"])
            descripcion = st.text_area("Descripción detallada")
            if st.form_submit_button("📤 ENVIAR REPORTE"):
                report_time = datetime.now().strftime('%H:%M:%S')
                st.session_state.incident_logs.insert(0, f"[{report_time}] TU REPORTE: {tipo_incidente} (PENDIENTE)")
                st.success("✅ Reporte enviado correctamente")
    
    with tabs[3]:
        st.subheader("🏪 PUNTOS SEGUROS VERIFICADOS")
        for lat, lon, nombre, horario in safe_locations:
            with st.container():
                st.markdown(f"**{nombre}**")
                st.caption(f"⏰ {horario} | 📍 {random.randint(200, 800)}m de distancia")
                st.divider()
    
    with tabs[4]:
        st.subheader("👤 CONFIGURACIÓN DE PERFIL")
        with st.form("profile_form"):
            st.session_state.user_name = st.text_input("Nombre completo", st.session_state.user_name)
            st.session_state.contact_1 = st.text_input("Contacto 1 (WhatsApp)", st.session_state.contact_1)
            st.session_state.contact_2 = st.text_input("Contacto 2 (WhatsApp)", st.session_state.contact_2)
            st.session_state.contact_authority = st.text_input("Contacto de autoridades", st.session_state.contact_authority)
            st.session_state.medical_info = st.text_area("Información médica importante", st.session_state.medical_info)
            if st.form_submit_button("💾 GUARDAR CONFIGURACIÓN"):
                st.success("✅ Perfil actualizado correctamente")
    
    with tabs[5]:
        st.subheader("🧠 ANÁLISIS PREDICTIVO")
        st.info("🔍 Sistema de análisis en tiempo real activo")
        
        # Métricas en tiempo real
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Riesgo Actual", "MODERADO", "-2%")
        with col2:
            st.metric("Incidentes Activos", len(st.session_state.dynamic_map_points))
        with col3:
            st.metric("Tiempo Respuesta", "45s", "5s")
        
        # Análisis simulado
        st.markdown('<div class="analysis-item">🌦️ <strong>CONDICIONES ACTUALES</strong>Clima favorable. Visibilidad óptima para vigilancia.</div>', unsafe_allow_html=True)
        st.markdown('<div class="analysis-item">🛡️ <strong>ZONAS SEGURAS</strong>Todas las comisarías operativas. Hospital Regional con capacidad.</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- ACTUALIZACIÓN AUTOMÁTICA EN STREAMLIT CLOUD ---
if time.time() - st.session_state.last_log_time > 20:
    log_new_incident()
    st.rerun()  # Esto fuerza la actualización en Streamlit Cloud