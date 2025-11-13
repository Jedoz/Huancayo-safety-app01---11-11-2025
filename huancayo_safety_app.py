# huancayo_safety_app.py
import streamlit as st
import streamlit.components.v1 as components
from streamlit_folium import st_folium
import folium
from folium.plugins import HeatMap
import random, threading, time, json, socket
from flask import Flask, request, jsonify
from flask_cors import CORS
import urllib.parse
import os

# ----------------------- CONFIG -----------------------
st.set_page_config(page_title="Huancayo Safety",
                   page_icon="🛡️",
                   layout="centered",
                   initial_sidebar_state="collapsed")

# ------------------ GLOBAL ALERT LOG (COMPARTIDO) ------------------
# Se usará el micro-servicio Flask para recibir logs desde el cliente JS.
ALERT_LOG = []  # lista en memoria; se puede persistir a archivo si quieres

# ------------------ ARRANCAR MICRO-SERVICIO FLASK ------------------
# Escuchar requests POST desde el JS del cliente para registrar alertas (log)
def start_flask_api(host_ip="0.0.0.0", port=8502):
    app = Flask("huancayo_local_api")
    CORS(app)

    @app.route("/log_alert", methods=["POST"])
    def log_alert():
        try:
            payload = request.get_json(force=True)
            payload['server_received_at'] = time.time()
            ALERT_LOG.append(payload)
            # opcional: guardar en archivo
            try:
                with open("alerts_log.jsonl", "a", encoding="utf-8") as f:
                    f.write(json.dumps(payload, ensure_ascii=False) + "\n")
            except Exception:
                pass
            return jsonify({"status": "ok"}), 200
        except Exception as e:
            return jsonify({"status": "error", "detail": str(e)}), 500

    # Ejecutar flask en hilo aparte (no bloquear Streamlit)
    def run():
        # debug=False, use_reloader=False
        app.run(host=host_ip, port=port, debug=False, use_reloader=False)

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    return thread

# Determinar IP local (para que el JS haga fetch a la dirección correcta)
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # doesn't have to be reachable
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

LOCAL_IP = get_local_ip()
FLASK_PORT = 8502
# arrancar Flask si no está corriendo ya
start_flask_api(host_ip="0.0.0.0", port=FLASK_PORT)

# ------------------ ESTILOS (VIDEOJUEGO TURQUESA/NEGRO/BLANCO) ------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700&display=swap');

