"""
Script para convertir videos horizontales a formato vertical (9:16)
con detección inteligente de rostros/personas usando MediaPipe

Autor: Claude
Fecha: 2026-02-05
"""
# 
import cv2
import mediapipe as mp
import numpy as np
from pathlib import Path
import argparse
from typing import List, Tuple, Optional
import math


class VideoConverter:
    """
    Convierte videos horizontales a verticales enfocándose en rostros detectados
    """
    
    def __init__(self, input_path: str, output_path: str, target_aspect: Tuple[int, int] = (9, 16)):
        """
        Args:
            input_path: Ruta del video de entrada
            output_path: Ruta del video de salida
            target_aspect: Relación de aspecto objetivo (ancho, alto)
        """
        self.input_path = input_path
        self.output_path = output_path
        self.target_aspect = target_aspect
        
        # Inicializar MediaPipe Face Detection
        self.mp_face_detection = mp.solutions.face_detection
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=0,  # 0 = corto alcance (rápido), 1 = largo alcance
            min_detection_confidence=0.5
        )
        
        # Para suavizado de posición
        self.previous_center_x = None
        self.smoothing_factor = 0.3  # Mayor = más suave pero menos responsivo
        
    def get_face_center(self, frame: np.ndarray) -> Optional[int]:
        """
        Detecta rostros y retorna el centro X promedio
        
        Args:
            frame: Frame del video en formato BGR
            
        Returns:
            Posición X del centro de los rostros detectados, o None
        """
        # Convertir BGR a RGB para MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_detection.process(rgb_frame)
        
        if results.detections:
            frame_height, frame_width = frame.shape[:2]
            centers_x = []
            
            for detection in results.detections:
                bbox = detection.location_data.relative_bounding_box
                # Calcular centro del bounding box
                center_x = int((bbox.xmin + bbox.width / 2) * frame_width)
                centers_x.append(center_x)
            
            # Retornar promedio de centros
            return int(np.mean(centers_x))
        
        return None
    
    def smooth_position(self, current_x: int) -> int:
        """
        Suaviza la posición del recorte para evitar saltos bruscos
        
        Args:
            current_x: Posición X actual
            
        Returns:
            Posición X suavizada
        """
        if self.previous_center_x is None:
            self.previous_center_x = current_x
            return current_x
        
        # Interpolación lineal simple
        smoothed_x = int(
            self.previous_center_x * (1 - self.smoothing_factor) + 
            current_x * self.smoothing_factor
        )
        
        self.previous_center_x = smoothed_x
        return smoothed_x
    
    def calculate_crop_area(self, frame: np.ndarray, center_x: Optional[int]) -> Tuple[int, int, int, int]:
        """
        Calcula el área de recorte vertical
        
        Args:
            frame: Frame del video
            center_x: Centro X detectado (o None para centrar)
            
        Returns:
            Tupla (x1, y1, x2, y2) del área de recorte
        """
        frame_height, frame_width = frame.shape[:2]
        
        # Calcular dimensiones del recorte vertical (9:16)
        crop_width = int(frame_height * self.target_aspect[0] / self.target_aspect[1])
        crop_height = frame_height
        
        # Si el video es muy horizontal, ajustar
        if crop_width > frame_width:
            crop_width = frame_width
            crop_height = int(frame_width * self.target_aspect[1] / self.target_aspect[0])
        
        # Determinar posición X del recorte
        if center_x is None:
            # Sin detección: centrar
            x1 = (frame_width - crop_width) // 2
        else:
            # Con detección: centrar en rostro con límites
            x1 = center_x - crop_width // 2
            # Aplicar suavizado
            x1 = self.smooth_position(x1)
            # Asegurar que no se salga del frame
            x1 = max(0, min(x1, frame_width - crop_width))
        
        y1 = (frame_height - crop_height) // 2
        x2 = x1 + crop_width
        y2 = y1 + crop_height
        
        return x1, y1, x2, y2
    
    def process_video(self, process_every_n_frames: int = 3, show_progress: bool = True):
        """
        Procesa el video completo
        
        Args:
            process_every_n_frames: Procesar detección cada N frames (optimización)
            show_progress: Mostrar progreso en consola
        """
        # Abrir video de entrada
        cap = cv2.VideoCapture(self.input_path)
        
        if not cap.isOpened():
            raise ValueError(f"No se pudo abrir el video: {self.input_path}")
        
        # Obtener propiedades del video
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        print(f"\n📹 Video original: {original_width}x{original_height} @ {fps}fps")
        print(f"📊 Total de frames: {total_frames}")
        
        # Leer primer frame para calcular dimensiones de salida
        ret, first_frame = cap.read()
        if not ret:
            raise ValueError("No se pudo leer el primer frame")
        
        x1, y1, x2, y2 = self.calculate_crop_area(first_frame, None)
        output_width = x2 - x1
        output_height = y2 - y1
        
        print(f"🎯 Video de salida: {output_width}x{output_height} @ {fps}fps")
        print(f"📐 Relación de aspecto: {self.target_aspect[0]}:{self.target_aspect[1]}")
        
        # Configurar video de salida
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(self.output_path, fourcc, fps, (output_width, output_height))
        
        # Resetear video al inicio
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        
        frame_count = 0
        last_detected_center = None
        
        print(f"\n🔄 Procesando video...\n")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Detectar rostros cada N frames para optimizar
            if frame_count % process_every_n_frames == 0:
                detected_center = self.get_face_center(frame)
                if detected_center is not None:
                    last_detected_center = detected_center
            
            # Calcular área de recorte
            x1, y1, x2, y2 = self.calculate_crop_area(frame, last_detected_center)
            
            # Recortar frame
            cropped_frame = frame[y1:y2, x1:x2]
            
            # Escribir frame procesado
            out.write(cropped_frame)
            
            frame_count += 1
            
            # Mostrar progreso
            if show_progress and frame_count % 30 == 0:
                progress = (frame_count / total_frames) * 100
                print(f"⏳ Progreso: {progress:.1f}% ({frame_count}/{total_frames} frames)")
        
        # Liberar recursos
        cap.release()
        out.release()
        self.face_detection.close()
        
        print(f"\n✅ ¡Proceso completado!")
        print(f"📁 Video guardado en: {self.output_path}")
        print(f"📊 Frames procesados: {frame_count}")


