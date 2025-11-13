import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap
import streamlit.components.v1 as components
import time 
import urllib.parse 

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="SECURE MAP HUANCAYO",
    page_icon="🚨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 2. DATOS SIMULADOS (Sin cambios) ---
danger_points = [
    (-12.065, -75.210, 'Alta', 'Robo'),
    (-12.067, -75.212, 'Media', 'Acoso'),
    (-12.064, -75.214, 'Baja', 'Sospechoso'),
    (-12.063, -75.209, 'Alta', 'Asalto'),
    (-12.062, -75.215, 'Media', 'Robo'),
]

safe_locations = [
    (-12.065, -75.211, 'Farmacia Segura', '24/7'),
    (-12.066, -75.213, 'Restaurante Refugio', '6 AM - 11 PM'),
    (-12.068, -75.209, 'Tienda Amiga', '8 AM - 10 PM'),
]

# --- 3. ESTILOS CSS MEJORADOS (Estética Videojuego/Cyberpunk) ---
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
    
    /* Estilo de Formularios */
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
        background-color: #112d3c;
        color: #ffffff;
        border: 1px solid #00f0ff;
    }
    .stForm {
        background: #0d1b2a;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #005f5f;
    }
    
    /* Botones normales y de envío (no-pánico) */
    .stButton > button:not([kind="primary"]):not([key="retry_gps"]):not([key="request_gps"]) {
        background: #00f0ff;
        color: #0a0a0f;
        font-family: 'Share Tech Mono', monospace;
        font-weight: bold;
        width: 100%; 
    }
    
    /* Botones de enlace (NUEVO) */
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
    /* Botón de enlace principal (usado para el Contacto 1) */
    .stLinkButton a[data-testid="baseLinkButton-primary"] {
         background-color: #ff2d95; /* Rosa pánico */
         color: #ffffff;
         border: 1px solid #ffffff;
    }
    /* Botón de enlace secundario (usado para otros contactos) */
    .stLinkButton a[data-testid="baseLinkButton-secondary"] {
         background-color: #112d3c;
         color: #00f0ff;
         border: 1px solid #00f0ff;
    }


    /* Scrollbar */
    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-track { background: #0a0a0f; }
    ::-webkit-scrollbar-thumb { background: #ff2d95; border-radius: 5px; }
    ::-webkit-scrollbar-thumb:hover { background: #00f0ff; }

</style>
""", unsafe_allow_html=True)

# --- 4. ESTADO DE SESIÓN (MODIFICADO PARA SIMULACIÓN) ---
if 'panic_active' not in st.session_state:
    st.session_state.panic_active = False
if 'contact_1' not in st.session_state:
    st.session_state.contact_1 = "+51999999999" # Ejemplo para iniciar con un número
if 'contact_2' not in st.session_state:
    st.session_state.contact_2 = "+51999888777" 
if 'contact_authority' not in st.session_state:
    st.session_state.contact_authority = "51987654321" # Sin el + para probar la limpieza
if 'medical_info' not in st.session_state:
    st.session_state.medical_info = "Tipo de sangre: O+, Alergias: Penicilina." 
if 'user_name' not in st.session_state:
    st.session_state.user_name = "Andrea G."

# LÓGICA DE UBICACIÓN AHORA ES FIJA Y EXITOSA (MODO SIMULACIÓN)
st.session_state.location = {
    "status": "success",  # SIMULACIÓN: Siempre exitoso
    "lat": -12.065,       # Latitud de Huancayo (Simulada)
    "lon": -75.210        # Longitud de Huancayo (Simulada)
}
# La variable location_permission_requested ya no es necesaria

# --- 5. ELIMINACIÓN DE COMPONENTE HTML/JS (Para evitar conflictos) ---
# El código para obtener la ubicación real ha sido eliminado para la simulación.

# --- 6. FUNCIONES MEJORADAS (Sin cambios) ---
def check_risk_zone(lat, lon):
    # Función de simulación de riesgo
    return {'nombre': 'Av. Ferrocarril', 'incidentes': 3, 'nivel': 'Alto', 'horario': 'última hora'}

def generate_whatsapp_url(number, lat, lon, user_name, medical_info):
    if not number or len(number) < 5:
        return None 
        
    user_name_upper = user_name.upper()
    
    message = (
        f"🚨 *¡¡¡EMERGENCIA CRÍTICA!!! ¡{user_name_upper} ESTÁ EN PELIGRO Y NECESITA AYUDA AHORA!* 🚨\n\n"
        f"¡ESTA ES UNA ALERTA DE PÁNICO REAL! ¡{user_name_upper} HA PRESIONADO EL BOTÓN DE EMERGENCIA!\n"
        "¡POR FAVOR, ACUDE O ENVÍA AYUDA DE INMEDIATO!\n\n"
        "📍 *UBICACIÓN GPS EXACTA (SIMULADA):*\n"
        f"https://maps.google.com/?q={lat},{lon}\n"
        f"Latitud: {lat}\n"
        f"Longitud: {lon}\n\n"
        "🩺 *INFORMACIÓN MÉDICA RELEVANTE:*\n"
        f"{medical_info}\n\n"
        "¡¡¡ACTÚA RÁPIDO, ES UNA EMERGENCIA!!! "
        "¡¡¡NO ES SIMULACRO!!!"
    )
    
    message_encoded = urllib.parse.quote(message)
    number_cleaned = number.replace('+', '').replace(' ', '')
    url = f"https://wa.me/{number_cleaned}?text={message_encoded}" 
    return url

# --- 7. ELIMINACIÓN DE LÓGICA DE EJECUCIÓN DEL COMPONENTE DE UBICACIÓN ---
# Ya no es necesaria al ser la ubicación fija.

# --- 8. PESTAÑAS (TABS) ---
tabs = st.tabs(["🏠", "🗺️", "📢", "🏪", "👤", "🧠"])

# ---------------- PESTAÑA INICIO ----------------
with tabs[0]:
    st.title("🛡️ SECURE MAP HUANCAYO")
    
    # --- SIMULACIÓN DE LÓGICA GPS FIJADA ---
    lat_sim = st.session_state.location["lat"]
    lon_sim = st.session_state.location["lon"]

    # Mostrar que el GPS está fijado y en modo simulación
    st.markdown(f'<div class="safe-zone" style="text-align: center; background: #50c878;">✅ GPS SIMULADO: {lat_sim:.4f}, {lon_sim:.4f}</div>', unsafe_allow_html=True)
    st.info("⚠️ ESTE MODO USA UNA UBICACIÓN FIJA (-12.065, -75.210) para pruebas. El botón PÁNICO está activo.")


    # Zona de riesgo (simulada)
    zona_riesgo = check_risk_zone(lat_sim, lon_sim)
    st.markdown(f'<div class="warning-alert">¡ALERTA! ZONA DE RIESGO: {zona_riesgo["nombre"]}</div>', unsafe_allow_html=True)
    
    # Placeholder para el contador y los botones de envío
    placeholder = st.empty()

    # Comprobar si el GPS está listo ANTES de dibujar el botón
    gps_ready = True # Siempre True en modo simulación

    # Botón de pánico GIGANTE
    if placeholder.button("🚨 PÁNICO 🚨", key="panic_main", type="primary", disabled=not gps_ready):
        
        # --- CONSTRUIR LISTA DE CONTACTOS ---
        contacts = [
            st.session_state.contact_1,
            st.session_state.contact_2,
            st.session_state.contact_authority
        ]
        contacts = [c for c in contacts if c and len(c) > 5]

        # --- VERIFICAR SI HAY CONTACTOS ---
        if not contacts:
            placeholder.error("¡No hay contactos de emergencia! Ve a PERFIL para agregarlos.")
        else:
            # --- INICIO: LÓGICA DE 3 SEGUNDOS ---
            try:
                with placeholder.container(): 
                    st.warning("Preparando alerta... 3 segundos")
                    time.sleep(1)
                    st.warning("Preparando alerta... 2 segundos")
                    time.sleep(1)
                    st.warning("Preparando alerta... 1 segundo")
                    time.sleep(1)
                
                # --- OBTENER DATOS PARA MENSAJES ---
                lat = st.session_state.location['lat']
                lon = st.session_state.location['lon']
                user_name = st.session_state.user_name
                medical_info = st.session_state.medical_info
                
                # --- LÓGICA DE ENVÍO MEJORADA! ---
                with placeholder.container():
                    st.success("¡ALERTA LISTA! PRESIONA PARA ENVIAR (SE ABRIRÁ WHATSAPP):")
                    
                    # Generar URL para Contacto 1
                    url_1 = generate_whatsapp_url(st.session_state.contact_1, lat, lon, user_name, medical_info)
                    if url_1:
                        # Usamos link_button para que se abra en una nueva pestaña
                        st.link_button(f"ENVIAR A CONTACTO 1 (Principal)", url_1, use_container_width=True, type="primary")

                    # Generar URL para Contacto 2
                    url_2 = generate_whatsapp_url(st.session_state.contact_2, lat, lon, user_name, medical_info)
                    if url_2:
                        st.link_button(f"ENVIAR A CONTACTO 2 (Secundario)", url_2, use_container_width=True, type="secondary")

                    # Generar URL para Autoridad
                    url_3 = generate_whatsapp_url(st.session_state.contact_authority, lat, lon, user_name, medical_info)
                    if url_3:
                        st.link_button(f"ENVIAR A AUTORIDAD", url_3, use_container_width=True, type="secondary")
                
                st.balloons()

            except Exception as e:
                placeholder.error(f"Error al preparar envío: {e}")
            # --- FIN: LÓGICA DE 3 SEGUNDOS ---

    # Estadísticas (HUD)
    col1, col2, col3 = st.columns(3)
    with col1: st.markdown('<div class="metric-card">📊<br><strong>12</strong><br>Incidentes Hoy</div>', unsafe_allow_html=True)
    with col2: st.markdown('<div class="metric-card">🛡️<br><strong>8</strong><br>Zonas Seguras</div>', unsafe_allow_html=True)
    with col3: st.markdown('<div class="metric-card">⚠️<br><strong>3</strong><br>Alertas Activas</div>', unsafe_allow_html=True)

# ---------------- PESTAÑA MAPA ----------------
with tabs[1]:
    st.title("🗺️ MAPA DE SEGURIDAD")
    
    # Centrar el mapa en la ubicación del usuario simulada
    map_center = [st.session_state.location['lat'], st.session_state.location['lon']]
    zoom = 16

    show_heatmap = st.checkbox("Ver Mapa de Calor", value=True)
    show_safe_zones = st.checkbox("Ver Zonas Seguras", value=True)
    
    m = folium.Map(location=map_center, zoom_start=zoom, tiles="CartoDB dark_matter")
    
    # Marcador del Usuario (Simulado)
    folium.Marker(
        [st.session_state.location['lat'], st.session_state.location['lon']],
        popup="¡TÚ ESTÁS AQUÍ! (SIMULADO)",
        icon=folium.Icon(color="blue", icon="person", prefix='fa')
    ).add_to(m)

    if show_heatmap:
        heat_data = [[lat, lon, 0.8 if nivel=='Alta' else 0.5 if nivel=='Media' else 0.2] for lat, lon, nivel, _ in danger_points]
        HeatMap(heat_data, radius=20, blur=10).add_to(m)
    
    for lat, lon, nivel, tipo in danger_points:
        color = "red" if nivel=="Alta" else "orange" if nivel=="Media" else "yellow"
        folium.CircleMarker([lat, lon], radius=6, popup=f"⚠️ {tipo}", color=color, fill=True, fill_color=color, fill_opacity=0.6).add_to(m)
    
    if show_safe_zones:
        for lat, lon, nombre, horario in safe_locations:
            folium.Marker([lat, lon], popup=f"🏪 {nombre} ({horario})", icon=folium.Icon(color="green", icon="shield", prefix='fa')).add_to(m)
    
    st_folium(m, width=360, height=400)

# ---------------- PESTAÑA REPORTAR ----------------
with tabs[2]:
    st.title("📢 REPORTAR INCIDENTE")
    with st.form("report_form"):
        tipo_incidente = st.selectbox("Tipo de Incidente", ["Robo","Acoso","Persona Sospechosa","Asalto","Accidente","Otro"])
        
        # Usar ubicación GPS simulada
        ubicacion_default = f"GPS SIMULADO: {st.session_state.location['lat']:.5f}, {st.session_state.location['lon']:.5f}"
        
        ubicacion = st.text_input("Ubicación aproximada", ubicacion_default)
        descripcion = st.text_area("Descripción del incidente", "Describa lo que sucedió...")
        
        submitted = st.form_submit_button("📤 ENVIAR REPORTE")
        if submitted:
            st.success("Reporte enviado. Gracias por tu colaboración.")
            # Aquí iría la lógica para guardar en la base de datos

# ---------------- PESTAÑA ZONAS ----------------
with tabs[3]:
    st.title("🏪 ZONAS SEGURAS CERCANAS")
    for lat, lon, nombre, horario in safe_locations:
        st.markdown(f'<div class="safe-zone"><strong>{nombre}</strong><br>⏰ Horario: {horario}</div>', unsafe_allow_html=True)

# ---------------- PESTAÑA PERFIL ----------------
with tabs[4]:
    st.title("👤 PERFIL DE USUARIO")
    st.info("Tu nombre e info médica se incluirán en las alertas de pánico.")
    
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
    st.title("🧠 ANÁLISIS PREDICTIVO (IA)")
    st.info("Patrones de riesgo detectados por el sistema:")
    st.markdown("""
    - **Viernes (18:00-22:00):** 🔺 70% más robos (Zona Centro).
    - **Días de Pago (Quincena/Fin de mes):** 🔺 85% más incidentes (Cajeros y Mercados).
    - **Parques (Nocturno):** 🔺 45% más reportes de acoso.
    - **Transporte Público (Hora Pico):** 🔺 60% riesgo de hurto.
    """)
    st.warning("RECOMENDACIÓN: Evitar Calle Real entre 19:00 y 21:00 los viernes.")