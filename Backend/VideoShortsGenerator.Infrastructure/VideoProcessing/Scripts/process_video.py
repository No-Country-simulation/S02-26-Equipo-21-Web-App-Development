import sys
import os
from moviepy import VideoFileClip
import moviepy.video.fx as vfx

def process_to_reel(input_path, output_path):
    try:
        # 1. Cargar el clip
        clip = VideoFileClip(input_path)
        w, h = clip.size
        
        # 2. Calcular dimensiones para 9:16
        target_ratio = 9/16
        target_width = h * target_ratio
        
        # 3. Recortar (Cálculo manual de coordenadas)
        x1 = (w - target_width) / 2
        y1 = 0
        x2 = x1 + target_width
        y2 = h
        
        # En v2.0 los efectos se aplican así:
        final_clip = clip.cropped(x1=x1, y1=y1, x2=x2, y2=y2)
        
        # 4. Redimensionar si es necesario
        if h != 1920:
            final_clip = final_clip.resized(height=1920)

        # 5. Guardar
        final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=30)
        
        clip.close()
        final_clip.close()
        print(f"Success: {output_path}")

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(1)
    process_to_reel(sys.argv[1], sys.argv[2])