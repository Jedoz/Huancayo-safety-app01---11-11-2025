import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap
import random
import time
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
/* Tamaño de celular Android */
.stApp {
    max-width: 420px;
    height: 800px;
    margin: auto;
    border-radius: 20px;
    padding: 0px;
    overflow: hidden;
}

/* Botón de pánico centrado y redondo */
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
    margin: 80px auto 20px auto;
}

/* Ajustes generales */
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

def get_user_location():
    # HTML + JS para obtener ubicación del GPS
    components.html("""
        <script>
        navigator.geolocation.getCurrentPosition(function(position) {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            document.querySelector('body').dataset.latitude = lat;
            document.querySelector('body').dataset.longitude = lon;
        });
        </script>
    """, height=0)

def send_whatsapp_message(number, message):
    url = f"https://wa.me/{number.replace('+','')}/?text={urllib.parse.quote(message)}"
    components.html(f'<script>window.open("{url}", "_blank")</script>', height=0)

# --- OBTENER UBICACIÓN ---
get_user_location()

# --- SECCIÓN INICIO ---
st.title("🛡️ SEGURIDAD HUANCAYO")
zona_riesgo = check_risk_zone(st.session_state.latitude, st.session_state.longitude)
st.warning(f"⚠️ Zona de riesgo: {zona_riesgo['nombre']}")

st.subheader("📋 INCIDENTES RECIENTES")
for incident in recent_incidents:
    verified = "✅" if incident['verificada'] else "⏳"
    st.write(f"{verified} **{incident['tipo']}** - {incident['ubicacion']}")
    st.caption(f"{incident['hora']}")

# --- FORMULARIO CONTACTO DE EMERGENCIA ---
st.subheader("📞 CONTACTO DE EMERGENCIA")
emergency_number = st.text_input("Número de emergencia (WhatsApp)", st.session_state.emergency_number)
st.session_state.emergency_number = emergency_number

# --- BOTÓN DE PÁNICO ---
st.markdown("""
<form action="#" method="get">
<button id="panic-button">🚨</button>
</form>
""", unsafe_allow_html=True)

# --- DETECCIÓN DEL BOTÓN ---
if st.button("Activar Pánico") or st.session_state.panic_triggered:
    st.session_state.panic_triggered = True
    
    my_lat = st.session_state.latitude + random.uniform(-0.0005,0.0005)
    my_lon = st.session_state.longitude + random.uniform(-0.0005,0.0005)
    
    message = f"🚨 ALERTA DE EMERGENCIA\n📍 Ubicación: https://www.google.com/maps/search/?api=1&query={my_lat},{my_lon}"
    
    st.success("✅ Alerta enviada. Redirigiendo a WhatsApp...")
    send_whatsapp_message(st.session_state.emergency_number, message)

# --- PESTAÑA MAPA ---
st.subheader("🗺️ MAPA DE SEGURIDAD")
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
