import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap
import datetime
import urllib.parse
from streamlit.components.v1 import html
import requests

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Huancayo Safety App",
    page_icon="🛡️",
    layout="centered"
)

# --- SESIÓN ---
if 'user_location' not in st.session_state:
    st.session_state.user_location = {"lat": -12.065, "lon": -75.210, "city": "Huancayo"}
if 'emergency_number' not in st.session_state:
    st.session_state.emergency_number = "+51999888777"
if 'gps_permission' not in st.session_state:
    st.session_state.gps_permission = False
if 'gps_attempted' not in st.session_state:
    st.session_state.gps_attempted = False

# --- COMPONENTE JAVASCRIPT PARA GPS EN TIEMPO REAL ---
def create_gps_script():
    return """
    <script>
    // Función para solicitar GPS
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
        
        return navigator.geolocation.watchPosition(
            function(position) {
                const liveData = {
                    lat: position.coords.latitude,
                    lon: position.coords.longitude,
                    accuracy: position.coords.accuracy,
                    timestamp: new Date().toISOString(),
                    source: "gps_continuous"
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
    }

    // Ejecutar automáticamente al cargar (opcional)
    // setTimeout(requestGPSPermission, 1000);
    </script>
    """

# --- FUNCIONES DE UBICACIÓN ---
def get_location_by_ip():
    """Obtiene ubicación por IP como fallback"""
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

def create_whatsapp_link(number, message):
    """Crea el enlace de WhatsApp"""
    encoded_message = urllib.parse.quote(message)
    whatsapp_url = f"https://wa.me/{number.replace('+', '')}?text={encoded_message}"
    return whatsapp_url

def trigger_whatsapp_emergency():
    """Envía alerta de WhatsApp con ubicación"""
    location = st.session_state.user_location
    
    # Determinar precisión del mensaje
    if location.get('source') in ['gps_live', 'gps_continuous']:
        accuracy_note = "🎯 PRECISIÓN GPS ALTA"
        accuracy_meters = f"±{location.get('accuracy', 15)} metros"
    elif location.get('method') == 'ip':
        accuracy_note = "📡 UBICACIÓN APROXIMADA"
        accuracy_meters = "±1-2 km"
    else:
        accuracy_note = "🗺️ UBICACIÓN MANUAL"
        accuracy_meters = "Ubicación establecida"

    emergency_message = (
        f"🚨 *¡EMERGENCIA! NECESITO AYUDA URGENTE* 🚨\n\n"
        f"📍 *Ubicación:* https://maps.google.com/?q={location['lat']},{location['lon']}\n"
        f"📱 *App:* Huancayo Safety App\n"
        f"🕐 *Hora:* {datetime.datetime.now().strftime('%H:%M:%S')}\n"
        f"🎯 *Tipo:* {accuracy_note}\n"
        f"📏 *Precisión:* {accuracy_meters}\n\n"
        f"¡POR FAVOR ENVÍEN AYUDA INMEDIATA!"
    )
    
    whatsapp_link = create_whatsapp_link(st.session_state.emergency_number, emergency_message)
    
    # Guardar en log
    with open("emergency_log.txt", "a", encoding="utf-8") as f:
        f.write(f"[{datetime.datetime.now()}] EMERGENCIA - {location}\n")
    
    return whatsapp_link, emergency_message

