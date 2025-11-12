import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap, MeasureControl
import random
import time
from datetime import datetime, timedelta

# Configuración de la página
st.set_page_config(page_title="Huancayo Safety App", page_icon="🛡️", layout="centered")

# --- SIMULACIÓN DE DATOS MEJORADA ---
danger_points = [
    (-12.065, -75.210, 'Alta', 'Robo'),
    (-12.067, -75.212, 'Media', 'Acoso'),
    (-12.064, -75.214, 'Baja', 'Sospechoso'),
    (-12.063, -75.209, 'Alta', 'Asalto'),
    (-12.062, -75.215, 'Media', 'Robo'),
]

# Lugares seguros (comercios aliados)
safe_locations = [
    (-12.065, -75.211, 'Farmacia Segura', '24/7'),
    (-12.066, -75.213, 'Restaurante Refugio', '6 AM - 11 PM'),
    (-12.068, -75.209, 'Tienda Amiga', '8 AM - 10 PM'),
]

# Incidentes recientes simulados
recent_incidents = [
    {'tipo': 'Robo', 'ubicacion': 'Av. Ferrocarril', 'hora': 'Hace 15 min', 'verificada': True},
    {'tipo': 'Acoso', 'ubicacion': 'Parque Huamanmarca', 'hora': 'Hace 30 min', 'verificada': False},
    {'tipo': 'Sospechoso', 'ubicacion': 'Calle Real', 'hora': 'Hace 45 min', 'verificada': True},
]

