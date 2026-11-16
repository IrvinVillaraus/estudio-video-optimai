#!/usr/bin/env python3
"""Video de puro motion graphics (sin grabación): escenas de texto + fotos opcionales, con la marca de la alumna.

escenas = [{"titulo": "...", "texto": "...", "foto": "/ruta/opcional.jpg"}, ...]
Uso: python3 crear.py escenas.json marca.json salida_dir
"""
import html, json, shutil, sys
from pathlib import Path

CIERRE = 3.0
TRANS = 0.45   # traslape entre escenas


def dur_escena(e):
    palabras = len((e.get("titulo", "") + " " + e.get("texto", "")).split())
    return min(5.5, max(2.6, 1.2 + 0.32 * palabras))


def composicion(marca, escenas):
    c = marca["colores"]
    prim, txt = c["primario"], c.get("texto", "#ffffff")
    acento = c.get("secundario", "#ffffff")
    logo = marca.get("logo")
    t, bloques, anim = 0.4, [], []
    for i, e in enumerate(escenas):
        d = dur_escena(e)
        foto = f'<div class="foto"><img src="assets/foto{i}.jpg" alt="" /></div>' if e.get("foto") else ""
        bloques.append(f'<div class="esc{" con-foto" if foto else ""}" id="e{i}">{foto}'
                       f'<div class="bar"></div><h1>{html.escape(e.get("titulo", ""))}</h1>'
                       f'<p>{html.escape(e.get("texto", ""))}</p></div>')
        s = f"#e{i}"
        anim.append(f'tl.fromTo("{s}",{{autoAlpha:0,y:80}},{{autoAlpha:1,y:0,duration:.5,ease:"power3.out"}},{t:.2f})')
        anim.append(f'.fromTo("{s} .bar",{{scaleX:0}},{{scaleX:1,duration:.5,ease:"power2.out"}},{t + .15:.2f})')
        anim.append(f'.fromTo("{s} h1",{{clipPath:"inset(0 0 100% 0)",y:40}},{{clipPath:"inset(0 0 0% 0)",y:0,duration:.6,ease:"power3.out"}},{t + .2:.2f})')
        anim.append(f'.fromTo("{s} p",{{autoAlpha:0,y:30}},{{autoAlpha:1,y:0,duration:.45}},{t + .55:.2f})')
        if foto:
            anim.append(f'.fromTo("{s} .foto img",{{scale:1.12}},{{scale:1,duration:{d + .5:.2f},ease:"none"}},{t:.2f})')
            anim.append(f'.fromTo("{s} .foto",{{clipPath:"inset(0 0 100% 0 round 40px)"}},{{clipPath:"inset(0 0 0% 0 round 40px)",duration:.7,ease:"power3.inOut"}},{t:.2f})')
        anim.append(f'.to("{s}",{{autoAlpha:0,y:-90,duration:.45,ease:"power2.in"}},{t + d - TRANS:.2f});')
        t += d - TRANS + .1
    fin = t
    total = fin + CIERRE
    chip = ('<div id="chip" class="logo"><img src="assets/logo.png" alt="" /></div>' if logo
            else f'<div id="chip">{html.escape(marca["nombre"])}</div>')
    placa = '<div class="placa"><img src="assets/logo.png" alt="" /></div>' if logo else ""
    return f"""<!doctype html>
<html lang="es"><head><meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family={marca['fuente'].replace(' ', '+')}:wght@500;800&display=swap" />
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body,#root{{width:1080px;height:1920px;overflow:hidden;background:{prim}}}
#root{{position:relative;font-family:'{marca['fuente']}',sans-serif;color:{txt}}}
.bola{{position:absolute;border-radius:50%;background:{acento};opacity:.12}}
#b1{{width:900px;height:900px;left:-300px;top:-250px}}
#b2{{width:700px;height:700px;right:-260px;bottom:-200px;background:#000;opacity:.14}}
#chip{{position:absolute;left:80px;top:100px;padding:18px 34px;border-radius:999px;background:{txt};color:{prim};font-weight:800;font-size:40px}}
#chip.logo,.placa{{background:#fff;padding:14px 26px;border-radius:24px}}
#chip.logo img{{height:64px;display:block}}
.placa img{{height:170px;display:block}}
.esc{{position:absolute;left:90px;right:90px;top:0;bottom:0;display:flex;flex-direction:column;justify-content:center;gap:36px;opacity:0}}
.esc.con-foto{{justify-content:flex-end;padding-bottom:300px}}
.foto{{width:100%;height:860px;border-radius:40px;overflow:hidden}}
.foto img{{width:100%;height:100%;object-fit:cover;display:block}}
.bar{{width:180px;height:16px;border-radius:8px;background:{acento};transform-origin:left center}}
.esc h1{{font-size:112px;font-weight:800;line-height:1.02;letter-spacing:-2px}}
.esc.con-foto h1{{font-size:88px}}
.esc p{{font-size:56px;font-weight:500;line-height:1.25;opacity:.92}}
#fin{{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:44px;text-align:center;padding:0 90px;opacity:0}}
#fin h1{{font-size:110px;font-weight:800;line-height:1}}
#fin p{{font-size:58px;font-weight:500}}
</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{total:.2f}" data-width="1080" data-height="1920">
<div class="bola" id="b1"></div><div class="bola" id="b2"></div>
{chip}
{''.join(bloques)}
<div id="fin">{placa}<h1>{html.escape(marca['nombre'])}</h1><p>{html.escape(marca['cta'])}</p></div>
</div>
<script>
const tl = gsap.timeline({{paused:true}});
tl.fromTo("#b1",{{x:0,y:0}},{{x:220,y:160,duration:{total:.2f},ease:"sine.inOut"}},0)
  .fromTo("#b2",{{x:0,y:0}},{{x:-180,y:-220,duration:{total:.2f},ease:"sine.inOut"}},0)
  .fromTo("#chip",{{autoAlpha:0,y:-30}},{{autoAlpha:1,y:0,duration:.5,ease:"power3.out"}},.1);
{chr(10).join(anim)}
tl.to("#chip",{{autoAlpha:0,duration:.3}},{fin - .2:.2f})
  .fromTo("#fin",{{autoAlpha:0,scale:.92}},{{autoAlpha:1,scale:1,duration:.6,ease:"back.out(1.5)"}},{fin:.2f})
  .fromTo("#fin p",{{autoAlpha:0,y:30}},{{autoAlpha:1,y:0,duration:.4}},{fin + .45:.2f})
  .to({{}},{{duration:.01}},{total - .01:.2f});
window.__timelines = window.__timelines || {{}};
window.__timelines["main"] = tl;
</script></body></html>"""


def preparar(escenas, marca, salida):
    out = Path(salida); (out / "assets").mkdir(parents=True, exist_ok=True)
    if marca.get("logo"):
        shutil.copy(marca["logo"], out / "assets" / "logo.png")
    for i, e in enumerate(escenas):
        if e.get("foto"):
            shutil.copy(e["foto"], out / "assets" / f"foto{i}.jpg")
    (out / "index.html").write_text(composicion(marca, escenas))
    return {"escenas": len(escenas), "duracion_s": round(sum(dur_escena(e) - TRANS + .1 for e in escenas) + .4 + CIERRE, 1)}


if __name__ == "__main__":
    escenas, marca, salida = json.loads(Path(sys.argv[1]).read_text()), json.loads(Path(sys.argv[2]).read_text()), sys.argv[3]
    print(json.dumps(preparar(escenas, marca, salida)))
