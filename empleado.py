import streamlit as st
import requests
from datetime import date, time

API_URL = "https://e05d-181-129-180-130.ngrok-free.app"

st.title("📄 Solicitud de Permiso de Salida")

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.subheader("🔐 Iniciar sesión")

    empleados_response = requests.get(f"{API_URL}/empleados_activos")
    empleados = empleados_response.json() if empleados_response.status_code == 200 else []

    with st.form("login_form"):
        nombre = st.selectbox("Nombre de usuario", empleados)
        password = st.text_input("Contraseña", type="password")
        submitted = st.form_submit_button("Ingresar")

        if submitted:
            response = requests.post(f"{API_URL}/login", json={
                "nombre": nombre,
                "password": password
            })
            if response.status_code == 200:
                st.session_state.autenticado = True
                st.session_state.nombre = nombre
                st.session_state.doc_empleado = response.json()["doc_empleado"]
                st.success("Inicio de sesión exitoso.")
                st.rerun()
            else:
                st.error("Credenciales inválidas o usuario inactivo.")
    st.stop()

st.subheader("📝 Crear nueva solicitud")

empleados_response = requests.get(f"{API_URL}/empleados_activos")
empleados = empleados_response.json() if empleados_response.status_code == 200 else []

with st.form("solicitud_form"):
    fecha_solicitada = st.date_input("Fecha de salida", min_value=date.today())
    hora_inicio = st.time_input("Hora de inicio", time(12, 0))
    hora_fin = st.time_input("Hora de fin", time(13, 0))
    dependencia = st.text_input("Dependencia / Departamento")
    jefe_inmediato = st.selectbox("Jefe inmediato", empleados)

    enviar = st.form_submit_button("Enviar solicitud")

    if enviar:
        hora_rango = f"{hora_inicio.strftime('%H:%M')} - {hora_fin.strftime('%H:%M')}"
        data = {
            "doc_empleado": st.session_state.doc_empleado,
            "fecha_solicitada": fecha_solicitada.strftime('%Y-%m-%d'),
            "hora_solicitada": hora_rango,
            "dependencia": dependencia,
            "solicitado_por": st.session_state.nombre,
            "jefe_inmediato": jefe_inmediato
        }
        response = requests.post(f"{API_URL}/nueva_solicitud", json=data)
        if response.status_code == 200:
            st.success("✅ Solicitud registrada con éxito.")
        else:
            st.error("❌ Error al registrar la solicitud.")

st.subheader("📚 Mis solicitudes registradas")

solicitudes_response = requests.get(f"{API_URL}/mis_solicitudes/{st.session_state.doc_empleado}")
if solicitudes_response.status_code == 200:
    solicitudes = solicitudes_response.json()
    if solicitudes:
        st.dataframe(solicitudes)
    else:
        st.info("No tienes solicitudes registradas.")
else:
    st.error("Error al cargar tus solicitudes.")