# -*- coding: utf-8 -*-
"""
Configuración del sitio Mente Abierta.
Edita estos datos y vuelve a generar la web con:  python3 build.py
"""

SITE = {
    "name": "Mente Abierta",
    "tagline": "Revista de curiosidades, ciencia e historia",
    "description": "Historias, ciencia, tecnología, curiosidades y conocimientos que merece la pena descubrir. Artículos originales, verificados y fáciles de leer.",
    # Dominio definitivo, sin barra final. Se usa en canonical, sitemap, RSS y datos estructurados.
    "url": "https://www.tudominio.es",
    "lang": "es-ES",
    "locale": "es_ES",
    "author": "Redacción de Mente Abierta",
    "author_initials": "MA",
    "twitter": "",  # p. ej. "@menteabierta"
}

# Datos legales del titular (LSSI-CE art. 10 y RGPD).
# Mientras un valor esté vacío, la web mostrará un marcador resaltado para que no se te olvide.
OWNER = {
    "TITULAR": "",          # Nombre y apellidos o razón social
    "NIF": "",              # NIF / CIF
    "DOMICILIO": "",        # Dirección postal completa
    "EMAIL": "craciunandrei266@gmail.com",  # Email de contacto (también en assets/js/config.js)
    "REGISTRO": "",         # Datos registrales si es sociedad (o déjalo vacío)
    "HOSTING": "",          # Proveedor de alojamiento (p. ej. Netlify, Hostinger...)
    "FECHA_LEGAL": "26 de septiembre de 2026",
}

OWNER_PLACEHOLDERS = {
    "TITULAR": "[Nombre y apellidos o razón social del titular]",
    "NIF": "[NIF/CIF]",
    "DOMICILIO": "[Domicilio postal completo]",
    "EMAIL": "[email de contacto]",
    "REGISTRO": "[Datos de inscripción registral, si procede]",
    "HOSTING": "[Proveedor de alojamiento]",
}
