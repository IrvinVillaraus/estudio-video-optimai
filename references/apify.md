# Apify: fotos reales para tus videos

Apify trae fotos reales (no hechas con IA) de bancos gratis con licencia comercial, como Pexels, Unsplash y Pixabay. Úsalo cuando ella no tenga sus propias fotos de algo, o cuando lo que dice «se puede ver» pero no lo grabó.

## Requisitos (una sola vez, paso a paso)

Guíala de uno en uno. Dale la liga, espera su «listo» y sigue.

1. Cuenta gratis: https://console.apify.com/sign-up. El plan gratis trae crédito cada mes.
2. En Claude: **Configuración → Conectores → Agregar conector personalizado**.
3. Nombre: `Apify`. URL: `https://mcp.apify.com`. Toca **Agregar**.
4. Toca **Conectar**, inicia sesión en Apify y da **Permitir acceso**.
5. Abre una conversación nueva en su carpeta y revisa que aparezcan las herramientas de Apify.

No hay llaves ni códigos que copiar: el inicio de sesión lo reemplaza. El método viejo con `npx` y token ya no se usa.

## Cómo se usa
1. **Busca el robot (Actor)** con el conector: `search-actors` con «pexels images», «unsplash images» o «pixabay images». Elige el de mejor calificación y más usuarios. Lee su descripción con `fetch-actor-details` antes de correrlo.
2. **Búsqueda en inglés y concreta:** `woman baker kneading dough, warm light`, mejor que `bakery`. Pide fotos verticales cuando se pueda y de 5 a 10 resultados.
3. **Costo:** antes de correr, dile cuánto cuesta (lo marca el Actor) y espera su «sí». Una búsqueda de 10 fotos suele costar centavos.
4. **Elige con ella:** baja las mejores 3 a 5 a `proyectos/<video>/assets/`, ábrelas con Read y enséñaselas. Ella decide cuáles van.
5. **Anota la fuente** (banco y autor) en `proyectos/<video>/fuentes.txt`.

## Reglas
- **Solo bancos con licencia comercial gratis:** Pexels, Unsplash, Pixabay. Nunca Google Imágenes, Instagram ni Pinterest.
- **Nada de marcas, logos ni caras de famosos.**
- **Real o IA:** si quiere algo que no existe (su producto en un lugar imaginario, un estilo acuarela), eso es Google Flow (`flow.md`), no Apify.
