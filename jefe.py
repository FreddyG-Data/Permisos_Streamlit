import streamlit as st
import requests
from datetime import datetime

API_URL = "https://a3ac-181-129-180-130.ngrok-free.app"

st.title("🧑‍💼 Aprobación de Permisos - Jefe Inmediato")

# Autenticación
if "autenticado_jefe" not in st.session_state:
    st.session_state.autenticado_jefe = False

if not st.session_state.autenticado_jefe:
    st.subheader("🔐 Iniciar sesión")

    # Obtener lista de empleados activos
    empleados_response = requests.get(f"{API_URL}/empleados_activos")
    empleados = empleados_response.json() if empleados_response.status_code == 200 else []

    with st.form("login_form_jefe"):
        nombre_jefe = st.selectbox("Nombre de usuario", empleados)
        password = st.text_input("Contraseña", type="password")
        submitted = st.form_submit_button("Ingresar")

        if submitted:
            response = requests.post(f"{API_URL}/login", json={
                "nombre": nombre_jefe,
                "password": password
            })
            if response.status_code == 200:
                st.session_state.autenticado_jefe = True
                st.session_state.nombre_jefe = nombre_jefe
                st.session_state.doc_jefe = response.json()["doc_empleado"]
                st.success("Inicio de sesión exitoso.")
            else:
                st.error("Credenciales inválidas o usuario inactivo.")
    st.stop()

# Consultar solicitudes pendientes donde el usuario es jefe_inmediato
st.subheader("📥 Solicitudes pendientes por aprobar")

response = requests.get(f"{API_URL}/solicitudes_pendientes/{st.session_state.nombre_jefe}")

if response.status_code == 200:
    solicitudes = response.json()

    if solicitudes:
        for solicitud in solicitudes:
            with st.expander(f"Solicitud de {solicitud['solicitado_por']} - {solicitud['fecha_solicitada']} {solicitud['hora_solicitada']}"):
                st.write(f"**Dependencia:** {solicitud['dependencia']}")
                st.write(f"**Fecha solicitada:** {solicitud['fecha_solicitada']}")
                st.write(f"**Hora solicitada:** {solicitud['hora_solicitada']}")
                st.write(f"**Estado actual:** {solicitud['estado']}")

                if st.button(f"✅ Aprobar solicitud", key=f"aprobar_{solicitud['id_permiso']}"):
                    now = datetime.now()
                    data = {
                        "id_permiso": solicitud["id_permiso"],
                        "jefe_inmediato": st.session_state.nombre_jefe,
                        "fecha_aprobacion": now.strftime("%Y-%m-%d"),
                        "hora_aprobacion": now.strftime("%H:%M"),
                        "estado": "Aprobado"
                    }
                    approve_response = requests.post(f"{API_URL}/aprobar_solicitud", json=data)
                    if approve_response.status_code == 200:
                        st.success("Solicitud aprobada.")
                        st.rerun()
                    else:
                        st.error("Error al aprobar la solicitud.")
    else:
        st.info("No tienes solicitudes pendientes.")
else:
    st.error("Error al consultar las solicitudes.")