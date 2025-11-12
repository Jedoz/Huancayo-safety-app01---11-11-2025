import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap
import random
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Huancayo Safety App",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- DATOS SIMULADOS ---
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

# --- SESSION STATE ---
if 'panic_active' not in st.session_state:
    st.session_state.panic_active = False
if 'panic_countdown' not in st.session_state:
    st.session_state.panic_countdown = 0

# --- FUNCIONES ---
def check_risk_zone(lat, lon):
    return {'nombre': 'Av. Ferrocarril', 'incidentes': 3, 'nivel': 'Alto', 'horario': 'última hora'}

def verificar_incidente(reporte):
    confirmaciones_necesarias = 3
    confirmaciones_actuales = random.randint(0, confirmaciones_necesarias)
    return confirmaciones_actuales >= confirmaciones_necesarias, confirmaciones_actuales

# --- PESTAÑAS ---
st.markdown('<div style="padding:10px;">', unsafe_allow_html=True)
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
    zona_riesgo = check_risk_zone(-12.065, -75.210)
    st.warning(f"⚠️ Zona de riesgo: {zona_riesgo['nombre']}")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Incidentes", "12")
    col2.metric("Zonas Seguras", "8")
    col3.metric("Alertas", "3")
    
    if st.button("🚨 BOTÓN DE PÁNICO"):
        st.session_state.panic_active = True
        st.session_state.panic_countdown = 3
    
    st.subheader("📋 INCIDENTES RECIENTES")
    for incident in recent_incidents:
        verified = "✅" if incident['verificada'] else "⏳"
        st.write(f"{verified} **{incident['tipo']}** - {incident['ubicacion']}")
        st.caption(f"{incident['hora']}")

with tab2:
    st.title("🗺️ MAPA DE SEGURIDAD")
    show_heatmap = st.checkbox("Mapa Calor", value=True)
    show_safe_zones = st.checkbox("Zonas Seguras", value=True)

    m = folium.Map(location=[-12.065, -75.210], zoom_start=15)
    
    if show_heatmap:
        heat_data = [[lat, lon, 0.8 if nivel=='Alta' else 0.5 if nivel=='Media' else 0.2] for lat, lon, nivel, _ in danger_points]
        HeatMap(heat_data, radius=20, blur=10).add_to(m)
    
    for lat, lon, nivel, tipo in danger_points:
        color = "red" if nivel=="Alta" else "orange" if nivel=="Media" else "yellow"
        folium.CircleMarker([lat, lon], radius=6, popup=f"⚠️ {tipo}", color=color, fill=True).add_to(m)
    
    if show_safe_zones:
        for lat, lon, nombre, horario in safe_locations:
            folium.Marker([lat, lon], popup=f"🏪 {nombre}", icon=folium.Icon(color="green")).add_to(m)

    st_folium(m, width=350, height=400)

with tab3:
    st.title("🚨 BOTÓN DE PÁNICO")
    if not st.session_state.panic_active:
        st.info("EN CASO DE PELIGRO INMINENTE")
        if st.button("🔴 ACTIVAR BOTÓN DE PÁNICO"):
            st.session_state.panic_active = True
            st.session_state.panic_countdown = 3
            st.experimental_rerun()
    else:
        if st.session_state.panic_countdown > 0:
            st.warning(f"🕒 La alerta se activará en {st.session_state.panic_countdown} segundos...")
            st.session_state.panic_countdown -= 1
            time.sleep(1)
            st.experimental_rerun()
        else:
            st.error("🚨 ¡ALERTA DE EMERGENCIA ACTIVADA!")
            my_lat = -12.065 + random.uniform(-0.001,0.001)
            my_lon = -75.210 + random.uniform(-0.001,0.001)
            st.success(f"✅ Alerta enviada\n📍 Ubicación: {my_lat:.5f}, {my_lon:.5f}")

with tab4:
    st.title("📢 REPORTAR INCIDENTE")
    with st.form("report_form"):
        tipo_incidente = st.selectbox("Tipo de Incidente", ["Robo","Acoso","Persona Sospechosa","Asalto","Accidente","Otro"])
        ubicacion = st.text_input("Ubicación aproximada")
        descripcion = st.text_area("Descripción")
        submitted = st.form_submit_button("📤 ENVIAR REPORTE")
        if submitted:
            verificado, confirmaciones = verificar_incidente({'tipo': tipo_incidente, 'ubicacion': ubicacion})
            if verificado:
                st.success("✅ Reporte enviado y VERIFICADO")
            else:
                st.warning(f"⏳ Reporte enviado. {confirmaciones}/3 confirmaciones")

with tab5:
    st.title("🏪 ZONAS SEGURAS")
    for lat, lon, nombre, horario in safe_locations:
        st.info(f"{nombre}\n⏰ {horario}\n📍 A 150m de tu ubicación")

with tab6:
    st.title("👤 PERFIL")
    nombre = st.text_input("Nombre", "Usuario")
    edad = st.number_input("Edad", 18, 100, 25)
    telefono = st.text_input("Teléfono", "+51 999888777")
    email = st.text_input("Email", "usuario@example.com")
    grupo_sanguineo = st.selectbox("Grupo Sanguíneo", ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])
    condiciones = st.text_area("Condiciones médicas o alergias")
    if st.button("💾 GUARDAR PERFIL"):
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
    col1.metric("PRECISIÓN", "87%", "2%")
    col2.metric("ALERTAS", "24", "+5")
st.markdown('</div>', unsafe_allow_html=True)
