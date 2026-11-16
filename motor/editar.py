#!/usr/bin/env python3
"""Motor de edición · Estudio de video OptimAI (versión computadora).

crudo.mp4 + marca.json [+ palabras.json] -> final.mp4
1. FFmpeg detecta silencios y los corta.
2. Quita además los tramos que pida la alumna y recorta a una duración máxima.
3. HyperFrames pone marca, subtítulos (4 estilos), zooms, imágenes encima, música y cierre con CTA.

Uso: python3 editar.py crudo.mp4 marca.json salida_dir [palabras.json]
"""
import json, re, shutil, subprocess, sys, html
from pathlib import Path

PAD = 0.12          # aire que se deja antes y después de cada frase
MIN_SIL = 0.35      # silencios más cortos que esto no se cortan
UMBRAL = "-35dB"
CIERRE = 2.5        # segundos del cierre con CTA
HF = "hyperframes@0.8.212"


def run(cmd):
    return subprocess.run(cmd, check=True, capture_output=True, text=True)


def duracion(f):
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f]).stdout)


def tramos_con_voz(f):
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", f, "-af", f"silencedetect=noise={UMBRAL}:d={MIN_SIL}", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    ini = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", err)]
    fin = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    total = duracion(f)
    silencios = list(zip(ini, fin + [total] * (len(ini) - len(fin))))
    tramos, t = [], 0.0
    for s, e in silencios:
        if s > t:
            tramos.append((max(0, t - PAD), min(total, s + PAD)))
        t = e
    if t < total:
        tramos.append((max(0, t - PAD), total))
    return [(a, b) for a, b in tramos if b - a > 0.2]


def restar(tramos, quitar):
    """Quita de los tramos con voz los rangos que pidió la alumna (tiempos del video crudo)."""
    for q0, q1 in sorted(quitar):
        nuevos = []
        for a, b in tramos:
            if q1 <= a or q0 >= b:
                nuevos.append((a, b)); continue
            if q0 > a: nuevos.append((a, q0))
            if q1 < b: nuevos.append((q1, b))
        tramos = nuevos
    return [(a, b) for a, b in tramos if b - a > 0.2]


def limitar(tramos, maximo):
    """Deja solo los primeros `maximo` segundos de video ya cortado."""
    out, acum = [], 0.0
    for a, b in tramos:
        if acum >= maximo: break
        b = min(b, a + maximo - acum); out.append((a, b)); acum += b - a
    return [(a, b) for a, b in out if b - a > 0.05]


def a_cortado(t, tramos):
    """Tiempo del video crudo -> tiempo del video cortado (si cae en un hueco, se pega al tramo siguiente)."""
    base = 0.0
    for a, b in tramos:
        if t < b:
            return base + max(0.0, t - a)
        base += b - a
    return base


def rango(de, a, tramos, tope):
    s, e = a_cortado(de, tramos), min(a_cortado(a, tramos), tope)
    return (s, e) if e - s > 0.15 else None


COLOR = {  # corrección de color simple con ffmpeg
    "natural": "eq=contrast=1.04:saturation=1.08",
    "calido": "eq=contrast=1.05:saturation=1.12,colorbalance=rs=.05:gs=.01:bs=-.05",
    "frio": "eq=contrast=1.05:saturation=1.05,colorbalance=rs=-.04:bs=.05",
    "vivo": "eq=contrast=1.1:saturation=1.3:brightness=.02",
    "suave": "eq=contrast=.95:saturation=.9:brightness=.03",
}


