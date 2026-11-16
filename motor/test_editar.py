from editar import remapear

tramos = [(0.0, 2.0), (3.0, 5.0)]
palabras = [{"w": "hola", "start": 0.5, "end": 0.9},
            {"w": "borde", "start": 2.9, "end": 3.4},   # empieza en el silencio cortado
            {"w": "fin", "start": 4.5, "end": 5.2}]
r = remapear(palabras, tramos)
assert [p["w"] for p in r] == ["hola", "borde", "fin"], r
assert abs(r[1]["start"] - 2.0) < 1e-9          # se pega al inicio del tramo 2
assert r[2]["end"] <= 4.0 + 1e-9                # no se sale del video cortado
print("ok")

from editar import restar, limitar, a_cortado
t = restar([(0.0, 10.0)], [(2.0, 4.0)])
assert t == [(0.0, 2.0), (4.0, 10.0)], t
assert limitar(t, 5.0) == [(0.0, 2.0), (4.0, 7.0)]
assert a_cortado(5.0, t) == 3.0 and a_cortado(3.0, t) == 2.0   # 3.0 cae en lo quitado: se pega al tramo siguiente
print("ok cortes")
