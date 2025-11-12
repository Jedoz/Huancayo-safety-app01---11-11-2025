import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap, MeasureControl
import random
import time
from datetime import datetime, timedelta

# Configuración de la página para tamaño real de celular
st.set_page_config(
    page_title="Huancayo Safety App", 
    page_icon="🛡️", 
    layout="centered",
    initial_sidebar_state="collapsed"  # Menú colapsado por defecto
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

# Estilos CSS para tamaño real de celular
st.markdown("""
<style>
    /* Tamaño real de celular - iPhone 12 Pro */
    .stApp {
        max-width: 390px;
        height: 844px;
        margin: auto;
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
    
    /* Menú hamburguesa */
    .menu-button {
        position: fixed;
        top: 15px;
        left: 15px;
        z-index: 9999;
        background: #000000;
        color: white;
        border: none;
        border-radius: 50%;
        width: 45px;
        height: 45px;
        font-size: 20px;
        cursor: pointer;
    }
    
    /* Sidebar estilo móvil */
    .stSidebar {
        background: #ffffff !important;
        border-right: 2px solid #000000;
    }
    
    /* Botones minimalistas */
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
        font-size: 12px;
    }
    
    /* Ajustar contenido al tamaño del celular */
    .main-content {
        padding: 15px;
        height: calc(100vh - 60px);
        overflow-y: auto;
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
if 'show_menu' not in st.session_state:
    st.session_state.show_menu = False

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

# --- MENÚ HAMBURGUESA DINÁMICO ---
st.markdown("""
<button class="menu-button" onclick="toggleMenu()">☰</button>
<script>
function toggleMenu() {
    // Streamlit no permite JavaScript directo, usamos session state
    window.parent.postMessage({type: 'streamlit:setComponentValue', value: 'toggle_menu'}, '*');
}
</script>
""", unsafe_allow_html=True)

# Toggle menu con botón de Streamlit
col1, col2, col3 = st.columns([1, 6, 1])
with col1:
    if st.button("☰", key="menu_toggle"):
        st.session_state.show_menu = not st.session_state.show_menu

# Mostrar/ocultar sidebar basado en session state
if st.session_state.show_menu:
    with st.sidebar:
        st.markdown("## 📱 MENÚ")
        st.markdown("---")
        
        menu_options = {
            "🏠 PRINCIPAL": "PRINCIPAL",
            "🗺️ MAPA": "MAPA", 
            "🚨 PÁNICO": "PÁNICO",
            "📢 REPORTAR": "REPORTAR",
            "🏪 ZONAS SEGURAS": "ZONAS SEGURAS",
            "👤 PERFIL": "PERFIL",
            "🧠 ANÁLISIS": "ANÁLISIS"
        }
        
        selected = st.radio("Navegación", list(menu_options.keys()))
        page = menu_options[selected]
        
        st.markdown("---")
        if st.button("❌ CERRAR MENÚ"):
            st.session_state.show_menu = False
            st.rerun()
else:
    page = st.session_state.get('current_page', 'PRINCIPAL')

# --- CONTENIDO PRINCIPAL ---
st.markdown('<div class="main-content">', unsafe_allow_html=True)

if page == "PRINCIPAL":
    st.title("🛡️ SEGURIDAD HUANCAYO")
    
    zona_riesgo = check_risk_zone(-12.065, -75.210)
    st.markdown(f'<div class="warning-alert">⚠️ Zona de riesgo: {zona_riesgo["nombre"]}</div>', unsafe_allow_html=True)
    
    # Estadísticas compactas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="metric-card">📊<br>12</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card">🛡️<br>8</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card">⚠️<br>3</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # Botones de acción principales
    if st.button("🚨 BOTÓN DE PÁNICO", use_container_width=True, type="primary"):
        page = "PÁNICO"
        st.session_state.show_menu = False
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗺️ VER MAPA", use_container_width=True):
            page = "MAPA"
            st.session_state.show_menu = False
    with col2:
        if st.button("📢 REPORTAR", use_container_width=True):
            page = "REPORTAR" 
            st.session_state.show_menu = False
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # Incidentes recientes
    st.subheader("📋 INCIDENTES")
    for incident in recent_incidents:
        verified = "✅" if incident['verificada'] else "⏳"
        st.write(f"{verified} **{incident['tipo']}**")
        st.caption(f"{incident['ubicacion']} ({incident['hora']})")

elif page == "MAPA":
    st.title("🗺️ MAPA")
    
    m = folium.Map(location=[-12.065, -75.210], zoom_start=15, width=350, height=500)
    
    # Heatmap
    heat_data = []
    for lat, lon, nivel, _ in danger_points:
        weight = 0.8 if nivel == 'Alta' else 0.5 if nivel == 'Media' else 0.2
        heat_data.append([lat, lon, weight])
    HeatMap(heat_data, radius=20, blur=10).add_to(m)
    
    # Marcadores
    for lat, lon, nivel, tipo in danger_points:
        color = "red" if nivel == "Alta" else "orange" if nivel == "Media" else "yellow"
        folium.CircleMarker([lat, lon], radius=8, popup=f"⚠️ {tipo}", color=color, fill=True).add_to(m)
    
    for lat, lon, nombre, horario in safe_locations:
        folium.Marker([lat, lon], popup=f"🏪 {nombre}", icon=folium.Icon(color="green")).add_to(m)
    
    st_folium(m, width=350, height=500)

elif page == "PÁNICO":
    st.title("🚨 EMERGENCIA")
    
    if not st.session_state.panic_active:
        st.error("EN CASO DE PELIGRO INMINENTE")
        
        with st.expander("CONTACTOS"):
            contacto1 = st.text_input("Contacto 1", "+51 999888777")
            contacto2 = st.text_input("Contacto 2", "+51 988777666")
        
        if st.button("🔴 ACTIVAR BOTÓN DE PÁNICO", use_container_width=True, type="primary"):
            st.session_state.panic_active = True
            st.session_state.panic_countdown = 3
            st.rerun()
    else:
        if st.session_state.panic_countdown > 0:
            st.warning(f"🕒 Activando en {st.session_state.panic_countdown}...")
            st.session_state.panic_countdown -= 1
            time.sleep(1)
            st.rerun()
        else:
            st.error("🚨 ALERTA ACTIVADA")
            st.success("Ubicación y alertas enviadas a contactos")
            
            if st.button("🟢 CANCELAR ALERTA", use_container_width=True):
                st.session_state.panic_active = False
                st.rerun()

elif page == "REPORTAR":
    st.title("📢 REPORTAR")
    
    with st.form("report_form"):
        tipo = st.selectbox("TIPO", ["Robo", "Acoso", "Persona Sospechosa", "Asalto", "Accidente"])
        ubicacion = st.text_input("UBICACIÓN", "Cerca de...")
        descripcion = st.text_area("DESCRIPCIÓN", "Describa lo que sucedió...")
        
        if st.form_submit_button("📤 ENVIAR REPORTE", use_container_width=True):
            st.success("Reporte enviado para verificación")

elif page == "ZONAS SEGURAS":
    st.title("🏪 ZONAS SEGURAS")
    
    for lat, lon, nombre, horario in safe_locations:
        with st.container():
            st.markdown(f'<div class="safe-zone">', unsafe_allow_html=True)
            st.write(f"**{nombre}**")
            st.write(f"⏰ {horario}")
            if st.button(f"📍 Navegar a {nombre}", key=nombre, use_container_width=True):
                st.info("Calculando ruta...")
            st.markdown('</div>', unsafe_allow_html=True)

elif page == "PERFIL":
    st.title("👤 PERFIL")
    
    with st.form("profile_form"):
        nombre = st.text_input("NOMBRE", "Usuario")
        telefono = st.text_input("TELÉFONO", "+51 999888777")
        
        st.subheader("CONTACTOS EMERGENCIA")
        emergencia1 = st.text_input("CONTACTO 1", "+51 999888777")
        emergencia2 = st.text_input("CONTACTO 2", "+51 988777666")
        
        if st.form_submit_button("💾 GUARDAR", use_container_width=True):
            st.success("Perfil actualizado")

elif page == "ANÁLISIS":
    st.title("🧠 ANÁLISIS")
    
    st.info("""
    **PATRONES DETECTADOS:**
    - Viernes 18:00-22:00: 70% más robos
    - Zona Centro: 85% más incidentes
    - Parques nocturnos: 45% más acoso
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("PRECISIÓN", "87%")
    with col2:
        st.metric("ALERTAS", "24")

st.markdown('</div>', unsafe_allow_html=True)

# Actualizar página actual
st.session_state.current_page = page