# Estilos CSS MINIMALISTA BLANCO Y NEGRO
st.markdown("""
<style>
    .stApp {
        max-width: 380px; 
        margin: auto; 
        border: 2px solid #000000; 
        border-radius: 20px; 
        padding: 10px;
        background: #ffffff;
        color: #000000;
    }
    .stSidebar {
        background: #ffffff;
    }
    .emergency-button {
        background: #000000;
        color: #ffffff;
        border: 2px solid #000000;
        padding: 20px;
        border-radius: 25px;
        font-size: 18px;
        font-weight: bold;
        margin: 10px 0;
        width: 100%;
    }
    .safe-zone {
        background: #f8f9fa;
        color: #000000;
        padding: 15px;
        border-radius: 10px;
        margin: 8px 0;
        border: 1px solid #000000;
    }
    .warning-alert {
        background: #000000;
        color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border: 1px solid #000000;
    }
    .predictive-analysis {
        background: #f8f9fa;
        color: #000000;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border: 1px solid #000000;
        border-left: 4px solid #000000;
    }
    .section-divider {
        border: 0.5px solid #000000;
        margin: 20px 0;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 10px;
        border-radius: 10px;
        border: 1px solid #000000;
        text-align: center;
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
if 'location_history' not in st.session_state:
    st.session_state.location_history = []
if 'last_location_sent' not in st.session_state:
    st.session_state.last_location_sent = datetime.now()

# --- FUNCIONES ---
def check_risk_zone(lat, lon):
    zona_riesgo = {
        'nombre': 'Av. Ferrocarril',
        'incidentes': 3,
        'nivel': 'Alto',
        'horario': 'última hora'
    }
    return zona_riesgo

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

def enviar_ubicacion_periodica():
    if st.session_state.panic_active:
        tiempo_transcurrido = datetime.now() - st.session_state.last_location_sent
        if tiempo_transcurrido.seconds >= 30:
            st.session_state.last_location_sent = datetime.now()
            return True
    return False

# --- BARRA DE NAVEGACIÓN MINIMALISTA ---
st.sidebar.markdown("## NAVEGACIÓN")
menu_options = ["PRINCIPAL", "MAPA", "PÁNICO", "REPORTAR", "ZONAS SEGURAS", "PERFIL", "ANÁLISIS"]
page = st.sidebar.radio("", menu_options)

# --- BOTÓN DE PÁNICO GLOBAL ---
st.sidebar.markdown("---")
if st.sidebar.button("🚨 BOTÓN DE PÁNICO", use_container_width=True):
    st.session_state.page = "PÁNICO"
    st.rerun()

# --- PÁGINA PRINCIPAL ---
if page == "PRINCIPAL":
    st.title("🛡️ SEGURIDAD HUANCAYO")
    
    # Notificación de zona de riesgo
    zona_riesgo = check_risk_zone(-12.065, -75.210)
    st.markdown(f'<div class="warning-alert">⚠️ Zona de riesgo: {zona_riesgo["nombre"]}. {zona_riesgo["incidentes"]} incidentes en la {zona_riesgo["horario"]}.</div>', unsafe_allow_html=True)
    
    # Estadísticas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="metric-card">Incidentes Hoy<br><strong>12</strong></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card">Zonas Seguras<br><strong>8</strong></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card">Alertas Activas<br><strong>3</strong></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # Accesos rápidos
    st.subheader("ACCIONES RÁPIDAS")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📱 CONTACTOS", use_container_width=True):
            st.session_state.page = "PERFIL"
    with col2:
        if st.button("🏪 LUGARES SEGUROS", use_container_width=True):
            st.session_state.page = "ZONAS SEGURAS"
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # Incidentes recientes
    st.subheader("INCIDENTES RECIENTES")
    for incident in recent_incidents:
        verified = "✅" if incident['verificada'] else "⏳"
        st.write(f"{verified} **{incident['tipo']}** - {incident['ubicacion']} ({incident['hora']})")

# --- MAPA SEGURO ---
elif page == "MAPA":
    st.title("🗺️ MAPA DE SEGURIDAD")
    
    # Filtros
    col1, col2 = st.columns(2)
    with col1:
        show_heatmap = st.checkbox("Mapa de Calor", value=True)
    with col2:
        show_safe_zones = st.checkbox("Zonas Seguras", value=True)
    
    # Crear mapa
    m = folium.Map(location=[-12.065, -75.210], zoom_start=15)
    
    # Heatmap
    if show_heatmap:
        heat_data = []
        for lat, lon, nivel, _ in danger_points:
            weight = 0.8 if nivel == 'Alta' else 0.5 if nivel == 'Media' else 0.2
            heat_data.append([lat, lon, weight])
        HeatMap(heat_data, radius=25, blur=15, max_zoom=13).add_to(m)
    
    # Marcadores de peligro
    for lat, lon, nivel, tipo in danger_points:
        color = "red" if nivel == "Alta" else "orange" if nivel == "Media" else "yellow"
        folium.CircleMarker(
            [lat, lon],
            radius=10,
            popup=f"⚠️ {tipo} - Riesgo {nivel}",
            tooltip=f"Riesgo {nivel}",
            color=color,
            fill=True,
            fillOpacity=0.7
        ).add_to(m)
    
    # Lugares seguros
    if show_safe_zones:
        for lat, lon, nombre, horario in safe_locations:
            folium.Marker(
                [lat, lon],
                popup=f"🏪 {nombre}\n⏰ {horario}",
                tooltip="Lugar Seguro",
                icon=folium.Icon(color="green", icon="home", prefix="fa")
            ).add_to(m)
    
    MeasureControl().add_to(m)
    st_folium(m, width=320, height=500)

# --- BOTÓN DE PÁNICO ---
elif page == "PÁNICO":
    st.title("🚨 BOTÓN DE PÁNICO")
    
    with st.expander("CONFIGURAR CONTACTOS"):
        contacto1 = st.text_input("Contacto Principal", "+51 999888777")
        contacto2 = st.text_input("Contacto Secundario", "+51 988777666")
    
    with st.expander("INFORMACIÓN MÉDICA"):
        grupo_sanguineo = st.selectbox("Grupo Sanguíneo", ["No especificado", "A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])
        alergias = st.text_input("Alergias o condiciones médicas")
    
    if not st.session_state.panic_active:
        if st.button("🔴 ACTIVAR BOTÓN DE PÁNICO", use_container_width=True):
            st.session_state.panic_active = True
            st.session_state.panic_countdown = 3
            st.rerun()
    else:
        if st.session_state.panic_countdown > 0:
            st.warning(f"🕒 La alerta se activará en {st.session_state.panic_countdown} segundos...")
            st.session_state.panic_countdown -= 1
            time.sleep(1)
            st.rerun()
        else:
            st.error("🚨 ¡ALERTA DE EMERGENCIA ACTIVADA!")
            
            my_lat = -12.065 + random.uniform(-0.001, 0.001)
            my_lon = -75.210 + random.uniform(-0.001, 0.001)
            
            if enviar_ubicacion_periodica():
                st.info("📍 Ubicación enviada a contactos")
            
            st.success(f"""
            ✅ Alerta enviada a:
            • {contacto1}
            • {contacto2}
            
            📍 Tu ubicación: {my_lat:.5f}, {my_lon:.5f}
            🩸 Grupo sanguíneo: {grupo_sanguineo}
            """)
            
            # Mapa de emergencia
            m = folium.Map(location=[my_lat, my_lon], zoom_start=17)
            folium.Marker([my_lat, my_lon], popup="🚨 PERSONA EN PELIGRO", icon=folium.Icon(color="red")).add_to(m)
            folium.Circle([my_lat, my_lon], radius=50, color="red", fill=True, opacity=0.6).add_to(m)
            
            for lat, lon, nombre, horario in safe_locations:
                folium.Marker([lat, lon], popup=f"🏪 {nombre}", icon=folium.Icon(color="green")).add_to(m)
            
            st_folium(m, width=320, height=400)
            
            # Cancelación por deslizamiento
            st.warning("Desliza para cancelar la alerta")
            cancel_slider = st.slider("", 0, 100, 0, key="panic_slider")
            if cancel_slider > 80:
                st.session_state.panic_active = False
                st.success("✅ Alerta cancelada")
                st.rerun()

# --- REPORTAR INCIDENTE ---
elif page == "REPORTAR":
    st.title("📢 REPORTAR INCIDENTE")
    
    with st.form("report_form"):
        tipo_incidente = st.selectbox("Tipo de Incidente", ["Robo", "Acoso", "Persona Sospechosa", "Asalto", "Accidente", "Otro"])
        ubicacion = st.text_input("Ubicación aproximada", "Cerca de...")
        descripcion = st.text_area("Descripción del incidente", "Describa lo que sucedió...")
        submitted = st.form_submit_button("📤 ENVIAR REPORTE", use_container_width=True)
        
        if submitted:
            verificado, confirmaciones = verificar_incidente({'tipo': tipo_incidente, 'ubicacion': ubicacion})
            nuevo_reporte = {
                'tipo': tipo_incidente, 'ubicacion': ubicacion, 'descripcion': descripcion,
                'timestamp': datetime.now().strftime("%H:%M"), 'verificado': verificado, 'confirmaciones': confirmaciones
            }
            st.session_state.reports.append(nuevo_reporte)
            
            if verificado:
                st.success("✅ Reporte enviado y VERIFICADO")
            else:
                st.warning(f"⏳ Reporte enviado. {confirmaciones}/3 confirmaciones necesarias")

# --- ZONAS SEGURAS ---
elif page == "ZONAS SEGURAS":
    st.title("🏪 ZONAS SEGURAS")
    
    for lat, lon, nombre, horario in safe_locations:
        st.markdown(f'<div class="safe-zone">', unsafe_allow_html=True)
        st.write(f"**🏪 {nombre}**")
        st.write(f"⏰ {horario}")
        st.write(f"📍 A 150m de tu ubicación")
        if st.button(f"🚶 Cómo llegar a {nombre}", key=nombre):
            st.info(f"🗺️ Navegando hacia {nombre}...")
        st.markdown('</div>', unsafe_allow_html=True)

# --- PERFIL ---
elif page == "PERFIL":
    st.title("👤 PERFIL")
    
    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre", "Usuario")
            edad = st.number_input("Edad", min_value=18, max_value=100, value=25)
        with col2:
            telefono = st.text_input("Teléfono", "+51 999888777")
            email = st.text_input("Email", "usuario@example.com")
        
        st.subheader("CONTACTOS DE EMERGENCIA")
        emergencia1 = st.text_input("Contacto Emergencia 1", "+51 999888777")
        emergencia2 = st.text_input("Contacto Emergencia 2", "+51 988777666")
        
        st.subheader("INFORMACIÓN MÉDICA")
        grupo_sanguineo = st.selectbox("Grupo Sanguíneo", ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])
        condiciones = st.text_area("Condiciones médicas o alergias")
        
        if st.form_submit_button("💾 GUARDAR PERFIL", use_container_width=True):
            st.success("✅ Perfil actualizado")

# --- ANÁLISIS PREDICTIVO ---
elif page == "ANÁLISIS":
    st.title("🧠 ANÁLISIS PREDICTIVO")
    
    st.markdown('<div class="predictive-analysis">', unsafe_allow_html=True)
    st.write("**PATRONES DETECTADOS**")
    st.write(analizar_patrones())
    st.markdown('</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Precisión Predictiva", "87%", "2%")
    with col2:
        st.metric("Alertas Preventivas", "24", "+5")
    
    st.subheader("PATRONES HISTÓRICOS")
    st.write("• **Viernes 18:00-22:00**: 70% aumento en robos")
    st.write("• **Zona Centro**: 85% más incidentes días de pago")
    st.write("• **Parques nocturnos**: 45% más reportes de acoso")

# --- INSTRUCCIONES ---
st.sidebar.markdown("---")
st.sidebar.info("EJECUTAR: streamlit run huancayo_safety_app.py")