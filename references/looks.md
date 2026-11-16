# Los 9 estilos de edición (looks)

Enséñaselos con su número, su nombre y para qué sirve, y que elija uno. Los ejemplos cortos están en `galeria/muestrario.html` (y los completos en `galeria/ligeros/`) (mismo video crudo, solo cambia la edición). Si no sabe cuál, recomienda según su giro.

En `opciones.json` basta con `"look": "<clave>"`. Todo lo que pida aparte (color, posición, transición) gana sobre el look.

| # | Estilo | Clave | Cómo se ve | Ideal para | Qué le pides a ella |
|---|---|---|---|---|---|
| 1 | **Creador dinámico** | `creador` | Subtítulo en píldora que ilumina palabra por palabra y un zoom en cada corte. Mucha energía. | Coaches, consultoras, servicios, marca personal | Nada extra |
| 2 | **Palabras gigantes** | `gigantes` | Una palabra enorme a la vez, flash blanco en los cortes y sus frases fuertes a pantalla completa con su color. | Tips, opiniones, frases que se comparten | Las 1 o 2 frases más fuertes (o tú las eliges de la transcripción) |
| 3 | **Con fotos** | `fotos` | Sus fotos aparecen justo cuando las menciona: en recuadro o a pantalla completa con texto, y entran con barrido. | Productos, comida, antes y después, resultados | Sus fotos (producto, local, clientes) |
| 4 | **Pasos en pantalla** | `pasos` | Mientras habla, abajo va apareciendo la lista numerada, paso por paso. Subtítulos arriba, discretos. | Tutoriales, recetas, «3 errores que…» | Los pasos (o tú los sacas de lo que dice) |
| 5 | **Cinemático** | `cinematico` | Color cálido de película, grano, viñeta y fugas de luz en los cortes. Subtítulo fino. | Moda, belleza, comida artesanal, bienestar | Nada extra |
| 6 | **Collage** | `collage` | Su video como foto pegada sobre papel con puntitos, con leve temblor y un glitch en los cortes. | Historias, marcas creativas, hecho a mano | Nada extra |
| 7 | **Neón** | `neon` | Subtítulos que brillan con su color, tono frío, grano y glitch. | Marcas jóvenes, tecnología, eventos, vida nocturna | Nada extra |
| 8 | **Acuarela** | `acuarela` | Karaoke y cierre pintado en acuarela con letra de pincel. | Marcas tiernas, artesanales, infantiles | Opcional: imágenes de Flow en acuarela para los apoyos |
| 9 | **Pixel** | `pixel` | Letra de videojuego, cierre pixelado y glitch. | Marcas gamer, juveniles, divertidas | Opcional: imágenes de Flow en pixel art |

## Piezas sueltas para combinar

- **Transiciones** (`transicion`): `flash` (destello blanco), `whip` (barrido con desenfoque), `zoom` (golpe de zoom), `glitch` (falla digital), `fuga` (fuga de luz). Se ponen en los cortes y al entrar cada foto, como máximo una cada 2.5 s.
- **Subtítulos** (`estilo`): `clasico`, `caja`, `minimal`, `karaoke`, `pildora`, `neon`, `gigante`.
- **Color** (`color`): `natural`, `calido`, `frio`, `vivo`, `suave`.
- **Extras:** `grano` (película), `marco: "collage"`, `zoom_auto` (zoom en frases alternas), `textos` (palabras a pantalla completa), `pasos` (lista en pantalla).
- **Más de 450 bloques** de HyperFrames (transiciones 3D, partículas, gráficas, mapas): `npx hyperframes catalog --query "<en inglés>"`. Úsalos cuando pida algo que no está aquí.
