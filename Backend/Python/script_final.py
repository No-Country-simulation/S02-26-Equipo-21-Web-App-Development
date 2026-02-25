# =============================================================================================
# script_procesamiento.py - ÚNICO SCRIPT COMPLETO
# Procesamiento de video horizontal a vertical con detección de momentos interesantes (shorts)
# Recibe: input_path, config (json), output_path
# Retorna: JSON con rutas de videos generados y duraciones
# =============================================================================================

# ==========================================================
# SILENCIAR WARNINGS (AL INICIO, ANTES DE CUALQUIER IMPORT)
# ==========================================================
import warnings
warnings.filterwarnings("ignore")
warnings.simplefilter("ignore")

import cv2
import numpy as np
import librosa
from scenedetect import SceneManager, open_video, ContentDetector
import os
import json
import sys
import subprocess
from typing import List, Tuple, Dict, Optional, Any
import logging
import traceback
import concurrent.futures
import multiprocessing
import time

# Importar MediaPipe correctamente para la versión 0.10.14
import mediapipe as mp
mp_pose = mp.solutions.pose
mp_face_detection = mp.solutions.face_detection

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constantes
FFMPEG_CMD = 'ffmpeg'
FFPROBE_CMD = 'ffprobe'
DEFAULT_TIMEOUT = 300

