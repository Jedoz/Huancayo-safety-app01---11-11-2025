import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap
import webbrowser
import streamlit.components.v1 as components
import time # ¡Importante para el contador de 3 segundos!

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Huancayo Safety HUD",
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
        width: 280px; /* Mucho más grande */
        height: 280px; /* Mucho más grande */
        font-size: 48px; /* Texto más grande */
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
        color: #0a0a0f; /* Texto negro para máximo contraste */
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

    /* Estilo de Pestañas (Tabs) */
    [data-baseweb="tab-list"] {
        background: #111;
    }
    [data-baseweb="tab"] {
        font-family: 'Share Tech Mono', monospace;
        font-size: 14px;
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
    .stButton > button:not([kind="primary"]) {
        background: #00f0ff;
        color: #0a0a0f;
        font-family: 'Share Tech Mono', monospace;
        font-weight: bold;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-track { background: #0a0a0f; }
    ::-webkit-scrollbar-thumb { background: #ff2d95; border-radius: 5px; }
    ::-webkit-scrollbar-thumb:hover { background: #00f0ff; }

</style>
""", unsafe_allow_html=True)

# --- 4. ESTADO DE SESIÓN ---
if 'panic_active' not in st.session_state:
    st.session_state.panic_active = False
# --- RENOMBRADO Y AÑADIDOS ---
if 'contact_1' not in st.session_state:
    st.session_state.contact_1 = "+51999888777" # Contacto Principal
if 'contact_2' not in st.session_state:
    st.session_state.contact_2 = "" # Contacto Secundario (Opcional)
if 'contact_authority' not in st.session_state:
    st.session_state.contact_authority = "" # Autoridad (Opcional)
if 'medical_info' not in st.session_state:
    st.session_state.medical_info = "Datos médicos no especificados" # Info Médica
# --- FIN DE CAMBIOS EN SESIÓN ---
if 'location' not in st.session_state:
    st.session_state.location = None # Aquí guardaremos el GPS
if 'user_name' not in st.session_state:
    st.session_state.user_name = "Usuario Anónimo" # ¡NUEVO! Guardar el nombre del usuario

# --- 5. COMPONENTE HTML/JS PARA OBTENER UBICACIÓN ---
# Este componente usa JS para pedir la ubicación al navegador
# y la devuelve a Streamlit usando `Streamlit.setComponentValue`
GET_LOCATION_HTML = """
<script>
    // Pedir permiso de geolocalización
    navigator.geolocation.getCurrentPosition(
        // Éxito: Enviar coordenadas a Streamlit
        (position) => {
            Streamlit.setComponentValue({
                "lat": position.coords.latitude,
                "lon": position.coords.longitude
            });
        },
        // Error: Enviar null
        (error) => {
            Streamlit.setComponentValue(null);
        }
    );
</script>
"""

# --- 6. FUNCIONES MEJORADAS ---
def check_risk_zone(lat, lon):
    # Lógica de simulación (sin cambios)
    return {'nombre': 'Av. Ferrocarril', 'incidentes': 3, 'nivel': 'Alto', 'horario': 'última hora'}

def trigger_whatsapp(contacts_to_alert, lat, lon, user_name, medical_info):
    # MENSAJE DE ALERTA MEJORADO Y PERSONALIZADO
    # Convertir nombre a mayúsculas para más urgencia
    user_name_upper = user_name.upper()
    
    message = (
        f"🚨 *¡¡¡EMERGENCIA CRÍTICA!!! ¡{user_name_upper} ESTÁ EN PELIGRO Y NECESITA AYUDA AHORA!* 🚨\n\n"
        f"¡ESTA ES UNA ALERTA DE PÁNICO REAL! ¡{user_name_upper} HA PRESIONADO EL BOTÓN DE EMERGENCIA!\n"
        "¡POR FAVOR, ACUDE O ENVÍA AYUDA DE INMEDIATO!\n\n"
        "📍 *UBICACIÓN GPS EXACTA:*\n"
        f"https://maps.google.com/?q={lat},{lon}\n"
        f"Latitud: {lat}\n"
        f"Longitud: {lon}\n\n"
        "🩺 *INFORMACIÓN MÉDICA RELEVANTE:*\n"
        f"{medical_info}\n\n"
        "¡¡¡ACTÚA RÁPIDO, ES UNA EMERGENCIA!!! "
        "¡¡¡NO ES SIMULACRO!!!"
    )
    
    import urllib.parse
    message_encoded = urllib.parse.quote(message)
    
    # --- LÓGICA DE ENVÍO MÚLTIPLE ---
    urls_opened = 0
    for number in contacts_to_alert:
        if number and len(number) > 5: # Asegurarse que el número no esté vacío
            number_cleaned = number.replace('+', '').replace(' ', '')
            url = f"https://wa.me/{number_cleaned}?text={message_encoded}"
            webbrowser.open(url)
            urls_opened += 1
    
    return urls_opened

# --- 7. EJECUCIÓN DEL COMPONENTE DE UBICACIÓN ---
# Ejecutamos el HTML/JS. El resultado (coordenadas o null) se guarda en `location_data`
# Lo ejecutamos ANTES de las pestañas para tener la info lista
if st.session_state.location is None:
    location_data = components.html(GET_LOCATION_HTML, height=0)

    # --- LA CORRECCIÓN ESTÁ AQUÍ ---
    # Verificamos que location_data sea un DICIONARIO (dict) antes de asignarlo.
    # El error anterior era que location_data podia ser un 'DeltaGenerator'
    # y el 'if location_data:' se evaluaba como True, guardando el objeto incorrecto.
    if isinstance(location_data, dict):
        st.session_state.location = location_data
        # Forzamos un re-run para que la app se actualice con la nueva ubicación
        st.rerun()
    elif location_data is None:
        # El componente devolvió 'null' (probablemente error de permisos o el usuario denegó)
        # No hacemos nada, la app mostrará el st.warning() en la pestaña Inicio
        pass

# --- 8. PESTAÑAS (TABS) ---
tabs = st.tabs([
    "🏠 INICIO",
    "🗺️ MAPA",
    "📢 REPORTAR",
    "🏪 ZONAS",
    "👤 PERFIL",
    "🧠 ANÁLISIS"
])

# ---------------- PESTAÑA INICIO ----------------
with tabs[0]:
    st.title("🛡️ SAFETY HUD: HUANCAYO")
    
    # Mostrar estado de GPS
    if st.session_state.location:
        st.markdown(f'<div class="safe-zone" style="text-align: center; background: #005f5f;">🛰️ GPS FIJADO: {st.session_state.location["lat"]:.4f}, {st.session_state.location["lon"]:.4f}</div>', unsafe_allow_html=True)
    else:
        st.warning("⚠️ No se pudo obtener tu ubicación. Activa el GPS y recarga la página para usar el botón de pánico.")

    # Zona de riesgo (simulada)
    zona_riesgo = check_risk_zone(-12.065, -75.210)
    st.markdown(f'<div class="warning-alert">¡ALERTA! ZONA DE RIESGO: {zona_riesgo["nombre"]}</div>', unsafe_allow_html=True)
    
    # Placeholder para el contador de 3 segundos
    countdown_placeholder = st.empty()

    # Botón de pánico GIGANTE
    # Usamos st.button con kind="primary" para que nuestro CSS lo detecte
    if st.button("🚨 PÁNICO 🚨", key="panic_main", type="primary"):
        if st.session_state.location:
            
            # --- CONSTRUIR LISTA DE CONTACTOS ---
            contacts_to_alert = [
                st.session_state.contact_1,
                st.session_state.contact_2,
                st.session_state.contact_authority
            ]
            # Filtrar vacíos
            contacts_to_alert = [c for c in contacts_to_alert if c and len(c) > 5]

            # --- VERIFICAR SI HAY CONTACTOS ---
            if not contacts_to_alert:
                countdown_placeholder.error("¡No hay contactos de emergencia! Ve a PERFIL para agregarlos.")
            else:
                # --- INICIO: LÓGICA DE 3 SEGUNDOS ---
                try:
                    # Mostrar cuenta regresiva en el placeholder
                    countdown_placeholder.warning("Preparando alerta... 3 segundos")
                    time.sleep(1)
                    countdown_placeholder.warning("Preparando alerta... 2 segundos")
                    time.sleep(1)
                    countdown_placeholder.warning("Preparando alerta... 1 segundo")
                    time.sleep(1)
                    
                    # --- ENVIAR ALERTA ---
                    lat = st.session_state.location['lat']
                    lon = st.session_state.location['lon']
                    user_name = st.session_state.user_name
                    medical_info = st.session_state.medical_info
                    
                    # ¡Enviamos los datos a la función de WhatsApp!
                    sent_count = trigger_whatsapp(contacts_to_alert, lat, lon, user_name, medical_info)
                    
                    st.session_state.panic_active = True
                    countdown_placeholder.success(f"¡Alerta de pánico enviada a {sent_count} contacto(s)!")
                    st.balloons()

                except Exception as e:
                    countdown_placeholder.error(f"Error al enviar: {e}")
                # --- FIN: LÓGICA DE 3 SEGUNDOS ---

        else:
            st.error("¡ERROR DE UBICACIÓN! No se puede enviar alerta sin GPS.")

    # Estadísticas (HUD)
    col1, col2, col3 = st.columns(3)
    with col1: st.markdown('<div class="metric-card">📊<br><strong>12</strong><br>Incidentes Hoy</div>', unsafe_allow_html=True)
    with col2: st.markdown('<div class="metric-card">🛡️<br><strong>8</strong><br>Zonas Seguras</div>', unsafe_allow_html=True)
    with col3: st.markdown('<div class="metric-card">⚠️<br><strong>3</strong><br>Alertas Activas</div>', unsafe_allow_html=True)

# ---------------- PESTAÑA MAPA ----------------
with tabs[1]:
    st.title("🗺️ MAPA DE SEGURIDAD")
    
    # Centrar el mapa en la ubicación del usuario si está disponible, si no, en Huancayo
    if st.session_state.location:
        map_center = [st.session_state.location['lat'], st.session_state.location['lon']]
        zoom = 16
    else:
        map_center = [-12.065, -75.210] # Default Huancayo
        zoom = 15

    show_heatmap = st.checkbox("Ver Mapa de Calor", value=True)
    show_safe_zones = st.checkbox("Ver Zonas Seguras", value=True)
    
    m = folium.Map(location=map_center, zoom_start=zoom, tiles="CartoDB dark_matter")
    
    # Marcador del Usuario (¡NUEVO!)
    if st.session_state.location:
        folium.Marker(
            [st.session_state.location['lat'], st.session_state.location['lon']],
            popup="¡TÚ ESTÁS AQUÍ!",
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
    
    # Ajustar tamaño del mapa al contenedor
    st_folium(m, width=360, height=400)

# ---------------- PESTAÑA REPORTAR ----------------
with tabs[2]:
    st.title("📢 REPORTAR INCIDENTE")
    with st.form("report_form"):
        tipo_incidente = st.selectbox("Tipo de Incidente", ["Robo","Acoso","Persona Sospechosa","Asalto","Accidente","Otro"])
        
        # Usar ubicación GPS si está disponible
        ubicacion_default = "Cerca de..."
        if st.session_state.location:
            ubicacion_default = f"GPS: {st.session_state.location['lat']:.5f}, {st.session_state.location['lon']:.5f}"
        
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
        # ¡CAMPO DE NOMBRE AÑADIDO!
        nombre = st.text_input("Tu Nombre", st.session_state.user_name) 
        
        st.subheader("Contactos de Emergencia")
        contact_1 = st.text_input("Contacto 1 (Principal)", st.session_state.contact_1)
        contact_2 = st.text_input("Contacto 2 (Opcional)", st.session_state.contact_2)
        contact_authority = st.text_input("Autoridad (Policía, Bomberos, etc. Opcional)", st.session_state.contact_authority)

        st.subheader("Información Médica")
        medical_info = st.text_area("Condiciones Médicas (Alergias, Tipo de Sangre, etc.)", st.session_state.medical_info)
        
        if st.form_submit_button("💾 GUARDAR PERFIL"):
            # ¡GUARDAR TODOS LOS CAMPOS!
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