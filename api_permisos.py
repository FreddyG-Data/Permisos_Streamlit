from flask import Flask, request, jsonify
import pyodbc
from datetime import datetime

app = Flask(__name__)

def get_db_connection():
    return pyodbc.connect("DSN=Systemclub;UID=Santiago;PWD=1203f", autocommit=True)

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    nombre = data.get("nombre")
    password = data.get("password")

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT doc_empleado FROM dba.usuarios 
            WHERE nombre_usuario = ? AND password_usuario = ? AND activo = 'S'
        """, (nombre, password))
        row = cursor.fetchone()
        if row:
            return jsonify({"success": True, "doc_empleado": row[0]})
        else:
            return jsonify({"success": False, "message": "Credenciales inválidas o usuario inactivo"}), 401

@app.route("/empleados_activos", methods=["GET"])
def empleados_activos():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT nombre_usuario FROM dba.usuarios WHERE activo = 'S'")
        empleados = [row[0] for row in cursor.fetchall()]
    return jsonify(empleados)

@app.route("/nueva_solicitud", methods=["POST"])
def nueva_solicitud():
    data = request.get_json()
    doc_empleado = data.get("doc_empleado")
    fecha_solicitada = data.get("fecha_solicitada")
    hora_solicitada = data.get("hora_solicitada")  # ahora es un rango tipo "14:00 - 15:30"
    dependencia = data.get("dependencia")
    solicitado_por = data.get("solicitado_por")
    jefe_inmediato = data.get("jefe_inmediato")

    now = datetime.now()
    fecha_registro = now.strftime('%Y-%m-%d')
    hora_registro = now.strftime('%H:%M')

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO dba.permisos_salida (
                    doc_empleado, fecha_solicitada, hora_solicitada,
                    dependencia, solicitado_por, jefe_inmediato,
                    fecha_registro, hora_registro, estado
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Pendiente')
            """, (doc_empleado, fecha_solicitada, hora_solicitada,
                  dependencia, solicitado_por, jefe_inmediato,
                  fecha_registro, hora_registro))
        return jsonify({"message": "Solicitud registrada"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/aprobar_solicitud", methods=["POST"])
def aprobar_solicitud():
    data = request.json
    id_permiso = data.get("id_permiso")
    fecha = datetime.now().date()
    hora = datetime.now().time().strftime('%H:%M')

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE dba.permisos_salida
            SET estado = 'Aprobado', fecha_aprobacion = ?, hora_aprobacion = ?
            WHERE id_permiso = ?
        """, (fecha, hora, id_permiso))
    return jsonify({"success": True, "message": "Solicitud aprobada"})

@app.route("/solicitudes_aprobadas", methods=["GET"])
def solicitudes_aprobadas_pendientes():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id_permiso, solicitado_por, fecha_solicitada, hora_solicitada,
                   dependencia, jefe_inmediato
            FROM dba.permisos_salida
            WHERE estado = 'Aprobado' AND recibido_por IS NULL
            ORDER BY fecha_solicitada DESC
        """)
        rows = cursor.fetchall()
        results = []
        for row in rows:
            results.append({
                "id_permiso": row[0],
                "solicitado_por": row[1],
                "fecha_solicitada": str(row[2]),
                "hora_solicitada": row[3],
                "dependencia": row[4],
                "jefe_inmediato": row[5]
            })
    return jsonify(results)

@app.route("/marcar_recibido/<int:id_permiso>", methods=["PUT"])
def marcar_recibido(id_permiso):
    data = request.json
    recibido_por = data.get("recibido_por")
    fecha = datetime.now().date()
    hora = datetime.now().time().strftime('%H:%M')

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE dba.permisos_salida
            SET recibido_por = ?, fecha_recibido = ?, hora_recibido = ?
            WHERE id_permiso = ?
        """, (recibido_por, fecha, hora, id_permiso))
    return jsonify({"success": True, "message": "Solicitud marcada como recibida"})

@app.route("/mis_solicitudes/<doc_empleado>", methods=["GET"])
def mis_solicitudes(doc_empleado):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT fecha_solicitada, hora_solicitada, dependencia,
                   jefe_inmediato, estado, fecha_aprobacion,
                   fecha_recibido
            FROM dba.permisos_salida
            WHERE doc_empleado = ?
            ORDER BY fecha_solicitada DESC
        """, (doc_empleado,))
        rows = cursor.fetchall()
        results = []
        for row in rows:
            results.append({
                "fecha_solicitada": str(row[0]),
                "hora_solicitada": row[1],
                "dependencia": row[2],
                "jefe_inmediato": row[3],
                "estado": row[4],
                "fecha_aprobacion": str(row[5]) if row[5] else None,
                "fecha_recibido": str(row[6]) if row[6] else None,
            })
    return jsonify(results)

@app.route("/solicitudes_pendientes/<jefe_inmediato>", methods=["GET"])
def solicitudes_pendientes(jefe_inmediato):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id_permiso, solicitado_por, fecha_solicitada, hora_solicitada,
                   dependencia, estado
            FROM dba.permisos_salida
            WHERE jefe_inmediato = ? AND estado = 'Pendiente'
            ORDER BY fecha_solicitada DESC
        """, (jefe_inmediato,))
        rows = cursor.fetchall()
        results = []
        for row in rows:
            results.append({
                "id_permiso": row[0],
                "solicitado_por": row[1],
                "fecha_solicitada": str(row[2]),
                "hora_solicitada": row[3],
                "dependencia": row[4],
                "estado": row[5]
            })
    return jsonify(results)

if __name__ == "__main__":
    app.run(port=5002, debug=False)