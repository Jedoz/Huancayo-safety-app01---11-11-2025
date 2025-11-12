import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap, MeasureControl
import random
import time
from datetime import datetime, timedelta
import urllib.parse

# Configuración de la página para celular
st.set_page_config(
    page_title="Huancayo Safety App", 
    page_icon="🛡️", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- SIMULACIÓN DE DATOS ---
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

recent_incidents = [
    {'tipo': 'Robo', 'ubicacion': 'Av. Ferrocarril', 'hora': 'Hace 15 min', 'verificada': True},
    {'tipo': 'Acoso', 'ubicacion': 'Parque Huamanmarca', 'hora': 'Hace 30 min', 'verificada': False},
    {'tipo': 'Sospechoso', 'ubicacion': 'Calle Real', 'hora': 'Hace 45 min', 'verificada': True},
]

# Estilos CSS para celular con botón gigante
st.markdown("""
<style>
    /* Tamaño real de celular - centrado perfecto */
    .stApp {
        max-width: 390px;
        height: 844px;
        margin: 10px auto;
        border: 12px solid #000000;
        border-radius: 40px;
        padding: 0px;
        background: #ffffff;
        color: #000000;
        overflow: hidden;
        position: relative;
        box-shadow: 0 0 20px rgba(0,0,0,0.3);
    }
    
    /* Ocultar scrollbars */
    .stApp::-webkit-scrollbar {
        display: none;
    }
    
    /* Pestañas superiores estilo Excel */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0px;
        background-color: #000000;
        padding: 5px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        background-color: #f0f0f0;
        border-radius: 8px 8px 0px 0px;
        padding: 0px 12px;
        margin: 0px 2px;
        font-size: 12px;
        font-weight: bold;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #000000 !important;
        color: #ffffff !important;
    }
    
    /* Contenido principal */
    .main-content {
        padding: 10px;
        height: calc(100vh - 120px);
        overflow-y: auto;
    }
    
    /* BOTÓN DE PÁNICO GIGANTE */
    .panic-button-giant {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(45deg, #FF0000, #FF4444);
        color: white;
        border: none;
        border-radius: 0px;
        font-size: 32px;
        font-weight: bold;
        cursor: pointer;
        z-index: 9999;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        animation: pulse-danger 1.5s infinite;
    }
    
    .panic-button-giant:hover {
        background: linear-gradient(45deg, #CC0000, #FF2222);
    }
    
    @keyframes pulse-danger {
        0% { transform: scale(1); }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); }
    }
    
    /* Botones normales */
    .emergency-button {
        background: #000000;
        color: #ffffff;
        border: 2px solid #000000;
        padding: 18px;
        border-radius: 25px;
        font-size: 16px;
        font-weight: bold;
        margin: 8px 0;
        width: 100%;
    }
    
    .safe-zone {
        background: #f8f9fa;
        color: #000000;
        padding: 12px;
        border-radius: 8px;
        margin: 6px 0;
        border: 1px solid #000000;
    }
    
    .warning-alert {
        background: #000000;
        color: #ffffff;
        padding: 12px;
        border-radius: 8px;
        margin: 8px 0;
        border: 1px solid #000000;
        font-size: 14px;
    }
    
    .metric-card {
        background: #f8f9fa;
        padding: 8px;
        border-radius: 8px;
        border: 1px solid #000000;
        text-align: center;
        font-size: 11px;
    }
    
    .section-divider {
        border: 0.5px solid #000000;
        margin: 15px 0;
    }
    
    .whatsapp-button {
        background: #25D366;
        color: white;
        border: none;
        padding: 12px;
        border-radius: 8px;
        font-size: 14px;
        font-weight: bold;
        margin: 5px 0;
        width: 100%;
        text-align: center;
        text-decoration: none;
        display: block;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar session state
if 'panic_active' not in st.session_state:
    st.session_state.panic_active = False
if 'panic_countdown' not in st.session_state:
    st.session_state.panic_countdown = 0
if 'reports' not in st.session_state:
    st.session_state.reports = []
if 'show_giant_panic' not in st.session_state:
    st.session_state.show_giant_panic = False
if 'emergency_contacts' not in st.session_state:
    st.session_state.emergency_contacts = {
        'contacto1': '+51 999888777',
        'contacto2': '+51 988777666'
    }

# --- FUNCIONES ---
def check_risk_zone(lat, lon):
    return {
        'nombre': 'Av. Ferrocarril',
        'incidentes': 3,
        'nivel': 'Alto',
        'horario': 'última hora'
    }

def verificar_incidente(reporte):
    confirmaciones_necesarias = 3
    confirmaciones_actuales = random.randint(0, confirmaciones_necesarias)
    if confirmaciones_actuales >= confirmaciones_necesarias:
        return True, confirmaciones_actuales
    return False, confirmaciones_actuales

def analizar_patrones():
    patrones = [
        "Días de pago + viernes + Zona Centro = 85% más robos",
        "Esta zona es 70% más peligrosa después de las 8 PM los viernes",
        "Los incidentes aumentan 60% los fines de semana en áreas comerciales",
    ]
    return random.choice(patrones)

def generar_mensaje_whatsapp(nombre, ubicacion, grupo_sanguineo, alergias):
    mensaje = f"🚨¡EMERGENCIA!🚨\n\n{nombre} necesita ayuda URGENTE\n📍Ubicación: {ubicacion}\n🩸Grupo sanguíneo: {grupo_sanguineo}\n💊Alergias: {alergias}\n\n⚠️Por favor contacta a emergencias inmediatamente"
    return urllib.parse.quote(mensaje)

# --- BOTÓN DE PÁNICO GIGANTE EN INICIO ---
if st.session_state.show_giant_panic:
    st.markdown("""
    <div class="panic-button-giant" onclick="activateGiantPanic()">
        <div style="font-size: 48px; margin-bottom: 20px;">🚨</div>
        <div>BOTÓN DE PÁNICO</div>
        <div style="font-size: 18px; margin-top: 10px;">TOCA PARA ACTIVAR</div>
        <div style="font-size: 14px; margin-top: 20px; opacity: 0.8;">Mantén presionado por 3 segundos</div>
    </div>
    
    <script>
    function activateGiantPanic() {
        // Enviar señal a Streamlit para activar pánico
        window.parent.postMessage({type: 'streamlit:setComponentValue', value: 'activate_giant_panic'}, '*');
    }
    </script>
    """, unsafe_allow_html=True)
    
    # Botón para activar desde Streamlit
    if st.button("🔴 ACTIVAR PÁNICO (Simulación)", key="giant_panic_hidden"):
        st.session_state.panic_active = True
        st.session_state.panic_countdown = 3
        st.session_state.show_giant_panic = False
        st.rerun()

# --- PESTAÑAS SUPERIORES ---
st.markdown('<div class="main-content">', unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🏠 INICIO", 
    "🗺️ MAPA", 
    "🚨 PÁNICO", 
    "📢 REPORTAR", 
    "🏪 ZONAS", 
    "👤 PERFIL", 
    "🧠 ANÁLISIS"
])

with tab1:
    st.title("🛡️ SEGURIDAD HUANCAYO")
    
    # BOTÓN GIGANTE EN INICIO
    st.markdown("### 🚨 ACCESO RÁPIDO A EMERGENCIA")
    if st.button("🎯 ACTIVAR BOTÓN GIGANTE DE PÁNICO", use_container_width=True, type="primary"):
        st.session_state.show_giant_panic = True
        st.rerun()
    
    st.markdown("---")
    
    zona_riesgo = check_risk_zone(-12.065, -75.210)
    st.markdown(f'<div class="warning-alert">⚠️ Zona de riesgo: {zona_riesgo["nombre"]}</div>', unsafe_allow_html=True)
    
    # Estadísticas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="metric-card">📊<br><strong>12</strong><br>Incidentes</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card">🛡️<br><strong>8</strong><br>Zonas Seguras</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card">⚠️<br><strong>3</strong><br>Alertas</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # Incidentes recientes
    st.subheader("📋 INCIDENTES RECIENTES")
    for incident in recent_incidents:
        verified = "✅" if incident['verificada'] else "⏳"
        st.write(f"{verified} **{incident['tipo']}** - {incident['ubicacion']}")
        st.caption(f"{incident['hora']}")

with tab2:
    st.title("🗺️ MAPA DE SEGURIDAD")
    
    # Filtros rápidos
    col1, col2 = st.columns(2)
    with col1:
        show_heatmap = st.checkbox("Mapa Calor", value=True)
    with col2:
        show_safe_zones = st.checkbox("Zonas Seguras", value=True)
    
    # Mapa compacto
    m = folium.Map(location=[-12.065, -75.210], zoom_start=15)
    
    if show_heatmap:
        heat_data = []
        for lat, lon, nivel, _ in danger_points:
            weight = 0.8 if nivel == 'Alta' else 0.5 if nivel == 'Media' else 0.2
            heat_data.append([lat, lon, weight])
        HeatMap(heat_data, radius=20, blur=10).add_to(m)
    
    for lat, lon, nivel, tipo in danger_points:
        color = "red" if nivel == "Alta" else "orange" if nivel == "Media" else "yellow"
        folium.CircleMarker([lat, lon], radius=6, popup=f"⚠️ {tipo}", color=color, fill=True).add_to(m)
    
    if show_safe_zones:
        for lat, lon, nombre, horario in safe_locations:
            folium.Marker([lat, lon], popup=f"🏪 {nombre}", icon=folium.Icon(color="green")).add_to(m)
    
    st_folium(m, width=350, height=400)

with tab3:
    st.title("🚨 BOTÓN DE PÁNICO")
    
    if not st.session_state.panic_active:
        st.error("EN CASO DE PELIGRO INMINENTE")
        
        with st.expander("📞 CONTACTOS DE EMERGENCIA"):
            contacto1 = st.text_input("Contacto Principal", st.session_state.emergency_contacts['contacto1'], key="contacto1")
            contacto2 = st.text_input("Contacto Secundario", st.session_state.emergency_contacts['contacto2'], key="contacto2")
            
            # Guardar contactos
            if st.button("💾 GUARDAR CONTACTOS"):
                st.session_state.emergency_contacts = {
                    'contacto1': contacto1,
                    'contacto2': contacto2
                }
                st.success("Contactos guardados")
        
        with st.expander("🏥 INFORMACIÓN MÉDICA"):
            grupo_sanguineo = st.selectbox("Grupo Sanguíneo", ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])
            alergias = st.text_input("Alergias o condiciones", "Ninguna")
        
        # BOTÓN DE PÁNICO PRINCIPAL
        if st.button("🔴 ACTIVAR BOTÓN DE PÁNICO", use_container_width=True, type="primary"):
            st.session_state.panic_active = True
            st.session_state.panic_countdown = 3
            st.session_state.grupo_sanguineo = grupo_sanguineo
            st.session_state.alergias = alergias
            st.rerun()
    else:
        if st.session_state.panic_countdown > 0:
            st.warning(f"🕒 La alerta se activará en {st.session_state.panic_countdown} segundos...")
            st.session_state.panic_countdown -= 1
            time.sleep(1)
            st.rerun()
        else:
            st.error("🚨 ¡ALERTA DE EMERGENCIA ACTIVADA!")
            
            # Simular ubicación
            my_lat = -12.065 + random.uniform(-0.001, 0.001)
            my_lon = -75.210 + random.uniform(-0.001, 0.001)
            ubicacion = f"{my_lat:.5f}, {my_lon:.5f}"
            
            # GENERAR ENLACES DE WHATSAPP
            mensaje = generar_mensaje_whatsapp(
                "Usuario en Peligro", 
                ubicacion, 
                st.session_state.grupo_sanguineo, 
                st.session_state.alergias
            )
            
            st.success(f"""
            ✅ Alerta enviada a contactos
            📍 Ubicación: {ubicacion}
            🩸 Grupo sanguíneo: {st.session_state.grupo_sanguineo}
            💊 Alergias: {st.session_state.alergias}
            """)
            
            # BOTONES DE WHATSAPP
            st.subheader("📤 ENVIAR MENSAJE POR WHATSAPP")
            
            col1, col2 = st.columns(2)
            with col1:
                whatsapp_url1 = f"https://wa.me/{st.session_state.emergency_contacts['contacto1'].replace('+', '').replace(' ', '')}?text={mensaje}"
                st.markdown(f'<a href="{whatsapp_url1}" target="_blank" class="whatsapp-button">📱 Contacto 1</a>', unsafe_allow_html=True)
            
            with col2:
                whatsapp_url2 = f"https://wa.me/{st.session_state.emergency_contacts['contacto2'].replace('+', '').replace(' ', '')}?text={mensaje}"
                st.markdown(f'<a href="{whatsapp_url2}" target="_blank" class="whatsapp-button">📱 Contacto 2</a>', unsafe_allow_html=True)
            
            # Simular envío automático
            st.info("📨 Mensaje automático enviado a contactos de emergencia")
            
            if st.button("🟢 CANCELAR ALERTA", use_container_width=True):
                st.session_state.panic_active = False
                st.rerun()

with tab4:
    st.title("📢 REPORTAR INCIDENTE")
    
    with st.form("report_form"):
        tipo_incidente = st.selectbox("Tipo de Incidente", 
                                    ["Robo", "Acoso", "Persona Sospechosa", "Asalto", "Accidente", "Otro"])
        ubicacion = st.text_input("Ubicación aproximada", "Cerca de...")
        descripcion = st.text_area("Descripción del incidente", "Describa lo que sucedió...")
        
        submitted = st.form_submit_button("📤 ENVIAR REPORTE", use_container_width=True)
        
        if submitted:
            verificado, confirmaciones = verificar_incidente({'tipo': tipo_incidente, 'ubicacion': ubicacion})
            if verificado:
                st.success("✅ Reporte enviado y VERIFICADO")
            else:
                st.warning(f"⏳ Reporte enviado. {confirmaciones}/3 confirmaciones")

with tab5:
    st.title("🏪 ZONAS SEGURAS")
    
    for lat, lon, nombre, horario in safe_locations:
        with st.container():
            st.markdown(f'<div class="safe-zone">', unsafe_allow_html=True)
            st.write(f"**{nombre}**")
            st.write(f"⏰ {horario}")
            st.write(f"📍 A 150m de tu ubicación")
            if st.button(f"🚶 Navegar a {nombre}", key=nombre, use_container_width=True):
                st.info(f"🗺️ Calculando ruta a {nombre}...")
            st.markdown('</div>', unsafe_allow_html=True)

with tab6:
    st.title("👤 PERFIL")
    
    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre", "Usuario")
            edad = st.number_input("Edad", min_value=18, max_value=100, value=25)
        with col2:
            telefono = st.text_input("Teléfono", "+51 999888777")
            email = st.text_input("Email", "usuario@example.com")
        
        st.subheader("📞 CONTACTOS EMERGENCIA")
        emergencia1 = st.text_input("Contacto 1", st.session_state.emergency_contacts['contacto1'])
        emergencia2 = st.text_input("Contacto 2", st.session_state.emergency_contacts['contacto2'])
        
        st.subheader("🏥 INFORMACIÓN MÉDICA")
        grupo_sanguineo = st.selectbox("Grupo Sanguíneo", ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])
        condiciones = st.text_area("Condiciones médicas o alergias", "Ninguna")
        
        if st.form_submit_button("💾 GUARDAR PERFIL", use_container_width=True):
            st.session_state.emergency_contacts = {
                'contacto1': emergencia1,
                'contacto2': emergencia2
            }
            st.success("✅ Perfil actualizado")

with tab7:
    st.title("🧠 ANÁLISIS PREDICTIVO")
    
    st.info("""
    **PATRONES DETECTADOS:**
    - Viernes 18:00-22:00: 70% más robos
    - Zona Centro: 85% más incidentes días de pago  
    - Parques nocturnos: 45% más reportes de acoso
    - Transporte público: 60% riesgo en horas pico
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("PRECISIÓN", "87%", "2%")
    with col2:
        st.metric("ALERTAS", "24", "+5")

st.markdown('</div>', unsafe_allow_html=True)