# ============================================
# DETECCIÓN DE GPU
# ============================================
def detectar_gpu() -> bool:
    try:
        result = subprocess.run(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'], 
                               capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and result.stdout.strip():
            logger.info(f"✅ GPU NVIDIA detectada")
            result_ff = subprocess.run([FFMPEG_CMD, '-encoders'], capture_output=True, text=True)
            if 'h264_nvenc' in result_ff.stdout:
                logger.info("✅ Codificador NVIDIA NVENC disponible")
                return True
    except:
        pass
    logger.info("ℹ️ Usando CPU")
    return False

HAS_GPU = detectar_gpu()


# ============================================
# CONSTANTES DE RESOLUCIÓN
# ============================================
class ResolucionVertical:
    CALIDADES = {
        '480p': (480, 854),    # SD - Más rápido
        '720p': (720, 1280),   # HD - Balanceado
        '1080p': (1080, 1920)  # Full HD - Más lento, mejor calidad
    }
    DEFAULT = '1080p'
    
    @classmethod
    def obtener_resolucion(cls, calidad: str) -> Tuple[int, int]:
        """
        Obtiene la resolución para una calidad dada.
        Si la calidad no existe, usa la default.
        """
        if calidad not in cls.CALIDADES:
            logger.warning(f"Calidad '{calidad}' no reconocida. Usando {cls.DEFAULT}")
            calidad = cls.DEFAULT
        return cls.CALIDADES[calidad]


# ============================================
# FUNCIÓN PARA OBTENER DURACIÓN DEL VIDEO
# ============================================
def obtener_duracion_video(video_path: str) -> float:
    """
    Obtiene la duración en segundos de un video usando ffprobe.
    
    Args:
        video_path: Ruta al video
        
    Returns:
        Duración en segundos (0 si hay error)
    """
    try:
        cmd = [
            FFPROBE_CMD, '-v', 'error', '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1', video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and result.stdout.strip():
            return float(result.stdout.strip())
    except Exception as e:
        logger.warning(f"Error obteniendo duración: {e}")
    return 0.0


# ============================================
# FUNCIÓN PARA GENERAR NOMBRE BASE DEL VIDEO
# ============================================
def obtener_nombre_base(video_path: str) -> str:
    """
    Obtiene el nombre base del video original (sin extensión, limpio).
    
    Args:
        video_path: Ruta completa del video
        
    Returns:
        Nombre base limpio (sin espacios, caracteres especiales, etc.)
    """
    # Obtener nombre del archivo sin extensión
    nombre_base = os.path.splitext(os.path.basename(video_path))[0]

    # Limpiar caracteres problemáticos para nombres de archivo
    # Reemplazar espacios y guiones por underscore
    nombre_base = nombre_base.replace(' ', '_').replace('-', '_')

    # Eliminar caracteres especiales (mantener letras, números y underscore)
    import re
    nombre_base = re.sub(r'[^a-zA-Z0-9_]', '', nombre_base)

    # Convertir a minúsculas para consistencia
    nombre_base = nombre_base.lower()
    return nombre_base or "video"


# ============================================
# FUNCIÓN PARA OBTENER DIMENSIONES DEL VIDEO
# ============================================
def obtener_dimensiones_video(video_path: str) -> Tuple[int, int]:
    try:
        probe_cmd = [
            FFPROBE_CMD, '-v', 'error', '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height', '-of', 'csv=p=0',
            video_path
        ]
        result = subprocess.run(probe_cmd, capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            dims = result.stdout.strip().split(',')
            return int(dims[0]), int(dims[1])
    except Exception as e:
        logger.warning(f"Error obteniendo dimensiones: {e}")
    return 1920, 1080


# ============================================
# FUNCIÓN PARA CONVERTIR VIDEO CON FFMPEG
# ============================================
def convertir_con_ffmpeg(input_path: str, output_path: str, 
                          inicio: Optional[float] = None, 
                          fin: Optional[float] = None,
                          ancho_destino: int = 720, 
                          alto_destino: int = 1280,
                          centro_x: Optional[int] = None,
                          usar_gpu: bool = False) -> bool:
    try:
        ancho_orig, alto_orig = obtener_dimensiones_video(input_path)
        
        nuevo_alto = alto_orig
        nuevo_ancho = int(alto_orig * 9 / 16)
        
        if nuevo_ancho > ancho_orig:
            nuevo_ancho = ancho_orig
            nuevo_alto = int(ancho_orig * 16 / 9)
        
        if centro_x is not None:
            x1 = max(0, centro_x - nuevo_ancho // 2)
            x2 = min(ancho_orig, x1 + nuevo_ancho)
            if x2 > ancho_orig:
                x2 = ancho_orig
                x1 = ancho_orig - nuevo_ancho
            if x1 < 0:
                x1 = 0
                x2 = nuevo_ancho
        else:
            x_centro = ancho_orig // 2
            x1 = max(0, x_centro - nuevo_ancho // 2)
            x2 = min(ancho_orig, x1 + nuevo_ancho)
            if x2 > ancho_orig:
                x2 = ancho_orig
                x1 = ancho_orig - nuevo_ancho
            if x1 < 0:
                x1 = 0
                x2 = nuevo_ancho
        
        filter_complex = f"crop={x2-x1}:{nuevo_alto}:{x1}:0,scale={ancho_destino}:{alto_destino}"
        
        cmd = [FFMPEG_CMD, '-i', input_path]
        
        if inicio is not None and fin is not None:
            cmd.extend(['-ss', str(inicio), '-to', str(fin)])
        
        if usar_gpu and HAS_GPU:
            vcodec = 'h264_nvenc'
            preset = 'p1'
            cmd.extend(['-rc', 'vbr', '-cq', '23', '-b:v', '0'])
        else:
            vcodec = 'libx264'
            preset = 'veryfast'
        
        cmd.extend([
            '-vf', filter_complex,
            '-c:v', vcodec,
            '-preset', preset,
            '-crf', '23',
            '-c:a', 'aac',
            '-b:a', '128k',
            '-threads', str(multiprocessing.cpu_count()),
            '-y', output_path
        ])
        
        # Capturar salida como binario para evitar errores de codificación
        result = subprocess.run(cmd, capture_output=True)
        
        if result.returncode != 0:
            # Intentar decodificar error si es posible
            try:
                error_msg = result.stderr.decode('utf-8', errors='ignore')[:200]
            except:
                error_msg = "Error desconocido en FFmpeg"
            logger.error(f"Error FFmpeg: {error_msg}")
            return False
        
        return os.path.exists(output_path) and os.path.getsize(output_path) > 0
        
    except Exception as e:
        logger.error(f"Error en conversión FFmpeg: {e}")
        return False


# ============================================
# CLASE PARA SEGUIMIENTO CON MEDIAPIPE
# ============================================
class SeguimientoPersonas:
    """
    Clase para seguimiento de personas usando MediaPipe.
    """
    def __init__(self):
        self.pose = mp_pose.Pose(
            static_image_mode=False,
            model_complexity=0,
            smooth_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.face_detection = mp_face_detection.FaceDetection(
            model_selection=0,
            min_detection_confidence=0.5
        )
        logger.info("✅ MediaPipe inicializado")
    
    def detectar_punto_interes(self, frame: np.ndarray) -> Optional[Tuple[int, int, float]]:
        
        try:
            # Convertir BGR a RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width = frame.shape[:2]
            
            # 1. Intentar detección facial (más rápido)
            results_face = self.face_detection.process(frame_rgb)
            if results_face and results_face.detections:
                # Usar la primera cara detectada
                detection = results_face.detections[0]
                bbox = detection.location_data.relative_bounding_box
                x = int((bbox.xmin + bbox.width/2) * width)
                y = int((bbox.ymin + bbox.height/2) * height)
                return (x, y, detection.score[0])
            
            # 2. Si no hay cara, intentar con pose completa
            results_pose = self.pose.process(frame_rgb)
            if results_pose and results_pose.pose_landmarks:
                # Usar el punto medio de los hombros como referencia
                left = results_pose.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]
                right = results_pose.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER]
                if left and right:
                    x = int(((left.x + right.x) / 2) * width)
                    y = int(((left.y + right.y) / 2) * height)
                    return (x, y, 0.8) # Confianza media
            
            return None
        except Exception:
            return None
    
    def cerrar(self):
        self.pose.close()
        self.face_detection.close()


# ============================================
# CLASE VIDEO ANALYZER - CON ANÁLISIS DE AUDIO
# ============================================
class VideoAnalyzer:
    def __init__(self, config: Dict):
        """
        Inicializa el analizador con configuración.
        
        Args:
            config: Diccionario con parámetros:
                - sensibilidad_cambio_escena: float (0.1 a 0.5)
                - umbral_volumen: float
                - min_duracion_segmento: int (segundos)
                - max_duracion_segmento: int (segundos)
                - priorizar: str ('audio', 'video', 'balanceado')
                - cantidad_shorts: int
                - calidad_video: str ('480p', '720p', '1080p') - opcional
                - modo_recorte: str ('centrado', 'seguimiento_persona')
                - usar_mediapipe: bool
        """
        self.config = config
        self.seguimiento = None
        self._validate_config()
        self._init_seguimiento()
    
    def _validate_config(self):
        
        required = ['sensibilidad_cambio_escena', 'umbral_volumen', 
                    'min_duracion_segmento', 'max_duracion_segmento', 
                    'priorizar', 'modo_recorte', 'usar_mediapipe']
        for param in required:
            if param not in self.config:
                raise ValueError(f"Falta parámetro: {param}")
        
        if self.config['modo_recorte'] == 'seguimiento_persona' and not self.config['usar_mediapipe']:
            raise ValueError("modo_recorte='seguimiento_persona' requiere usar_mediapipe=True")
    
    def _init_seguimiento(self):
        if self.config['modo_recorte'] == 'seguimiento_persona' and self.config['usar_mediapipe']:
            self.seguimiento = SeguimientoPersonas()
            logger.info("🔄 Seguimiento de personas activado")
    
    def _analizar_audio(self, video_path: str) -> List[Tuple[int, int, float]]:
        """Analiza audio y retorna momentos con alta energía"""
        audio_temp = None
        try:
            audio_temp = video_path + "_temp_audio.wav"
            
            # Extraer audio con FFmpeg - CAPTURAR SALIDA COMO BINARIO
            cmd = [
                FFMPEG_CMD, '-i', video_path,
                '-vn', '-acodec', 'pcm_s16le',
                '-ar', '44100', '-ac', '1', '-y', audio_temp
            ]
            
            logger.info(f"Extrayendo audio...")
            # Capturar salida como binario, NO como texto
            result = subprocess.run(cmd, capture_output=True)
            
            # Verificar si el archivo se creó
            if not os.path.exists(audio_temp) or os.path.getsize(audio_temp) == 0:
                logger.warning("No se pudo extraer audio")
                return []
            
            # Cargar y analizar con librosa
            y, sr = librosa.load(audio_temp, sr=44100, mono=True)
            frame_length = int(sr * 2)
            hop_length = int(sr * 0.5)
            
            rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
            times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop_length)
            
            umbral = self.config.get('umbral_volumen', 0.5) * np.max(rms)
            
            momentos = []
            en_segmento = False
            inicio = 0
            energia = 0
            
            for i, val in enumerate(rms):
                t = times[i]
                if val > umbral and not en_segmento:
                    en_segmento = True
                    inicio = max(0, t - 1)
                    energia = val
                elif val > umbral and en_segmento:
                    energia += val
                elif val <= umbral and en_segmento:
                    fin = t + 1
                    duracion = fin - inicio
                    if duracion >= 2:
                        punt = min(energia / (duracion * len(rms)) * 100, 1.0)
                        momentos.append((int(inicio), int(fin), punt))
                    en_segmento = False
                    energia = 0
            
            logger.info(f"✅ Audio analizado: {len(momentos)} momentos detectados")
            return momentos
            
        except Exception as e:
            logger.error(f"Error en análisis de audio: {e}")
            return []
        finally:
            if audio_temp and os.path.exists(audio_temp):
                try:
                    os.remove(audio_temp)
                except:
                    pass
    
    def _analizar_movimiento(self, video_path: str) -> List[Tuple[int, int, float]]:
        try:
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS) or 30
            skip = 5
            resultados = []
            
            ret, prev = cap.read()
            if not ret:
                return []
            
            prev = cv2.resize(prev, (640, 360))
            prev_gray = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)
            frame_count = 0
            segment_start = None
            acumulado = 0
            
            while True:
                for _ in range(skip - 1):
                    if not cap.grab():
                        break
                    frame_count += 1
                
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame = cv2.resize(frame, (640, 360))
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                diff = cv2.absdiff(prev_gray, gray)
                movimiento = np.mean(diff)
                
                if movimiento > 10:
                    if segment_start is None:
                        segment_start = frame_count / fps
                    acumulado += movimiento
                else:
                    if segment_start is not None:
                        segment_end = frame_count / fps
                        duracion = segment_end - segment_start
                        if duracion >= 2:
                            puntuacion = min(acumulado / (duracion * fps) / 25, 1.0)
                            resultados.append((int(segment_start), int(segment_end), puntuacion))
                        segment_start = None
                        acumulado = 0
                
                prev_gray = gray
                frame_count += 1
            
            cap.release()
            logger.info(f"✅ Movimiento analizado: {len(resultados)} momentos")
            return resultados
        except Exception as e:
            logger.error(f"Error análisis movimiento: {e}")
            return []
    
    def detectar_momentos_interesantes(self, video_path: str) -> List[Tuple[int, int]]:
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video no encontrado: {video_path}")
        
        logger.info(f"Analizando video: {video_path}")
        
        # Verificar video - capturar salida como binario
        cmd = [FFMPEG_CMD, '-v', 'error', '-i', video_path, '-f', 'null', '-']
        subprocess.run(cmd, capture_output=True)
        
        # Detectar escenas
        video = open_video(video_path)
        scene_manager = SceneManager()
        threshold = 15 + (self.config['sensibilidad_cambio_escena'] * 30)
        scene_manager.add_detector(ContentDetector(threshold=threshold))
        scene_manager.detect_scenes(video)
        
        escenas = []
        for scene in scene_manager.get_scene_list():
            start = int(scene[0].get_seconds())
            end = int(scene[1].get_seconds())
            escenas.append((start, end))
        
        logger.info(f"📽️ Escenas detectadas: {len(escenas)}")
        
        # ANÁLISIS DE AUDIO
        momentos_audio = self._analizar_audio(video_path)
        
        # Análisis de movimiento
        momentos_movimiento = self._analizar_movimiento(video_path)
        
        # Combinar métricas
        priorizar = self.config['priorizar']
        segmentos = []
        
        for inicio, fin in escenas:
            punt = 0.5
            
            # Buscar audio coincidente
            if momentos_audio:
                for a_inicio, a_fin, a_punt in momentos_audio:
                    if max(inicio, a_inicio) < min(fin, a_fin):
                        if priorizar == 'audio':
                            punt = a_punt
                        elif priorizar == 'balanceado':
                            punt = (punt + a_punt) / 2
                        break
            
            # Buscar movimiento coincidente
            if momentos_movimiento:
                for m_inicio, m_fin, m_punt in momentos_movimiento:
                    if max(inicio, m_inicio) < min(fin, m_fin):
                        if priorizar == 'video':
                            punt = m_punt
                        elif priorizar == 'balanceado':
                            punt = (punt + m_punt) / 2
                        break
            
            segmentos.append((inicio, fin, punt))
        
        # Ordenar por puntuación
        segmentos.sort(key=lambda x: x[2], reverse=True)
        
        # Filtrar por duración
        resultado = []
        for inicio, fin, _ in segmentos:
            duracion = fin - inicio
            if self.config['min_duracion_segmento'] <= duracion <= self.config['max_duracion_segmento']:
                resultado.append((inicio, fin))
        
        logger.info(f"🎯 Segmentos finales: {len(resultado)}")
        return resultado[:self.config.get('cantidad_shorts', 3)]
    
    def calcular_centro_recorte(self, video_path: str, segmento: Tuple[int, int]) -> Optional[int]:
        if not self.seguimiento:
            return None
        
        try:
            ancho_orig, _ = obtener_dimensiones_video(video_path)
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            start_frame = int(segmento[0] * fps)
            end_frame = int(segmento[1] * fps)
            step = max(1, (end_frame - start_frame) // 5)
            
            puntos = []
            pesos = []
            cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
            
            for f in range(start_frame, end_frame, step):
                cap.set(cv2.CAP_PROP_POS_FRAMES, f)
                ret, frame = cap.read()
                if not ret:
                    break
                
                small = cv2.resize(frame, (640, 480))
                punto = self.seguimiento.detectar_punto_interes(small)
                if punto:
                    x, _, conf = punto
                    x_orig = int(x * ancho_orig / 640)
                    puntos.append(x_orig)
                    pesos.append(conf)
            
            cap.release()
            
            if puntos:
                return int(np.average(puntos, weights=pesos))
        except Exception as e:
            logger.error(f"Error calculando centro: {e}")
        
        return None
    
    def cerrar(self):
        if self.seguimiento:
            self.seguimiento.cerrar()


# ============================================
# FUNCIONES DE GENERACIÓN
# ============================================
def detectar_momentos_interesantes(video_path, config):
    analizador = None
    try:
        analizador = VideoAnalyzer(config)
        return analizador.detectar_momentos_interesantes(video_path)
    except Exception as e:
        logger.error(f"Error detectando momentos: {e}")
        return []
    finally:
        if analizador:
            analizador.cerrar()


def generar_short(video_path, inicio, fin, output_path, config):
    logger.info(f"Generando short: {output_path} ({inicio}s-{fin}s)")
    
    try:
        calidad = config.get('calidad_video', ResolucionVertical.DEFAULT)
        ancho, alto = ResolucionVertical.obtener_resolucion(calidad)
        
        centro_x = None
        if config.get('modo_recorte') == 'seguimiento_persona' and config.get('usar_mediapipe'):
            analizador = VideoAnalyzer(config)
            centro_x = analizador.calcular_centro_recorte(video_path, (inicio, fin))
            analizador.cerrar()
            if centro_x:
                logger.info(f"Centro detectado: x={centro_x}")
        
        ok = convertir_con_ffmpeg(video_path, output_path, inicio, fin, ancho, alto, centro_x, HAS_GPU)
        
        if ok:
            return output_path
        
        logger.warning("FFmpeg falló, usando fallback")
        return _fallback_moviepy(video_path, inicio, fin, output_path, config)
        
    except Exception as e:
        logger.error(f"Error generando short: {e}")
        return _fallback_moviepy(video_path, inicio, fin, output_path, config)


def _fallback_moviepy(video_path, inicio, fin, output_path, config):
    try:
        from moviepy import VideoFileClip
        
        calidad = config.get('calidad_video', ResolucionVertical.DEFAULT)
        ancho, alto = ResolucionVertical.obtener_resolucion(calidad)
        
        clip = VideoFileClip(video_path)
        duracion = clip.duration
        
        if inicio >= duracion or fin > duracion:
            inicio = max(0, min(inicio, duracion - 1))
            fin = min(fin, duracion)
        
        segmento = clip.subclipped(inicio, fin)
        ancho_orig, alto_orig = segmento.size
        
        nuevo_alto = alto_orig
        nuevo_ancho = int(alto_orig * 9 / 16)
        
        if nuevo_ancho > ancho_orig:
            nuevo_ancho = ancho_orig
            nuevo_alto = int(ancho_orig * 16 / 9)
        
        x_centro = ancho_orig // 2
        x1 = max(0, x_centro - nuevo_ancho // 2)
        x2 = min(ancho_orig, x1 + nuevo_ancho)
        
        if x2 > ancho_orig:
            x2 = ancho_orig
            x1 = ancho_orig - nuevo_ancho
        if x1 < 0:
            x1 = 0
            x2 = nuevo_ancho
        
        vertical = segmento.cropped(x1=x1, y1=0, x2=x2, y2=nuevo_alto)
        final = vertical.resized((ancho, alto))
        final.write_videofile(output_path, codec='libx264', audio_codec='aac', logger=None)
        
        clip.close()
        return output_path
    except Exception as e:
        logger.error(f"Error en fallback: {e}")
        return output_path


def generar_video_completo(video_path, output_path, config):
    logger.info(f"Generando video completo: {output_path}")
    
    try:
        calidad = config.get('calidad_video', ResolucionVertical.DEFAULT)
        ancho, alto = ResolucionVertical.obtener_resolucion(calidad)
        
        centro_x = None
        if config.get('modo_recorte') == 'seguimiento_persona' and config.get('usar_mediapipe'):
            analizador = VideoAnalyzer(config)
            ancho_orig, _ = obtener_dimensiones_video(video_path)
            
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duracion = frames / fps if fps > 0 else 0
            
            muestras = []
            for t in np.arange(0, duracion, 10):
                cap.set(cv2.CAP_PROP_POS_FRAMES, int(t * fps))
                ret, frame = cap.read()
                if ret:
                    small = cv2.resize(frame, (640, 480))
                    punto = analizador.seguimiento.detectar_punto_interes(small)
                    if punto:
                        x, _, _ = punto
                        muestras.append(int(x * ancho_orig / 640))
            
            cap.release()
            analizador.cerrar()
            
            if muestras:
                centro_x = int(np.mean(muestras))
                logger.info(f"Centro promedio: x={centro_x}")
        
        ok = convertir_con_ffmpeg(video_path, output_path, None, None, ancho, alto, centro_x, HAS_GPU)
        
        if ok:
            return output_path
        
        logger.warning("FFmpeg falló, usando fallback")
        return _fallback_moviepy_completo(video_path, output_path, config)
        
    except Exception as e:
        logger.error(f"Error generando video completo: {e}")
        return _fallback_moviepy_completo(video_path, output_path, config)


def _fallback_moviepy_completo(video_path, output_path, config):
    try:
        from moviepy import VideoFileClip
        
        calidad = config.get('calidad_video', ResolucionVertical.DEFAULT)
        ancho, alto = ResolucionVertical.obtener_resolucion(calidad)
        
        clip = VideoFileClip(video_path)
        ancho_orig, alto_orig = clip.size
        
        nuevo_alto = alto_orig
        nuevo_ancho = int(alto_orig * 9 / 16)
        
        if nuevo_ancho > ancho_orig:
            nuevo_ancho = ancho_orig
            nuevo_alto = int(ancho_orig * 16 / 9)
        
        x_centro = ancho_orig // 2
        x1 = max(0, x_centro - nuevo_ancho // 2)
        x2 = min(ancho_orig, x1 + nuevo_ancho)
        
        if x2 > ancho_orig:
            x2 = ancho_orig
            x1 = ancho_orig - nuevo_ancho
        if x1 < 0:
            x1 = 0
            x2 = nuevo_ancho
        
        vertical = clip.cropped(x1=x1, y1=0, x2=x2, y2=nuevo_alto)
        final = vertical.resized((ancho, alto))
        final.write_videofile(output_path, codec='libx264', audio_codec='aac', logger=None)
        
        clip.close()
        return output_path
    except Exception as e:
        logger.error(f"Error en fallback: {e}")
        return output_path


# ============================================
# FUNCIÓN PRINCIPAL - ORQUESTADORA
# ============================================
def procesar_video(input_path, config, output_base_path):
    logger.info("=" * 50)
    logger.info("INICIANDO PROCESAMIENTO CON AUDIO")
    logger.info(f"Video: {input_path}")
    logger.info(f"GPU: {HAS_GPU}")
    logger.info("=" * 50)
    
    os.makedirs(output_base_path, exist_ok=True)
    
    nombre_base = obtener_nombre_base(input_path)
    calidad = config.get('calidad_video', ResolucionVertical.DEFAULT)
    
    # Detectar momentos (incluye audio)
    segmentos = detectar_momentos_interesantes(input_path, config)
    
    # SIEMPRE generar el video completo, haya o no segmentos
    nombre_completo = f"{nombre_base}_vertical_{calidad}.mp4"
    ruta_completo = os.path.join(output_base_path, nombre_completo)
    ruta_completo = generar_video_completo(input_path, ruta_completo, config)
    
    if not segmentos:
        logger.warning("No se detectaron segmentos interesantes. Solo se generó el video completo.")
        
        # Obtener duración del video completo
        duracion_completo = obtener_duracion_video(input_path)
        
        return {
            "shorts": [],
            "completo_vertical": {
                "ruta": ruta_completo if os.path.exists(ruta_completo) else None,
                "duracion": duracion_completo
            },
            "segmentos_utilizados": [],
            "cantidad_shorts_generados": 0,
            "calidad_utilizada": calidad,
            "gpu_utilizada": HAS_GPU,
            "nombre_base": nombre_base
        }
    
    # Generar shorts en paralelo (solo si hay segmentos)
    shorts = []
    cantidad = config.get('cantidad_shorts', 3)
    a_procesar = segmentos[:cantidad]
    
    args = []
    for i, (inicio, fin) in enumerate(a_procesar):
        nombre = f"{nombre_base}_short_{i+1}_{calidad}.mp4"
        ruta = os.path.join(output_base_path, nombre)
        args.append((input_path, inicio, fin, ruta, config))
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(multiprocessing.cpu_count(), len(args))) as ex:
        futuros = [ex.submit(lambda a: generar_short(*a), arg) for arg in args]
        for f in concurrent.futures.as_completed(futuros):
            try:
                r = f.result(timeout=DEFAULT_TIMEOUT)
                if r:
                    shorts.append(r)
            except Exception as e:
                logger.error(f"Error en worker: {e}")
    
    # Construir lista de shorts con información de duración
    shorts_con_info = []
    for i, (inicio, fin) in enumerate(a_procesar):
        if i < len(shorts):
            shorts_con_info.append({
                "ruta": shorts[i],
                "duracion": fin - inicio
            })
    
    # Obtener duración del video completo
    duracion_completo = obtener_duracion_video(input_path)
    
    return {
        "shorts": shorts_con_info,
        "completo_vertical": {
            "ruta": ruta_completo if os.path.exists(ruta_completo) else None,
            "duracion": duracion_completo
        },
        "segmentos_utilizados": a_procesar,
        "cantidad_shorts_generados": len(shorts),
        "calidad_utilizada": calidad,
        "gpu_utilizada": HAS_GPU,
        "nombre_base": nombre_base
    }


# ============================================
# EJECUCIÓN PRINCIPAL
# ============================================
if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(json.dumps({"error": "Se requieren 3 argumentos"}))
        sys.exit(1)
    
    input_path = sys.argv[1]   # Ruta del video original
    config_json = sys.argv[2]  # String JSON con configuración
    output_path = sys.argv[3]  # Ruta base para guardar resultados
    
    try:
        # Convertir config de string JSON a diccionario
        config = json.loads(config_json)
        # Validar configuración mínima
        config.setdefault('sensibilidad_cambio_escena', 0.3)
        config.setdefault('umbral_volumen', 0.5)
        config.setdefault('min_duracion_segmento', 10)
        config.setdefault('max_duracion_segmento', 30)
        config.setdefault('priorizar', 'balanceado')
        config.setdefault('cantidad_shorts', 3)
        config.setdefault('calidad_video', ResolucionVertical.DEFAULT)
        config.setdefault('modo_recorte', 'centrado')
        config.setdefault('usar_mediapipe', False)
        
        # Validar combinación de parámetros
        if config['modo_recorte'] == 'seguimiento_persona' and not config['usar_mediapipe']:
            raise ValueError("modo_recorte='seguimiento_persona' requiere usar_mediapipe=True")
        
        # Ejecutar procesamiento
        resultados = procesar_video(input_path, config, output_path)

        # Imprimir resultados en JSON para que .NET los capture
        print(json.dumps(resultados))
        
    except Exception as e:
        logger.error(f"Error fatal: {e}")
        print(json.dumps({"error": str(e)}))
        sys.exit(1)