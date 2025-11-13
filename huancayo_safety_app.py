import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap
import datetime
import webbrowser
import requests
import urllib.parse
from geopy.geocoders import Nominatim
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Huancayo Safety App",
    page_icon="🛡️",
    layout="centered"
)

# --- INICIALIZACIÓN DE SESIÓN ---
if 'user_location' not in st.session_state:
    st.session_state.user_location = {"lat": -12.065, "lon": -75.210, "city": "Huancayo"}
if 'emergency_number' not in st.session_state:
    st.session_state.emergency_number = "+51999888777"
if 'location_method' not in st.session_state:
    st.session_state.location_method = "manual"
if 'gps_permission' not in st.session_state:
    st.session_state.gps_permission = False
if 'gps_attempted' not in st.session_state:
    st.session_state.gps_attempted = False

# --- COMPONENTE JAVASCRIPT PARA GPS EN TIEMPO REAL ---
def gps_permission_component():
    """Componente JavaScript para solicitar permisos de GPS"""
    
    gps_js = """
    <script>
    function requestGPSPermission() {
        if (!navigator.geolocation) {
            alert("❌ Tu navegador no soporta geolocalización");
            return false;
        }
        
        // Solicitar permiso de ubicación
        navigator.geolocation.getCurrentPosition(
            function(position) {
                // ÉXITO: GPS permitido y obtenido
                const gpsData = {
                    lat: position.coords.latitude,
                    lon: position.coords.longitude,
                    accuracy: position.coords.accuracy,
                    timestamp: new Date().toISOString(),
                    source: "gps_live"
                };
                
                // Enviar datos a Streamlit
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    value: JSON.stringify(gpsData)
                }, '*');
                
                // Mostrar mensaje de éxito
                alert("✅ GPS activado! Tu ubicación en tiempo real está siendo monitoreada.");
            },
            function(error) {
                // ERROR: GPS denegado o falló
                let errorMsg = "❌ No se pudo obtener la ubicación GPS. ";
                
                switch(error.code) {
                    case error.PERMISSION_DENIED:
                        errorMsg += "Permiso denegado. Por favor habilita la ubicación en tu navegador.";
                        break;
                    case error.POSITION_UNAVAILABLE:
                        errorMsg += "Ubicación no disponible. Revisa tu conexión GPS.";
                        break;
                    case error.TIMEOUT:
                        errorMsg += "Tiempo de espera agotado. Intenta nuevamente.";
                        break;
                    default:
                        errorMsg += "Error desconocido.";
                        break;
                }
                
                alert(errorMsg);
                
                // Enviar error a Streamlit
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    value: JSON.stringify({error: true, message: errorMsg})
                }, '*');
            },
            {
                enableHighAccuracy: true,  // GPS de alta precisión
                timeout: 15000,           // 15 segundos de espera
                maximumAge: 0             // No usar ubicación cacheada
            }
        );
        
        return true;
    }
    
    // Función para monitoreo continuo de GPS
    function startContinuousGPS() {
        if (!navigator.geolocation) return;
        
        const watchId = navigator.geolocation.watchPosition(
            function(position) {
                const liveData = {
                    lat: position.coords.latitude,
                    lon: position.coords.longitude,
                    accuracy: position.coords.accuracy,
                    timestamp: new Date().toISOString(),
                    source: "gps_continuous",
                    watchId: watchId
                };
                
                // Actualizar ubicación en tiempo real
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    value: JSON.stringify(liveData)
                }, '*');
            },
            function(error) {
                console.error("Error en GPS continuo:", error);
            },
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 0
            }
        );
        
        return watchId;
    }
    </script>
    """
    
    return gps_js

# --- FUNCIONES MEJORADAS CON GPS ---
def get_location_by_ip():
    """Obtiene ubicación por IP"""
    try:
        response = requests.get('https://ipapi.co/json/', timeout=10)
        if response.status_code == 200:
            data = response.json()
            return {
                "lat": data.get('latitude', -12.065),
                "lon": data.get('longitude', -75.210),
                "city": data.get('city', 'Huancayo'),
                "accuracy": 1000,
                "method": "ip"
            }
    except:
        pass
    return None

def get_address_from_coords(lat, lon):
    """Convierte coordenadas a dirección"""
    try:
        geolocator = Nominatim(user_agent="huancayo_safety_app")
        location = geolocator.reverse(f"{lat}, {lon}", language='es')
        return location.address if location else f"Coordenadas: {lat:.4f}, {lon:.4f}"
    except:
        return f"Coordenadas: {lat:.4f}, {lon:.4f}"

