#!/usr/bin/env python3
"""Lee una referencia visual (foto, captura o video) y saca lo que Claude necesita para copiar el ESTILO, no el contenido.

Uso: .venv/bin/python scripts/referencia.py <foto|video> <carpeta_salida>
Deja: paleta.json (5 colores hex de más a menos usado), cuadros.jpg (hoja de 6 cuadros si es video) y ritmo.json (cortes por minuto).
Claude mira cuadros.jpg y decide: estilo de subtítulos, posición, color, ritmo de zooms y si usa un estilo alterno.
"""
import json, re, subprocess, sys
from pathlib import Path
from PIL import Image

src, out = Path(sys.argv[1]), Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
es_video = src.suffix.lower() in (".mp4", ".mov", ".m4v", ".webm")
foto = out / "cuadros.jpg"
if es_video:
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(src)], capture_output=True, text=True).stdout)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-vf", f"fps=6/{max(dur,1):.2f},scale=360:-2,tile=3x2", "-frames:v", "1", str(foto)], check=True)
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(src), "-vf", "select='gt(scene,0.35)',showinfo", "-f", "null", "-"], capture_output=True, text=True).stderr
    cortes = len(re.findall(r"pts_time:", err))
    (out / "ritmo.json").write_text(json.dumps({"duracion_s": round(dur, 1), "cortes": cortes, "cortes_por_minuto": round(cortes / dur * 60, 1)}))
else:
    Image.open(src).convert("RGB").save(foto, quality=88)
im = Image.open(foto).convert("RGB").resize((160, 160)).quantize(colors=5, method=Image.Quantize.MEDIANCUT)
pal, cuentas = im.getpalette(), sorted(im.getcolors(), reverse=True)
colores = ["#%02x%02x%02x" % tuple(pal[i * 3:i * 3 + 3]) for _, i in cuentas]
(out / "paleta.json").write_text(json.dumps(colores))
print(json.dumps({"paleta": colores, "cuadros": str(foto), "ritmo": json.loads((out / "ritmo.json").read_text()) if es_video else None}, ensure_ascii=False))
