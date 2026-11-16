#!/usr/bin/env python3
"""Renderiza el proyecto, deja el audio a −14 LUFS y arma la carpeta «listos» para publicar (o programar en el curso CM).

Uso: python3 scripts/render.py proyectos/<video>/edicion "Texto para publicar (3 líneas y 3 hashtags)" [tema]
"""
import datetime, json, platform, re, subprocess, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
proj, texto = Path(sys.argv[1]), sys.argv[2]
tema = re.sub(r"[^a-z0-9]+", "-", (sys.argv[3] if len(sys.argv) > 3 else proj.parent.name).lower()).strip("-")
win = platform.system() == "Windows"
crudo = proj / "render.mp4"
subprocess.run(["npx", "--yes", "hyperframes@0.8.212", "render", str(proj), "-o", str(crudo), "--no-low-memory-mode", "-w", "2"], check=True, shell=win)  # ponytail: 2 workers caben en 8 GB; 2.7x más rápido que el modo seguro
listos = RAIZ / "listos" / f"{datetime.date.today():%Y-%m-%d}-{tema}"; listos.mkdir(parents=True, exist_ok=True)
final = listos / "video.mp4"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(crudo), "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
                "-movflags", "+faststart", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", str(final)], check=True)
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "1.2", "-i", str(final), "-frames:v", "1", "-q:v", "3", str(listos / "portada.jpg")], check=True)
(listos / "texto.txt").write_text(texto.strip() + "\n", encoding="utf-8")
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(final)], capture_output=True, text=True).stdout)
(listos / "publicacion.json").write_text(json.dumps({"video": "video.mp4", "portada": "portada.jpg", "texto": texto.strip(), "duracion_s": round(dur, 1),
                                                     "formato": "9:16", "creado": datetime.datetime.now().isoformat(timespec="minutes")}, ensure_ascii=False, indent=1))
print(listos)
