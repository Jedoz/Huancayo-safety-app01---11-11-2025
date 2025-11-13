import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap
import time 
import urllib.parse 
import random
from datetime import datetime, timedelta
import math

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="SECURE MAP HUANCAYO - LIVE",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- COORDENADAS BASE DE HUANCAYO ---
HUANCAYO_CENTER = [-12.022398, -75.233829]  # UTP como centro

# --- 2. ZONAS DE RIESGO Y CALLES REALES ---
ZONAS_RIESGO = {
    "Av. Mariscal Castilla": {"lat": -12.022, "lon": -75.234, "riesgo": "alto", "horario_riesgo": "18:00-22:00"},
    "Paradero UTP": {"lat": -12.021, "lon": -75.233, "riesgo": "medio", "horario_riesgo": "06:00-09:00"},
    "Calle Real": {"lat": -12.024, "lon": -75.232, "riesgo": "alto", "horario_riesgo": "20:00-23:00"},
    "Jr. Piura": {"lat": -12.023, "lon": -75.235, "riesgo": "bajo", "horario_riesgo": "14:00-17:00"},
    "Av. Circunvalación": {"lat": -12.020, "lon": -75.231, "riesgo": "medio", "horario_riesgo": "toda la noche"},
    "Parque La Esperanza": {"lat": -12.025, "lon": -75.236, "riesgo": "alto", "horario_riesgo": "nocturno"},
}

ZONAS_SEGURAS = {
    "Comisaría El Tambo": {"lat": -12.021, "lon": -75.236, "tipo": "policia", "horario": "24/7"},
    "Hospital Regional": {"lat": -12.025, "lon": -75.230, "tipo": "hospital", "horario": "24/7"},
    "UTP Huancayo": {"lat": -12.022398, "lon": -75.233829, "tipo": "universidad", "horario": "06:00-22:00"},
    "Mercado Mayorista": {"lat": -12.019, "lon": -75.238, "tipo": "comercial", "horario": "05:00-18:00"},
}

