"""
Script de ejemplo para probar el conversor de video

Este script muestra cómo usar el VideoConverter programáticamente
"""

from video_horizontal_to_vertical import VideoConverter
from pathlib import Path


def ejemplo_basico(entrada="mi_video_horizontal.mp4", salida="mi_video_vertical.mp4"):
    """Ejemplo de uso más simple"""
    print("=" * 60)
    print("EJEMPLO 1: Conversión Básica")
    print("=" * 60)
    
    # Reemplaza con tu archivo de video
    input_video = entrada
    output_video = salida
    
    if not Path(input_video).exists():
        print(f"⚠️  Archivo '{input_video}' no encontrado")
        print("   Crea un archivo de prueba o cambia la ruta")
        return
    
    # Crear conversor
    converter = VideoConverter(
        input_path=input_video,
        output_path=output_video
    )
    
    # Procesar
    converter.process_video()
    

def ejemplo_optimizado():
    """Ejemplo con optimización de velocidad"""
    print("\n" + "=" * 60)
    print("EJEMPLO 2: Conversión Optimizada (más rápida)")
    print("=" * 60)
    
    input_video = "video_largo.mp4"
    output_video = "video_vertical_rapido.mp4"
    
    if not Path(input_video).exists():
        print(f"⚠️  Archivo '{input_video}' no encontrado")
        return
    
    converter = VideoConverter(
        input_path=input_video,
        output_path=output_video
    )
    
    # Procesar cada 5 frames (más rápido)
    converter.process_video(process_every_n_frames=5)


def ejemplo_preciso():
    """Ejemplo con máxima precisión"""
    print("\n" + "=" * 60)
    print("EJEMPLO 3: Conversión Precisa (cada frame)")
    print("=" * 60)
    
    input_video = "presentacion.mp4"
    output_video = "presentacion_vertical_precisa.mp4"
    
    if not Path(input_video).exists():
        print(f"⚠️  Archivo '{input_video}' no encontrado")
        return
    
    converter = VideoConverter(
        input_path=input_video,
        output_path=output_video
    )
    
    # Procesar cada frame (más lento pero más preciso)
    converter.process_video(process_every_n_frames=1)


def ejemplo_aspecto_cuadrado():
    """Ejemplo con relación de aspecto cuadrada (1:1)"""
    print("\n" + "=" * 60)
    print("EJEMPLO 4: Conversión a Formato Cuadrado (1:1)")
    print("=" * 60)
    
    input_video = "video_instagram.mp4"
    output_video = "video_cuadrado.mp4"
    
    if not Path(input_video).exists():
        print(f"⚠️  Archivo '{input_video}' no encontrado")
        return
    
    # Aspecto cuadrado para Instagram posts
    converter = VideoConverter(
        input_path=input_video,
        output_path=output_video,
        target_aspect=(1, 1)  # 1:1 (cuadrado)
    )
    
    converter.process_video()


def ejemplo_multiples_videos():
    """Ejemplo procesando múltiples videos en lote"""
    print("\n" + "=" * 60)
    print("EJEMPLO 5: Procesamiento por Lotes")
    print("=" * 60)
    
    # Lista de videos a procesar
    videos = [
        "video1.mp4",
        "video2.mp4",
        "video3.mp4"
    ]
    
    for video in videos:
        if not Path(video).exists():
            print(f"⏭️  Saltando '{video}' (no existe)")
            continue
        
        output = f"{Path(video).stem}_vertical.mp4"
        
        print(f"\n🎬 Procesando: {video}")
        
        converter = VideoConverter(
            input_path=video,
            output_path=output
        )
        
        converter.process_video(process_every_n_frames=3)
        
        print(f"✅ Completado: {output}\n")


if __name__ == "__main__":
    print("\n🎥 EJEMPLOS DE USO DEL CONVERSOR DE VIDEO\n")
    
    # Descomentar el ejemplo que quieras probar:
    print("Ingrese el nombre del video de entrada (default: mi_video_horizontal.mp4):")
    input_video = input("Nombre del video de entrada: ").strip()
    output_video = f"{Path(input_video).stem}_vertical.mp4"
    ejemplo_basico(input_video, output_video)
    # ejemplo_optimizado()
    # ejemplo_preciso()
    # ejemplo_aspecto_cuadrado()
    # ejemplo_multiples_videos()
    
    print("\n" + "=" * 60)
    print("✨ Ejemplos completados")
    print("=" * 60)
