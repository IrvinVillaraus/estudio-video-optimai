# Cambiar el fondo (sin pantalla verde)

Ella se graba donde sea y tú le cambias el fondo: acuarela, su local ilustrado, un paisaje, un color de su marca.

1. **El fondo**, en este orden:
   - una foto suya, de su local o de su producto;
   - Google Flow con Claude en Chrome (`flow.md`), sin costo. Prompt base: `watercolor illustration of <lugar de su negocio>, empty, no people, soft paper texture, pastel palette matching <sus colores hex>, vertical 9:16`. El fondo **sin personas** y con el centro despejado.
2. **Cambia el fondo:** `PY scripts/fondo.py proyectos/<video>/crudo/crudo.mp4 proyectos/<video>/assets/fondo.jpg proyectos/<video>/crudo/con-fondo.mp4 --movimiento`.
   - Tarda unos 8 segundos por cada segundo de video. Avísale: «ve por un café ☕».
   - `--movimiento` hace un acercamiento lento sobre el fondo para que no se vea estático.
3. **Revisa:** saca 3 cuadros y mira los bordes del pelo y las manos. Si parpadean, díselo y propón otro fondo más parecido a su ropa o un look sin cambio de fondo.
4. **Edita** con `editar.py` usando `con-fondo.mp4` como crudo. Funciona con todos los estilos; el que mejor combina es Acuarela (8).

Funciona mejor si ella se graba con luz de frente, con un fondo liso detrás y sin moverse mucho.