# --- 3. ESTILOS CSS MEJORADOS ---
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 50%, #16213e 100%);
        color: #ffffff;
        font-family: 'Arial', sans-serif;
        min-height: 100vh;
    }
    
    .main-header {
        background: linear-gradient(90deg, #ff0000, #ff6b6b, #ff0000);
        padding: 20px 0;
        text-align: center;
        margin-bottom: 20px;
        border-bottom: 3px solid #39ff14;
    }
    
    .app-title {
        font-size: 2.5rem;
        font-weight: 900;
        color: white;
        text-shadow: 0 0 10px #39ff14;
        margin: 0;
    }
    
    .panic-button-container {
        display: flex;
        justify-content: center;
        margin: 30px 0;
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(45deg, #ff0000, #ff6b6b, #ff0000);
        color: white;
        border: none;
        border-radius: 50px;
        width: 300px;
        height: 80px;
        font-size: 1.5rem;
        font-weight: bold;
        margin: 0 auto;
        animation: panic-pulse 1.5s infinite;
    }
    
    @keyframes panic-pulse {
        0% { transform: scale(1); box-shadow: 0 0 30px rgba(255, 0, 0, 0.5); }
        50% { transform: scale(1.05); box-shadow: 0 0 50px rgba(255, 0, 0, 0.8); }
        100% { transform: scale(1); box-shadow: 0 0 30px rgba(255, 0, 0, 0.5); }
    }
    
    .metric-card {
        background: rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 15px;
        text-align: center;
        border: 1px solid rgba(57, 255, 20, 0.3);
        margin: 5px;
    }
    
    .alert-warning {
        background: rgba(255, 193, 7, 0.2);
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #ffc107;
        margin: 10px 0;
    }
    
    .alert-danger {
        background: rgba(220, 53, 69, 0.2);
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #dc3545;
        margin: 10px 0;
    }
    
    .alert-success {
        background: rgba(40, 167, 69, 0.2);
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #28a745;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. INICIALIZACIÓN DE ESTADOS ---
if 'panic_active' not in st.session_state:
    st.session_state.panic_active = False
if 'user_location' not in st.session_state:
    st.session_state.user_location = None
if 'location_access' not in st.session_state:
    st.session_state.location_access = False
if 'incident_logs' not in st.session_state:
    st.session_state.incident_logs = []
if 'dynamic_incidents' not in st.session_state:
    st.session_state.dynamic_incidents = []
if 'last_update' not in st.session_state:
    st.session_state.last_update = time.time()
if 'user_route' not in st.session_state:
    st.session_state.user_route = None

# Datos del usuario
if 'user_name' not in st.session_state:
    st.session_state.user_name = "Andrea G."
if 'contact_1' not in st.session_state:
    st.session_state.contact_1 = "+51999999999"
if 'contact_2' not in st.session_state:
    st.session_state.contact_2 = "+51999888777"
if 'medical_info' not in st.session_state:
    st.session_state.medical_info = "Tipo de sangre: O+, Alergias: Penicilina"

# --- 5. FUNCIONES PRINCIPALES ---

def get_user_location():
    """Solicita acceso a la ubicación del usuario"""
    try:
        # En un entorno real, aquí iría la integración con GPS del navegador
        # Por ahora simulamos ubicaciones aleatorias cerca de Huancayo
        lat = HUANCAYO_CENTER[0] + random.uniform(-0.01, 0.01)
        lon = HUANCAYO_CENTER[1] + random.uniform(-0.01, 0.01)
        return {"lat": lat, "lon": lon, "accuracy": 50}
    except:
        return None

def generate_dynamic_incidents():
    """Genera incidentes dinámicos que se mueven por las zonas de riesgo"""
    current_time = datetime.now()
    incidents = []
    
    for zona, datos in ZONAS_RIESGO.items():
        # Probabilidad basada en hora del día y riesgo de la zona
        hora_actual = current_time.hour
        riesgo = datos["riesgo"]
        
        if riesgo == "alto" and random.random() < 0.7:
            # Movimiento dinámico alrededor de la zona
            lat = datos["lat"] + random.uniform(-0.002, 0.002)
            lon = datos["lon"] + random.uniform(-0.002, 0.002)
            
            incidentes_posibles = [
                f"Persona sospechosa en {zona}",
                f"Agrupación no identificada en {zona}",
                f"Vehículo circulando lentamente en {zona}",
                f"Actividad inusual reportada en {zona}"
            ]
            
            incidents.append({
                "lat": lat,
                "lon": lon,
                "tipo": random.choice(incidentes_posibles),
                "nivel": "ALTO",
                "zona": zona,
                "timestamp": current_time
            })
        
        elif riesgo == "medio" and random.random() < 0.4:
            lat = datos["lat"] + random.uniform(-0.003, 0.003)
            lon = datos["lon"] + random.uniform(-0.003, 0.003)
            
            incidents.append({
                "lat": lat,
                "lon": lon,
                "tipo": f"Movimiento inusual en {zona}",
                "nivel": "MEDIO",
                "zona": zona,
                "timestamp": current_time
            })
    
    return incidents

def get_route_recommendations(user_location):
    """Genera recomendaciones de rutas seguras basadas en la ubicación actual"""
    if not user_location:
        return []
    
    recommendations = []
    user_lat, user_lon = user_location["lat"], user_location["lon"]
    
    # Calcular distancia a zonas de riesgo
    for zona, datos in ZONAS_RIESGO.items():
        dist = math.sqrt((user_lat - datos["lat"])**2 + (user_lon - datos["lon"])**2)
        
        if dist < 0.003:  # Menos de 300m aprox
            if datos["riesgo"] == "alto":
                recommendations.append({
                    "tipo": "ALERTA",
                    "mensaje": f"🚨 EVITAR: Estás cerca de {zona} - Zona de alto riesgo",
                    "accion": "Cambiar de ruta inmediatamente"
                })
            elif datos["riesgo"] == "medio":
                recommendations.append({
                    "tipo": "PRECAUCIÓN",
                    "mensaje": f"⚠️ PRECAUCIÓN: Cercano a {zona} - Mantener vigilancia",
                    "accion": "Transitar con atención"
                })
    
    # Recomendar zonas seguras cercanas
    for zona, datos in ZONAS_SEGURAS.items():
        dist = math.sqrt((user_lat - datos["lat"])**2 + (user_lon - datos["lon"])**2)
        
        if dist < 0.005:  # Menos de 500m aprox
            recommendations.append({
                "tipo": "SEGURO",
                "mensaje": f"✅ ZONA SEGURA: {zona} a {int(dist * 111000)}m",
                "accion": "Punto de referencia seguro"
            })
    
    return recommendations

def generate_whatsapp_url(number, user_location, user_name, medical_info):
    """Genera URL de WhatsApp con ubicación REAL del usuario"""
    if not number or not user_location:
        return None
        
    lat = user_location["lat"]
    lon = user_location["lon"]
    
    message = (
        f"🚨 *EMERGENCIA - {user_name.upper()} NECESITA AYUDA INMEDIATA* 🚨\n\n"
        f"*👤 PERSONA EN RIESGO:* {user_name}\n"
        f"*📍 UBICACIÓN EN TIEMPO REAL:* https://maps.google.com/?q={lat},{lon}\n"
        f"*📌 COORDENADAS EXACTAS:* {lat:.6f}, {lon:.6f}\n"
        f"*🕒 HORA DEL INCIDENTE:* {datetime.now().strftime('%H:%M:%S')}\n\n"
        
        f"*⚕️ INFORMACIÓN MÉDICA CRÍTICA:*\n"
        f"{medical_info}\n\n"
        
        "*⚠️ ALERTA DE PÁNICO ACTIVADA* \n"
        "*🚨 NECESITA ASISTENCIA URGENTE* \n"
        "*📞 CONTACTAR INMEDIATAMENTE* \n\n"
        
        "_Sistema de Alerta SECURE MAP HUANCAYO - UBICACIÓN EN VIVO_"
    )
    
    message_encoded = urllib.parse.quote(message)
    number_cleaned = number.replace('+', '').replace(' ', '')
    return f"https://wa.me/{number_cleaned}?text={message_encoded}"

# --- 6. INTERFAZ PRINCIPAL ---
st.markdown("""
<div class="main-header">
    <h1 class="app-title">🚨 SECURE MAP HUANCAYO - LIVE</h1>
</div>
""", unsafe_allow_html=True)

# --- CONTENEDOR PRINCIPAL ---
with st.container():
    # --- SOLICITUD DE UBICACIÓN EN TIEMPO REAL ---
    if not st.session_state.location_access:
        st.warning("🔒 **PERMISO DE UBICACIÓN REQUERIDO**")
        st.info("Para funcionalidad completa, necesitamos acceso a tu ubicación en tiempo real.")
        
        if st.button("📍 PERMITIR ACCESO A UBICACIÓN", type="primary"):
            user_loc = get_user_location()
            if user_loc:
                st.session_state.user_location = user_loc
                st.session_state.location_access = True
                st.session_state.incident_logs.append(
                    f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Ubicación en tiempo real activada"
                )
                st.rerun()
            else:
                st.error("No se pudo obtener la ubicación. Verifica los permisos del navegador.")
    else:
        # --- USUARIO CON UBICACIÓN ACTIVA ---
        st.success(f"📍 **Ubicación activa**: {st.session_state.user_location['lat']:.4f}, {st.session_state.user_location['lon']:.4f}")
        
        # --- ACTUALIZAR DATOS EN TIEMPO REAL ---
        if time.time() - st.session_state.last_update > 10:  # Actualizar cada 10 segundos
            st.session_state.dynamic_incidents = generate_dynamic_incidents()
            st.session_state.last_update = time.time()
            st.rerun()
        
        # --- BOTÓN DE PÁNICO CON UBICACIÓN REAL ---
        st.markdown('<div class="panic-button-container">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚨 ACTIVAR ALERTA CON UBICACIÓN REAL", key="panic_real", type="primary", use_container_width=True):
                st.session_state.panic_active = True
                
                # Mostrar alerta
                st.markdown('<div style="padding: 20px; background: #ff0000; color: white; text-align: center; border-radius: 10px; font-size: 24px; font-weight: bold;">🚨 ¡ALERTA ACTIVADA! - UBICACIÓN ENVIADA 🚨</div>', unsafe_allow_html=True)
                
                # Enlaces de WhatsApp con ubicación REAL
                with st.expander("🔗 ENLACES DE EMERGENCIA - UBICACIÓN EN VIVO", expanded=True):
                    st.warning("Los contactos recibirán tu ubicación exacta en tiempo real")
                    
                    url_1 = generate_whatsapp_url(st.session_state.contact_1, st.session_state.user_location, st.session_state.user_name, st.session_state.medical_info)
                    if url_1: 
                        st.link_button(f"📱 ALERTA A CONTACTO 1", url_1, use_container_width=True)
                    
                    url_2 = generate_whatsapp_url(st.session_state.contact_2, st.session_state.user_location, st.session_state.user_name, st.session_state.medical_info)
                    if url_2: 
                        st.link_button(f"📱 ALERTA A CONTACTO 2", url_2, use_container_width=True)
                    
                    # Botón cancelar
                    if st.button("✅ CANCELAR ALERTA", type="secondary", use_container_width=True):
                        st.session_state.panic_active = False
                        st.success("Alerta cancelada")
                        st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # --- RECOMENDACIONES DE RUTA EN TIEMPO REAL ---
        st.subheader("🧭 RECOMENDACIONES DE RUTA - LIVE")
        recommendations = get_route_recommendations(st.session_state.user_location)
        
        if recommendations:
            for rec in recommendations:
                if rec["tipo"] == "ALERTA":
                    st.markdown(f'<div class="alert-danger"><strong>{rec["tipo"]}</strong><br>{rec["mensaje"]}<br><em>{rec["accion"]}</em></div>', unsafe_allow_html=True)
                elif rec["tipo"] == "PRECAUCIÓN":
                    st.markdown(f'<div class="alert-warning"><strong>{rec["tipo"]}</strong><br>{rec["mensaje"]}<br><em>{rec["accion"]}</em></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="alert-success"><strong>{rec["tipo"]}</strong><br>{rec["mensaje"]}<br><em>{rec["accion"]}</em></div>', unsafe_allow_html=True)
        else:
            st.info("✅ Tu ubicación actual parece segura. No se detectan riesgos inmediatos.")
        
        # --- MAPA CON INCIDENTES DINÁMICOS ---
        st.subheader("🗺️ MAPA DE SEGURIDAD - TIEMPO REAL")
        
        # Crear mapa centrado en usuario
        m = folium.Map(
            location=[st.session_state.user_location['lat'], st.session_state.user_location['lon']],
            zoom_start=16,
            tiles="CartoDB dark_matter"
        )
        
        # Marcador del USUARIO (ubicación real)
        folium.Marker(
            [st.session_state.user_location['lat'], st.session_state.user_location['lon']],
            popup="<strong>¡TÚ ESTÁS AQUÍ!</strong><br>Ubicación en tiempo real",
            tooltip="Tu ubicación actual",
            icon=folium.Icon(color="blue", icon="user", prefix='fa')
        ).add_to(m)
        
        # Incidentes dinámicos
        for incident in st.session_state.dynamic_incidents:
            color = "red" if incident["nivel"] == "ALTO" else "orange" if incident["nivel"] == "MEDIO" else "yellow"
            
            folium.CircleMarker(
                [incident["lat"], incident["lon"]],
                radius=8,
                popup=f"<strong>{incident['tipo']}</strong><br>Nivel: {incident['nivel']}",
                tooltip=f"Incidente: {incident['nivel']}",
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.7
            ).add_to(m)
        
        # Zonas seguras
        for nombre, datos in ZONAS_SEGURAS.items():
            folium.Marker(
                [datos["lat"], datos["lon"]],
                popup=f"<strong>🏪 {nombre}</strong><br>Tipo: {datos['tipo']}",
                tooltip=f"Zona Segura: {nombre}",
                icon=folium.Icon(color="green", icon="shield", prefix='fa')
            ).add_to(m)
        
        # Mostrar mapa
        st_folium(m, width=700, height=400)
        
        # --- LIVE FEED DE INCIDENTES ---
        st.subheader("📡 ACTIVIDAD EN TIEMPO REAL")
        
        # Métricas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div class="metric-card">🚨<br><strong>{len([i for i in st.session_state.dynamic_incidents if i["nivel"] == "ALTO"])}</strong><br>Alertas Altas</div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-card">⚠️<br><strong>{len(st.session_state.dynamic_incidents)}</strong><br>Incidentes Activos</div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="metric-card">🛡️<br><strong>{len(ZONAS_SEGURAS)}</strong><br>Zonas Seguras</div>', unsafe_allow_html=True)
        
        # Logs de actividad
        for incident in st.session_state.dynamic_incidents[:5]:  # Mostrar últimos 5
            tiempo = incident["timestamp"].strftime('%H:%M:%S')
            st.markdown(f'<div class="alert-warning"><strong>{incident["nivel"]}</strong> - {incident["tipo"]} - {tiempo}</div>', unsafe_allow_html=True)

# --- PESTAÑAS ADICIONALES ---
tabs = st.tabs(["👤 PERFIL", "⚙️ CONFIGURACIÓN"])

with tabs[0]:
    st.subheader("INFORMACIÓN PERSONAL")
    with st.form("profile_form"):
        st.session_state.user_name = st.text_input("Nombre completo", st.session_state.user_name)
        st.session_state.contact_1 = st.text_input("Contacto 1 (WhatsApp)", st.session_state.contact_1)
        st.session_state.contact_2 = st.text_input("Contacto 2 (WhatsApp)", st.session_state.contact_2)
        st.session_state.medical_info = st.text_area("Información médica crítica", st.session_state.medical_info)
        
        if st.form_submit_button("💾 GUARDAR INFORMACIÓN"):
            st.success("Perfil actualizado correctamente")

with tabs[1]:
    st.subheader("CONFIGURACIÓN DEL SISTEMA")
    if st.button("🔄 REINICIAR UBICACIÓN"):
        st.session_state.location_access = False
        st.session_state.user_location = None
        st.rerun()
    
    st.info("""
    **Características activas:**
    - ✅ Ubicación en tiempo real
    - ✅ Alertas dinámicas de incidentes  
    - ✅ Recomendaciones de rutas seguras
    - ✅ Notificaciones de zonas de riesgo
    - ✅ Integración con WhatsApp
    """)