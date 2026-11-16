#!/usr/bin/env python3
"""Acuarelas vivas: fondos de acuarela que cambian con lo que dice y elementos que aparecen, detrás y delante de ella.

Uso: python3 motor/acuarela_viva.py proyectos/<video>/plan-acuarela.json proyectos/<video>/edicion
Luego: python3 scripts/render.py proyectos/<video>/edicion "<texto>" <tema>

plan-acuarela.json (tiempos del video original, en segundos):
{"video_alfa": "ruta a la persona sin fondo (fondo.py --alfa)", "palabras": "ruta .palabras.json", "logo": "ruta o null",
 "colores": {"texto": "#4a1f5c", "clave": "#d0142c"}, "cierre": "Frase final 💜", "estrellas_desde": 33.8,
 "fondos": [["fondo-a.jpg", 0], ["fondo-b.jpg", 11.2]],
 "elementos": [{"img": "girasol.png", "de": 1.6, "a": 11, "capa": "atras|frente", "x": -60, "y": 760, "ancho": 620,
                "entrada": "crece|vuela|cae|flota|brilla|pinta"}],
 "clave": ["palabras", "que", "van", "en", "rojo"], "assets": "carpeta con los fondos y elementos"}
"""
import html, json, os, shutil, subprocess, sys
plan = json.load(open(sys.argv[1])); E = sys.argv[2]; A = E + "/assets"
os.makedirs(A, exist_ok=True)
for f in os.listdir(plan["assets"]):
    if f.endswith((".png", ".jpg", ".jpeg")):
        shutil.copy(os.path.join(plan["assets"], f), f"{A}/{f}")
shutil.copy(plan["video_alfa"], A + "/aura.webm")
if plan.get("logo"):
    shutil.copy(plan["logo"], A + "/logo.jpg")
DUR = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", plan["video_alfa"]],
                           capture_output=True, text=True).stdout)
CIERRE = 3.0; TOTAL = DUR + CIERRE
pal = json.load(open(plan["palabras"]))
FONDOS = [tuple(f) for f in plan["fondos"]]
EL = [(e["img"], e["de"], min(e["a"], TOTAL), e.get("capa", "atras"), e["x"], e["y"], e["ancho"], e.get("entrada", "pinta"), "") for e in plan["elementos"]]
CLAVE = {w.lower() for w in plan.get("clave", [])}
COL = {"texto": "#4a1f5c", "clave": "#d0142c", **plan.get("colores", {})}

def grupos(p, n=5):
    out, g = [], []
    for w in p:
        g.append(w)
        if len(g) >= n or w["w"].endswith((".", ",", "?")):
            out.append(g); g = []
    return out + ([g] if g else [])
subs = []
for i, g in enumerate(grupos(pal)):
    fin = g[-1]["end"] + 0.25
    txt = " ".join(f'<span class="r">{html.escape(w["w"])}</span>' if w["w"].lower().strip(".,¡!¿?") in CLAVE else html.escape(w["w"]) for w in g)
    subs.append(f'<div class="sub" data-s="{g[0]["start"]:.2f}" data-e="{fin:.2f}"><span class="cinta">{txt}</span></div>')

fondos = "".join(f'<div class="fondo" id="f{i}" style="background-image:url(assets/{f})" data-s="{s}"></div>' for i, (f, s) in enumerate(FONDOS))
def el(i, e):
    f, de, a, capa, x, y, w, ent, _ = e
    return f'<img class="el {ent}" id="e{i}" src="assets/{f}" data-s="{de}" data-e="{a}" style="left:{x}px;top:{y}px;width:{w}px" alt="">'
atras = "".join(el(i, e) for i, e in enumerate(EL) if e[3] == "atras")
frente = "".join(el(i, e) for i, e in enumerate(EL) if e[3] == "frente")
estrellas = "".join(f'<div class="est" style="left:{x}px;top:{y}px;width:{w}px"><svg viewBox="0 0 40 40"><path d="M20 0C22 14 26 18 40 20C26 22 22 26 20 40C18 26 14 22 0 20C14 18 18 14 20 0Z" fill="{c}"/></svg></div>'
                    for x, y, w, c in [(90, 420, 46, "#d4a72c"), (950, 330, 38, "#fff"), (160, 1000, 34, "#fff"), (980, 900, 50, "#d4a72c"), (60, 1300, 40, "#d4a72c"), (1000, 1250, 36, "#fff"), (520, 260, 30, "#fff")])

