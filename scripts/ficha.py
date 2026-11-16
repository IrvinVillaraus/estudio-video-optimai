#!/usr/bin/env python3
"""Ficha de marca OptimAI: revisar, pasarla al motor y sincronizarla con el conector del celular.

Uso:
  python3 scripts/ficha.py revisar  marcas/<negocio>/ficha.json      → dice qué falta (POR COMPLETAR o vacío)
  python3 scripts/ficha.py motor    marcas/<negocio>/ficha.json      → escribe marca.json para motor/editar.py
  python3 scripts/ficha.py conector marcas/<negocio>/ficha.json      → la sube al conector (usa OPTIMAI_CLAVE de .env)
"""
import json, os, re, sys, urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
URL = "https://video.optimaiautomation.tech/mcp"
HEX = re.compile(r"^#[0-9a-fA-F]{6}$")


def env(k):
    f = RAIZ / ".env"
    if f.exists():
        for l in f.read_text().splitlines():
            if l.startswith(k + "="):
                return l.split("=", 1)[1].strip()
    return os.environ.get(k, "")


def faltantes(d, ruta=""):
    out = []
    for k, v in d.items():
        if k.startswith("_"): continue
        r = f"{ruta}.{k}" if ruta else k
        if isinstance(v, dict): out += faltantes(v, r)
        elif v in ("", None, [], "POR COMPLETAR") or (isinstance(v, str) and "|" in v): out.append(r)
    return out


def motor(f, ficha):
    v, c = ficha["visual"], ficha["visual"]["colores"]
    logo = (f.parent / v["logo"]) if v.get("logo") else None
    m = {"nombre": ficha["negocio"]["nombre"], "fuente": v["fuentes"].get("titulos") or "Poppins",
         "cta": ficha["cta"]["texto"] + (f' · {ficha["cta"]["whatsapp"]}' if ficha["cta"].get("whatsapp") not in ("", "POR COMPLETAR") else ""),
         "colores": {k: c[k] for k in ("primario", "secundario", "texto") if HEX.match(c.get(k, ""))}}
    if logo and logo.exists(): m["logo"] = str(logo)
    salida = f.parent / "marca.json"; salida.write_text(json.dumps(m, ensure_ascii=False, indent=1)); return salida


def conector(ficha):
    clave = env("OPTIMAI_CLAVE")
    if not clave: sys.exit("Falta OPTIMAI_CLAVE en .env (viene en el correo de bienvenida).")
    c = ficha["visual"]["colores"]
    args = {"nombre": ficha["negocio"]["nombre"], "fuente": ficha["visual"]["fuentes"].get("titulos") or "Poppins",
            "cta": ficha["cta"]["texto"], "ficha": ficha, **{k: c[k] for k in ("primario", "secundario", "texto") if HEX.match(c.get(k, ""))}}
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "mi_marca", "arguments": args}}).encode()
    req = urllib.request.Request(URL, body, {"Content-Type": "application/json", "X-Clave": clave})
    print(json.loads(urllib.request.urlopen(req, timeout=30).read())["result"]["content"][0]["text"])


accion, f = sys.argv[1], Path(sys.argv[2]); ficha = json.loads(f.read_text())
if accion == "revisar":
    x = faltantes(ficha); print("Completa:" if x else "Ficha completa."); [print(" -", r) for r in x]
elif accion == "motor": print(motor(f, ficha))
elif accion == "conector": conector(ficha)
else: sys.exit(__doc__)
