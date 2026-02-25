# test_video.py - Script para probar con todas las configuraciones
import json
import subprocess
import sys
import os

# Ruta completa del script Python
script_path = r"C:\Users\jortiz\Downloads\simulacion\S02-26-Equipo-21-Web-App-Development\Backend\Python\script_final.py"

# Configuración de prueba
video_path = r"C:\Users\jortiz\Downloads\prueba.mp4"
output_path = r"C:\Users\jortiz\Downloads\output_test"

# Crear carpeta de salida si no existe
os.makedirs(output_path, exist_ok=True)

config = {
    # Parámetros de detección
    "sensibilidad_cambio_escena": 0.3,
    "umbral_volumen": 0.5,
    "min_duracion_segmento": 5,
    "max_duracion_segmento": 20,
    "priorizar": "balanceado",
    "cantidad_shorts": 3,
    "calidad_video": "720p",           # "480p", "720p", "1080p"
    
    # Parámetros de recorte

    #OPCIÓN 1: Recorte simple (SIN MediaPipe)
    #"modo_recorte": "centrado",        # Recorte fijo en el centro
    #"usar_mediapipe": False             # No usar MediaPipe

    # OPCIÓN 2: Recorte inteligente (CON MediaPipe)
    "modo_recorte": "seguimiento_persona",  # Activa el modo avanzado
    "usar_mediapipe": True                    # Necesario para este modo
}

# Convertir a JSON string
config_json = json.dumps(config)

print("=" * 60)
print("PRUEBA DE DETECCIÓN DE MOMENTOS INTERESANTES")
print("=" * 60)
print(f"Script: {script_path}")
print(f"Video: {video_path}")
print(f"Config: {config}")
print(f"Output: {output_path}")
print("=" * 60)
print("\nEjecutando...\n")

# Usar subprocess en lugar de os.system para mejor manejo
try:
    resultado = subprocess.run(
        [sys.executable, script_path, video_path, config_json, output_path],
        capture_output=True,
        text=True,
        check=False
    )
    
    print("=== SALIDA DEL SCRIPT ===")
    print(resultado.stdout)
    
    if resultado.stderr:
        print("\n=== ERRORES ===")
        print(resultado.stderr)
        
except Exception as e:
    print(f"Error al ejecutar: {e}")

print("\n" + "=" * 60)
print("PRUEBA COMPLETADA")
print("=" * 60)