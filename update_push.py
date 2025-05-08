import time
import os
import re
import requests

# Esperar a que Ngrok arranque
time.sleep(2)

# 1. Obtener la URL pública desde JSON de Ngrok
try:
    response = requests.get("http://127.0.0.1:4040/api/tunnels")
    print("📦 JSON recibido:")
    print(response.text)  # Para depuración

    tunnels = response.json()["tunnels"]
    public_url = [t["public_url"] for t in tunnels if t["proto"] == "https"][0]
    print("✅ URL pública extraída:", public_url)
except Exception as e:
    print("❌ Error obteniendo la URL de Ngrok:", e)
    exit(1)

# 2. Archivos Streamlit a actualizar
modulos = [
    "C:/Codigo/Permisos/empleado.py",
    "C:/Codigo/Permisos/jefe.py",
    "C:/Codigo/Permisos/recursos_humanos.py"
]

# 3. Reemplazar API_URL en los módulos
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

# 4. Push a GitHub
repo_dir = "C:/Codigo/Permisos"
os.chdir(repo_dir)

os.system("git add .")
os.system(f'git commit -m "Actualización de Ngrok URL: {public_url}"')
os.system("git push -u origin master")
print("🚀 Cambios subidos a GitHub.")