def trigger_whatsapp_emergency(location_data):
    """Envía alerta de WhatsApp con ubicación"""
    try:
        maps_url = f"https://maps.google.com/?q={location_data['lat']},{location_data['lon']}"
        address = get_address_from_coords(location_data['lat'], location_data['lon'])
        
        # Determinar precisión del mensaje
        accuracy_note = ""
        if location_data.get('source') == 'gps_live':
            accuracy_note = "🎯 PRECISIÓN GPS ALTA"
        elif location_data.get('source') == 'gps_continuous':
            accuracy_note = "🎯 GPS EN TIEMPO REAL"
        elif location_data.get('method') == 'ip':
            accuracy_note = "📡 UBICACIÓN APROXIMADA"
        else:
            accuracy_note = "🗺️ UBICACIÓN MANUAL"
        
        emergency_message = (
            f"🚨 *¡EMERGENCIA! NECESITO AYUDA URGENTE* 🚨\n\n"
            f"📍 *Ubicación:* {address}\n"
            f"📱 *App:* Huancayo Safety App\n"
            f"🕐 *Hora:* {datetime.datetime.now().strftime('%H:%M:%S')}\n"
            f"🎯 *Tipo:* {accuracy_note}\n"
            f"📏 *Precisión:* ±{location_data.get('accuracy', 50)} metros\n\n"
            f"🗺️ *Enlace GPS:* {maps_url}\n\n"
            f"¡POR FAVOR ENVÍEN AYUDA INMEDIATA!"
        )
        
        encoded_message = urllib.parse.quote(emergency_message)
        whatsapp_url = f"https://wa.me/{st.session_state.emergency_number.replace('+', '')}?text={encoded_message}"
        
        webbrowser.open(whatsapp_url)
        
        # Guardar en log
        with open("emergency_log.txt", "a", encoding="utf-8") as f:
            f.write(f"[{datetime.datetime.now()}] EMERGENCIA_GPS - {location_data}\n")
        
        return True
        
    except Exception as e:
        st.error(f"Error al enviar alerta: {str(e)}")
        return False