# --- COMPONENTE DE SOLICITUD DE GPS ---
def gps_permission_section():
    """Sección para solicitar permisos de GPS"""
    
    st.markdown("### 📍 Activación de GPS en Tiempo Real")
    
    # Inyectar el JavaScript del GPS
    html(create_gps_script(), height=0)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        **🎯 GPS en Tiempo Real:**
        - Ubicación precisa con ±10-50 metros
        - Monitoreo continuo de tu posición
        - Alertas con coordenadas exactas
        - Funciona incluso en movimiento
        
        **📱 En tu teléfono:**
        1. Presiona 'Activar GPS'
        2. Permite el acceso a ubicación
        3. ¡Listo! Tu GPS estará activo
        """)
    
    with col2:
        # Botón para solicitar permisos de GPS
        if st.button("📍 Activar GPS", 
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
    if st.session_state.user_location.get('source') in ['gps_live', 'gps_continuous']:
        st.success("✅ **GPS ACTIVADO** - Tu ubicación en tiempo real está siendo monitoreada")
    elif st.session_state.gps_attempted:
        st.warning("⚠️ **GPS PENDIENTE** - Por favor permite la ubicación en tu navegador")
    else:
        st.info("📡 **SIN GPS** - Presiona 'Activar GPS' para ubicación precisa")

# --- MÉTODOS ALTERNATIVOS DE UBICACIÓN ---
def alternative_location_methods():
    """Métodos alternativos si el GPS falla"""
    
    st.markdown("#### 🗺️ Métodos Alternativos")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📡 Usar Mi IP", use_container_width=True):
            with st.spinner("Detectando ubicación por IP..."):
                location = get_location_by_ip()
                if location:
                    st.session_state.user_location = location
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
            st.success("📍 Ubicación: Huancayo Centro")
            st.rerun()
    
    with col3:
        ubicaciones = {
            "Plaza Huamanmarca": (-12.065, -75.210),
            "Mercado Central": (-12.063, -75.212),
            "UNCP": (-12.054, -75.201),
            "Estadio": (-12.072, -75.198)
        }
        
        selected_loc = st.selectbox("Zonas conocidas:", list(ubicaciones.keys()))
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
    }
    .metric-card {
        background: linear-gradient(135deg, #112d4e, #1e3a5f);
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin: 5px;
        border: 1px solid #3a506b;
    }
    .location-badge {
        background: #1b5e20;
        color: #a5d6a7;
        padding: 12px;
        border-radius: 10px;
        text-align: center;
        border: 2px solid #4caf50;
        margin: 10px 0;
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
    
    # Sección de GPS
    gps_permission_section()
    
    # Métodos alternativos
    alternative_location_methods()
    
    # Mostrar estado actual de ubicación
    st.markdown("---")
    loc = st.session_state.user_location
    
    # Determinar icono y color según el método
    if loc.get('source') in ['gps_live', 'gps_continuous']:
        badge_color = "#1b5e20"
        border_color = "#4caf50"
        icon = "🎯"
        precision_text = f"±{loc.get('accuracy', 15)} metros - GPS ACTIVO"
    elif loc.get('method') == 'ip':
        badge_color = "#ff6f00"
        border_color = "#ff9800"
        icon = "📡"
        precision_text = "±1-2 km - Por IP"
    else:
        badge_color = "#1565c0"
        border_color = "#2196f3"
        icon = "🗺️"
        precision_text = "Ubicación manual"
    
    st.markdown(f"""
    <div class="location-badge">
        <strong>{icon} UBICACIÓN ACTUAL</strong><br>
        <span style='font-size: 16px;'>📍 {loc['city']}</span><br>
        <span style='font-size: 12px;'>📏 {precision_text}</span><br>
        <span style='font-size: 10px;'>Lat: {loc['lat']:.6f}, Lon: {loc['lon']:.6f}</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Botón de pánico principal
    st.markdown("### 🚨 Botón de Emergencia")
    
    if st.button("🚨\nEMERGENCIA INMEDIATA\n\n"
                "📍 Tu ubicación EXACTA se enviará\n"
                "📱 Alerta a contacto de emergencia\n"
                "🎯 Máxima precisión con GPS", 
                key="panic_button",
                use_container_width=True):
        
        whatsapp_link, message = trigger_whatsapp_emergency()
        
        st.success("""
        ✅ **¡ALERTA GENERADA CON ÉXITO!**
        
        **Se ha preparado tu mensaje de emergencia:**
        - 🎯 Tu ubicación exacta incluida
        - 📱 Enlace de WhatsApp listo
        - ⏰ Hora y precisión registradas
        """)
        st.balloons()
        
        # Mostrar el enlace de WhatsApp
        st.markdown(f"""
        <div style='
            background: #25D366; 
            color: white; 
            padding: 20px; 
            border-radius: 10px; 
            text-align: center;
            margin: 15px 0;
            border: 3px solid #ffffff;
        '>
            <h3>📱 ENLACE DE WHATSAPP LISTO</h3>
            <p>¡Haz clic en el botón de abajo para abrir WhatsApp!</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Botón para abrir WhatsApp
        st.markdown(f'<a href="{whatsapp_link}" target="_blank"><button style="background:#25D366;color:white;padding:20px;border:none;border-radius:10px;font-size:20px;font-weight:bold;width:100%;">📱 ABRIR WHATSAPP Y ENVIAR ALERTA</button></a>', unsafe_allow_html=True)
        
        # Instrucciones adicionales
        st.markdown("""
        ### 📲 Si usas en teléfono:
        1. **Presiona el botón verde de arriba**
        2. **Se abrirá WhatsApp automáticamente**
        3. **Verás el mensaje de emergencia listo**
        4. **Solo presiona ENVIAR**
        """)
        
        # Mostrar detalles del mensaje
        with st.expander("📋 Ver mensaje completo que se enviará"):
            st.text_area("", value=message, height=200, key="message_preview")

# --- MAPA MEJORADO ---
elif menu == "🗺️ Mapa":
    st.header("🗺️ Mapa de Seguridad en Tiempo Real")
    
    # Crear mapa centrado en la ubicación del usuario
    m = folium.Map(
        location=[st.session_state.user_location["lat"], st.session_state.user_location["lon"]], 
        zoom_start=15,
        tiles="OpenStreetMap"
    )
    
    # Marcador de la ubicación del usuario
    folium.Marker(
        [st.session_state.user_location["lat"], st.session_state.user_location["lon"]],
        popup="📍 TÚ ESTÁS AQUÍ",
        tooltip="Tu ubicación actual",
        icon=folium.Icon(color="blue", icon="user", prefix="fa")
    ).add_to(m)
    
    # Círculo de precisión si es GPS
    if st.session_state.user_location.get('source') in ['gps_live', 'gps_continuous']:
        accuracy = st.session_state.user_location.get('accuracy', 50)
        folium.Circle(
            location=[st.session_state.user_location["lat"], st.session_state.user_location["lon"]],
            radius=accuracy,
            popup=f"Precisión: ~{accuracy}m",
            color="blue",
            fillColor="lightblue",
            fillOpacity=0.2
        ).add_to(m)
    
    # Heatmap de zonas peligrosas
    heat_data = [[lat, lon, 0.8 if nivel=='Alta' else 0.5 if nivel=='Media' else 0.2] 
                for lat, lon, nivel, _ in danger_points]
    HeatMap(heat_data, radius=15, blur=10).add_to(m)
    
    # Zonas seguras
    for lat, lon, nombre, horario, icono in safe_locations:
        folium.Marker(
            [lat, lon],
            popup=f"{icono} {nombre}\n⏰ {horario}",
            tooltip=f"Zona Segura: {nombre}",
            icon=folium.Icon(color="green", icon="home", prefix="fa")
        ).add_to(m)
    
    # Mostrar mapa
    st_folium(m, width=700, height=500)

# --- PÁGINAS RESTANTES (IGUAL QUE TU VERSIÓN ORIGINAL) ---
elif menu == "📢 Reportar":
    st.header("📢 REPORTAR INCIDENTE")
    with st.form("report_form"):
        tipo = st.selectbox("Tipo de incidente", ["Robo","Acoso","Sospechoso","Asalto","Accidente","Otro"])
        ubicacion = st.text_input("Ubicación aproximada", "Ej. Av. Ferrocarril")
        descripcion = st.text_area("Describe lo sucedido")
        if st.form_submit_button("📤 ENVIAR"):
            with open("logs_emergencias.txt", "a", encoding="utf-8") as f:
                f.write(f"[{datetime.datetime.now()}] Reporte: {tipo}, {ubicacion}, {descripcion}\n")
            st.success("Reporte enviado correctamente ✅")

elif menu == "🛡️ Zonas Seguras":
    st.header("🏪 ZONAS SEGURAS")
    for lat, lon, nombre, horario, icono in safe_locations:
        st.markdown(f"{icono} **{nombre}** — ⏰ {horario}")

elif menu == "👤 Perfil":
    st.header("👤 PERFIL DE USUARIO")
    with st.form("perfil_form"):
        nombre = st.text_input("Nombre", "Usuario")
        telefono = st.text_input("Número de emergencia", st.session_state.emergency_number)
        if st.form_submit_button("💾 Guardar"):
            st.session_state.emergency_number = telefono
            st.success("Perfil actualizado ✅")

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