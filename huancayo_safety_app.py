import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap
import random
import time
import webbrowser

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

# --- ESTILOS CSS ---
st.markdown("""
<style>
    .stApp { max-width: 390px; height: 844px; margin: 0 auto; padding: 0; background: #0d1b2a; color: #ffffff; }
    .panic-button {
        background: linear-gradient(135deg, #1abc9c, #16a085);
        color: #ffffff;
        border-radius: 50%;
        width: 180px;
        height: 180px;
        font-size: 28px;
        font-weight: bold;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 50px auto;
        box-shadow: 0 0 25px #1abc9c;
        border: 3px solid #ffffff;
        transition: transform 0.2s;
    }
    .panic-button:hover { transform: scale(1.1); }
    .metric-card { background: #112d3c; padding: 8px; border-radius: 8px; text-align: center; font-size: 11px; margin:5px 0;}
    .warning-alert { background: #e63946; color: #ffffff; padding: 12px; border-radius: 8px; margin: 8px 0; font-size: 14px; }
    .safe-zone { background: #1f4068; padding: 10px; border-radius: 8px; margin: 6px 0; color: #ffffff;}
</style>
""", unsafe_allow_html=True)

# --- SESIÓN ---
if 'panic_active' not in st.session_state:
    st.session_state.panic_active = False
if 'emergency_number' not in st.session_state:
    st.session_state.emergency_number = "+51999888777"

# --- FUNCIONES ---
def check_risk_zone(lat, lon):
    return {'nombre': 'Av. Ferrocarril', 'incidentes': 3, 'nivel': 'Alto', 'horario': 'última hora'}

def trigger_whatsapp(number, message):
    url = f"https://wa.me/{number.replace('+','')}/?text={message}"
    webbrowser.open(url)

# --- PESTAÑAS ---
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
    st.title("🛡️ SEGURIDAD HUANCAYO")
    
    # Zona de riesgo
    zona_riesgo = check_risk_zone(-12.065, -75.210)
    st.markdown(f'<div class="warning-alert">⚠️ Zona de riesgo: {zona_riesgo["nombre"]}</div>', unsafe_allow_html=True)
    
    # Botón de pánico gigante
    if st.button("🚨 PÁNICO", key="panic_main"):
        message = f"🚨 EMERGENCIA! Ubicación aproximada: https://maps.google.com/?q=-12.065,-75.210"
        trigger_whatsapp(st.session_state.emergency_number, message)
        st.session_state.panic_active = True
        st.success("¡Alerta enviada a WhatsApp!")

    # Estadísticas
    col1, col2, col3 = st.columns(3)
    with col1: st.markdown('<div class="metric-card">📊<br><strong>12</strong><br>Incidentes</div>', unsafe_allow_html=True)
    with col2: st.markdown('<div class="metric-card">🛡️<br><strong>8</strong><br>Zonas Seguras</div>', unsafe_allow_html=True)
    with col3: st.markdown('<div class="metric-card">⚠️<br><strong>3</strong><br>Alertas</div>', unsafe_allow_html=True)

# ---------------- PESTAÑA MAPA ----------------
with tabs[1]:
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

# ---------------- PESTAÑA REPORTAR ----------------
with tabs[2]:
    st.title("📢 REPORTAR INCIDENTE")
    with st.form("report_form"):
        tipo_incidente = st.selectbox("Tipo de Incidente", ["Robo","Acoso","Persona Sospechosa","Asalto","Accidente","Otro"])
        ubicacion = st.text_input("Ubicación aproximada", "Cerca de...")
        descripcion = st.text_area("Descripción del incidente", "Describa lo que sucedió...")
        submitted = st.form_submit_button("📤 ENVIAR REPORTE")
        if submitted:
            st.success("Reporte enviado correctamente")

# ---------------- PESTAÑA ZONAS ----------------
with tabs[3]:
    st.title("🏪 ZONAS SEGURAS")
    for lat, lon, nombre, horario in safe_locations:
        st.markdown(f'<div class="safe-zone">**{nombre}** ⏰ {horario}</div>', unsafe_allow_html=True)

# ---------------- PESTAÑA PERFIL ----------------
with tabs[4]:
    st.title("👤 PERFIL")
    with st.form("profile_form"):
        nombre = st.text_input("Nombre", "Usuario")
        emergencia_num = st.text_input("Contacto de emergencia", st.session_state.emergency_number)
        if st.form_submit_button("💾 GUARDAR PERFIL"):
            st.session_state.emergency_number = emergencia_num
            st.success("Perfil actualizado")

# ---------------- PESTAÑA ANÁLISIS ----------------
with tabs[5]:
    st.title("🧠 ANÁLISIS PREDICTIVO")
    st.info("""
    **PATRONES DETECTADOS:**
    - Viernes 18:00-22:00: 70% más robos
    - Zona Centro: 85% más incidentes días de pago  
    - Parques nocturnos: 45% más reportes de acoso
    - Transporte público: 60% riesgo en horas pico
    """)

