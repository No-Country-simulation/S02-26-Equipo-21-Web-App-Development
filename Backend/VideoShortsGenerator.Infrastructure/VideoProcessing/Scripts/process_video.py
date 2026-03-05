import sys
import os
from moviepy import VideoFileClip, CompositeVideoClip, ColorClip

def process_to_reel(input_path, output_path):
    try:
        # 1. Cargar el clip
        clip = VideoFileClip(input_path)
        
        # Tamaño estándar de Shorts/Reels
        target_w = 1080
        target_h = 1920
        
        # 2. Redimensionar el clip
        main_clip = clip.resized(width=target_w)
        
        # 3. Crear un fondo negro
        background = ColorClip(size=(target_w, target_h), color=(0, 0, 0))
        background = background.with_duration(clip.duration)

        # 4. Poner el video original centrado sobre el fondo negro
        final_video = CompositeVideoClip(
            [background, main_clip.with_position("center")], 
            size=(target_w, target_h)
        )

        # 5. Configurar duración y exportar
        final_video.duration = clip.duration
        final_video.write_videofile(
            output_path, 
            codec="libx264", 
            audio_codec="aac", 
            fps=30
        )
        
        clip.close()
        final_video.close()
        print(f"Success: {output_path}")

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(1)
    process_to_reel(sys.argv[1], sys.argv[2])