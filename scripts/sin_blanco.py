#!/usr/bin/env python3
"""Vuelve transparente el papel blanco de las acuarelas sueltas (elementos de Flow). Uso: PY scripts/sin_blanco.py <carpeta>
Guarda <nombre>.png junto a cada .jpg. Los fondos (los que se llaman fondo-*) no se tocan."""
import glob, os, sys
import numpy as np
from PIL import Image
for f in glob.glob(os.path.join(sys.argv[1], "*.jp*g")):
    if os.path.basename(f).startswith("fondo"):
        continue
    a = np.asarray(Image.open(f).convert("RGB")).astype(np.float32)
    al = np.clip((255 - a.min(axis=2) - 8) * 2.2, 0, 255) / 255.0
    c = np.where(al[..., None] > 0.02, (a - 255 * (1 - al[..., None])) / np.maximum(al[..., None], 0.02), 255)
    Image.fromarray(np.dstack([np.clip(c, 0, 255), al * 255]).astype(np.uint8)).save(os.path.splitext(f)[0] + ".png")
    print("listo", os.path.splitext(f)[0] + ".png")
