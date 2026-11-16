#!/usr/bin/env python3
"""Muestra la transcripción en frases numeradas con tiempos del video crudo (para elegir qué quitar, zooms o B-roll).

Uso: python3 scripts/frases.py video.mp4.palabras.json
"""
import json, sys
p = json.load(open(sys.argv[1])); fr, act = [], []
for w in p:
    if act and (w["start"] - act[-1]["end"] > 0.5 or len(act) >= 12 or act[-1]["w"][-1:] in ".?!"):
        fr.append(act); act = []
    act.append(w)
if act: fr.append(act)
for i, f in enumerate(fr, 1):
    print(f'{i:>2}. [{f[0]["start"]:6.2f}–{f[-1]["end"]:6.2f}] {" ".join(x["w"] for x in f)}')
