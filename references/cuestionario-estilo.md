# Cuestionario de estilo (lo primero después de instalar)

Objetivo: que salga de aquí con **su estilo elegido** y guardado en su ficha. Usa AskUserQuestion, una pregunta a la vez.

## 1 · ¿Cómo quieres elegir?

| Opción | Qué haces |
|---|---|
| **Ver ejemplos** (recomendado) | Abre `galeria/muestrario.html` en su navegador: los 10 estilos en video corto con su descripción. En Mac: `open galeria/muestrario.html`. En Windows: `start galeria\muestrario.html`. Luego pregúntale el número. |
| **Tengo una referencia** | Que te mande aquí una captura o arrastre a la carpeta un video que le guste. Ve a la sección 3. |
| **Ayúdame a decidir** | Haz las 4 preguntas de la sección 2 y recomienda. |

## 2 · Las 4 preguntas

1. **¿Qué vendes?** Producto físico / comida / servicio o asesoría / belleza o moda / algo creativo o hecho a mano.
2. **¿Cómo quieres que se sienta?** Con mucha energía / elegante y tranquilo / divertido / tierno.
3. **¿Qué tipo de videos harás más?** Hablando a cámara / tutoriales o pasos / mostrando mi producto / contando historias.
4. **¿Tienes fotos de tu producto o negocio?** Sí, muchas / pocas / ninguna.

**Recomienda (máximo 2 opciones, con su número).** Si duda, la primera recomendación es el **10 · Una Mujer a la Vez**, el estilo de los reels de Aura.

| Si… | Recomienda |
|---|---|
| Servicio o asesoría + energía | 1 Creador dinámico |
| Tips u opiniones + energía | 2 Palabras gigantes |
| Producto o comida + tiene fotos | 3 Con fotos |
| Tutoriales o pasos | 4 Pasos en pantalla |
| Belleza, moda o comida + elegante | 5 Cinemático |
| Hecho a mano o historias | 6 Collage |
| Joven o tecnología | 7 Neón |
| Tierno o artesanal | 8 Acuarela |
| Divertido o juvenil | 9 Pixel |

Ábrele el muestrario para que vea las dos que recomiendas antes de que decida.

## 3 · Con referencia

1. Si es video: `PY scripts/referencia.py <archivo> proyectos/referencia`. Mira `cuadros.jpg`, `paleta.json` y `ritmo.json`. Si es captura, mírala directo.
2. Dile en 3 líneas qué ves: el tipo de subtítulos, los colores, el ritmo (rápido o pausado) y los efectos.
3. Elige el look más cercano y los ajustes que la acercan más: `estilo` de subtítulos, `posicion`, `color`, `transicion`, `grano`.
4. **Copia el estilo, nunca la marca, el logo ni el contenido de otros.**

## 4 · Guarda su elección

Guarda en `marcas/<negocio>/ficha.json`, dentro de `video`:
- `look`: la clave (`aura`, `creador`, `gigantes`, `fotos`, `pasos`, `cinematico`, `collage`, `neon`, `acuarela`, `pixel`);
- `ajustes`: lo que sacaste de su referencia, si la hubo.

Dile que puede cambiarlo cuando quiera con «quiero otro estilo», y que en cada video puede probar otro sin cambiar el guardado.