/* App container */
.stApp {
    background: linear-gradient(180deg, #001219 0%, #002b36 100%);
    color: #e6fffb;
    font-family: 'Orbitron', sans-serif;
    border-radius: 12px;
    padding: 8px;
}

/* Titulos */
h1, h2, h3 { color: #00ffd1; text-shadow: 0 0 8px rgba(0,255,209,0.12); }

/* Botón principal circular (estilo 'reactor' turquesa) */
/* Lo creamos en dos versiones: rojo para SOS legacy, y TURQUESA activo */
#panic-button {
    width: 160px;
    height: 160px;
    border-radius: 100%;
    display:flex;
    align-items:center;
    justify-content:center;
    margin: 24px auto;
    font-size: 34px;
    font-weight:700;
    color: #001219;
    background: radial-gradient(circle at 30% 30%, #00ffd1 0%, #00b4d8 50%, #006d77 100%);
    border: 4px solid rgba(255,255,255,0.12);
    box-shadow: 0 0 40px rgba(0,255,209,0.18), inset 0 -6px 12px rgba(0,0,0,0.2);
    transition: transform .12s ease, box-shadow .12s ease;
    cursor: pointer;
}
#panic-button:active { transform: scale(0.96); box-shadow: 0 0 60px rgba(0,255,209,0.28); }

/* Texto sobre fondo oscuro: mayor contraste */
.section-title { color:#ffffff; text-shadow:none; }

/* Inputs */
input, textarea {
    background: rgba(255,255,255,0.03) !important;
    color: #e6fffb !important;
    border: 1px solid rgba(0,255,209,0.12) !important;
    border-radius: 8px !important;
}

/* Botones Streamlit */
.stButton>button {
    background: linear-gradient(90deg, #00b4d8, #0077b6) !important;
    color: white !important;
    border-radius: 10px !important;
    padding: 10px 16px !important;
    font-weight: 700 !important;
    box-shadow: 0 6px 20px rgba(0,180,216,0.12) !important;
    border: none !important;
}

/* Ajuste mobile-friendly */
@media (max-width: 480px) {
    .stApp { max-width: 420px; margin: 0 auto; padding: 6px; }
    #panic-button { width: 170px; height: 170px; font-size: 36px; }
}

</style>
""", unsafe_allow_html=True)

# ------------------ DATOS SIMULADOS / SESSION STATE ------------------
# Danger points, safe locations, incidents (se mantienen)
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

if 'panic_active' not in st.session_state:
    st.session_state.panic_active = False
if 'panic_countdown' not in st.session_state:
    st.session_state.panic_countdown = 0
if 'reports' not in st.session_state:
    st.session_state.reports = []
if 'profile' not in st.session_state:
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
if 'latitude' not in st.session_state:
    st.session_state.latitude = -12.065
if 'longitude' not in st.session_state:
    st.session_state.longitude = -75.210
if 'emergency_number' not in st.session_state:
    st.session_state.emergency_number = "+51999888777"

# ------------------ UTILIDADES ------------------
def verificar_incidente_simulado():
    confirmaciones_necesarias = 3
    confirmaciones_actuales = random.randint(0, confirmaciones_necesarias)
    return confirmaciones_actuales >= confirmaciones_necesarias, confirmaciones_actuales

def generate_whatsapp_url(number, lat, lon, extra_text=""):
    number_clean = number.replace("+", "").strip()
    if not number_clean:
        return None
    message = f"🚨 ALERTA DE EMERGENCIA 🚨%0AUbicación: https://www.google.com/maps/search/?api=1&query={lat},{lon}%0A{urllib.parse.quote(extra_text)}"
    return f"https://wa.me/{number_clean}?text={message}"

# ------------------ UI: PESTAÑAS ------------------
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🏠 INICIO",
    "🗺️ MAPA",
    "🚨 PÁNICO",
    "📢 REPORTAR",
    "🏪 ZONAS",
    "👤 PERFIL",
    "🧠 ANÁLISIS"
])

# ---------------- PESTAÑA: INICIO (AQUI VA EL BOTON PRINCIPAL) ----------------
with tab1:
    st.markdown("<h1 style='text-align:center;'>🛡 HUANCAYO SAFETY</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#dff6f0;'>Sistema de seguridad personal — interfaz móvil 2025</p>", unsafe_allow_html=True)

    # Zona de riesgo resumida
    st.markdown("### <span class='section-title'>⚠️ Zona de riesgo</span>", unsafe_allow_html=True)
    st.info("Av. Ferrocarril — Última hora")

    # CONTACTO DE EMERGENCIA VISIBLE
    st.markdown("### <span class='section-title'>📞 Contacto de emergencia</span>", unsafe_allow_html=True)
    emergency_input = st.text_input("Número WhatsApp (ej: +51987654321)", value=st.session_state.emergency_number)
    st.session_state.emergency_number = emergency_input.strip()

    # Botón circular ACTIVO: JS obtiene coords, abre WhatsApp y llama al microservicio local para log
    # El JS usa la IP local que calculamos arriba (LOCAL_IP) y FLASK_PORT para el POST.
    js_code = f"""
    <div style="text-align:center; margin-top:10px;">
      <button id="panic-button">SOS</button>
    </div>
    <script>
    const btn = document.getElementById('panic-button');
    btn.addEventListener('click', async function(e) {{
        e.preventDefault();
        // 1) obtener geolocalización
        function openWhatsAppWithCoords(lat, lon) {{
            const number = "{st.session_state.emergency_number.replace('"', '\\"')}";
            const base = "https://wa.me/";
            const msg = encodeURIComponent("🚨 ALERTA DE EMERGENCIA 🚨\\nUbicación: https://www.google.com/maps/search/?api=1&query=" + lat + "," + lon);
            const full = base + number.replace('+','') + "?text=" + msg;
            // abrir WhatsApp
            window.open(full, "_blank");
            // 2) intentar enviar POST al microservicio local para registrar
            try {{
                fetch("http://{LOCAL_IP}:{FLASK_PORT}/log_alert", {{
                    method: "POST",
                    headers: {{ "Content-Type": "application/json" }},
                    body: JSON.stringify({{
                        tipo: "Pánico",
                        lat: lat,
                        lon: lon,
                        contacto: number,
                        cliente_ts: Date.now()
                    }})
                }});
            }} catch(err) {{
                // console.warn("No se pudo registrar en el servidor local:", err);
            }}
        }}

        if (navigator && navigator.geolocation) {{
            navigator.geolocation.getCurrentPosition(function(position) {{
                const lat = position.coords.latitude.toFixed(6);
                const lon = position.coords.longitude.toFixed(6);
                openWhatsAppWithCoords(lat, lon);
            }}, function(error) {{
                // si falla, usamos coordenadas del servidor como fallback
                const lat = "{st.session_state.latitude}";
                const lon = "{st.session_state.longitude}";
                openWhatsAppWithCoords(lat, lon);
            }}, {{ enableHighAccuracy: true, timeout: 8000 }});
        }} else {{
            // fallback si el navegador no soporta geoloc
            const lat = "{st.session_state.latitude}";
            const lon = "{st.session_state.longitude}";
            openWhatsAppWithCoords(lat, lon);
        }}
    }});
    </script>
    """
    components.html(js_code, height=140)

    # Mostrar incidentes recientes debajo
    st.markdown("### <span class='section-title'>📋 Incidentes recientes</span>", unsafe_allow_html=True)
    for inc in recent_incidents:
        verified = "✅" if inc.get('verificada') else "⏳"
        st.markdown(f"- {verified} **{inc['tipo']}** — {inc['ubicacion']} ({inc['hora']})")

# ---------------- PESTAÑA: MAPA ----------------
with tab2:
    st.markdown("### 🗺️ MAPA DE SEGURIDAD", unsafe_allow_html=True)
    show_heatmap = st.checkbox("Mostrar HeatMap", value=True)
    show_safe_zones = st.checkbox("Mostrar Zonas Seguras", value=True)

    m = folium.Map(location=[st.session_state.latitude, st.session_state.longitude], zoom_start=15, tiles="CartoDB dark_matter")

    if show_heatmap:
        heat_data = [[lat, lon, 0.8 if nivel=='Alta' else 0.5 if nivel=='Media' else 0.2] for lat, lon, nivel, _ in danger_points]
        HeatMap(heat_data, radius=20, blur=12).add_to(m)

    for lat, lon, nivel, tipo in danger_points:
        color = "red" if nivel=="Alta" else "orange" if nivel=="Media" else "yellow"
        folium.CircleMarker([lat, lon], radius=6, popup=f"{tipo} - {nivel}", color=color, fill=True).add_to(m)

    if show_safe_zones:
        for lat, lon, nombre, horario in safe_locations:
            folium.Marker([lat, lon], popup=f"{nombre} — {horario}", icon=folium.Icon(color="green")).add_to(m)

    st_folium(m, width=360, height=420)

# ---------------- PESTAÑA: PÁNICO (INFO) ----------------
with tab3:
    st.markdown("### 🚨 PÁNICO", unsafe_allow_html=True)
    st.info("El botón principal ya está en la pantalla de inicio (accesible al abrir la app).")
    if st.button("Simular alerta (registro en app)"):
        # log interno
        my_lat = st.session_state.latitude + random.uniform(-0.0005,0.0005)
        my_lon = st.session_state.longitude + random.uniform(-0.0005,0.0005)
        report = {"tipo": "Pánico (manual)", "ubicacion": f"{my_lat:.6f},{my_lon:.6f}", "hora": "Ahora", "verificada": True}
        st.session_state.reports.append(report)
        st.success("Alerta simulada registrada en la sesión.")

# ---------------- PESTAÑA: REPORTAR ----------------
with tab4:
    st.markdown("### 📢 REPORTAR INCIDENTE", unsafe_allow_html=True)
    with st.form("report_form"):
        tipo = st.selectbox("Tipo", ["Robo","Acoso","Persona Sospechosa","Asalto","Accidente","Otro"])
        ubic = st.text_input("Ubicación aproximada", "Cerca de...")
        desc = st.text_area("Descripción")
        submitted = st.form_submit_button("Enviar reporte")
        if submitted:
            verif, conf = verificar_incidente_simulado()
            st.session_state.reports.append({"tipo": tipo, "ubicacion": ubic, "descripcion": desc, "hora":"Reciente", "verificada": verif})
            if verif:
                st.success("✅ Reporte enviado y verificado")
            else:
                st.warning(f"⏳ Reporte enviado. {conf}/3 confirmaciones")

# ---------------- PESTAÑA: ZONAS ----------------
with tab5:
    st.markdown("### 🏪 ZONAS SEGURAS", unsafe_allow_html=True)
    for lat, lon, nombre, horario in safe_locations:
        st.markdown(f"- **{nombre}** — {horario}")

# ---------------- PESTAÑA: PERFIL ----------------
with tab6:
    st.markdown("### 👤 PERFIL", unsafe_allow_html=True)
    with st.form("profile_form"):
        c1, c2 = st.columns(2)
        with c1:
            nombre = st.text_input("Nombre", st.session_state.profile.get("nombre"))
            edad = st.number_input("Edad", min_value=18, max_value=100, value=st.session_state.profile.get("edad"))
        with c2:
            telefono = st.text_input("Teléfono", st.session_state.profile.get("telefono"))
            email = st.text_input("Email", st.session_state.profile.get("email"))
        contacto1 = st.text_input("Contacto 1 (WhatsApp)", st.session_state.profile.get("contacto1"))
        contacto2 = st.text_input("Contacto 2 (WhatsApp)", st.session_state.profile.get("contacto2"))
        grupo = st.selectbox("Grupo sanguíneo", ["O+","O-","A+","A-","B+","B-","AB+","AB-"], index=0)
        condiciones = st.text_area("Condiciones médicas", st.session_state.profile.get("condiciones"))
        if st.form_submit_button("Guardar perfil"):
            st.session_state.profile.update({
                "nombre": nombre, "edad": edad, "telefono": telefono, "email": email,
                "contacto1": contacto1, "contacto2": contacto2, "grupo_sanguineo": grupo, "condiciones": condiciones
            })
            st.success("Perfil guardado.")
            # también actualizar emergency_number si usuario guardó contacto1
            if contacto1:
                st.session_state.emergency_number = contacto1

# ---------------- PESTAÑA: ANALISIS ----------------
with tab7:
    st.markdown("### 🧠 ANÁLISIS PREDICTIVO", unsafe_allow_html=True)
    st.info("""
    - Viernes 18:00–22:00: 70% más robos.
    - Zona Centro: 85% más incidentes días de pago.
    - Parques nocturnos: 45% más reportes de acoso.
    - Transporte público: 60% riesgo en horas pico.
    """)
    st.markdown("#### Registros de alertas (local):")
    if ALERT_LOG:
        for a in ALERT_LOG[-10:][::-1]:
            ts = a.get("cliente_ts") or a.get("server_received_at")
            st.markdown(f"- {a.get('tipo')} • {a.get('lat')},{a.get('lon')} • contacto: {a.get('contacto')}")
    else:
        st.write("Aún no hay alertas registradas en el servidor local.")

# ------------------ SIDEBAR - INFO ------------------
st.sidebar.markdown("## ⚙️ Info / Pruebas")
st.sidebar.info(f"""
• IP local detectada: {LOCAL_IP}
• Microservicio Flask: http://{LOCAL_IP}:{FLASK_PORT}/log_alert
• Ejecuta Streamlit con: `streamlit run huancayo_safety_app.py --server.address=0.0.0.0`
• Abre la Network URL en tu celular (misma Wi-Fi).
""")
