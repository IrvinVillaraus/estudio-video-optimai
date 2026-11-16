#!/usr/bin/env python3
"""Transcribe palabra por palabra (español) y guarda <video>.palabras.json. Úsalo con el python de .venv.

Uso: .venv/bin/python scripts/transcribir.py video.mp4 [modelo: small|base|medium]
"""
import json, sys
from pathlib import Path
from faster_whisper import WhisperModel

video = Path(sys.argv[1]); modelo = sys.argv[2] if len(sys.argv) > 2 else "small"
salida = Path(str(video) + ".palabras.json")
if salida.exists():
    print(salida); sys.exit(0)
segs, _ = WhisperModel(modelo, device="cpu", compute_type="int8").transcribe(str(video), language="es", word_timestamps=True, vad_filter=True)
palabras = [{"w": w.word.strip(), "start": round(w.start, 3), "end": round(w.end, 3)} for s in segs for w in (s.words or []) if w.word.strip()]
salida.write_text(json.dumps(palabras, ensure_ascii=False))
print(salida)
