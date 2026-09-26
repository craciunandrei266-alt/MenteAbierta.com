/* =========================================================
   Mente Abierta — configuración editable
   Cambia estos valores sin tocar el resto del código.
   ========================================================= */
window.MA_CONFIG = {
  // Google AdSense ------------------------------------------------------
  // Déjalo en false hasta que Google apruebe la web. Cuando la aprueben,
  // pon true y escribe tu ID de editor (ca-pub-XXXXXXXXXXXXXXXX).
  adsEnabled: false,
  adsenseClient: "ca-pub-XXXXXXXXXXXXXXXX",
  // IDs de los bloques de anuncio creados en tu panel de AdSense.
  // Si dejas uno vacío, ese hueco no se mostrará.
  adSlots: {
    "home-mid": "",
    "article-inline": "",
    "article-aside": "",
    "listing": ""
  },

  // Banner de cookies propio -------------------------------------------
  // Para tráfico del Espacio Económico Europeo y Reino Unido, Google exige
  // una CMP certificada (TCF v2.2) para mostrar anuncios personalizados.
  // Si activas la de AdSense ("Privacidad y mensajes"), pon esto en false.
  useOwnCookieBanner: true,

  // Correos y formularios -----------------------------------------------
  siteName: "Mente Abierta",
  // Email visible en la web.
  contactEmail: "craciunandrei266@gmail.com",
  // Adónde llegan los mensajes del formulario de contacto (vía FormSubmit.co).
  // La PRIMERA vez que alguien use un formulario en la web publicada, FormSubmit
  // te enviará un correo "Activate Form": púlsalo y a partir de ahí todo funciona.
  // Después te enviarán un código aleatorio: si lo pegas aquí en lugar del email,
  // tu dirección no aparecerá en el código de la web.
  formEmail: "craciunandrei266@gmail.com",

  // Respuesta automática que recibe quien te escribe por el formulario de contacto.
  contactAutoReply: "¡Hola! Hemos recibido tu mensaje en Mente Abierta. Lo leeremos con atención y te responderemos lo antes posible, normalmente en 2 o 3 días laborables. Gracias por escribirnos.",

  // Opcional: además de FormSubmit, enviar también a otro servicio (p. ej. Formspree).
  contactEndpoint: ""
};
