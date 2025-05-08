import streamlit as st
import requests

API_URL = "https://e229-181-129-180-130.ngrok-free.app"
USUARIOS_AUTORIZADOS = ["ESTHER JAIMES", "LUDY ARGUELLO"]

st.title("📥 Registro de Solicitudes Recibidas")

if "rrhh_autenticado" not in st.session_state:
    st.session_state.rrhh_autenticado = False

if not st.session_state.rrhh_autenticado:
    empleados_response = requests.get(f"{API_URL}/empleados_activos")
    empleados = empleados_response.json() if empleados_response.status_code == 200 else []

    autorizados = [e for e in empleados if e.strip().upper() in [u.upper() for u in USUARIOS_AUTORIZADOS]]

    st.subheader("🔐 Iniciar sesión (RRHH)")

    with st.form("login_rrhh"):
        nombre = st.selectbox("Nombre de usuario (RRHH)", autorizados)
        password = st.text_input("Contraseña", type="password")
        login = st.form_submit_button("Ingresar")

        if login:
            response = requests.post(f"{API_URL}/login", json={
                "nombre": nombre,
                "password": password
            })
            if response.status_code == 200 and nombre in USUARIOS_AUTORIZADOS:
                st.session_state.rrhh_autenticado = True
                st.session_state.nombre_rrhh = nombre
                st.success("Autenticación exitosa.")
                st.rerun()
            else:
                st.error("Credenciales inválidas o usuario no autorizado.")
    st.stop()

st.subheader("📋 Solicitudes aprobadas no registradas")

response = requests.get(f"{API_URL}/solicitudes_aprobadas")
if response.status_code == 200:
    solicitudes = response.json()
    if solicitudes:
        for solicitud in solicitudes:
            with st.expander(f"Solicitud #{solicitud['id_permiso']} - {solicitud['solicitado_por']}"):
                st.write(f"📅 Fecha: {solicitud['fecha_solicitada']}")
                st.write(f"⏰ Hora: {solicitud['hora_solicitada']}")
                st.write(f"📌 Dependencia: {solicitud['dependencia']}")
                st.write(f"👤 Jefe Inmediato: {solicitud['jefe_inmediato']}")
                if st.button("Marcar como recibida", key=solicitud["id_permiso"]):
                    res = requests.post(f"{API_URL}/recibir_solicitud", json={
                        "id_permiso": solicitud["id_permiso"],
                        "recibido_por": st.session_state.nombre_rrhh
                    })
                    if res.status_code == 200:
                        st.success("Solicitud marcada como recibida.")
                        st.rerun()
                    else:
                        st.error("Error al registrar recepción.")
    else:
        st.info("No hay solicitudes pendientes de recibir.")
else:
    st.error("Error al consultar solicitudes.")