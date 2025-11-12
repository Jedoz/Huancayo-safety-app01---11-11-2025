import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap
import random
import urllib.parse
import streamlit.components.v1 as components

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Huancayo Safety App",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CSS PARA ANDROID Y BOTÓN PANICO ---
st.markdown("""
<style>
.stApp {
    max-width: 420px;
    height: 800px;
    margin: auto;
    border-radius: 20px;
    padding: 0px;
    overflow: hidden;
}
#panic-button {
    background-color: red;
    color: white;
    border: none;
    border-radius: 50%;
    width: 120px;
    height: 120px;
    font-size: 20px;
    font-weight: bold;
    display: block;
    margin: 40px auto 20px auto;
}
body {
    font-family: sans-serif;
}
</style>
""", unsafe_allow_html=True)

# --- DATOS SIMULADOS ---
danger_points = [
    (-12.065, -75.210, 'Alta', 'Robo'),
    (-12.067, -75.212, 'Media', 'Acoso'),
    (-12.064, -75.214, 'Baja', 'Sospechoso'),
]

safe_locations = [
    (-12.065, -75.211, 'Farmacia Segura', '24/7'),
    (-12.066, -75.213, 'Restaurante Refugio', '6 AM - 11 PM'),
]

recent_incidents = [
    {'tipo': 'Robo', 'ubicacion': 'Av. Ferrocarril', 'hora': 'Hace 15 min', 'verificada': True},
    {'tipo': 'Acoso', 'ubicacion': 'Parque Huamanmarca', 'hora': 'Hace 30 min', 'verificada': False},
]

# --- SESSION STATE ---
if 'latitude' not in st.session_state:
    st.session_state.latitude = -12.065
if 'longitude' not in st.session_state:
    st.session_state.longitude = -75.210
if 'emergency_number' not in st.session_state:
    st.session_state.emergency_number = "+51999888777"
if 'panic_triggered' not in st.session_state:
    st.session_state.panic_triggered = False

# --- FUNCIONES ---
def check_risk_zone(lat, lon):
    return {'nombre': 'Av. Ferrocarril', 'incidentes': 3, 'nivel': 'Alto', 'horario': 'última hora'}

def send_whatsapp_message(number, message):
    url = f"https://wa.me/{number.replace('+','')}/?text={urllib.parse.quote(message)}"
    components.html(f'<script>window.open("{url}", "_blank")</script>', height=0)

# --- PESTAÑAS ---
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🏠 INICIO",
    "🗺️ MAPA",
    "🚨 PÁNICO",
    "📢 REPORTAR",
    "🏪 ZONAS",
    "👤 PERFIL",
    "🧠 ANÁLISIS"
])

# ---------------- PESTAÑA 1: INICIO ----------------
with tab1:
    st.title("🛡️ SEGURIDAD HUANCAYO")
    zona_riesgo = check_risk_zone(st.session_state.latitude, st.session_state.longitude)
    st.warning(f"⚠️ Zona de riesgo: {zona_riesgo['nombre']}")

    st.subheader("📋 INCIDENTES RECIENTES")
    for incident in recent_incidents:
        verified = "✅" if incident['verificada'] else "⏳"
        st.write(f"{verified} **{incident['tipo']}** - {incident['ubicacion']}")
        st.caption(f"{incident['hora']}")

    # --- BOTÓN DE PÁNICO CIRCULAR EN INICIO ---
    st.subheader("🚨 BOTÓN DE PÁNICO")
    st.subheader("📞 CONTACTO DE EMERGENCIA")
    emergency_number = st.text_input("Número de emergencia (WhatsApp)", st.session_state.emergency_number)
    st.session_state.emergency_number = emergency_number

    st.markdown("""
    <form action="#" method="get">
    <button id="panic-button">🚨</button>
    </form>
    """, unsafe_allow_html=True)

    if st.button("Activar Pánico") or st.session_state.panic_triggered:
        st.session_state.panic_triggered = True
        my_lat = st.session_state.latitude + random.uniform(-0.0005,0.0005)
        my_lon = st.session_state.longitude + random.uniform(-0.0005,0.0005)
        message = f"🚨 ALERTA DE EMERGENCIA\n📍 Ubicación: https://www.google.com/maps/search/?api=1&query={my_lat},{my_lon}"
        st.success("✅ Alerta enviada. Redirigiendo a WhatsApp...")
        send_whatsapp_message(st.session_state.emergency_number, message)

# ---------------- PESTAÑA 2: MAPA ----------------
with tab2:
    st.title("🗺️ MAPA DE SEGURIDAD")
    show_heatmap = st.checkbox("Mostrar HeatMap", value=True)
    show_safe_zones = st.checkbox("Mostrar Zonas Seguras", value=True)

    m = folium.Map(location=[st.session_state.latitude, st.session_state.longitude], zoom_start=15)

    if show_heatmap:
        heat_data = [[lat, lon, 0.8 if nivel=='Alta' else 0.5 if nivel=='Media' else 0.2] for lat, lon, nivel, _ in danger_points]
        HeatMap(heat_data, radius=20, blur=10).add_to(m)

    for lat, lon, nivel, tipo in danger_points:
        color = "red" if nivel=="Alta" else "orange" if nivel=="Media" else "yellow"
        folium.CircleMarker([lat, lon], radius=6, popup=f"⚠️ {tipo}", color=color, fill=True).add_to(m)

    if show_safe_zones:
        for lat, lon, nombre, horario in safe_locations:
            folium.Marker([lat, lon], popup=f"🏪 {nombre}", icon=folium.Icon(color="green")).add_to(m)

    st_folium(m, width=380, height=400)

# ---------------- PESTAÑA 3: PÁNICO ----------------
with tab3:
    st.title("🚨 PÁNICO")
    st.info("El botón de pánico principal está en la pestaña Inicio.")

# ---------------- PESTAÑA 4: REPORTAR ----------------
with tab4:
    st.title("📢 REPORTAR INCIDENTE")
    with st.form("report_form"):
        tipo_incidente = st.selectbox("Tipo de Incidente",
                                      ["Robo", "Acoso", "Persona Sospechosa", "Asalto", "Accidente", "Otro"])
        ubicacion = st.text_input("Ubicación aproximada", "Cerca de...")
        descripcion = st.text_area("Descripción del incidente", "Describa lo que sucedió...")
        submitted = st.form_submit_button("📤 ENVIAR REPORTE")
        if submitted:
            st.success("✅ Reporte enviado")

# ---------------- PESTAÑA 5: ZONAS ----------------
with tab5:
    st.title("🏪 ZONAS SEGURAS")
    for lat, lon, nombre, horario in safe_locations:
        st.markdown(f"**{nombre}** ⏰ {horario} 📍 A 150m de tu ubicación")

# ---------------- PESTAÑA 6: PERFIL ----------------
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
        grupo_sanguineo = st.selectbox("Grupo Sanguíneo", ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])
        condiciones = st.text_area("Condiciones médicas o alergias")
        if st.form_submit_button("💾 GUARDAR PERFIL"):
            st.success("✅ Perfil actualizado")

# ---------------- PESTAÑA 7: ANÁLISIS ----------------
with tab7:
    st.title("🧠 ANÁLISIS PREDICTIVO")
    st.info("""
    **PATRONES DETECTADOS:**
    - Viernes 18:00-22:00: 70% más robos
    - Zona Centro: 85% más incidentes días de pago
    - Parques nocturnos: 45% más reportes de acoso
    - Transporte público: 60% riesgo en horas pico
    """)