def main():
    """Función principal con argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(
        description='Convierte videos horizontales a verticales con detección inteligente de rostros'
    )
    parser.add_argument(
        'input',
        type=str,
        help='Ruta del video de entrada'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Ruta del video de salida (default: input_vertical.mp4)'
    )
    parser.add_argument(
        '-f', '--frames',
        type=int,
        default=3,
        help='Procesar detección cada N frames (default: 3, mayor = más rápido pero menos preciso)'
    )
    parser.add_argument(
        '-ar', '--aspect-ratio',
        type=str,
        default='9:16',
        help='Relación de aspecto de salida (default: 9:16)'
    )
    
    args = parser.parse_args()
    
    # Validar archivo de entrada
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"❌ Error: El archivo '{args.input}' no existe")
        return
    
    # Generar ruta de salida si no se especifica
    if args.output is None:
        output_path = input_path.parent / f"{input_path.stem}_vertical{input_path.suffix}"
    else:
        output_path = Path(args.output)
    
    # Parsear aspect ratio
    try:
        aspect_parts = args.aspect_ratio.split(':')
        aspect_ratio = (int(aspect_parts[0]), int(aspect_parts[1]))
    except:
        print(f"❌ Error: Formato de aspect ratio inválido. Use formato 'ancho:alto' (ej: 9:16)")
        return

    # Crear conversor y procesar
    try:
        converter = VideoConverter(
            input_path=str(input_path),
            output_path=str(output_path),
            target_aspect=aspect_ratio
        )
        converter.process_video(process_every_n_frames=args.frames)
    except Exception as e:
        print(f"\n❌ Error durante el procesamiento: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