def cortar(f, tramos, out, color=None):
    parts = "".join(f"[0:v]trim={a:.3f}:{b:.3f},setpts=PTS-STARTPTS[v{i}];[0:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS[a{i}];"
                    for i, (a, b) in enumerate(tramos))
    cat = "".join(f"[v{i}][a{i}]" for i in range(len(tramos))) + f"concat=n={len(tramos)}:v=1:a=1[v0][a]"
    cat += f";[v0]{COLOR[color]}[v]" if color in COLOR else ";[v0]null[v]"
    run(["ffmpeg", "-y", "-hide_banner", "-i", f, "-filter_complex", parts + cat, "-map", "[v]", "-map", "[a]",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-r", "30", "-c:a", "aac", "-b:a", "160k", out])


def remapear(palabras, tramos):
    """Pasa los tiempos de Whisper (video crudo) a la línea de tiempo ya cortada."""
    # Whisper se equivoca ~100 ms en los bordes: cada palabra va al tramo con más traslape (o al más cercano).
    bases, base = [], 0.0
    for a, b in tramos:
        bases.append(base); base += b - a
    out = []
    for p in palabras:
        s, e = p["start"], max(p["end"], p["start"] + 0.05)
        i = max(range(len(tramos)), key=lambda k: (min(e, tramos[k][1]) - max(s, tramos[k][0]),
                                                   -min(abs(s - tramos[k][1]), abs(e - tramos[k][0]))))
        a, b = tramos[i]
        s2, e2 = min(max(s, a), b), min(max(e, a), b)
        out.append({"w": p["w"], "start": bases[i] + s2 - a, "end": bases[i] + max(e2, s2 + 0.05) - a})
    return out


def frases(palabras, n=3):
    return [palabras[i:i + n] for i in range(0, len(palabras), n)]


ESTILOS = {  # estilo de subtítulos -> CSS
    "clasico": "font-size:84px;color:#fff;-webkit-text-stroke:10px #000;paint-order:stroke fill",
    "caja": "font-size:70px;color:{texto};background:{primario};padding:14px 30px;border-radius:22px;left:50%;right:auto;"
            "width:max-content;max-width:960px;translate:-50% 0",
    "karaoke": "font-size:84px;color:#fff;-webkit-text-stroke:10px #000;paint-order:stroke fill",
    "minimal": "font-size:56px;color:#fff;font-weight:600;text-shadow:0 3px 14px rgba(0,0,0,.75)",
    "pildora": "font-size:78px;color:#fff;-webkit-text-stroke:8px #000;paint-order:stroke fill",
    "neon": "font-size:80px;color:#fff;text-shadow:0 0 12px {acento},0 0 34px {acento},0 0 70px {acento}",
    "aura": "font-size:78px;color:#fff;font-family:'Playfair Display',serif;font-weight:900;text-transform:uppercase;line-height:1.05;"
            "text-shadow:0 3px 0 #000,0 6px 18px rgba(0,0,0,.8)",
    "gigante": "font-size:170px;color:#fff;-webkit-text-stroke:14px #000;paint-order:stroke fill;text-transform:uppercase",
}
POR_PALABRA = {"karaoke": 2, "pildora": 3, "gigante": 1}  # estilos que iluminan palabra por palabra -> palabras por frase

# Transiciones en cada corte (jump cut) y al entrar cada B-roll. Solo GSAP/CSS: rápidas de renderizar.
TRANSICIONES = {
    "flash": 'tl.fromTo("#fx-flash",{{autoAlpha:.95}},{{autoAlpha:0,immediateRender:false,duration:.16}},{t:.2f});',
    "whip": 'tl.fromTo("#cam",{{x:-260,filter:"blur(18px)"}},{{x:0,filter:"blur(0px)",immediateRender:false,duration:.2,ease:"power3.out"}},{t:.2f});',
    "zoom": 'tl.fromTo("#cam",{{scale:1.28}},{{scale:1,immediateRender:false,duration:.28,ease:"power3.out"}},{t:.2f});',
    "glitch": 'tl.set("#cam",{{x:24,filter:"hue-rotate(90deg) saturate(3) contrast(1.4)"}},{t:.2f}).set("#cam",{{x:-18}},{t1:.2f})'
              '.set("#cam",{{x:0,filter:"none"}},{t2:.2f});',
    "fuga": 'tl.fromTo("#fx-fuga",{{autoAlpha:0}},{{autoAlpha:.85,immediateRender:false,duration:.25}},{t0:.2f}).to("#fx-fuga",{{autoAlpha:0,duration:.45}},{t:.2f});',
}

# Looks de la galería: combinaciones listas. Lo que pida la alumna en opciones.json gana sobre el look.
LOOKS = {
    "creador": {"estilo": "pildora", "posicion": "centro", "transicion": "zoom", "color": "vivo", "zoom_auto": True},
    "gigantes": {"estilo": "gigante", "posicion": "centro", "transicion": "flash", "color": "vivo"},
    "fotos": {"estilo": "caja", "posicion": "abajo", "transicion": "whip", "color": "natural"},
    "pasos": {"estilo": "minimal", "posicion": "arriba", "transicion": "whip", "color": "natural"},
    "cinematico": {"estilo": "minimal", "posicion": "abajo", "transicion": "fuga", "color": "calido", "grano": True},
    "collage": {"estilo": "caja", "posicion": "abajo", "transicion": "glitch", "color": "suave", "marco": "collage"},
    "neon": {"estilo": "neon", "posicion": "centro", "transicion": "glitch", "color": "frio", "grano": True},
    "aura": {"estilo": "aura", "posicion": "arriba", "transicion": "zoom", "color": "calido"},
    "aura-acuarela": {"estilo": "aura", "posicion": "arriba", "transicion": "fuga", "color": "natural", "adornos": True},
    "acuarela": {"estilo": "karaoke", "posicion": "centro", "transicion": "fuga", "color": "calido", "estilo_alterno": "acuarela"},
    "pixel": {"estilo": "karaoke", "posicion": "centro", "transicion": "glitch", "color": "vivo", "estilo_alterno": "pixel"},
}


def ruido_png(ruta, lado=256):
    """Textura de grano (PNG gris con alfa) solo con la librería estándar."""
    import os, struct, zlib
    filas = b"".join(b"\x00" + bytes(v for px in os.urandom(lado) for v in (px, px // 4 + 20)) for _ in range(lado))
    def trozo(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    Path(ruta).write_bytes(b"\x89PNG\r\n\x1a\n" + trozo(b"IHDR", struct.pack(">IIBBBBB", lado, lado, 8, 4, 0, 0, 0))
                          + trozo(b"IDAT", zlib.compress(filas)) + trozo(b"IEND", b""))
POSICION = {"abajo": 1440, "centro": 880, "arriba": 330}

# Estilo alterno del cierre y los textos (sin IA: CSS). Las imágenes del estilo (Flow) entran como B-roll.
ESTILO_ALTERNO = {
    "acuarela": {"fuente": "Caveat Brush", "css": """
#fin{{background:{fondo}}}
#fin::before{{content:"";position:absolute;inset:-10%;background:radial-gradient(circle at 30% 35%,{primario} 0 28%,transparent 46%),
  radial-gradient(circle at 72% 62%,{secundario} 0 24%,transparent 44%),radial-gradient(circle at 45% 80%,{primario}99 0 18%,transparent 40%);
  filter:url(#acuarela) blur(6px);opacity:.85}}
#fin h1,#fin p{{position:relative;color:#2b2118;font-family:'Caveat Brush',cursive}}
#fin h1{{font-size:132px}}
.sub{{font-family:'Caveat Brush',cursive}}""",
                 "svg": '<svg width="0" height="0" style="position:absolute"><filter id="acuarela"><feTurbulence type="fractalNoise" baseFrequency=".012" numOctaves="4" seed="7"/>'
                        '<feDisplacementMap in="SourceGraphic" scale="90"/></filter></svg>'},
    "pixel": {"fuente": "Press Start 2P", "css": """
#fin{{background:{primario};background-image:linear-gradient(45deg,#0001 25%,transparent 25% 75%,#0001 75%),linear-gradient(45deg,#0001 25%,transparent 25% 75%,#0001 75%);
  background-size:48px 48px;background-position:0 0,24px 24px;image-rendering:pixelated}}
#fin h1{{font-family:'Press Start 2P',monospace;font-size:72px;line-height:1.3;text-shadow:8px 8px 0 #0006}}
#fin p{{font-family:'Press Start 2P',monospace;font-size:34px;line-height:1.6}}
.sub{{font-family:'Press Start 2P',monospace;font-size:48px !important;line-height:1.4}}
#chip{{border-radius:0;box-shadow:8px 8px 0 #0006}}""", "svg": ""},
}


def composicion(marca, dur_video, palabras, op=None):
    op = op or {}
    c = marca["colores"]
    total = dur_video + CIERRE
    estilo = op.get("estilo") if op.get("estilo") in ESTILOS else "clasico"
    gs = frases(palabras, POR_PALABRA.get(estilo, 6 if estilo == "aura" else 3))
    top = POSICION.get(op.get("posicion"), 1440)
    if estilo == "gigante":
        top -= 120
    acento = c.get("secundario") or c["primario"]

    def texto(g):
        if estilo == "aura":  # la palabra más larga de la frase va en rojo, como en las portadas de Aura
            clave = max(range(len(g)), key=lambda k: len(g[k]["w"].strip(".,¡!¿?")))
            return " ".join(f'<span class="rojo">{html.escape(p["w"])}</span>' if k == clave else html.escape(p["w"]) for k, p in enumerate(g))
        if estilo not in POR_PALABRA:
            return html.escape(" ".join(p["w"] for p in g))
        return " ".join(f'<span class="k" data-s="{p["start"]:.2f}" data-e="{p["end"]:.2f}">{html.escape(p["w"])}</span>' for p in g)
    subs = "".join(
        f'<div class="sub" data-s="{g[0]["start"]:.2f}" data-e="{min(g[-1]["end"], gs[i + 1][0]["start"]) if i + 1 < len(gs) else g[-1]["end"]:.2f}">'
        f'{texto(g)}</div>'
        for i, g in enumerate(gs))
    def medio(im):
        if im["arch"].lower().endswith((".mp4", ".mov", ".webm", ".m4v")):  # B-roll en video, sin su audio
            return (f'<video class="clip" src="assets/{im["arch"]}" data-start="{im["s"]:.2f}" data-duration="{im["e"] - im["s"]:.2f}" '
                    f'data-volume="0" muted playsinline></video>')
        return f'<img src="assets/{im["arch"]}" alt="" />'
    imgs = "".join(
        f'<div class="ov {im["modo"]}" data-s="{im["s"]:.2f}" data-e="{im["e"]:.2f}">{medio(im)}'
        + (f'<h2>{html.escape(im["texto"])}</h2>' if im.get("texto") else "") + '</div>'
        for im in op.get("imagenes", []))
    css_sub = ESTILOS[estilo].format(texto=c["texto"], primario=c["primario"], acento=acento)
    # Transición en cada corte y al entrar cada B-roll
    trans = TRANSICIONES.get(op.get("transicion"))
    momentos = sorted(set([round(t, 2) for t in op.get("cortes", [])] + [round(im["s"], 2) for im in op.get("imagenes", [])]))
    elegidos, ult = [], -9.0
    for t in momentos:  # una transición cada 2.5 s como mínimo: más seguido marea
        if 0.3 < t < dur_video - .3 and t - ult >= 2.5:
            elegidos.append(t); ult = t
    js_trans = "".join(trans.format(t=t, t0=max(0, t - .25), t1=t + .05, t2=t + .11) for t in elegidos) if trans else ""
    # Palabras gigantes a pantalla completa en las frases fuertes
    textos = "".join(f'<div class="big" data-s="{x["s"]:.2f}" data-e="{x["e"]:.2f}">{html.escape(x["texto"])}</div>' for x in op.get("textos", []))
    # Pasos que van apareciendo en la mitad de abajo
    pasos = op.get("pasos", [])
    panel = ('<div id="pasos">' + "".join(f'<div class="paso" data-s="{p["s"]:.2f}"><b>{i + 1}</b>{html.escape(p["texto"])}</div>'
                                         for i, p in enumerate(pasos)) + '</div>') if pasos else ""
    grano = '<div id="fx-grano"></div><div id="fx-vineta"></div>' if op.get("grano") else ""
    # Adornos: estrellitas doradas que brillan en las orillas (no tapan la cara)
    POS = [(70, 330), (960, 260), (120, 700), (990, 620), (60, 1080), (1000, 1010), (150, 1420), (930, 1380), (520, 200), (880, 1640)]
    estrella = '<svg viewBox="0 0 40 40"><path d="M20 0C22 14 26 18 40 20C26 22 22 26 20 40C18 26 14 22 0 20C14 18 18 14 20 0Z" fill="{c}"/></svg>'
    adornos = "".join(f'<div class="adorno" style="left:{x}px;top:{y}px;width:{44 + (i % 3) * 14}px">{estrella.format(c="#d4a72c" if i % 2 else "#ffffff")}</div>'
                      for i, (x, y) in enumerate(POS)) if op.get("adornos") else ""
    collage = op.get("marco") == "collage"
    js_zoom = "".join(f'tl.to("#cam",{{scale:1.18,duration:.35,ease:"power2.out"}},{a:.2f})'
                      f'.to("#cam",{{scale:1,duration:.35,ease:"power2.inOut"}},{max(a + 0.35, b - 0.35):.2f});'
                      for a, b in op.get("zooms", []))
    alt = ESTILO_ALTERNO.get(op.get("estilo_alterno"))
    css_alt = alt["css"].format(fondo=c.get("fondo", "#fff8f0"), primario=c["primario"], secundario=acento) if alt else ""
    if estilo == "aura" and not alt:
        alt = {"fuente": "Playfair Display:wght@900", "css": "", "svg": ""}
        css_alt = ""
    fuente_alt = (f'<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family={alt["fuente"].replace(" ", "+")}&display=swap" />' if alt else "")
    musica = (f'<audio id="m" class="clip" src="assets/musica.m4a" data-start="0" data-duration="{total:.2f}" data-volume="1"></audio>'
              if op.get("musica") else "")
    logo = marca.get("logo")  # el logo siempre va sobre placa blanca
    chip = ('<div id="chip" class="logo"><img src="assets/logo.png" alt="" /></div>' if logo
            else f'<div id="chip">{html.escape(marca["nombre"])}</div>')
    placa = '<div class="placa"><img src="assets/logo.png" alt="" /></div>' if logo else ""
    return f"""<!doctype html>
<html lang="es"><head><meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family={marca['fuente'].replace(' ', '+')}:wght@600;800&display=swap" />
{fuente_alt}
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body,#root{{width:1080px;height:1920px;overflow:hidden;background:#000}}
#root{{position:relative;font-family:'{marca['fuente']}',sans-serif}}
#v{{position:absolute;inset:0;width:1080px;height:1920px;object-fit:cover}}
#chip{{position:absolute;left:60px;top:90px;padding:18px 34px;border-radius:999px;background:{c['primario']};color:{c['texto']};font-weight:800;font-size:40px}}
#cam{{position:absolute;inset:0;overflow:hidden}}
.sub{{position:absolute;left:60px;right:60px;top:{top}px;text-align:center;font-weight:800;line-height:1.1;opacity:0;{css_sub}}}
.sub .k{{-webkit-text-stroke:10px #000;paint-order:stroke fill}}
.ov{{position:absolute;opacity:0}}
.ov.completa{{inset:0}}
.ov.completa img,.ov.completa video{{width:1080px;height:1920px;object-fit:cover;display:block}}
.ov h2{{position:absolute;left:70px;right:70px;top:260px;text-align:center;font-size:96px;font-weight:800;line-height:1.05;color:{c['texto']};text-shadow:0 6px 24px rgba(0,0,0,.55)}}
.ov.recuadro h2{{top:auto;bottom:-150px;font-size:58px;color:#fff}}
.ov.recuadro{{left:190px;top:820px;width:700px;height:560px;background:#fff;padding:18px;border-radius:36px;box-shadow:0 30px 80px rgba(0,0,0,.45)}}
.ov.recuadro img,.ov.recuadro video{{width:100%;height:100%;object-fit:cover;border-radius:22px;display:block}}
#fin{{position:absolute;inset:0;background:{c['primario']};color:{c['texto']};display:flex;flex-direction:column;align-items:center;justify-content:center;gap:40px;opacity:0;text-align:center;padding:0 80px}}
#fin h1{{font-size:110px;font-weight:800;line-height:1}}
#fin p{{font-size:58px;font-weight:600}}
#chip.logo,.placa{{background:#fff;padding:14px 26px;border-radius:24px}}
#chip.logo img{{height:64px;display:block}}
.placa img{{height:150px;display:block}}
.placa{{position:relative}}
.k{{padding:0 12px;border-radius:18px}}
.sub .rojo{{color:#e11d2e}}
.big{{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;text-align:center;padding:0 60px;opacity:0;
  font-size:190px;font-weight:800;line-height:.95;color:#fff;text-transform:uppercase;background:{c['primario']}e6}}
#pasos{{position:absolute;left:50px;right:50px;bottom:170px;display:flex;flex-direction:column;gap:22px}}
.paso{{display:flex;align-items:center;gap:26px;background:#fffffff0;color:#1c1c1c;font-size:50px;font-weight:800;padding:24px 30px;border-radius:28px;
  opacity:0;box-shadow:0 14px 40px rgba(0,0,0,.35)}}
.paso b{{flex:none;width:76px;height:76px;border-radius:50%;background:{c['primario']};color:{c['texto']};display:flex;align-items:center;justify-content:center}}
.adorno{{position:absolute;filter:drop-shadow(0 2px 6px #0004);pointer-events:none}}
#fx-flash{{position:absolute;inset:0;background:#fff;opacity:0;pointer-events:none}}
#fx-fuga{{position:absolute;inset:-20%;opacity:0;mix-blend-mode:screen;pointer-events:none;
  background:radial-gradient(circle at 15% 20%,#ff9a3c 0 15%,transparent 45%),radial-gradient(circle at 90% 70%,#ff4f6d 0 12%,transparent 40%)}}
#fx-grano{{position:absolute;inset:-64px;background:url(assets/grano.png);opacity:.16;mix-blend-mode:overlay;pointer-events:none}}
#fx-vineta{{position:absolute;inset:0;background:radial-gradient(ellipse at center,transparent 55%,rgba(0,0,0,.55));pointer-events:none}}
{'''#root{background:#efe6d6;background-image:radial-gradient(#0002 2px,transparent 2.5px);background-size:22px 22px}
#cam{inset:150px 70px 330px;border:18px solid #fff;box-shadow:0 30px 70px rgba(0,0,0,.4);rotate:-1.5deg}
#cam #v{width:100%;height:100%}''' if collage else ''}
{('.sub{color:'+op['color_sub']+' !important;text-shadow:0 0 3px #fff,0 0 10px #fff,0 0 22px #fffc !important}') if op.get('color_sub') else ''}
{'#fin{background:url(assets/cierre.jpg) center/cover !important;justify-content:flex-start !important;padding-top:300px !important}#fin h1,#fin p{color:'+c['primario']+' !important;text-shadow:0 0 14px #fff,0 0 4px #fff}' if op.get('fondo_cierre') else ''}
{css_alt}
</style></head><body>
{alt["svg"] if alt else ""}
<div id="root" data-composition-id="main" data-start="0" data-duration="{total:.2f}" data-width="1080" data-height="1920">
<div id="cam"><video id="v" class="clip" src="assets/cortado.mp4" data-start="0" data-duration="{dur_video:.2f}" data-volume="1" data-has-audio="true"></video></div>
{musica}
{imgs}
{grano}
{adornos}
<div id="fx-fuga"></div>
{panel}
{chip}
{subs}
{textos}
<div id="fx-flash"></div>
<div id="fin">{placa}<h1>{html.escape(marca['nombre'])}</h1><p>{html.escape(marca['cta'])}</p></div>
</div>
<script>
const tl = gsap.timeline({{paused:true}});
tl.fromTo("#chip",{{autoAlpha:0,y:-30}},{{autoAlpha:1,y:0,duration:.5,ease:"power3.out"}},.2);
document.querySelectorAll(".sub").forEach(el=>{{
  const s=+el.dataset.s, e=+el.dataset.e;
  tl.fromTo(el,{{autoAlpha:0,scale:.85}},{{autoAlpha:1,scale:1,duration:.12}},s).set(el,{{autoAlpha:0}},e);
}});
document.querySelectorAll(".k").forEach(el=>{{ tl.set(el,{'{backgroundColor:"'+acento+'",color:"#111"}' if estilo == "pildora" else '{color:"'+acento+'"}'},+el.dataset.s);{' tl.set(el,{backgroundColor:"transparent",color:"#fff"},+el.dataset.e);' if estilo == "pildora" else ''} }});
document.querySelectorAll(".big").forEach(el=>{{
  const s=+el.dataset.s, e=+el.dataset.e;
  tl.fromTo(el,{{autoAlpha:0,scale:1.6}},{{autoAlpha:1,scale:1,duration:.18,ease:"power4.out"}},s).to(el,{{autoAlpha:0,duration:.12}},e-.12);
}});
document.querySelectorAll(".paso").forEach(el=>{{
  tl.fromTo(el,{{autoAlpha:0,x:-120}},{{autoAlpha:1,x:0,duration:.35,ease:"back.out(1.7)"}},+el.dataset.s);
}});
document.querySelectorAll(".adorno").forEach((el,i)=>{{
  tl.fromTo(el,{{scale:.55,rotate:0,autoAlpha:.5}},{{scale:1.1,rotate:45,autoAlpha:1,duration:.9+(i%3)*.25,ease:"sine.inOut",yoyo:true,repeat:Math.floor({total:.2f}/(.9+(i%3)*.25))}},(i*.37)%1.5);
}});
if(document.querySelector("#fx-grano")) tl.to("#fx-grano",{{backgroundPosition:"{int(total * 12 * 97)}px {int(total * 12 * 61)}px",duration:{total:.2f},ease:"steps({int(total * 12)})"}},0);
{'tl.to("#cam",{rotate:0.5,duration:.25,ease:"steps(1)",yoyo:true,repeat:'+str(int(total * 4))+'},0);' if collage else ''}
{js_trans}
document.querySelectorAll(".ov").forEach(el=>{{
  const s=+el.dataset.s, e=+el.dataset.e;
  tl.fromTo(el,{{autoAlpha:0,scale:.92}},{{autoAlpha:1,scale:1,duration:.3,ease:"power3.out"}},s).to(el,{{autoAlpha:0,duration:.2}},e-.2);
}});
{js_zoom}
tl.to("#chip",{{autoAlpha:0,duration:.2}},{dur_video - 0.2:.2f})
  .fromTo("#fin",{{autoAlpha:0}},{{autoAlpha:1,duration:.35}},{dur_video - 0.15:.2f})
  .fromTo("#fin h1",{{y:60,scale:.9}},{{y:0,scale:1,duration:.6,ease:"back.out(1.6)"}},{dur_video:.2f})
  .fromTo("#fin p",{{autoAlpha:0,y:30}},{{autoAlpha:1,y:0,duration:.4}},{dur_video + 0.4:.2f})
  .to({{}},{{duration:.01}},{total - 0.01:.2f});
window.__timelines = window.__timelines || {{}};
window.__timelines["main"] = tl;
</script></body></html>"""


def preparar(crudo, marca, salida, palabras, op=None):
    """Deja en salida/ el proyecto HyperFrames listo para renderizar.

    op (todo opcional, tiempos en segundos del video CRUDO):
      quitar=[(de,a)], duracion=segundos del video final con cierre, zooms=[(de,a)],
      imagenes=[{archivo (foto o clip de video = B-roll),de,a,modo:completa|recuadro,texto opcional}],
      musica=ruta, estilo, posicion, color: natural|calido|frio|vivo|suave, estilo_alterno: acuarela|pixel,
      look (ver LOOKS), transicion: flash|whip|zoom|glitch|fuga, grano, marco: collage, zoom_auto,
      textos=[{de,a,texto}] palabras gigantes, pasos=[{de,texto}]
    """
    op = {**LOOKS.get((op or {}).get("look"), {}), **(op or {})}
    out = Path(salida); (out / "assets").mkdir(parents=True, exist_ok=True)
    if marca.get("logo"):
        shutil.copy(marca["logo"], out / "assets" / "logo.png")
    tramos = restar(tramos_con_voz(crudo), op.get("quitar", []))
    if not tramos:
        raise ValueError("Después de quitar esas partes no queda video.")
    if op.get("duracion"):
        tramos = limitar(tramos, max(3.0, float(op["duracion"]) - CIERRE))
    cortar(crudo, tramos, str(out / "assets" / "cortado.mp4"), op.get("color"))
    dur = duracion(str(out / "assets" / "cortado.mp4"))
    fin_voz = tramos[-1][1]
    palabras = [p for p in palabras if p["start"] < fin_voz and not any(q0 <= p["start"] and p["end"] <= q1 for q0, q1 in op.get("quitar", []))]
    comp = {k: op.get(k) for k in ("estilo", "posicion", "estilo_alterno", "transicion", "grano", "marco", "adornos", "color_sub", "fondo_cierre")}
    comp["musica"] = bool(op.get("musica"))
    acum, comp["cortes"] = 0.0, []
    for a, b in tramos[:-1]:  # dónde cae cada corte en el video ya cortado
        acum += b - a
        comp["cortes"].append(acum)
    zooms = op.get("zooms") or ([list(t) for t in tramos[1::2]] if op.get("zoom_auto") else [])
    comp["zooms"] = [r for r in (rango(a, b, tramos, dur) for a, b in zooms) if r]
    comp["textos"] = [{"s": r[0], "e": r[1], "texto": x["texto"]} for x in op.get("textos", []) if (r := rango(x["de"], x["a"], tramos, dur))]
    comp["pasos"] = [{"s": r[0], "texto": x["texto"]} for x in op.get("pasos", []) if (r := rango(x["de"], x["de"] + .5, tramos, dur))]
    if op.get("grano"):
        ruido_png(out / "assets" / "grano.png")
    if op.get("fondo_cierre"):
        shutil.copy(op["fondo_cierre"], out / "assets" / "cierre.jpg")
    comp["imagenes"] = []
    for i, im in enumerate(op.get("imagenes", [])):
        r = rango(im["de"], im["a"], tramos, dur)
        if r:
            arch = f"img{i}{Path(im['archivo']).suffix or '.jpg'}"
            shutil.copy(im["archivo"], out / "assets" / arch)
            comp["imagenes"].append({"arch": arch, "s": r[0], "e": r[1], "texto": im.get("texto"),
                                     "modo": im.get("modo") if im.get("modo") in ("completa", "recuadro") else "recuadro"})
    if op.get("musica"):
        total = dur + CIERRE
        # ponytail: volumen fijo bajo la voz; ducking con sidechaincompress si se oye tapada
        run(["ffmpeg", "-y", "-hide_banner", "-stream_loop", "-1", "-i", op["musica"], "-t", f"{total:.2f}", "-vn",
             "-af", f"volume={op.get('volumen_musica', 0.14)},afade=t=in:d=0.6,afade=t=out:st={max(0, total - 1.5):.2f}:d=1.5",
             "-c:a", "aac", "-b:a", "160k", str(out / "assets" / "musica.m4a")])
    (out / "index.html").write_text(composicion(marca, dur, remapear(palabras, tramos) if palabras else [], comp))
    (out / "tramos.json").write_text(json.dumps(tramos))
    return {"crudo_s": round(duracion(crudo), 2), "final_s": round(dur + CIERRE, 2), "tramos": len(tramos),
            "subtitulos": bool(palabras), "zooms": len(comp["zooms"]), "imagenes": len(comp["imagenes"]),
            "musica": bool(op.get("musica"))}


def main():
    """Uso: editar.py crudo.mp4 marca.json salida_dir [palabras.json] [opciones.json]"""
    crudo, marca_f, salida = sys.argv[1:4]
    palabras = json.loads(Path(sys.argv[4]).read_text()) if len(sys.argv) > 4 and sys.argv[4] != "-" else []
    op = json.loads(Path(sys.argv[5]).read_text()) if len(sys.argv) > 5 else {}
    print(json.dumps(preparar(crudo, json.loads(Path(marca_f).read_text()), salida, palabras, op), ensure_ascii=False))


if __name__ == "__main__":
    main()
