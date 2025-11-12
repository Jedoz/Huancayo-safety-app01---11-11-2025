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

# Estilos CSS mejorados
st.markdown("""
<style>
    .stApp {
        max-width: 380px; 
        margin: auto; 
        border: 16px solid #333; 
        border-radius: 40px; 
        padding: 10px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .emergency-button {
        background: linear-gradient(45deg, #FF416C, #FF4B2B);
        color: white;
        border: none;
        padding: 20px;
        border-radius: 50px;
        font-size: 18px;
        font-weight: bold;
        margin: 10px 0;
    }
    .safe-zone {
        background: linear-gradient(45deg, #00b09b, #96c93d);
        color: white;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
    }
    .warning-alert {
        background: linear-gradient(45deg, #ff9966, #ff5e62);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        animation: pulse 2s infinite;
    }
    .predictive-analysis {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 5px solid #ffd700;
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
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

# --- FUNCIONES NUEVAS SEGÚN REQUERIMIENTOS ---
def check_risk_zone(lat, lon):
    """Verifica si el usuario está en zona de riesgo"""
    zona_riesgo = {
        'nombre': 'Av. Ferrocarril',
        'incidentes': 3,
        'nivel': 'Alto',
        'horario': 'última hora'
    }
    return zona_riesgo

def verificar_incidente(reporte):
    """Sistema mejorado de verificación comunitaria"""
    confirmaciones_necesarias = 3
    confirmaciones_actuales = random.randint(0, confirmaciones_necesarias)
    
    if confirmaciones_actuales >= confirmaciones_necesarias:
        return True, confirmaciones_actuales
    return False, confirmaciones_actuales

def analizar_patrones():
    """Algoritmo de análisis predictivo simulado"""
    patrones = [
        "🔍 Días de pago + viernes + Zona Centro = 85% más robos",
        "📊 Esta zona es 70% más peligrosa después de las 8 PM los viernes",
        "🎯 Los incidentes aumentan 60% los fines de semana en áreas comerciales",
        "⚠️ Correlación detectada: Lluvia + noche = 45% más acosos en parques"
    ]
    return random.choice(patrones)

def enviar_ubicacion_periodica():
    """Simula envío periódico de ubicación durante emergencia"""
    if st.session_state.panic_active:
        tiempo_transcurrido = datetime.now() - st.session_state.last_location_sent
        if tiempo_transcurrido.seconds >= 30:  # Cada 30 segundos
            st.session_state.last_location_sent = datetime.now()
            return True
    return False

# --- BARRA DE NAVEGACIÓN MEJORADA ---
menu_options = ["🏠 Inicio", "🗺️ Mapa Seguro", "🚨 Botón de Pánico", "📢 Reportar Incidente", "🏪 Zonas Seguras", "👤 Perfil", "🧠 Análisis Predictivo"]
page = st.sidebar.radio("Navegación", menu_options)

# --- BOTÓN DE PÁNICO GLOBAL EN SIDEBAR ---
st.sidebar.markdown("---")
if st.sidebar.button("🚨 BOTÓN DE PÁNICO GLOBAL", use_container_width=True, type="primary"):
    st.session_state.page = "🚨 Botón de Pánico"
    st.rerun()

# --- PÁGINA DE INICIO ---
if page == "🏠 Inicio":
    st.title("🛡️ Huancayo Safety App")
    
    # Notificación automática de zona de riesgo
    zona_riesgo = check_risk_zone(-12.065, -75.210)
    if zona_riesgo:
        st.markdown(f'<div class="warning-alert">⚠️ Estás entrando a zona de alto riesgo: {zona_riesgo["nombre"]}. {zona_riesgo["incidentes"]} incidentes reportados en la {zona_riesgo["horario"]}.</div>', unsafe_allow_html=True)
    
    # Estadísticas rápidas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Incidentes Hoy", "12", "-2")
    with col2:
        st.metric("Zonas Seguras", "8", "+1")
    with col3:
        st.metric("Alertas Activas", "3", "0")
    
    # Accesos rápidos
    st.subheader("🚀 Acciones Rápidas")
    quick_col1, quick_col2 = st.columns(2)
    
    with quick_col1:
        if st.button("📱 Contactos Emergencia", use_container_width=True):
            st.session_state.page = "👤 Perfil"
    
    with quick_col2:
        if st.button("🏪 Lugares Seguros", use_container_width=True):
            st.session_state.page = "🏪 Zonas Seguras"
    
    # Incidentes recientes
    st.subheader("📋 Incidentes Recientes")
    for incident in recent_incidents:
        verified = "✅" if incident['verificada'] else "⏳"
        st.write(f"{verified} **{incident['tipo']}** - {incident['ubicacion']} ({incident['hora']})")

# --- MAPA SEGURO MEJORADO ---
elif page == "🗺️ Mapa Seguro":
    st.subheader("🗺️ Mapa de Seguridad en Tiempo Real")
    
    # Filtros
    col1, col2 = st.columns(2)
    with col1:
        show_heatmap = st.checkbox("Mapa de Calor", value=True)
    with col2:
        show_safe_zones = st.checkbox("Zonas Seguras", value=True)
    
    # Crear mapa
    m = folium.Map(location=[-12.065, -75.210], zoom_start=15)
    
    # Heatmap de riesgo
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
    
    # Control de medidas
    MeasureControl().add_to(m)
    
    st_folium(m, width=320, height=500)

# --- BOTÓN DE PÁNICO MEJORADO ---
elif page == "🚨 Botón de Pánico":
    st.subheader("🚨 Botón de Pánico de Emergencia")
    
    # Configuración de contactos
    with st.expander("📞 Configurar Contactos de Emergencia"):
        contacto1 = st.text_input("Contacto Principal", "+51 999888777")
        contacto2 = st.text_input("Contacto Secundario", "+51 988777666")
        mensaje_personalizado = st.text_area("Mensaje de Emergencia", "¡Necesito ayuda urgente! Mi ubicación es:")
    
    # Información médica
    with st.expander("🏥 Información Médica"):
        grupo_sanguineo = st.selectbox("Grupo Sanguíneo", ["No especificado", "A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])
        alergias = st.text_input("Alergias o condiciones médicas")
    
    # Botón de pánico con cuenta regresiva
    if not st.session_state.panic_active:
        if st.button("🔴 ACTIVAR BOTÓN DE PÁNICO", use_container_width=True, type="primary"):
            st.session_state.panic_active = True
            st.session_state.panic_countdown = 3
            st.rerun()
    else:
        # Cuenta regresiva
        if st.session_state.panic_countdown > 0:
            st.warning(f"🕒 La alerta se activará en {st.session_state.panic_countdown} segundos...")
            st.session_state.panic_countdown -= 1
            time.sleep(1)
            st.rerun()
        else:
            # Alerta activada
            st.error("🚨 ¡ALERTA DE EMERGENCIA ACTIVADA!")
            
            # Simular ubicación
            my_lat = -12.065 + random.uniform(-0.001, 0.001)
            my_lon = -75.210 + random.uniform(-0.001, 0.001)
            
            # Envío periódico de ubicación
            if enviar_ubicacion_periodica():
                st.info("📍 Ubicación enviada a contactos de emergencia y usuarios cercanos")
            
            # Mostrar información de emergencia
            st.success(f"""
            ✅ Alerta enviada a:
            • {contacto1}
            • {contacto2}
            • Usuarios cercanos (5 personas)
            
            📍 Tu ubicación: {my_lat:.5f}, {my_lon:.5f}
            🩸 Grupo sanguíneo: {grupo_sanguineo}
            💊 Alergias: {alergias if alergias else 'Ninguna'}
            """)
            
            # Mapa de emergencia
            m = folium.Map(location=[my_lat, my_lon], zoom_start=17)
            folium.Marker(
                [my_lat, my_lon],
                popup="🚨 PERSONA EN PELIGRO",
                tooltip="¡Necesita ayuda urgente!",
                icon=folium.Icon(color="red", icon="exclamation-triangle", prefix="fa")
            ).add_to(m)
            
            # Radio de búsqueda
            folium.Circle(
                [my_lat, my_lon],
                radius=50,
                color="red",
                fill=True,
                opacity=0.6,
                fillOpacity=0.2
            ).add_to(m)
            
            # Lugares seguros cercanos
            for lat, lon, nombre, horario in safe_locations:
                folium.Marker(
                    [lat, lon],
                    popup=f"🏪 {nombre} (Lugar Seguro)",
                    icon=folium.Icon(color="green", icon="home")
                ).add_to(m)
            
            st_folium(m, width=320, height=400)
            
            # CANCELACIÓN POR DESLIZAMIENTO
            st.warning("Desliza hacia la derecha para cancelar la alerta")
            cancel_slider = st.slider("", 0, 100, 0, key="panic_slider")
            if cancel_slider > 80:
                st.session_state.panic_active = False
                st.success("✅ Alerta cancelada por deslizamiento")
                st.rerun()

# --- SISTEMA DE REPORTES MEJORADO ---
elif page == "📢 Reportar Incidente":
    st.subheader("📢 Reportar Incidente en Tiempo Real")
    
    # Formulario de reporte
    with st.form("report_form"):
        tipo_incidente = st.selectbox("Tipo de Incidente", 
                                    ["Robo", "Acoso", "Persona Sospechosa", "Asalto", "Accidente", "Otro"])
        
        ubicacion = st.text_input("Ubicación aproximada", "Cerca de...")
        
        descripcion = st.text_area("Descripción del incidente", "Describa lo que sucedió...")
        
        # Opción para subir evidencia
        evidencia = st.file_uploader("Subir foto o video (opcional)", type=['jpg', 'png', 'mp4'])
        
        submitted = st.form_submit_button("📤 ENVIAR REPORTE", use_container_width=True)
        
        if submitted:
            # Sistema mejorado de verificación
            verificado, confirmaciones = verificar_incidente({
                'tipo': tipo_incidente,
                'ubicacion': ubicacion
            })
            
            nuevo_reporte = {
                'tipo': tipo_incidente,
                'ubicacion': ubicacion,
                'descripcion': descripcion,
                'timestamp': datetime.now().strftime("%H:%M"),
                'verificado': verificado,
                'confirmaciones': confirmaciones
            }
            
            st.session_state.reports.append(nuevo_reporte)
            
            if verificado:
                st.success("✅ Reporte enviado y VERIFICADO por la comunidad")
            else:
                st.warning(f"⏳ Reporte enviado. {confirmaciones}/3 confirmaciones necesarias para verificación")

# --- ZONAS SEGURAS ---
elif page == "🏪 Zonas Seguras":
    st.subheader("🏪 Lugares Seguros y Comercios Aliados")
    
    for lat, lon, nombre, horario in safe_locations:
        with st.container():
            st.markdown(f'<div class="safe-zone">', unsafe_allow_html=True)
            st.write(f"**🏪 {nombre}**")
            st.write(f"⏰ Horario: {horario}")
            st.write(f"📍 A 150m de tu ubicación")
            if st.button(f"🚶‍♂️ Cómo llegar a {nombre}", key=nombre):
                # Simular navegación
                st.info(f"🗺️ Navegando hacia {nombre}...")
            st.markdown('</div>', unsafe_allow_html=True)

# --- PERFIL MEJORADO ---
elif page == "👤 Perfil":
    st.subheader("👤 Perfil de Usuario")
    
    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre", "Edwar")
            edad = st.number_input("Edad", min_value=18, max_value=100, value=25)
        with col2:
            telefono = st.text_input("Teléfono", "+51 999888777")
            email = st.text_input("Email", "usuario@example.com")
        
        st.subheader("📞 Contactos de Emergencia")
        emergencia1 = st.text_input("Contacto Emergencia 1", "+51 999888777")
        emergencia2 = st.text_input("Contacto Emergencia 2", "+51 988777666")
        
        st.subheader("🏥 Información Médica")
        grupo_sanguineo = st.selectbox("Grupo Sanguíneo", ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])
        condiciones = st.text_area("Condiciones médicas o alergias")
        
        if st.form_submit_button("💾 Guardar Perfil", use_container_width=True):
            st.success("✅ Perfil actualizado correctamente")

# --- NUEVA PÁGINA: ANÁLISIS PREDICTIVO ---
elif page == "🧠 Análisis Predictivo":
    st.subheader("🧠 Análisis Predictivo de Seguridad")
    
    st.markdown('<div class="predictive-analysis">', unsafe_allow_html=True)
    st.write("**🤖 IA de Seguridad - Patrones Detectados**")
    st.write(analizar_patrones())
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Más análisis
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Precisión Predictiva", "87%", "2%")
    with col2:
        st.metric("Alertas Preventivas", "24", "+5")
    
    st.subheader("📈 Patrones Históricos")
    st.write("• **Viernes 18:00-22:00**: 70% aumento en robos")
    st.write("• **Zona Centro**: 85% más incidentes días de pago")
    st.write("• **Parques nocturnos**: 45% más reportes de acoso")
    st.write("• **Transporte público**: 60% riesgo en horas pico")

# --- INSTRUCCIONES DE EJECUCIÓN ---
st.sidebar.markdown("---")
st.sidebar.info("""
**📱 Cómo ejecutar:**
1. Guardar como `huancayo_safety_app.py`
2. Abrir terminal en la carpeta
3. Ejecutar: `streamlit run huancayo_safety_app.py`
4. Abrirá automáticamente en el navegador
""")