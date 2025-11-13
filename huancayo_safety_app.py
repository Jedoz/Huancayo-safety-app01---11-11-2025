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
# Coordenadas reales proporcionadas: -12.022398351778946, -75.23382979742267
UTP_LAT = -12.022398351778946
UTP_LON = -75.23382979742267

# --- 2. DATOS BASE ---
# Plantillas para la simulación dinámica
INCIDENT_TEMPLATES = [
    ("Robo de celular", "Av. Circunvalación - Paradero UTP"),
    ("Acoso", "Cruce Av. Real con Jr. Piura"),
    ("Riña/Pelea", "Cerca a la puerta de la UTP"),
    ("Venta de droga", "Parque La Esperanza"),
    ("Sospechoso siguiendo", "Espalda de la universidad"),
]

safe_locations = [
    (UTP_LAT + 0.001, UTP_LON + 0.003, 'Comisaría El Tambo', '24/7'),
    (UTP_LAT - 0.003, UTP_LON - 0.001, 'Hospital Regional', '24/7'),
    (UTP_LAT + 0.002, UTP_LON - 0.003, 'Banco de la Nación', '8 AM - 6 PM'),
]

# --- 3. ESTILOS CSS (Sin cambios, manteniendo estética Cyberpunk) ---
st.markdown("""
<style>
    /* Importar fuente Sci-Fi/Tech */
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');

    /* Keyframes para la animación de pulso */
    @keyframes pulse {
        0% {
            transform: scale(1);
            box-shadow: 0 0 25px #ff00ff, 0 0 35px #ff00ff;
        }
        50% {
            transform: scale(1.05);
            box-shadow: 0 0 45px #ff00ff, 0 0 55px #ff00ff;
        }
        100% {
            transform: scale(1);
            box-shadow: 0 0 25px #ff00ff, 0 0 35px #ff00ff;
        }
    }

    /* Estilo base de la App (Simulación Móvil) */
    .stApp {
        background-color: #0a0a0f; /* Negro Cyberpunk */
        color: #ffffff;
        font-family: 'Share Tech Mono', monospace;
        max-width: 390px; /* Ancho de iPhone Pro */
        min-height: 844px; /* Altura mínima */
        margin: 10px auto;
        padding: 0 !important; /* Sin padding exterior */
        border: 1px solid #333;
        border-radius: 20px;
        box-shadow: 0 0 20px rgba(0,0,0,0.5);
        overflow: hidden; /* Para mantener los bordes redondeados */
    }
    
    /* Ocultar footer de Streamlit */
    footer {
        visibility: hidden;
    }
    
    /* Contenedor principal de Streamlit */
    div[data-testid="stAppViewContainer"] {
        padding: 0 1rem 1rem 1rem !important;
    }

    /* --- BOTÓN DE PÁNICO GIGANTE Y PULSANTE --- */
    .stButton > button[kind="primary"] {
        background: linear-gradient(145deg, #ff2d95, #e6007e);
        color: #ffffff;
        border-radius: 50%;
        width: 280px; 
        height: 280px; 
        font-size: 48px; 
        font-weight: bold;
        font-family: 'Share Tech Mono', monospace;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 25px auto;
        border: 4px solid #ffffff;
        text-shadow: 0 0 10px #ffffff;
        
        /* Animación de Pulso */
        animation: pulse 1.5s infinite ease-in-out;
        transition: transform 0.2s;
    }
    .stButton > button[kind="primary"]:hover {
        transform: scale(1.1) !important;
        background: linear-gradient(145deg, #ff55aa, #ff2d95);
    }
    .stButton > button[kind="primary"]:active {
        transform: scale(1.05) !important;
    }
    
    /* --- BOTÓN DE PÁNICO DESACTIVADO --- */
    .stButton > button[kind="primary"]:disabled {
        background: #555;
        color: #999;
        border-color: #888;
        box-shadow: none;
        animation: none; /* Sin pulso cuando está desactivado */
    }

    /* --- Tarjetas de Métricas (HUD) --- */
    .metric-card {
        background: #112d3c;
        padding: 12px;
        border-radius: 8px;
        text-align: center;
        font-size: 14px;
        margin: 5px 0;
        color: #00f0ff; /* Neón Cian */
        border: 1px solid #00f0ff;
        box-shadow: 0 0 10px #00f0ff;
        font-weight: bold;
    }
    .metric-card strong {
        font-size: 20px;
        color: #ffffff;
        display: block;
    }

    /* --- Alerta de Zona (HUD Warning) --- */
    .warning-alert {
        background: #ff2d95; /* Neón Magenta */
        color: #0a0a0f; 
        padding: 14px;
        border-radius: 8px;
        margin: 10px 0;
        font-size: 16px;
        font-weight: bold;
        text-align: center;
        border: 2px solid #ffffff;
        box-shadow: 0 0 15px #ff2d95;
    }
    
    /* --- Notificación Dinámica (Nuevo) --- */
    .dynamic-log-container {
        max-height: 150px; /* Altura máxima para scroll */
        overflow-y: auto;
        border: 1px solid #005f5f;
        padding: 5px;
        border-radius: 8px;
    }
    .dynamic-log-item {
        background: #0d1b2a;
        padding: 8px;
        border-radius: 4px;
        color: #00f0ff;
        font-size: 13px;
        border-left: 3px solid #ff00ff;
        margin-bottom: 5px;
    }
    .dynamic-log-item strong {
        color: #ffffff;
    }

    /* --- Zona Segura (HUD Safe) --- */
    .safe-zone {
        background: #005f5f; /* Verde/Cian oscuro */
        padding: 12px;
        border-radius: 8px;
        margin: 8px 0;
        color: #ffffff;
        font-weight: bold;
        border: 1px solid #00f0ff;
        box-shadow: 0 0 10px #00f0ff;
    }
    
    /* --- GPS Status (Nuevo) --- */
    .gps-status-ready {
        background: #005f5f;
        color: #00f0ff;
        padding: 8px;
        border-radius: 4px;
        font-size: 14px;
        text-align: center;
        font-weight: bold;
        border: 1px solid #00f0ff;
    }
    
    /* --- Estilo de Pestañas (Tabs) MEJORADO (SOLO ICONOS) --- */
    [data-baseweb="tab-list"] {
        background: #111;
        justify-content: space-around; 
        width: 100%;
    }
    [data-baseweb="tab"] {
        font-family: 'Share Tech Mono', monospace;
        font-size: 26px; 
        padding: 10px 0; 
        background: #111;
        color: #888;
    }
    [data-baseweb="tab"][aria-selected="true"] {
        background: #112d3c;
        color: #00f0ff;
        border-bottom: 3px solid #00f0ff;
    }
    
    /* Botones normales y de envío (no-pánico) */
    .stButton > button:not([kind="primary"]):not([key="retry_gps"]):not([key="request_gps"]) {
        background: #00f0ff;
        color: #0a0a0f;
        font-family: 'Share Tech Mono', monospace;
        font-weight: bold;
        width: 100%; 
    }
    
    /* Botones de enlace */
    .stLinkButton {
        margin-bottom: 10px;
    }
    .stLinkButton a {
        background-color: #00f0ff;
        color: #0a0a0f;
        font-family: 'Share Tech Mono', monospace;
        font-weight: bold;
        padding: 15px;
        border-radius: 8px;
        text-decoration: none;
        display: block;
        text-align: center;
        font-size: 16px;
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
    # Inicializar con algunos puntos base para que no esté vacío al inicio
    st.session_state.dynamic_map_points = [
        (UTP_LAT + 0.001, UTP_LON - 0.001, 'Alta', 'Robo en paradero'),
        (UTP_LAT - 0.001, UTP_LON + 0.002, 'Media', 'Acoso verbal'),
    ]

# LÓGICA DE UBICACIÓN FIJA 
st.session_state.location = {
    "status": "success",  
    "lat": UTP_LAT,       
    "lon": UTP_LON        
}

# --- 5. FUNCIONES PRINCIPALES ---

def generate_random_huancayo_point():
    """Genera una coordenada aleatoria en la zona de Huancayo (radio de 3 km alrededor de UTP)."""
    # Generar un punto dentro de un radio de aprox. 3 km (0.03 grados) de la UTP
    random_lat = UTP_LAT + random.uniform(-0.03, 0.03)
    random_lon = UTP_LON + random.uniform(-0.03, 0.03)
    
    nivel = random.choice(['Baja', 'Media', 'Alta'])
    incident_type, _ = random.choice(INCIDENT_TEMPLATES)
    
    return (random_lat, random_lon, nivel, incident_type)

def log_new_incident():
    """Agrega un nuevo incidente al registro de texto y al mapa si ha pasado el tiempo."""
    CURRENT_TIME = time.time()
    MIN_INTERVAL_SECONDS = 60 

    if CURRENT_TIME > st.session_state.last_log_time + MIN_INTERVAL_SECONDS:
        # Generar punto de mapa dinámico
        lat, lon, nivel, incident = generate_random_huancayo_point()
        
        # 1. ACTUALIZAR MAPA
        new_map_point = (lat, lon, nivel, incident)
        st.session_state.dynamic_map_points.insert(0, new_map_point)
        # Mantener solo los 20 puntos más recientes en el mapa
        if len(st.session_state.dynamic_map_points) > 20:
            st.session_state.dynamic_map_points.pop()
        
        # 2. ACTUALIZAR LOG TEXTUAL
        location_name = f"L/L {lat:.4f}, {lon:.4f}"
        report_time_dt = datetime.now() - timedelta(seconds=random.randint(1, 5))
        report_time_str = report_time_dt.strftime('%H:%M:%S')
        
        new_log = f"[{report_time_str}] REGISTRO {nivel.upper()}: {incident} cerca de {location_name}"
        st.session_state.incident_logs.insert(0, new_log)
        
        # Mantener solo los 5 logs más recientes
        if len(st.session_state.incident_logs) > 5:
            st.session_state.incident_logs.pop()
            
        st.session_state.last_log_time = CURRENT_TIME
        
        return True 
    return False

def generate_dynamic_recommendations():
    """Genera un análisis y recomendaciones dinámicas basadas en la hora y el día."""
    now = datetime.now()
    hour = now.hour
    day = now.weekday() # Lunes es 0, Domingo es 6
    
    recommendations = []
    
    # Análisis de Franja Horaria
    if 6 <= hour < 9:
        recommendations.append("🔺 ALERTA MAÑANA (06:00-09:00): Riesgo de hurto en paraderos por alta afluencia.")
    elif 18 <= hour < 22:
        recommendations.append("🚨 ALERTA NOCTURNA (18:00-22:00): Zonas perimetrales UTP tienen 85% más robos.")
    elif hour >= 22 or hour < 6:
        recommendations.append("👁️ MÁXIMA VIGILANCIA: Calles despejadas aumentan riesgo de asalto focalizado.")
    else:
        recommendations.append("✅ SITUACIÓN ESTABLE: Nivel de riesgo promedio. Mantente atento.")
        
    # Análisis Semanal
    if day >= 4: # Viernes, Sábado, Domingo
        recommendations.append("⚠️ FIN DE SEMANA: Mayor actividad nocturna, precaución extra en áreas de ocio.")
    
    # Análisis Mensual (Días de Pago)
    if now.day in [14, 15, 29, 30]: 
        recommendations.append("💰 PELIGRO DÍA DE PAGO: Evita mostrar efectivo. Riesgo de seguimiento 90% mayor.")
        
    # Consejos Tácticos
    recommendations.append("🛡️ CONSEJO: Desplaza tu ruta 100m de los puntos marcados en el Mapa Dinámico.")
    
    return recommendations

def generate_whatsapp_url(number, lat, lon, user_name, medical_info):
    """Genera la URL de WhatsApp con un mensaje de emergencia estilo militar."""
    if not number or len(number) < 5:
        return None 
        
    user_name_upper = user_name.upper()
    
    # --- MENSAJE DE ALERTA ESTILO MILITAR/URGENTE ---
    message = (
        f"🔴 *ALARMA | CÓDIGO ROJO - ACTIVACIÓN PÁNICO ({user_name_upper})* 🔴\n\n"
        f"COMANDO: REQUERIMIENTO DE APOYO INMEDIATO. SITUACIÓN DE RIESGO CONFIRMADA.\n"
        f"USUARIO: {user_name_upper}.\n\n"
        
        "✅ *COORDENADAS TÁCTICAS (Ubicación Actual):*\n"
        f"MAPA TÁCTICO: https://maps.google.com/?q={lat},{lon}\n"
        f"L/L (Latitud/Longitud): {lat}, {lon}\n\n"
        
        "⚕️ *INFO MÉDICA VITAL:*\n"
        f"DETALLES: {medical_info}\n\n"
        
        "*PRIORIDAD MÁXIMA. PROCEDER A LA ZONA. REPITO: EMERGENICA REAL.*"
    )
    
    message_encoded = urllib.parse.quote(message)
    number_cleaned = number.replace('+', '').replace(' ', '')
    url = f"https://wa.me/{number_cleaned}?text={message_encoded}" 
    return url

# Ejecutar la lógica de log dinámico en cada carga/interacción
log_new_incident()

# --- 7. PESTAÑAS (TABS) ---
tabs = st.tabs(["🏠", "🗺️", "📢", "🏪", "👤", "🧠"])

# ---------------- PESTAÑA INICIO ----------------
with tabs[0]:
    st.title("🛡️ SECURE MAP HUANCAYO")
    
    # --- INFORMACIÓN DE UBICACIÓN ---
    lat_fixed = st.session_state.location["lat"]
    lon_fixed = st.session_state.location["lon"]

    # Indicador de estado GPS
    st.markdown(f'<div class="gps-status-ready">📡 GPS CONECTADO | ESTADO: FIJO UTP</div>', unsafe_allow_html=True)

    # MOSTRAR LOGS DINÁMICOS
    st.subheader("⚠️ REGISTRO DE INCIDENTES (LIVE FEED)")
    st.caption(f"Última actualización: {datetime.now().strftime('%H:%M:%S')}")
    st.markdown('<div class="dynamic-log-container">', unsafe_allow_html=True)
    for log in st.session_state.incident_logs:
        st.markdown(f'<div class="dynamic-log-item"><strong>ALERTA</strong> - {log}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


    # Zona de riesgo (fija)
    # Usar un análisis dinámico basado en los puntos del mapa para el nivel de riesgo de la zona fija.
    high_risk_count = sum(1 for _, _, nivel, _ in st.session_state.dynamic_map_points if nivel == 'Alta')
    risk_level = "CRÍTICO" if high_risk_count > 5 else "ALTO" if high_risk_count > 2 else "MODERADO"

    st.markdown(f'<div class="warning-alert">¡ALERTA! RIESGO PERIMETRAL: {risk_level} ({high_risk_count} incidentes cercanos)</div>', unsafe_allow_html=True)
    
    # Placeholder para el contador y los botones de envío
    placeholder = st.empty()

    gps_ready = True 

    # Botón de pánico GIGANTE
    if placeholder.button("🚨 PÁNICO 🚨", key="panic_main", type="primary", disabled=not gps_ready):
        
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
            # Redibujar el botón de pánico desactivado para que el error sea visible
            st.button("🚨 PÁNICO 🚨", key="panic_main_disabled", type="primary", disabled=True)
            placeholder.error("¡No hay contactos de emergencia! Ve a PERFIL para agregarlos.")
        else:
            # --- INICIO: LÓGICA DE 3 SEGUNDOS ---
            try:
                st.session_state.last_alert_time = time.time()
                
                with placeholder.container(): 
                    st.warning("Activación de Protocolo de Alerta Táctica... 3 segundos")
                    time.sleep(1)
                    st.warning("Activación de Protocolo de Alerta Táctica... 2 segundos")
                    time.sleep(1)
                    st.warning("Activación de Protocolo de Alerta Táctica... 1 segundo")
                    time.sleep(1)
                
                # --- OBTENER DATOS PARA MENSAJES ---
                lat = st.session_state.location['lat']
                lon = st.session_state.location['lon']
                user_name = st.session_state.user_name
                medical_info = st.session_state.medical_info
                
                # --- LÓGICA DE ENVÍO MEJORADA (Generar enlaces) ---
                with placeholder.container():
                    st.success("¡ALERTA TÁCTICA LISTA! PRESIONA PARA ABRIR EN WHATSAPP:")
                    
                    # Generar URL para Contacto 1 (Principal)
                    url_1 = generate_whatsapp_url(st.session_state.contact_1, lat, lon, user_name, medical_info)
                    if url_1 and st.session_state.contact_1 in contacts_to_alert:
                        st.link_button(f"🔴 ENVIAR A CONTACTO 1: {st.session_state.contact_1}", url_1, use_container_width=True, type="primary")

                    # Generar URL para Contacto 2 (Secundario)
                    url_2 = generate_whatsapp_url(st.session_state.contact_2, lat, lon, user_name, medical_info)
                    if url_2 and st.session_state.contact_2 in contacts_to_alert:
                        st.link_button(f"🟡 ENVIAR A CONTACTO 2: {st.session_state.contact_2}", url_2, use_container_width=True, type="secondary")

                    # Generar URL para Autoridad
                    url_3 = generate_whatsapp_url(st.session_state.contact_authority, lat, lon, user_name, medical_info)
                    if url_3 and st.session_state.contact_authority in contacts_to_alert:
                        st.link_button(f"🚔 ENVIAR A AUTORIDAD/EMERGENCIA: {st.session_state.contact_authority}", url_3, use_container_width=True, type="secondary")
                
                st.balloons()

            except Exception as e:
                placeholder.error(f"Error al preparar envío: {e}")
            # --- FIN: LÓGICA DE 3 SEGUNDOS ---

    # Estadísticas (HUD) - basadas en la cantidad de puntos dinámicos
    incident_count = len(st.session_state.dynamic_map_points)
    col1, col2, col3 = st.columns(3)
    with col1: st.markdown(f'<div class="metric-card">📊<br><strong>{incident_count}</strong><br>Incidentes Activos</div>', unsafe_allow_html=True)
    with col2: st.markdown(f'<div class="metric-card">🛡️<br><strong>{len(safe_locations)}</strong><br>Zonas Seguras</div>', unsafe_allow_html=True)
    with col3: st.markdown(f'<div class="metric-card">⚠️<br><strong>{high_risk_count}</strong><br>Riesgo Alto</div>', unsafe_allow_html=True)

# ---------------- PESTAÑA MAPA ----------------
with tabs[1]:
    st.title("🗺️ MAPA DE SEGURIDAD (LIVE)")
    
    # Centrar el mapa en la ubicación del usuario (UTP)
    map_center = [st.session_state.location['lat'], st.session_state.location['lon']]
    zoom = 15 # Un zoom más amplio para ver toda la zona de Huancayo

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
        # Usar los puntos dinámicos para el HeatMap
        heat_data = [[lat, lon, 0.8 if nivel=='Alta' else 0.5 if nivel=='Media' else 0.2] for lat, lon, nivel, _ in st.session_state.dynamic_map_points]
        HeatMap(heat_data, radius=18, blur=10).add_to(m)
    
    for lat, lon, nivel, tipo in st.session_state.dynamic_map_points:
        color = "red" if nivel=="Alta" else "orange" if nivel=="Media" else "yellow"
        folium.CircleMarker([lat, lon], radius=5, popup=f"⚠️ {tipo} ({nivel})", color=color, fill=True, fill_color=color, fill_opacity=0.8).add_to(m)
    
    # Zonas Seguras
    if show_safe_zones:
        for lat, lon, nombre, horario in safe_locations:
            folium.Marker([lat, lon], popup=f"🏪 {nombre} ({horario})", icon=folium.Icon(color="green", icon="shield", prefix='fa')).add_to(m)
    
    st_folium(m, width=360, height=400)
    st.caption("Puntos rojos/amarillos son incidentes activos generados en tiempo real.")

# ---------------- PESTAÑA REPORTAR ----------------
with tabs[2]:
    st.title("📢 REPORTAR INCIDENTE")
    
    st.info("Tu ubicación de reporte es la coordenada GPS fija UTP.")
    
    with st.form("report_form"):
        tipo_incidente = st.selectbox("Tipo de Incidente", ["Robo","Acoso","Persona Sospechosa","Asalto","Accidente","Otro"])
        
        # Mostrar ubicación GPS fija
        ubicacion_default = f"GPS UTP: {st.session_state.location['lat']:.5f}, {st.session_state.location['lon']:.5f}"
        
        ubicacion = st.text_input("Ubicación aproximada (automática)", ubicacion_default, disabled=True)
        descripcion = st.text_area("Descripción del incidente", "Describa lo que sucedió...")
        
        submitted = st.form_submit_button("📤 ENVIAR REPORTE")
        if submitted:
            # Lógica para añadir un log inmediato al feed dinámico
            report_time_str = datetime.now().strftime('%H:%M:%S')
            new_log = f"[{report_time_str}] TU REPORTE: {tipo_incidente} en Zona UTP (PENDIENTE)"
            st.session_state.incident_logs.insert(0, new_log)
            
            st.success("Reporte enviado. Gracias por tu colaboración.")
            # Aquí iría la lógica para guardar en la base de datos

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

# ---------------- PESTAÑA ANÁLISIS ----------------
with tabs[5]:
    st.title("🧠 ANÁLISIS PREDICTIVO (LIVE)")
    st.caption(f"Actualizado: {datetime.now().strftime('%H:%M:%S')}")
    
    # Generar recomendaciones dinámicas en cada recarga
    recommendations = generate_dynamic_recommendations()

    st.subheader("Patrones de Riesgo Detectados")
    for rec in recommendations:
        # Estilo de lista para las recomendaciones
        icon = "🔺" if "ALERTA" in rec else "🚨" if "PELIGRO" in rec else "✅" if "ESTABLE" in rec else "🛡️"
        st.markdown(f'<div style="background:#111; padding:8px; margin-bottom:5px; border-left: 3px solid #00f0ff;">{icon} {rec}</div>', unsafe_allow_html=True)

# --- 8. BUCLE DE ACTUALIZACIÓN FORZADA (CADA 60 SEGUNDOS) ---
# Esta lógica asegura que la aplicación se recargue automáticamente para generar nuevos logs y puntos de mapa.
if not st.session_state.panic_active:
    refresh_placeholder = st.empty()
    
    # Calcular cuánto falta para la próxima actualización de 60 segundos
    time_since_last_log = time.time() - st.session_state.last_log_time
    time_to_wait = int(60 - time_since_last_log)
    
    # Solo mostrar el contador si el tiempo es positivo
    if time_to_wait > 0:
        # Mostrar cuenta regresiva sin bloquear la UI por completo
        with refresh_placeholder.container():
             st.markdown(f"<div style='text-align:center; color:#555; margin-top:10px;'>Recibiendo datos en {time_to_wait} segundos...</div>", unsafe_allow_html=True)
             
        # Pausa de 1 segundo (esto es para que el usuario pueda ver el contador)
        time.sleep(1) 
        # Forzar re-ejecución del script (re-run) para verificar si ya pasó el minuto
        st.rerun()

    else:
        # El log_new_incident() ya se ejecutó al inicio del script y actualizó last_log_time.
        # Esperamos 1 segundo antes de forzar el re-run para el siguiente ciclo.
        with refresh_placeholder.container():
            st.markdown(f"<div style='text-align:center; color:#50c878; margin-top:10px;'>DATOS EN TIEMPO REAL: ACTUALIZACIÓN COMPLETA</div>", unsafe_allow_html=True)
        time.sleep(1) 
        st.rerun()