#!/usr/bin/env python3
import sys
import os
import traceback
from moviepy.editor import VideoFileClip

def process_simple(input_path: str, output_path: str) -> None:
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input not found: {input_path}")

    clip = VideoFileClip(input_path)
    try:
        w, h = clip.size
        target_ratio = 9 / 16
        target_width = int(h * target_ratio)

        x1 = int(max(0, (w - target_width) / 2))
        x2 = x1 + target_width
        # Crop and resize to vertical (width x height)
        cropped = clip.crop(x1=x1, y1=0, x2=x2, y2=h)
        final = cropped.resize(height=1920)  # objetivo: 1080x1920 (se escala por altura)

        final.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=30, logger=None)
    finally:
        try:
            clip.close()
        except:
            pass
        try:
            cropped.close()
            final.close()
        except:
            pass

if __name__ == "__main__":
    try:
        if len(sys.argv) < 3:
            print("Error: requiere input_path y output_path", file=sys.stderr)
            sys.exit(1)
        input_path = sys.argv[1]
        output_path = sys.argv[2]
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        process_simple(input_path, output_path)
        print(f"Success: {output_path}")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)