doc = f"""<!doctype html><html lang="es"><head><meta charset="UTF-8"><meta name="viewport" content="width=1080, height=1920">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@800;900&display=swap">
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body,#root{{width:1080px;height:1920px;overflow:hidden;background:#f7ece8}}
#root{{position:relative;font-family:'Playfair Display',serif}}
.fondo{{position:absolute;inset:-4%;background-size:cover;background-position:center;--r:-30%;
  -webkit-mask-image:radial-gradient(circle at 50% 55%,#000 var(--r),transparent calc(var(--r) + 28%));mask-image:radial-gradient(circle at 50% 55%,#000 var(--r),transparent calc(var(--r) + 28%))}}
#f0{{--r:200%}}
.el{{position:absolute;opacity:0;--p:-20%;-webkit-mask-image:linear-gradient(0deg,#000 var(--p),transparent calc(var(--p) + 22%));mask-image:linear-gradient(0deg,#000 var(--p),transparent calc(var(--p) + 22%))}}
.el.vuela,.el.cae,.el.flota,.el.brilla{{-webkit-mask-image:none;mask-image:none}}
#auracap{{position:absolute;inset:0}}
#aura{{position:absolute;inset:0;width:1080px;height:1920px;object-fit:cover}}
.est{{position:absolute;opacity:0;filter:drop-shadow(0 2px 6px #0003)}}
.sub{{position:absolute;left:50px;right:50px;top:1470px;text-align:center;opacity:0}}
.cinta{{display:inline;font-size:66px;font-weight:900;line-height:1.35;text-transform:uppercase;color:{COL["texto"]};padding:6px 18px;
  background:#fffaf5e6;box-decoration-break:clone;-webkit-box-decoration-break:clone;border-radius:14px}}
.r{{color:{COL["clave"]}}}
#chip{{position:absolute;left:46px;top:70px;background:#fff;padding:12px 20px;border-radius:20px;box-shadow:0 6px 20px #0002}}
#chip img{{height:62px;display:block}}
#fin{{position:absolute;inset:0;opacity:0;display:flex;flex-direction:column;align-items:center;justify-content:flex-start;padding-top:860px;gap:26px;text-align:center}}
#fin .placa{{background:#fff;padding:18px 30px;border-radius:26px;box-shadow:0 10px 30px #0002}}#fin .placa img{{height:130px;display:block}}
#fin p{{font-size:60px;font-weight:900;color:#4a1f5c;background:#fffaf5ee;margin:0 70px;padding:18px 30px;border-radius:22px;line-height:1.15}}
</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL:.2f}" data-width="1080" data-height="1920">
{fondos}
{atras}
<div id="auracap"><video id="aura" class="clip" src="assets/aura.webm" data-start="0" data-duration="{DUR:.2f}" data-volume="1" data-has-audio="true"></video></div>
{frente}
{estrellas}
{'<div id="chip"><img src="assets/logo.jpg" alt=""></div>' if plan.get("logo") else ''}
{''.join(subs)}
<div id="fin"><div class="placa"><img src="assets/logo.jpg" alt=""></div><p>{html.escape(plan.get("cierre", ""))}</p></div>
</div>
<script>
const tl = gsap.timeline({{paused:true}});
// fondos: deriva lenta + cambio que se corre como pintura
document.querySelectorAll(".fondo").forEach((f,i)=>{{
  tl.fromTo(f,{{scale:1.0,x:0}},{{scale:1.07,x:(i%2?-18:18),duration:{TOTAL:.2f},ease:"none"}},0);
  const s=+f.dataset.s; if(s>0) tl.fromTo(f,{{"--r":"-30%"}},{{"--r":"200%",duration:1.6,ease:"power2.in"}},s-0.4);
}});
// elementos: cada uno entra según lo que dice Aura
document.querySelectorAll(".el").forEach(el=>{{
  const s=+el.dataset.s, e=+el.dataset.e, d=e-s;
  if(el.classList.contains("crece")){{
    tl.fromTo(el,{{autoAlpha:1,"--p":"-25%",scaleY:.6,transformOrigin:"50% 100%"}},{{"--p":"125%",scaleY:1,duration:1.8,ease:"power2.out"}},s)
      .to(el,{{rotate:2,duration:1.2,ease:"sine.inOut",yoyo:true,repeat:Math.max(1,Math.floor((d-2.5)/1.2))}},s+1.8);
  }} else if(el.classList.contains("vuela")){{
    tl.fromTo(el,{{autoAlpha:0,x:-520,y:260,rotate:-8}},{{autoAlpha:1,x:0,y:0,rotate:4,duration:2.4,ease:"sine.out"}},s)
      .to(el,{{y:-40,rotate:-3,duration:1.1,ease:"sine.inOut",yoyo:true,repeat:Math.max(1,Math.floor((d-3.4)/1.1))}},s+2.4);
  }} else if(el.classList.contains("cae")){{
    tl.fromTo(el,{{autoAlpha:0,y:-200,rotate:-6}},{{autoAlpha:.95,y:1500,rotate:10,duration:Math.min(d,4.5)+1.5,ease:"none"}},s)
      .to(el,{{autoAlpha:0,duration:.8}},s+Math.min(d,4.5)+0.7);
  }} else if(el.classList.contains("flota")){{
    tl.fromTo(el,{{autoAlpha:0,x:280,filter:"blur(10px)"}},{{autoAlpha:1,x:0,filter:"blur(0px)",duration:1.6,ease:"power2.out"}},s)
      .to(el,{{x:-160,y:30,duration:d-2.4,ease:"sine.inOut"}},s+1.6);
  }} else if(el.classList.contains("brilla")){{
    tl.fromTo(el,{{autoAlpha:0,scale:.7,filter:"brightness(.6) blur(8px)"}},{{autoAlpha:1,scale:1,filter:"brightness(1.15) blur(0px)",duration:1.2,ease:"back.out(1.6)"}},s)
      .to(el,{{scale:1.06,filter:"brightness(1.35)",duration:.7,ease:"sine.inOut",yoyo:true,repeat:Math.max(1,Math.floor((d-2)/.7))}},s+1.2);
  }} else {{
    tl.fromTo(el,{{autoAlpha:1,"--p":"-25%"}},{{"--p":"125%",duration:1.6,ease:"power2.out"}},s)
      .to(el,{{y:-12,duration:1.3,ease:"sine.inOut",yoyo:true,repeat:Math.max(1,Math.floor((d-2.4)/1.3))}},s+1.6);
  }}
  if(e<{TOTAL - 0.1:.2f}) tl.to(el,{{autoAlpha:0,filter:"blur(12px)",duration:.8,ease:"power1.in"}},e-.8);
}});
// estrellitas desde «verte brillar»
document.querySelectorAll(".est").forEach((s,i)=>{{
  tl.fromTo(s,{{autoAlpha:0,scale:.3}},{{autoAlpha:1,scale:1,duration:.5,ease:"back.out(2)"}},{plan.get("estrellas_desde", TOTAL - 8):.2f}+i*.18)
    .to(s,{{scale:.6,rotate:45,duration:.8+(i%3)*.2,ease:"sine.inOut",yoyo:true,repeat:6}},{plan.get("estrellas_desde", TOTAL - 8) + .6:.2f}+i*.18);
}});
// subtítulos
document.querySelectorAll(".sub").forEach(el=>{{
  const s=+el.dataset.s, e=+el.dataset.e;
  tl.fromTo(el,{{autoAlpha:0,y:24,scale:.96}},{{autoAlpha:1,y:0,scale:1,duration:.22,ease:"power2.out"}},s).set(el,{{autoAlpha:0}},e);
}});
tl.fromTo("#chip",{{autoAlpha:0,y:-20}},{{autoAlpha:1,y:0,duration:.5}},.3).to("#chip",{{autoAlpha:0,duration:.3}},{DUR - 0.3:.2f});
tl.to("#auracap",{{opacity:0,duration:.5}},{DUR - 0.5:.2f})
  .fromTo("#fin",{{autoAlpha:0}},{{autoAlpha:1,duration:.6}},{DUR - 0.2:.2f})
  .fromTo("#fin .placa",{{scale:.8}},{{scale:1,duration:.7,ease:"back.out(1.7)"}},{DUR:.2f})
  .to({{}},{{duration:.01}},{TOTAL - 0.01:.2f});
window.__timelines = window.__timelines || {{}}; window.__timelines["main"] = tl;
</script></body></html>"""
open(E + "/index.html", "w").write(doc)
print("ok", E, round(TOTAL, 1), "s")
