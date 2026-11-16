# Acuarelas vivas (estilo 11)

Acuarelas que **cobran vida según lo que ella dice**:
- el fondo cambia por partes del mensaje y cada cambio se corre como pintura;
- los elementos (flores, mariposas, una nube, un farol…) se pintan solos, flotan y se van;
- unos van detrás de ella y otros por delante.

Ideal para reels de reflexión, historias y frases que inspiran.

## Paso a paso

1. **Transcribe** y lee las frases (`transcribir.py`, `frases.py`).
2. **Arma el guion visual con ella**, en una tabla de 4 a 6 momentos: cada uno con «lo que dice», el fondo y 1 o 2 elementos que lo dibujan.
   - Fondos: 2 o 3, uno por parte del mensaje (por ejemplo, alegre → gris → luminoso).
   - Elementos: objetos concretos de lo que dice: «sueños» = mariposas, «crecer» = girasol, «hacerte pequeña» = maceta diminuta.
   - Espera su OK antes de generar.
3. **Genera las acuarelas en Google Flow** con Claude en Chrome (`flow.md`, sin costo):
   - Fondos en 9:16: `Hand-painted watercolor illustration, vertical 9:16 background: <escena>, <paleta de su ficha>, visible paper texture. Completely empty, no people, no text, the center clear and calm.`
   - Elementos en 1:1: `<objeto>, loose hand-painted watercolor, <colores>, isolated on a pure white background, centered, nothing touching the edges, no text, no shadow.`
   - Descárgalos a `proyectos/<video>/acuarelas/`.
   - Quita el blanco de los elementos para que floten con transparencia: `PY scripts/sin_blanco.py proyectos/<video>/acuarelas`.
4. **Separa a la persona** con fondo transparente: `PY scripts/fondo.py <crudo> --alfa proyectos/<video>/persona.webm`. Tarda unos 8 minutos por minuto de video: «ve por un café ☕».
5. **Escribe `plan-acuarela.json`** (el formato está al inicio de `motor/acuarela_viva.py`). Reglas:
   - Los elementos de `atras` van a los lados o arriba de su cabeza; nunca detrás de su cuerpo, donde no se ven.
   - Los de `frente` (mariposas, pétalos) cruzan sin tapar su cara.
   - Entradas: `crece` (plantas), `vuela` (mariposas, aves), `cae` (pétalos, confeti), `flota` (nubes), `brilla` (luces, faroles), `pinta` (todo lo demás).
   - `clave`: las 8 a 12 palabras más fuertes, que salen en rojo.
6. **Arma y revisa:**
   - `python3 motor/acuarela_viva.py proyectos/<video>/plan-acuarela.json proyectos/<video>/edicion`
   - Saca cuadros con `npx hyperframes@0.8.212 snapshot` en cada momento y revisa que todo se vea.
7. **Render final:** `render.py`, igual que siempre.
