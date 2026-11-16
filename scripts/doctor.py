#!/usr/bin/env python3
"""Revisa (y con --fix instala) lo que necesita el Estudio de video OptimAI. Mac y Windows.

Uso: python3 scripts/doctor.py [--fix]
Lo que pide contraseña de la computadora NO se corre solo: se imprime el comando para que la alumna lo apruebe.
"""
import os, platform, shutil, subprocess, sys
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
    r = subprocess.run([str(PY), "-c", "import faster_whisper, PIL, cv2, mediapipe"], capture_output=True)
    return r.returncode == 0


COMPAT = ((3, 9), (3, 12))  # el transcriptor y el cambio de fondo (MediaPipe) aún no tienen versión para Python más nuevo


def python_compatible():
    """Un Python 3.9–3.13 ya instalado, o None."""
    if COMPAT[0] <= sys.version_info[:2] <= COMPAT[1]:
        return [sys.executable]
    for v in ("3.12", "3.11", "3.10", "3.9"):
        cmd = ["py", f"-{v}"] if WIN else [f"python{v}"]
        if shutil.which(cmd[0]) and subprocess.run(cmd + ["-c", "import venv"], capture_output=True).returncode == 0:
            return cmd
    return None


def uv():
    """uv descarga Python 3.12 sin contraseña. Se instala solo si hace falta."""
    ruta = shutil.which("uv") or next((str(p) for p in (Path.home() / ".local/bin/uv", Path.home() / ".local/bin/uv.exe",
                                                       Path.home() / ".cargo/bin/uv") if p.exists()), None)
    if ruta:
        return ruta
    print("⏳ Instalando uv (descarga una versión de Python compatible)…")
    if WIN:
        subprocess.run(["powershell", "-ExecutionPolicy", "ByPass", "-c", "irm https://astral.sh/uv/install.ps1 | iex"], check=True)
    else:
        subprocess.run("curl -LsSf https://astral.sh/uv/install.sh | sh", shell=True, check=True)
    return uv()


def crear_venv():
    paquetes = ["faster-whisper==1.1.1", "requests", "pillow", "mediapipe==0.10.14", "opencv-python-headless"]
    if PY.exists() and subprocess.run([str(PY), "-c", f"import sys; sys.exit(not {COMPAT[0]} <= sys.version_info[:2] <= {COMPAT[1]})"]).returncode:
        shutil.rmtree(VENV)  # se hizo con un Python demasiado nuevo
    base = python_compatible()
    if base:
        if not PY.exists():
            subprocess.run(base + ["-m", "venv", str(VENV)], check=True)
        subprocess.run([str(PY), "-m", "pip", "install", "-q", "--upgrade", "pip"], check=True)
        subprocess.run([str(PY), "-m", "pip", "install", "-q"] + paquetes, check=True)
    else:
        u = uv()
        if not PY.exists():
            subprocess.run([u, "venv", "--python", "3.12", str(VENV)], check=True)
        subprocess.run([u, "pip", "install", "--python", str(PY), "-q"] + paquetes, check=True)


CHEQUEOS = [
    ("Python 3.9 o más", lambda: sys.version_info >= (3, 9), None, "Instala Python desde python.org (marca «Add to PATH» en Windows)."),
    ("FFmpeg (cortar y unir video)", lambda: hay("ffmpeg") and hay("ffprobe"), "ffmpeg", None),
    ("Node.js (motor de animación HyperFrames)", lambda: hay("node") and hay("npx"), "node", None),
    ("Google Chrome (render y Google Flow)", chrome, "chrome", None),
    ("Transcriptor de voz, fotos y cambio de fondo", py_ok, "venv", None),
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
    # Guías oficiales para que Claude domine los dos motores de animación (se descargan de su fuente, no las copiamos)
    for nombre, paquete, prueba in [("HyperFrames", "heygen-com/hyperframes", "hyperframes"),
                                    ("Remotion", "remotion-dev/skills", "remotion-best-practices")]:
        if not (RAIZ / ".claude/skills" / prueba).exists() and FIX:
            print(f"⏳ Instalando las guías de {nombre} para Claude…")
            subprocess.run(["npx", "--yes", "skills", "add", paquete, "-a", "claude-code", "-y", "--copy"],
                           cwd=RAIZ, capture_output=True, shell=WIN)
        if (RAIZ / ".claude/skills" / prueba).exists():
            print(f"✅ Guías de {nombre} para Claude")
        else:
            faltan += 1
            print(f"❌ Guías de {nombre}: corre otra vez con --fix y con internet.")
print("\nTodo listo." if not faltan else f"\nFaltan {faltan}. Corre los comandos de arriba y vuelve a revisar.")
sys.exit(1 if faltan else 0)
