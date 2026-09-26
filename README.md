# Mente Abierta — revista digital

**Para verla ya:** haz doble clic en `MenteAbierta.html`. Es la web completa en un solo archivo y se abre en Chrome, Edge, Firefox o Safari (con internet se ven las fotos). Para publicarla en internet usa la carpeta `public/`.

Web estática lista para subir a cualquier hosting (Netlify, Hostinger, GitHub Pages, Cloudflare Pages…). La web terminada está en la carpeta **`public/`**.

## Antes de publicar (imprescindible)

1. **Tus datos legales:** abre `config.py`, rellena `OWNER` (titular, NIF, domicilio, email, hosting) y `SITE["url"]` con tu dominio. Después ejecuta:
   ```
   pip install markdown
   python3 build.py && python3 bundle.py
   ```
   Mientras un dato esté vacío, la web muestra un marcador amarillo en su lugar para que no se te olvide.
2. **Activa los correos (una sola vez):** ver la sección «Correos» más abajo.
3. **Revisa los textos legales** con un profesional: son un modelo adaptado a la normativa española (LSSI-CE, RGPD, LOPDGDD), no asesoramiento jurídico.
4. **Revisa y personaliza los artículos.** Añade tu nombre y experiencia en "Sobre nosotros": Google valora que haya una persona real detrás.
5. Sube el contenido de `public/` a la raíz de tu dominio y envía `sitemap.xml` a Google Search Console.

## Correos (formulario de contacto)

Los formularios envían correos de verdad mediante **FormSubmit** (gratis, sin cuenta ni servidor). Ya están configurados con `craciunandrei266@gmail.com` en `public/assets/js/config.js`.

**Qué pasa cuando alguien los usa:**
- **Contacto:** te llega un correo con nombre, email, motivo y mensaje (al pulsar «Responder» contestas directamente al visitante), y el visitante recibe una respuesta automática de confirmación.

El texto de la respuesta automática se cambia en `config.js` (`contactAutoReply`).

**Activación (solo la primera vez):**
1. Sube la web a tu hosting (no funciona abriendo el archivo en tu ordenador).
2. Envía un mensaje de prueba desde la página de contacto.
3. Te llegará a Gmail un correo de FormSubmit con el botón **Activate Form** (mira en spam si no aparece). Púlsalo.
4. Listo: desde ese momento los formularios funcionan. FormSubmit te enviará además un código aleatorio; si lo pegas en `formEmail` en lugar de tu email, tu dirección no quedará visible en el código de la web.


## Google AdSense

- Solicita AdSense cuando la web lleve unas semanas publicada con el dominio propio y algo de tráfico. Google decide la aprobación; nada la garantiza.
- Cuando te aprueben: en `public/assets/js/config.js` pon `adsEnabled: true`, tu `adsenseClient` (ca-pub-…) y los IDs de bloque en `adSlots`. Los huecos ya están reservados (portada, dentro del artículo, lateral en escritorio y listados) y permanecen ocultos hasta entonces.
- Sustituye el contenido de `public/ads.txt` por la línea que te dé AdSense.
- Para visitantes de la UE/Reino Unido Google exige una CMP certificada (TCF v2.2). Lo más sencillo: activar "Privacidad y mensajes" en AdSense y poner `useOwnCookieBanner: false`.

## Añadir artículos

Crea un `.md` en `content/articulos/` copiando la cabecera de uno existente y ejecuta `python3 build.py`. Sintaxis extra:
- `[[slug-de-otro-articulo]]` o `[[slug|texto]]` → enlace interno
- `:::dato {cifra} Título` … `:::` → caja de dato destacado
- `:::nota` / `:::cita Autor` / `:::fuentes` … `:::`
- `!fig clave-imagen | pie de foto` → imagen dentro del texto (las imágenes se registran en `data.py`)
- `++texto++` → subrayado tipo rotulador

## Imágenes

Fotos de Unsplash (licencia gratuita, uso comercial permitido), servidas desde su CDN en tamaño optimizado con `srcset` y carga diferida. Los autores aparecen en cada pie de foto y en `creditos-imagenes.html`.
