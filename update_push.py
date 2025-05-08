import requests
import time
import os
import re

# Esperar un poco por si Ngrok aún no está listo
time.sleep(2)

# 1. Obtener la URL pública de Ngrok
try:
    response = requests.get("http://127.0.0.1:4040/api/tunnels")
    tunnels = response.json()["tunnels"]
    public_url = [t["public_url"] for t in tunnels if t["proto"] == "https"][0]
except Exception as e:
    print("❌ Error obteniendo la URL de Ngrok:", e)
    exit(1)

print("✅ URL pública de Ngrok:", public_url)

# 2. Archivos Streamlit a actualizar
modulos = ["empleado.py", "jefe.py", "rrhh.py"]

for archivo in modulos:
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            contenido = f.read()

        nuevo_contenido = re.sub(
            r'API_URL\s*=\s*["\']http://localhost:5002["\']',
            f'API_URL = "{public_url}"',
            contenido
        )

        with open(archivo, "w", encoding="utf-8") as f:
            f.write(nuevo_contenido)

        print(f"✅ Actualizado: {archivo}")

    except Exception as e:
        print(f"❌ Error actualizando {archivo}:", e)

# 3. Hacer git add, commit y push
os.system("git add .")
os.system(f'git commit -m "Actualización de Ngrok URL: {public_url}"')
os.system("git push")
print("🚀 Cambios subidos a GitHub.")
