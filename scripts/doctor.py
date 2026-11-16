#!/usr/bin/env python3
"""Revisa (y con --fix instala) lo que necesita el Estudio de video OptimAI. Mac y Windows.

Uso: python3 scripts/doctor.py [--fix]
Lo que pide contraseña de la computadora NO se corre solo: se imprime el comando para que la alumna lo apruebe.
"""
import os, platform, shutil, subprocess, sys, venv
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
WIN = platform.system() == "Windows"
VENV = RAIZ / ".venv"
PY = VENV / ("Scripts/python.exe" if WIN else "bin/python")
FIX = "--fix" in sys.argv

INSTALAR = {  # comando por sistema; winget no pide contraseña, brew solo a veces
    "ffmpeg": ("winget install -e --id Gyan.FFmpeg", "brew install ffmpeg"),
    "node": ("winget install -e --id OpenJS.NodeJS.LTS", "brew install node"),
    "chrome": ("winget install -e --id Google.Chrome", "brew install --cask google-chrome"),
}


def hay(cmd):
    return shutil.which(cmd) is not None


def chrome():
    if WIN:
        rutas = [os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
                 os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe")]
    else:
        rutas = ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"]
    return any(Path(r).exists() for r in rutas) or hay("chromium") or hay("google-chrome")


def py_ok():
    if not PY.exists():
        return False
    r = subprocess.run([str(PY), "-c", "import faster_whisper, PIL"], capture_output=True)
    return r.returncode == 0


def crear_venv():
    if not PY.exists():
        venv.create(VENV, with_pip=True)
    subprocess.run([str(PY), "-m", "pip", "install", "-q", "--upgrade", "pip"], check=True)
    subprocess.run([str(PY), "-m", "pip", "install", "-q", "faster-whisper==1.1.1", "requests", "pillow"], check=True)


CHEQUEOS = [
    ("Python 3.9 o más", lambda: sys.version_info >= (3, 9), None, "Instala Python desde python.org (marca «Add to PATH» en Windows)."),
    ("FFmpeg (cortar y unir video)", lambda: hay("ffmpeg") and hay("ffprobe"), "ffmpeg", None),
    ("Node.js (motor de animación HyperFrames)", lambda: hay("node") and hay("npx"), "node", None),
    ("Google Chrome (render y Google Flow)", chrome, "chrome", None),
    ("Transcriptor de voz (faster-whisper) y fotos (Pillow)", py_ok, "venv", None),
]

faltan = 0
for nombre, ok, clave, ayuda in CHEQUEOS:
    if ok():
        print(f"✅ {nombre}"); continue
    if FIX and clave == "venv":
        print(f"⏳ Instalando {nombre}…"); crear_venv()
        if ok():
            print(f"✅ {nombre}"); continue
    faltan += 1
    cmd = INSTALAR.get(clave, (None, None))[0 if WIN else 1] if clave in INSTALAR else None
    print(f"❌ {nombre}" + (f"\n   Comando: {cmd}" if cmd else "") + (f"\n   {ayuda}" if ayuda else ""))
    if not WIN and cmd and cmd.startswith("brew") and not hay("brew"):
        print('   Primero Homebrew: /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"')

if not faltan:
    r = subprocess.run(["npx", "--yes", "hyperframes@0.8.212", "--version"], capture_output=True, text=True, shell=WIN)
    print("✅ HyperFrames " + r.stdout.strip() if r.returncode == 0 else "❌ HyperFrames no responde: corre otra vez con internet.")
print("\nTodo listo." if not faltan else f"\nFaltan {faltan}. Corre los comandos de arriba y vuelve a revisar.")
sys.exit(1 if faltan else 0)
