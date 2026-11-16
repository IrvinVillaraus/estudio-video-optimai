#!/usr/bin/env python3
"""Baja a la compu el video (o fotos) que la alumna subió desde su celular con el link del conector.

Uso: python3 scripts/traer.py <subida_id o link de subida> <carpeta_destino>
Necesita OPTIMAI_CLAVE en .env.
"""
import json, re, sys, urllib.request
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from ficha import env  # noqa: E402

BASE = "https://video.optimaiautomation.tech"
sid = re.sub(r".*/subir/", "", sys.argv[1]).strip("/"); dest = Path(sys.argv[2]); dest.mkdir(parents=True, exist_ok=True)
clave = env("OPTIMAI_CLAVE") or sys.exit("Falta OPTIMAI_CLAVE en .env (viene en el correo de bienvenida).")
h = {"X-Clave": clave}
lista = json.loads(urllib.request.urlopen(urllib.request.Request(f"{BASE}/descargar/{sid}", headers=h), timeout=30).read())
for i, a in enumerate(lista["archivos"], 1):
    destino = dest / a["nombre"]
    with urllib.request.urlopen(urllib.request.Request(f"{BASE}/descargar/{sid}/{i}", headers=h), timeout=600) as r, open(destino, "wb") as f:
        while trozo := r.read(1 << 20): f.write(trozo)
    print(destino)