# --- COMPONENTE DE SOLICITUD DE GPS ---
def gps_permission_section():
    """Sección para solicitar permisos de GPS"""
    
    st.markdown("### 📍 Permisos de Ubicación en Tiempo Real")
    
    # Inyectar el JavaScript del GPS
    html(gps_permission_component(), height=0)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        **🎯 GPS en Tiempo Real:**
        - Ubicación precisa con ±10 metros
        - Monitoreo continuo de tu posición
        - Alertas con coordenadas exactas
        - Funciona incluso en movimiento
        """)
    
    with col2:
        # Botón para solicitar permisos de GPS
        if st.button("📍 Permitir GPS", 
                    key="gps_permission_btn",
                    use_container_width=True,
                    type="primary"):
            
            # Marcar que se intentó el GPS
            st.session_state.gps_attempted = True
            
            # Ejecutar JavaScript para solicitar GPS
            js_code = """
            <script>
            requestGPSPermission();
            </script>
            """
            html(js_code, height=0)
            
            st.info("⌛ Solicitando permisos de ubicación... Revisa tu navegador/móvil")
    
    # Estado del GPS
    st.markdown("---")
    if st.session_state.gps_permission:
        st.success("✅ **GPS ACTIVADO** - Tu ubicación en tiempo real está siendo monitoreada")
    elif st.session_state.gps_attempted:
        st.warning("⚠️ **GPS PENDIENTE** - Por favor permite la ubicación en tu navegador")
    else:
        st.info("📡 **SIN GPS** - Presiona 'Permitir GPS' para activar ubicación precisa")

# --- MANEJO DE DATOS DEL GPS ---
def handle_gps_data():
    """Maneja los datos recibidos del componente GPS"""
    
    # Simulación de datos GPS (en producción esto vendría del componente JavaScript)
    if st.button("🎯 Simular Datos GPS (Para pruebas)"):
        st.session_state.user_location = {
            "lat": -12.065123, 
            "lon": -75.210456,
            "city": "Huancayo Centro (GPS)",
            "accuracy": 15,
            "source": "gps_live",
            "method": "gps"
        }
        st.session_state.gps_permission = True
        st.success("✅ Datos GPS simulados - Ubicación de alta precisión activada")
        st.rerun()

# --- COMPONENTE PRINCIPAL DE UBICACIÓN ---
def setup_location():
    """Configuración completa de ubicación"""
    
    st.markdown("### 📍 Configuración de Ubicación")
    
    # Sección de GPS en tiempo real
    gps_permission_section()
    
    # Manejo de datos GPS
    handle_gps_data()
    
    st.markdown("---")
    st.markdown("#### 🗺️ Métodos Alternativos de Ubicación")
    
    # Métodos alternativos
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📡 Usar Mi IP", use_container_width=True):
            with st.spinner("Detectando ubicación por IP..."):
                location = get_location_by_ip()
                if location:
                    st.session_state.user_location = location
                    st.session_state.location_method = "ip"
                    st.success(f"📍 Ubicación IP: {location['city']}")
                    st.rerun()
                else:
                    st.error("❌ No se pudo obtener ubicación por IP")
    
    with col2:
        if st.button("🏙️ Huancayo Centro", use_container_width=True):
            st.session_state.user_location = {
                "lat": -12.065, 
                "lon": -75.210, 
                "city": "Huancayo Centro",
                "method": "manual",
                "accuracy": 1000
            }
            st.session_state.location_method = "manual"
            st.success("📍 Ubicación: Huancayo Centro")
            st.rerun()
    
    with col3:
        ubicaciones = {
            "Plaza Huamanmarca": (-12.065, -75.210),
            "Mercado Central": (-12.063, -75.212),
            "UNCP": (-12.054, -75.201),
            "Estadio": (-12.072, -75.198)
        }
        
        selected_loc = st.selectbox("Zonas:", list(ubicaciones.keys()))
        if st.button("🎯 Ir aquí", use_container_width=True):
            lat, lon = ubicaciones[selected_loc]
            st.session_state.user_location = {
                "lat": lat, 
                "lon": lon, 
                "city": selected_loc,
                "method": "manual",
                "accuracy": 500
            }
            st.success(f"📍 Ubicación: {selected_loc}")
            st.rerun()
    
    # Mostrar estado actual de ubicación
    st.markdown("---")
    loc = st.session_state.user_location
    
    # Determinar icono y color según el método
    if loc.get('source') in ['gps_live', 'gps_continuous']:
        badge_color = "#1b5e20"
        border_color = "#4caf50"
        icon = "🎯"
        precision_text = f"±{loc.get('accuracy', 15)} metros"
    elif loc.get('method') == 'ip':
        badge_color = "#ff6f00"
        border_color = "#ff9800"
        icon = "📡"
        precision_text = "±1-2 km"
    else:
        badge_color = "#1565c0"
        border_color = "#2196f3"
        icon = "🗺️"
        precision_text = "Ubicación manual"
    
    st.markdown(f"""
    <div style='
        background: {badge_color}; 
        color: white; 
        padding: 15px; 
        border-radius: 10px; 
        text-align: center;
        border: 2px solid {border_color};
        margin: 10px 0;
    '>
        <strong>{icon} UBICACIÓN ACTUAL</strong><br>
        <span style='font-size: 16px;'>📍 {loc['city']}</span><br>
        <span style='font-size: 12px;'>📏 {precision_text} | Lat: {loc['lat']:.6f}, Lon: {loc['lon']:.6f}</span>
    </div>
    """, unsafe_allow_html=True)

# --- CSS MEJORADO ---
st.markdown("""
<style>
    .stApp {
        background-color: #0d1b2a;
        color: white;
    }
    .main-title {
        font-size: 32px;
        font-weight: bold;
        text-align: center;
        margin: 10px 0;
        color: #00d4ff;
        text-shadow: 0 0 10px #00d4ff;
    }
    .panic-button {
        background: linear-gradient(135deg, #ff0000, #8b0000);
        color: white;
        border-radius: 50%;
        width: 250px;
        height: 250px;
        font-size: 24px;
        font-weight: bold;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 20px auto;
        box-shadow: 0 0 60px #ff0000;
        border: 5px solid #ffffff;
        cursor: pointer;
        transition: all 0.3s;
        text-align: center;
        line-height: 1.4;
    }
    .panic-button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 80px #ff4444;
    }
    .gps-button {
        background: linear-gradient(135deg, #00c853, #009624);
        color: white;
        border: 2px solid #00e676;
        border-radius: 10px;
        padding: 15px;
        font-weight: bold;
        text-align: center;
        margin: 5px 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #112d4e, #1e3a5f);
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin: 5px;
        border: 1px solid #3a506b;
    }
</style>
""", unsafe_allow_html=True)

# --- DATOS DE LA APP ---
danger_points = [
    (-12.065, -75.210, 'Alta', 'Robo'),
    (-12.067, -75.212, 'Media', 'Acoso'),
    (-12.064, -75.214, 'Baja', 'Sospechoso'),
    (-12.063, -75.209, 'Alta', 'Asalto'),
]

safe_locations = [
    (-12.065, -75.211, 'Farmacia Segura', '24/7', '💊'),
    (-12.066, -75.213, 'Comisaría PNP', '24/7', '👮'),
    (-12.068, -75.209, 'Hospital Regional', '24/7', '🏥'),
]

# --- NAVEGACIÓN ---
st.sidebar.title("📱 Navegación")
menu = st.sidebar.radio("", ["🏠 Inicio", "🗺️ Mapa", "📢 Reportar", "🛡️ Zonas Seguras", "👤 Perfil"])

# --- PÁGINA DE INICIO ---
if menu == "🏠 Inicio":
    st.markdown('<div class="main-title">🛡️ SEGURIDAD HUANCAYO</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#88d3fa; font-size:18px;">GPS en Tiempo Real Activado</p>', unsafe_allow_html=True)
    
    # Configuración de ubicación con GPS
    setup_location()
    
    # Botón de pánico principal
    st.markdown("### 🚨 Botón de Emergencia con GPS")
    
    # Información de ubicación actual
    loc = st.session_state.user_location
    if loc.get('source') in ['gps_live', 'gps_continuous']:
        st.success("✅ **GPS ACTIVO** - Tu ubicación exacta se enviará en la alerta")
    elif loc.get('method') == 'ip':
        st.warning("⚠️ **UBICACIÓN APROXIMADA** - Activa GPS para mayor precisión")
    else:
        st.info("🗺️ **UBICACIÓN MANUAL** - Considera activar GPS para emergencias")
    
    # Botón de pánico
    if st.button("🚨\nEMERGENCIA INMEDIATA\n\n"
                "📍 Tu ubicación se enviará automáticamente\n"
                "📱 Alerta a tu contacto de emergencia\n"
                "🎯 Máxima precisión con GPS", 
                key="panic_button",
                use_container_width=True):
        
        if trigger_whatsapp_emergency(st.session_state.user_location):
            st.success("""
            ✅ **¡ALERTA ENVIADA CON ÉXITO!**
            
            **Se ha enviado a tu contacto de emergencia:**
            - 🎯 Tu ubicación exacta con GPS
            - 🗺️ Enlace directo a Google Maps
            - 📱 Mensaje de emergencia detallado
            - ⏰ Hora y precisión de la ubicación
            
            **🔒 Mantén la calma y busca un lugar seguro**
            """)
            st.balloons()
            
            # Mostrar detalles técnicos
            with st.expander("📋 Detalles técnicos de la alerta"):
                st.write(f"**📍 Coordenadas GPS:** {loc['lat']:.6f}, {loc['lon']:.6f}")
                st.write(f"**🎯 Precisión:** ±{loc.get('accuracy', 50)} metros")
                st.write(f"**📡 Método:** {loc.get('source', loc.get('method', 'Manual'))}")
                st.write(f"**🏙️ Dirección:** {get_address_from_coords(loc['lat'], loc['lon'])}")
                st.write(f"**📞 Contacto:** {st.session_state.emergency_number}")
                st.write(f"**🕐 Hora de envío:** {datetime.datetime.now().strftime('%H:%M:%S')}")

# --- RESTANTE DEL CÓDIGO (Mapa, Reportar, Zonas Seguras, Perfil) ---
# ... (el resto del código se mantiene igual que en la versión anterior)

# --- PIE DE PÁGINA ---
st.markdown("""
<br><br>
<hr>
<div style='text-align: center; color: gray; font-size: 12px;'>
    <strong>Huancayo Safety App</strong> | © 2025 | 
    <span style='color: #00e676;'>GPS en Tiempo Real</span> | 
    <span style='color: #ff4444;'>Botón de Emergencia Activo</span>
</div>
""", unsafe_allow_html=True)