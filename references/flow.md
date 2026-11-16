# Google Flow con Claude in Chrome

Flow (labs.google/flow) genera imágenes y clips de video con IA usando la cuenta de Google de la alumna. Aquí es la fuente principal de B-roll y de estilos alternativos.

## Requisitos
- La extensión **Claude in Chrome** instalada y conectada (`mcp__claude-in-chrome__*`).
- La alumna entra a Flow en su Chrome normal, con su cuenta. **Tú nunca escribes su contraseña ni códigos.**
- **Google da créditos gratis cada día en Flow.** Si hace pocos videos, no necesita pagar ningún plan. Las imágenes no gastan créditos; los clips de video sí. Antes de generar un video, dile cuántos créditos cuesta y cuántos le quedan hoy.

## Reglas
1. **Usa su Chrome y la pestaña que ya tiene abierta.** No abras otra ventana ni otro navegador.
2. **Una sola generación (x1).** Antes de generar, revisa que el contador esté en 1.
3. **Video = costo.** Lee en pantalla cuántos créditos cuesta y cuántos le quedan. Díselo y espera su «sí». Las imágenes se generan sin preguntar.
4. **Prompts:**
   - En inglés, describiendo sujeto, acción, lugar, luz, encuadre vertical 9:16 y el estilo.
   - Sin marcas, logos ni personas reales.
   - Usa como referencia la foto del producto de la alumna cuando aplique.
5. **Descarga:** baja cada resultado y muévelo a `proyectos/<video>/assets/` con un nombre claro (`broll-tamal-vapor.mp4`).
6. **Si algo falla o Flow pide iniciar sesión,** detente y díselo. No reintentes a ciegas, porque cuesta.

## Prompts base por estilo (cambia el sujeto)
| Estilo | Prompt |
|---|---|
| Realista (B-roll) | `close-up of fresh homemade tamales steaming on a clay plate, warm morning light, shallow depth of field, vertical 9:16, cinematic food shot` |
| Acuarela | `watercolor illustration of …, soft paper texture, loose brush strokes, pastel palette matching #c2410c and #facc15, vertical 9:16` |
| Pixel art | `16-bit pixel art scene of …, crisp pixels, limited palette, retro game style, vertical 9:16` |
| Personaje animado | `friendly 3D cartoon character of a … (no real person), expressive, clean background in brand color, vertical 9:16` |

Para video, agrega el movimiento: `slow push-in`, `gentle steam rising`, `character waves and smiles`. Pide 5 a 8 s.
