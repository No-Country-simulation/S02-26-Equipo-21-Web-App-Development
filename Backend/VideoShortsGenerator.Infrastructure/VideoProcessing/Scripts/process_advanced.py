#!/usr/bin/env python3
import sys
import os
import subprocess
import traceback
import cv2
import numpy as np
import mediapipe as mp

mp_face = mp.solutions.face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.4)
mp_hands = mp.solutions.hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.4)
mp_pose = mp.solutions.pose.Pose(static_image_mode=False, model_complexity=0, min_detection_confidence=0.4)

def sample_center_x(input_path: str, max_samples: int = 30, step_secs: float = 0.5):
    """Muestra frames espaciados en el video y usa MediaPipe para estimar el centro X más relevante."""
    if not os.path.exists(input_path):
        return None
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        return None

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    duration = frames / fps if fps > 0 else 0
    samples = min(int(duration / max(step_secs, 0.1)) + 1, max_samples)

    xs = []
    weights = []

    for i in range(samples):
        t = min(i * step_secs, max(0, duration - 0.001))
        cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
        ret, frame = cap.read()
        if not ret:
            continue
        h, w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # 1) Face
        try:
            res_f = mp_face.process(rgb)
            if res_f and res_f.detections:
                d = res_f.detections[0].location_data.relative_bounding_box
                cx = (d.xmin + d.width/2) * w
                score = float(res_f.detections[0].score[0]) if res_f.detections[0].score else 0.6
                xs.append(cx); weights.append(max(0.2, score))
                continue
        except:
            pass

        # 2) Hands
        try:
            res_h = mp_hands.process(rgb)
            if res_h and res_h.multi_hand_landmarks:
                # usar primer hand landmark promedio x
                lm = res_h.multi_hand_landmarks[0]
                xs_land = [p.x for p in lm.landmark]
                cx = np.mean(xs_land) * w
                xs.append(cx); weights.append(0.5)
                continue
        except:
            pass

        # 3) Pose shoulders
        try:
            res_p = mp_pose.process(rgb)
            if res_p and res_p.pose_landmarks:
                lm = res_p.pose_landmarks.landmark
                left = lm[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER]
                right = lm[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER]
                cx = ((left.x + right.x) / 2) * w
                xs.append(cx); weights.append(0.4)
                continue
        except:
            pass

    cap.release()
    if not xs:
        return None
    return int(np.average(xs, weights=weights))

def ffmpeg_crop_scale(input_path: str, output_path: str, center_x: int = None, target_w: int = 1080, target_h: int = 1920, timeout: int = 300) -> bool:
    # Obtener dimensiones originales
    probe = ["ffprobe","-v","error","-select_streams","v:0","-show_entries","stream=width,height","-of","csv=p=0", input_path]
    try:
        p = subprocess.run(probe, capture_output=True, text=True, timeout=10)
        if p.returncode != 0 or not p.stdout.strip():
            return False
        w_orig, h_orig = map(int, p.stdout.strip().split(","))
    except:
        return False

    new_h = h_orig
    new_w = int(h_orig * 9 / 16)
    if new_w > w_orig:
        new_w = w_orig
        new_h = int(w_orig * 16 / 9)

    if center_x is None:
        x1 = max(0, (w_orig - new_w) // 2)
    else:
        x1 = int(center_x - new_w // 2)
        x1 = max(0, min(x1, w_orig - new_w))

    filter_v = f"crop={new_w}:{new_h}:{x1}:0,scale={target_w}:{target_h}"

    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-vf", filter_v,
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        output_path
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=timeout)
        return r.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 0
    except:
        return False

def process_advanced(input_path: str, output_path: str) -> None:
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input not found: {input_path}")

    # intentar detectar centro con mediapipe usando muestreo ligero
    center_x = sample_center_x(input_path, max_samples=40, step_secs=0.5)
    ok = ffmpeg_crop_scale(input_path, output_path, center_x=center_x)
    if not ok:
        # fallback: centro por defecto
        ok = ffmpeg_crop_scale(input_path, output_path, center_x=None)
    if not ok:
        raise RuntimeError("FFmpeg failed to produce output")

if __name__ == "__main__":
    try:
        if len(sys.argv) < 3:
            print("Error: requiere input_path y output_path", file=sys.stderr)
            sys.exit(1)
        input_path = sys.argv[1]
        output_path = sys.argv[2]
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        process_advanced(input_path, output_path)
        print(f"Success: {output_path}")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)