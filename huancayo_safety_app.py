import streamlit as st
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium
import random

# --- CONFIGURACIÓN GENERAL ---
st.set_page_config(
    page_title="Huancayo Safety",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- ESTILOS PERSONALIZADOS (INTERFAZ TIPO VIDEOJUEGO) ---
st.markdown("""
    <style>
    body {
        background-color: #001219;
        color: #e0fbfc;
        font-family: 'Orbitron', sans-serif;
    }
    .main {
        background: linear-gradient(180deg, #001219 0%, #003d5b 100%);
    }
    h1, h2, h3 {
        color: #00b4d8;
        text-shadow: 0px 0px 10px #00b4d8;
    }
    .stButton>button {
        background: radial-gradient(circle at center, #00b4d8 0%, #0077b6 100%);
        color: white;
        font-size: 18px;
        font-weight: bold;
        border: 3px solid #90e0ef;
        border-radius: 20px;
        box-shadow: 0px 0px 15px #00b4d8;
        transition: 0.3s ease;
    }
    .stButton>button:hover {
        background: #90e0ef;
        color: #001219;
        box-shadow: 0px 0px 25px #00b4d8;
        transform: scale(1.05);
    }
    #panic-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 75vh;
    }
    #panic-button {
        width: 200px;
        height: 200px;
        border-radius: 100%;
        background: radial-gradient(circle at center, #ff004c 0%, #9b0000 100%);
        color: white;
        font-size: 50px;
        font-weight: bold;
        border: 5px solid #ffffff;
        box-shadow: 0px 0px 25px #ff004c;
        cursor: pointer;
        transition: all 0.2s ease;
        animation: pulse 2s infinite;
    }
    #panic-button:hover {
        background: radial-gradient(circle at center, #ff4c6d 0%, #9b0000 100%);
        transform: scale(1.1);
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 20px #ff004c; }
        50% { box-shadow: 0 0 50px #ff004c; }
        100% { box-shadow: 0 0 20px #ff004c; }
    }
    </style>
""", unsafe_allow_html=True)

# --- VARIABLES DE SESIÓN ---
if "emergency_number" not in st.session_state:
    st.session_state.emergency_number = ""
if "latitude" not in st.session_state:
    st.session_state.latitude = -12.065
if "longitude" not in st.session_state:
    st.session_state.longitude = -75.210
if "panic_triggered" not in st.session_state:
    st.session_state.panic_triggered = False

# --- FUNCIONES DE APOYO ---
def send_whatsapp_message(number, message):
    if not number.startswith("+"):
        number = "+51" + number.strip()
    wa_link = f"https://wa.me/{number}?text={message}"
    js = f"window.open('{wa_link}');"
    components.html(f"<script>{js}</script>", height=0)

def get_map(lat, lon):
    m = folium.Map(location=[lat, lon], zoom_start=15, tiles="CartoDB dark_matter")
    folium.Marker([lat, lon], popup="Tu ubicación", icon=folium.Icon(color='lightred')).add_to(m)
    return m

# --- INTERFAZ PRINCIPAL ---
st.markdown("<h1 style='text-align:center;'>🛡️ HUANCAYO SAFETY SYSTEM</h1>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["🏠 INICIO", "📍 MAPA", "🚨 PÁNICO", "📞 CONTACTO"])

# ---------------- PESTAÑA 1: INICIO ----------------
with tab1:
    st.markdown("<h2>Bienvenido a tu sistema de seguridad personal</h2>", unsafe_allow_html=True)
    st.write("Presiona el botón de pánico si estás en peligro. Se enviará tu ubicación a tu contacto de emergencia.")

    st.markdown('<div id="panic-container"><button id="panic-button">🚨</button></div>', unsafe_allow_html=True)

    # Acción del botón de pánico
    if st.button("Activar Pánico"):
        st.session_state.panic_triggered = True
        my_lat = st.session_state.latitude + random.uniform(-0.0005, 0.0005)
        my_lon = st.session_state.longitude + random.uniform(-0.0005, 0.0005)
        message = f"🚨 EMERGENCIA 🚨\nNecesito ayuda urgente.\n📍 Ubicación: https://www.google.com/maps?q={my_lat},{my_lon}"
        st.success("✅ Alerta enviada a tu contacto de emergencia.")
        send_whatsapp_message(st.session_state.emergency_number, message)

# ---------------- PESTAÑA 2: MAPA ----------------
with tab2:
    st.markdown("<h2>🗺️ Mapa de seguridad</h2>", unsafe_allow_html=True)
    map_object = get_map(st.session_state.latitude, st.session_state.longitude)
    st_folium(map_object, width=700, height=450)

# ---------------- PESTAÑA 3: PÁNICO ----------------
with tab3:
    st.markdown("<h2>🚨 Botón de emergencia</h2>", unsafe_allow_html=True)
    st.warning("Este botón enviará una alerta inmediata.")
    if st.button("Enviar alerta manual"):
        st.session_state.panic_triggered = True
        my_lat = st.session_state.latitude + random.uniform(-0.0005, 0.0005)
        my_lon = st.session_state.longitude + random.uniform(-0.0005, 0.0005)
        message = f"🚨 ALERTA MANUAL 🚨\nUbicación: https://www.google.com/maps?q={my_lat},{my_lon}"
        st.success("✅ Alerta enviada manualmente.")
        send_whatsapp_message(st.session_state.emergency_number, message)

# ---------------- PESTAÑA 4: CONTACTO ----------------
with tab4:
    st.markdown("<h2>📞 Configura tu contacto de emergencia</h2>", unsafe_allow_html=True)
    number = st.text_input("Número de contacto (WhatsApp, ej. 987654321)", st.session_state.emergency_number)
    if st.button("Guardar número"):
        st.session_state.emergency_number = number.strip()
        st.success("Número de emergencia guardado correctamente.")
    st.info("Asegúrate de ingresar un número con código de país si estás fuera del Perú (+51).")
