#!/usr/bin/env python3
"""Cambia el fondo de un video donde la alumna habla a cámara (sin pantalla verde).

Uso: PY scripts/fondo.py <video> <fondo.jpg|png> <salida.mp4> [--movimiento]
- El fondo puede ser una imagen de Flow (acuarela, su local ilustrado, etc.).
- --movimiento: acercamiento lento sobre el fondo, para que no se vea estático.
El resultado se usa como «crudo» en editar.py, igual que cualquier otro video.
"""
import subprocess, sys
import cv2, mediapipe as mp, numpy as np

video, fondo_f, salida = sys.argv[1:4]
mov = "--movimiento" in sys.argv
# ffmpeg lee cualquier formato (los videos de Instagram o del celular a veces no los abre OpenCV)
info = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate:format=duration",
                       "-of", "default=nw=1:nk=1", video], capture_output=True, text=True).stdout.split()
w, h = int(info[0]), int(info[1]); a_, b_ = info[2].split("/"); fps = float(a_) / float(b_ or 1)
n = int(float(info[3]) * fps) or 1
lector = subprocess.Popen(["ffmpeg", "-v", "error", "-i", video, "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)


def cubrir(img, ww, hh):  # recorta y escala la imagen para llenar el cuadro sin deformarla
    ih, iw = img.shape[:2]
    s = max(ww / iw, hh / ih)
    img = cv2.resize(img, (int(iw * s + .5), int(ih * s + .5)))
    y, x = (img.shape[0] - hh) // 2, (img.shape[1] - ww) // 2
    return img[y:y + hh, x:x + ww]


base = cubrir(cv2.imread(fondo_f), int(w * 1.12), int(h * 1.12)) if mov else cubrir(cv2.imread(fondo_f), w, h)
ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{w}x{h}", "-r", str(fps), "-i", "-",
                       "-i", video, "-map", "0:v", "-map", "1:a?", "-c:v", "libx264", "-crf", "18", "-preset", "veryfast",
                       "-pix_fmt", "yuv420p", "-c:a", "copy", "-shortest", salida], stdin=subprocess.PIPE)
prev = None
with mp.solutions.selfie_segmentation.SelfieSegmentation(model_selection=0) as seg:
    i = 0
    while True:
        raw = lector.stdout.read(w * h * 3)
        if len(raw) < w * h * 3:
            break
        fr = np.frombuffer(raw, np.uint8).reshape(h, w, 3)
        m = seg.process(cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)).segmentation_mask
        prev = m if prev is None else 0.6 * m + 0.4 * prev   # ponytail: suavizado simple entre cuadros; si parpadea el borde, sube el 0.4
        a = cv2.GaussianBlur(np.clip((prev - 0.35) / 0.3, 0, 1), (0, 0), 3)[..., None]
        if mov:  # acercamiento lento: del 112 % al 100 % recortando el centro
            t = i / max(1, n - 1); s = 1 + 0.12 * (1 - t)
            bw, bh = int(w * s), int(h * s)
            b = cv2.resize(base, (bw, bh))[(bh - h) // 2:(bh - h) // 2 + h, (bw - w) // 2:(bw - w) // 2 + w]
        else:
            b = base
        ff.stdin.write((fr * a + b * (1 - a)).astype(np.uint8).tobytes())
        i += 1
ff.stdin.close(); ff.wait()
print("listo", salida, i, "cuadros")
