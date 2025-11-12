# huancayo_safety_app.py
import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap
import random
import time
from datetime import datetime
import requests

# Para geolocalización desde el navegador
from streamlit_javascript import st_javascript

# ----------------- CONFIG -----------------
st.set_page_config(
    page_title="Huancayo Safety App",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ----------------- CSS (mobile frame) -----------------
st.markdown(
    """
<style>
    .stApp {
        max-width: 390px;
        height: 844px;
        margin: 10px auto;
        border: 10px solid #000000;
        border-radius: 28px;
        padding: 0px;
        background: #ffffff;
        color: #000000;
        overflow: hidden;
        box-shadow: 0 0 20px rgba(0,0,0,0.25);
    }
    .main-content { padding: 10px; height: calc(100vh - 120px); overflow-y: auto; }
    .emergency-button { background: #000000; color: #ffffff; padding: 12px; border-radius: 18px; width:100%; }
    .safe-zone { background: #f8f9fa; padding: 10px; border-radius: 8px; margin:6px 0; border:1px solid #000; }
    .warning-alert { background:#000; color:#fff; padding:10px; border-radius:8px; margin:8px 0; }
    .metric-card { background:#f8f9fa; padding:8px; border-radius:8px; border:1px solid #000; text-align:center; font-size:12px;}
    .section-divider { border:0.5px solid #000; margin:12px 0; }
</style>
""",
    unsafe_allow_html=True,
)

# ----------------- DATA SIMULADA -----------------
danger_points = [
    (-12.065, -75.210, "Alta", "Robo"),
    (-12.067, -75.212, "Media", "Acoso"),
    (-12.064, -75.214, "Baja", "Sospechoso"),
    (-12.063, -75.209, "Alta", "Asalto"),
    (-12.062, -75.215, "Media", "Robo"),
]

safe_locations = [
    (-12.065, -75.211, "Farmacia Segura", "24/7"),
    (-12.066, -75.213, "Restaurante Refugio", "6 AM - 11 PM"),
    (-12.068, -75.209, "Tienda Amiga", "8 AM - 10 PM"),
]

recent_incidents = [
    {"tipo": "Robo", "ubicacion": "Av. Ferrocarril", "hora": "Hace 15 min", "verificada": True},
    {"tipo": "Acoso", "ubicacion": "Parque Huamanmarca", "hora": "Hace 30 min", "verificada": False},
    {"tipo": "Sospechoso", "ubicacion": "Calle Real", "hora": "Hace 45 min", "verificada": True},
]

# ------------- SESSION STATE -------------
if "panic_active" not in st.session_state:
    st.session_state.panic_active = False
if "panic_countdown" not in st.session_state:
    st.session_state.panic_countdown = 0
if "reports" not in st.session_state:
    st.session_state.reports = []
if "profile" not in st.session_state:
    st.session_state.profile = {
        "nombre": "Usuario",
        "edad": 25,
        "telefono": "+51 999888777",
        "email": "usuario@example.com",
        "contacto1": "+51 999888777",
        "contacto2": "+51 988777666",
        "grupo_sanguineo": "O+",
        "condiciones": "",
    }
if "last_known_location" not in st.session_state:
    # default center Huancayo
    st.session_state.last_known_location = (-12.065, -75.210)

# ------------- UTILIDADES -------------
def verificar_incidente(reporte):
    """Simula verificación: necesita 3 confirmaciones."""
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

def ip_geolocation_fallback():
    """Intenta obtener ubicación por IP (servicio público). Puede fallar sin internet."""
    try:
        r = requests.get("https://ipinfo.io/json", timeout=3)
        if r.ok:
            data = r.json()
            if "loc" in data:
                lat, lon = map(float, data["loc"].split(","))
                return lat, lon
    except Exception:
        return None
    return None

# ------------- BARRA SUPERIOR / PESTAÑAS -------------
st.markdown('<div class="main-content">', unsafe_allow_html=True)
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
    ["🏠 INICIO", "🗺️ MAPA", "🚨 PÁNICO", "📢 REPORTAR", "🏪 ZONAS", "👤 PERFIL", "🧠 ANÁLISIS"]
)

# ---------------- TAB 1 - INICIO ----------------
with tab1:
    st.title("🛡️ SEGURIDAD HUANCAYO")
    # check simple risk
    st.markdown('<div class="warning-alert">⚠️ Zona de riesgo: Av. Ferrocarril (última hora)</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="metric-card">📊<br><strong>12</strong><br>Incidentes</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card">🛡️<br><strong>8</strong><br>Zonas Seguras</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card">⚠️<br><strong>3</strong><br>Alertas</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # Botón de pánico grande
    if st.button("🚨 BOTÓN DE PÁNICO", use_container_width=True, key="panic_main"):
        st.session_state.panic_active = True
        st.session_state.panic_countdown = 5
        st.experimental_rerun()

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    st.subheader("📋 INCIDENTES RECIENTES")
    for incident in recent_incidents + st.session_state.reports[::-1]:
        verified = "✅" if incident.get("verificada", False) else "⏳"
        when = incident.get("hora", "")
        st.write(f"{verified} **{incident['tipo']}** - {incident['ubicacion']}  • {when}")
    st.caption("Los reportes propios aparecen arriba al enviar.")

# ---------------- TAB 2 - MAPA ----------------
with tab2:
    st.title("🗺️ MAPA DE SEGURIDAD")

    # Obtener ubicación del navegador (pide permiso)
    st.caption("Pulsa 'Obtener ubicación' para usar la ubicación del navegador (permiso requerido). Si NO das permiso, se usará ubicación por IP como fallback.")
    get_geo = st.button("📍 Obtener ubicación desde navegador", key="get_geo_btn")

    if get_geo:
        # código JS para solicitar geoloc en el navegador usando streamlit_javascript
        js_code = """
        await new Promise((resolve) => {
            navigator.geolocation.getCurrentPosition(
                (pos) => resolve([pos.coords.latitude, pos.coords.longitude]),
                (err) => resolve(null),
                {enableHighAccuracy: true, timeout: 8000}
            );
        });
        """
        coords = st_javascript(js_code, key="geo_eval")
        if coords:
            try:
                lat, lon = float(coords[0]), float(coords[1])
                st.session_state.last_known_location = (lat, lon)
                st.success(f"Ubicación detectada: {lat:.5f}, {lon:.5f}")
            except Exception:
                st.warning("No se pudo leer la ubicación del navegador, intentando fallback por IP...")
                fallback = ip_geolocation_fallback()
                if fallback:
                    st.session_state.last_known_location = fallback
                    st.info("Ubicación aproximada por IP obtenida.")
                else:
                    st.error("No se pudo obtener ubicación por IP.")
        else:
            st.warning("Permiso denegado o tiempo de espera. Intentando fallback por IP...")
            fallback = ip_geolocation_fallback()
            if fallback:
                st.session_state.last_known_location = fallback
                st.info("Ubicación aproximada por IP obtenida.")
            else:
                st.error("No se pudo obtener ubicación por IP.")

    # Filtros
    col1, col2 = st.columns(2)
    with col1:
        show_heatmap = st.checkbox("Mapa Calor", value=True)
    with col2:
        show_safe_zones = st.checkbox("Zonas Seguras", value=True)

    center = st.session_state.last_known_location
    m = folium.Map(location=center, zoom_start=15, control_scale=True)

    # Heatmap
    if show_heatmap:
        heat_data = []
        for lat, lon, nivel, _ in danger_points:
            weight = 0.9 if nivel == "Alta" else 0.6 if nivel == "Media" else 0.25
            heat_data.append([lat, lon, weight])
        if heat_data:
            HeatMap(heat_data, radius=25, blur=15).add_to(m)

    # Markers peligrosos
    for lat, lon, nivel, tipo in danger_points:
        color = "red" if nivel == "Alta" else "orange" if nivel == "Media" else "yellow"
        folium.CircleMarker(
            [lat, lon],
            radius=6,
            popup=f"⚠️ {tipo} — Nivel: {nivel}",
            color=color,
            fill=True,
        ).add_to(m)

    # Zonas seguras
    if show_safe_zones:
        for lat, lon, nombre, horario in safe_locations:
            folium.Marker(
                [lat, lon],
                popup=f"🏪 {nombre} — {horario}",
                icon=folium.Icon(color="green", icon="info-sign"),
            ).add_to(m)

    # Mi ubicación en el mapa
    folium.Marker(center, popup="📍 Tú (aprox.)", icon=folium.Icon(color="blue", icon="user")).add_to(m)

    # Mostrar mapa
    st_data = st_folium(m, width=350, height=450)

# ---------------- TAB 3 - PANIC ----------------
with tab3:
    st.title("🚨 BOTÓN DE PÁNICO")

    if not st.session_state.panic_active:
        st.error("EN CASO DE PELIGRO INMINENTE")
        with st.expander("📞 CONTACTOS DE EMERGENCIA (desde perfil)"):
            st.write(st.session_state.profile["contacto1"])
            st.write(st.session_state.profile["contacto2"])
        with st.expander("🏥 INFORMACIÓN MÉDICA (desde perfil)"):
            st.write(f"Grupo sanguíneo: {st.session_state.profile['grupo_sanguineo']}")
            st.write(f"Condiciones: {st.session_state.profile['condiciones'] or 'Ninguna registrada'}")

        if st.button("🔴 ACTIVAR BOTÓN DE PÁNICO", use_container_width=True):
            st.session_state.panic_active = True
            st.session_state.panic_countdown = 5
            st.experimental_rerun()
    else:
        # Countdown
        if st.session_state.panic_countdown > 0:
            st.warning(f"🕒 La alerta se activará en {st.session_state.panic_countdown} segundos...")
            # decrementar con sleep breve y rerun para animación
            st.session_state.panic_countdown -= 1
            time.sleep(1)
            st.experimental_rerun()
        else:
            st.error("🚨 ¡ALERTA DE EMERGENCIA ACTIVADA!")
            # Ubicación final (última conocida)
            lat, lon = st.session_state.last_known_location
            st.success(
                f"✅ Alerta enviada a contactos: {st.session_state.profile['contacto1']}, {st.session_state.profile['contacto2']}\n\n"
                f"📍 Ubicación aproximada: {lat:.5f}, {lon:.5f}\n"
                f"🩸 Grupo sanguíneo: {st.session_state.profile['grupo_sanguineo']}"
            )

            # simulación: añadir reporte tipo "Pánico"
            p_report = {
                "tipo": "Pánico",
                "ubicacion": f"{lat:.5f}, {lon:.5f}",
                "hora": "Ahora",
                "verificada": True,
            }
            # solo agregar una vez por alerta activa
            if not any(r.get("tipo") == "Pánico" and r.get("hora") == "Ahora" for r in st.session_state.reports):
                st.session_state.reports.append(p_report)

            if st.button("🟢 CANCELAR ALERTA", use_container_width=True):
                st.session_state.panic_active = False
                st.experimental_rerun()

# ---------------- TAB 4 - REPORTAR ----------------
with tab4:
    st.title("📢 REPORTAR INCIDENTE")
    with st.form("report_form"):
        tipo_incidente = st.selectbox(
            "Tipo de Incidente",
            ["Robo", "Acoso", "Persona Sospechosa", "Asalto", "Accidente", "Otro"],
        )
        ubicacion = st.text_input("Ubicación aproximada", "Cerca de...")
        descripcion = st.text_area("Descripción del incidente", "Describa lo que sucedió...")
        submitted = st.form_submit_button("📤 ENVIAR REPORTE")

        if submitted:
            verificado, confirmaciones = verificar_incidente({"tipo": tipo_incidente, "ubicacion": ubicacion})
            nuevo = {
                "tipo": tipo_incidente,
                "ubicacion": ubicacion,
                "descripcion": descripcion,
                "hora": "Hace unos segundos",
                "verificada": verificado,
                "confirmaciones": confirmaciones,
            }
            st.session_state.reports.append(nuevo)
            if verificado:
                st.success("✅ Reporte enviado y VERIFICADO")
            else:
                st.warning(f"⏳ Reporte enviado. {confirmaciones}/3 confirmaciones")

# ---------------- TAB 5 - ZONAS ----------------
with tab5:
    st.title("🏪 ZONAS SEGURAS")
    for lat, lon, nombre, horario in safe_locations:
        st.markdown('<div class="safe-zone">', unsafe_allow_html=True)
        st.write(f"**{nombre}**")
        st.write(f"⏰ {horario}")
        st.write(f"📍 Aprox. a 150m de tu ubicación")
        # boton con key único
        if st.button(f"🚶 Navegar a {nombre}", key=f"nav_{nombre}"):
            st.info(f"🗺️ Calculando ruta a {nombre}... (simulado)")
        st.markdown("</div>", unsafe_allow_html=True)

# ---------------- TAB 6 - PERFIL ----------------
with tab6:
    st.title("👤 PERFIL")
    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre", st.session_state.profile["nombre"])
            edad = st.number_input("Edad", min_value=18, max_value=100, value=st.session_state.profile["edad"])
        with col2:
            telefono = st.text_input("Teléfono", st.session_state.profile["telefono"])
            email = st.text_input("Email", st.session_state.profile["email"])

        st.subheader("📞 CONTACTOS EMERGENCIA")
        emergencia1 = st.text_input("Contacto 1", st.session_state.profile["contacto1"])
        emergencia2 = st.text_input("Contacto 2", st.session_state.profile["contacto2"])

        st.subheader("🏥 INFORMACIÓN MÉDICA")
        grupo_sanguineo = st.selectbox(
            "Grupo Sanguíneo",
            ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"],
            index=["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"].index(st.session_state.profile["grupo_sanguineo"]),
        )
        condiciones = st.text_area("Condiciones médicas o alergias", st.session_state.profile["condiciones"])

        if st.form_submit_button("💾 GUARDAR PERFIL"):
            st.session_state.profile.update(
                {
                    "nombre": nombre,
                    "edad": edad,
                    "telefono": telefono,
                    "email": email,
                    "contacto1": emergencia1,
                    "contacto2": emergencia2,
                    "grupo_sanguineo": grupo_sanguineo,
                    "condiciones": condiciones,
                }
            )
            st.success("✅ Perfil actualizado")

# ---------------- TAB 7 - ANALISIS ----------------
with tab7:
    st.title("🧠 ANÁLISIS PREDICTIVO")
    st.info(
        """
**PATRONES DETECTADOS (simulado):**
- Viernes 18:00-22:00: 70% más robos
- Zona Centro: 85% más incidentes días de pago  
- Parques nocturnos: 45% más reportes de acoso
- Transporte público: 60% riesgo en horas pico
"""
    )
    col1, col2 = st.columns(2)
    with col1:
        st.metric("PRECISIÓN", "87%", "2%")
    with col2:
        st.metric("ALERTAS", str(len(st.session_state.reports)), "+5")

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.subheader("ANÁLISIS EN TIEMPO REAL")
    st.write("📍 **Zona actual**: Riesgo MEDIO")
    st.write("🕒 **Horario**: Bajo riesgo (simulado)")
    st.write("👥 **Concurrencia**: Normal (simulado)")

st.markdown("</div>", unsafe_allow_html=True)

# ---------------- SIDEBAR - INFO MOBIL ----------------
st.sidebar.markdown("---")
st.sidebar.info(
    """
**📱 PARA USAR EN CELULAR (modo desarrollo):**

1. Ejecuta en tu PC: `streamlit run huancayo_safety_app.py`
2. Si estás en la misma red, abre en tu celular: `http://TU_IP:8501`
3. Para compartir públicamente usa `ngrok` o despliega en un servidor.

**NOTAS:**
- El botón 'Obtener ubicación' pedirá permiso al navegador. Si no conceden permiso, intentamos obtener una ubicación aproximada por IP.
- Esto es una demo: envíos de alertas y reportes son simulados. Para integrarlo con SMS/LLAMADAS necesitarás una API (Twilio, etc.).
"""
)

# ---------------- FIN ----------------
