# -*- coding: utf-8 -*-
"""
Generador estático de Mente Abierta.
Uso:  pip install markdown   y después   python3 build.py
Crea la web completa en la carpeta ./public
"""
import html
import json
import math
import os
import re
import shutil
from datetime import date

import markdown

from config import SITE, OWNER, OWNER_PLACEHOLDERS
from data import CATEGORIES, IMAGES, img_url

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "public")
CONTENT = os.path.join(BASE, "content")
CAT = {slug: {"slug": slug, "name": name, "desc": desc} for slug, name, desc in CATEGORIES}
MONTHS = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
MONTHS_SHORT = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sept", "oct", "nov", "dic"]
FONTS = "https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400..800&family=Literata:ital,opsz,wght@0,7..72,400..700;1,7..72,400..600&display=swap"
VERSION = "1"


def e(s):
    return html.escape(str(s), quote=True)


def slugify(s):
    s = s.lower()
    for a, b in (("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"), ("ü", "u"), ("ñ", "n")):
        s = s.replace(a, b)
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:60]


def fdate(d, short=False):
    if short:
        return "%d %s %d" % (d.day, MONTHS_SHORT[d.month - 1], d.year)
    return "%d de %s de %d" % (d.day, MONTHS[d.month - 1], d.year)


# ------------------------------------------------------------------ icons
ICON = {
    "arrow": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
    "search": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>',
    "moon": '<svg class="i-moon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>',
    "sun": '<svg class="i-sun" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>',
    "menu": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path class="bar bar-1" d="M4 7h16"/><path class="bar bar-2" d="M4 12h16"/><path class="bar bar-3" d="M4 17h16"/></svg>',
    "up": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 19V5M6 11l6-6 6 6"/></svg>',
    "link": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M10 14a5 5 0 0 0 7 0l3-3a5 5 0 0 0-7-7l-1 1"/><path d="M14 10a5 5 0 0 0-7 0l-3 3a5 5 0 0 0 7 7l1-1"/></svg>',
    "x": '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.8 3h3.1l-6.8 7.7 8 10.3h-6.2l-4.9-6.3L5.4 21H2.3l7.2-8.3L1.8 3h6.4l4.4 5.8L17.8 3zm-1.1 16.2h1.7L7.4 4.7H5.6l11.1 14.5z"/></svg>',
    "fb": '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M13.5 22v-8h2.7l.4-3.2h-3.1V8.8c0-.9.3-1.5 1.6-1.5h1.7V4.4c-.3 0-1.3-.1-2.5-.1-2.4 0-4.1 1.5-4.1 4.2v2.3H7.5V14h2.7v8h3.3z"/></svg>',
    "wa": '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm0 18.2a8.2 8.2 0 0 1-4.2-1.1l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8-.2-.1-.4-.1-.6.1l-.8 1c-.1.2-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.3-.4.3-.4.7-1.3.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.7 11.8 11.8 0 0 0 4.5 4c1.7.7 2.3.8 3.2.6.5-.1 1.5-.6 1.7-1.2.2-.6.2-1.1.1-1.2l-.4-.2z"/></svg>',
    "in": '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M6.9 21H3.4V9h3.5v12zM5.1 7.4a2 2 0 1 1 0-4.1 2 2 0 0 1 0 4.1zM21 21h-3.5v-5.8c0-1.4 0-3.2-2-3.2s-2.2 1.5-2.2 3.1V21H9.8V9h3.3v1.6h.1a3.7 3.7 0 0 1 3.3-1.8c3.5 0 4.2 2.3 4.2 5.4V21z"/></svg>',
}
LOGO = ('<svg class="logo__mark" width="30" height="30" viewBox="0 0 32 32" aria-hidden="true"><path d="M27.3 11.2A12 12 0 1 0 28 16" fill="none" stroke="currentColor" stroke-width="3.4" stroke-linecap="round"/>'
        '<circle cx="16" cy="16" r="4.4" fill="#2438a6"/><circle cx="27.6" cy="6.4" r="2.2" fill="#e8b92f"/></svg>')
FAVICON = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="7" fill="#131a19"/>'
           '<path d="M25 12.2A10 10 0 1 0 25.6 16" fill="none" stroke="#f3f5f4" stroke-width="3" stroke-linecap="round"/>'
           '<circle cx="15.6" cy="16" r="3.6" fill="#8fa0ff"/><circle cx="25.3" cy="8" r="1.9" fill="#f3d466"/></svg>')


# ------------------------------------------------------------------ owner placeholders
def owner(key):
    v = OWNER.get(key, "")
    if v:
        return e(v)
    return '<span class="ph">%s</span>' % e(OWNER_PLACEHOLDERS.get(key, "[" + key + "]"))


def fill_owner(text):
    return re.sub(r"\{\{([A-Z_]+)\}\}", lambda m: owner(m.group(1)) if m.group(1) in OWNER else m.group(0), text)


# ------------------------------------------------------------------ images
def picture(key, cls="media", sizes="100vw", w=1200, ratio=(3, 2), eager=False, fallback="", cat=None, alt=None, link=None):
    pid, default_alt, _, _ = IMAGES[key]
    alt = default_alt if alt is None else alt
    widths = [400, 640, 900, 1200, 1600]
    h_of = lambda ww: int(round(ww * ratio[1] / ratio[0]))
    srcset = ", ".join("%s %dw" % (e(img_url(key, ww, h_of(ww))), ww) for ww in widths)
    loading = 'fetchpriority="high" loading="eager"' if eager else 'loading="lazy"'
    img = ('<img src="%s" srcset="%s" sizes="%s" alt="%s" width="%d" height="%d" %s decoding="async"%s>'
           % (e(img_url(key, w, h_of(w))), srcset, sizes, e(alt), w, h_of(w), loading,
              (' data-parallax=".05"' if cls.endswith("parallax") else "")))
    catattr = ' data-cat="%s"' % cat if cat else ""
    klass = cls.replace(" parallax", "")
    if link:
        return '<a class="%s" href="%s" tabindex="-1" aria-hidden="true" data-fallback="%s"%s>%s</a>' % (klass, link, e(fallback), catattr, img)
    return '<div class="%s" data-fallback="%s"%s>%s</div>' % (klass, e(fallback), catattr, img)


def credit(key):
    _, _, author, url = IMAGES[key]
    return 'Foto: <a href="%s" rel="noopener" target="_blank">%s</a> / Unsplash' % (e(url), e(author))


# ------------------------------------------------------------------ articles
def parse_article(path):
    raw = open(path, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.S)
    meta_raw, body = m.group(1), m.group(2)
    meta = {}
    for line in meta_raw.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    y, mo, d = [int(x) for x in meta["date"].split("-")]
    a = {
        "slug": meta["slug"], "title": meta["title"], "dek": meta["dek"], "cat": meta["category"],
        "date": date(y, mo, d), "image": meta["image"], "keywords": meta.get("keywords", ""),
        "related": [s.strip() for s in meta.get("related", "").split(",") if s.strip()],
        "featured": meta.get("featured", "") == "true", "src": body,
        "updated": meta.get("updated", ""),
    }
    words = len(re.findall(r"\w+", re.sub(r"[:\[\]!{}#*]", " ", body)))
    a["words"] = words
    a["read"] = max(3, int(math.ceil(words / 210.0)))
    return a


def render_body(a, articles_by_slug, root):
    src = a["src"]
    blocks = {}

    def stash(html_str):
        k = "BLOCKTOKEN%dX" % len(blocks)
        blocks[k] = html_str
        return "\n\n" + k + "\n\n"

    def md(text):
        return markdown.markdown(text, extensions=["tables", "sane_lists"])

    # internal links
    def ilink(m):
        slug = m.group(1).strip()
        text = m.group(2)
        if slug not in articles_by_slug:
            raise SystemExit("Enlace interno roto en %s: %s" % (a["slug"], slug))
        t = text if text else articles_by_slug[slug]["title"]
        return '<a href="%s.html">%s</a>' % (slug, t)
    src = re.sub(r"\[\[([a-z0-9\-]+)(?:\|([^\]]+))?\]\]", ilink, src)

    # custom blocks
    def block(m):
        kind, arg, inner = m.group(1), m.group(2).strip(), m.group(3)
        if kind == "dato":
            big = ""
            mm = re.match(r"^\{(.+?)\}\s*(.*)$", arg)
            if mm:
                big, arg = mm.group(1), mm.group(2)
            return stash('<aside class="fact"><div class="fact__label">%s</div>%s%s</aside>' % (
                e(arg or "Dato clave"), ('<span class="big">%s</span>' % e(big)) if big else "", md(inner)))
        if kind == "nota":
            return stash('<div class="note">%s</div>' % md(inner))
        if kind == "cita":
            return stash('<blockquote>%s%s</blockquote>' % (md(inner), ('<cite>%s</cite>' % e(arg)) if arg else ""))
        if kind == "html":
            return stash(inner)
        if kind == "fuentes":
            return stash('<section class="sources" aria-labelledby="fuentes"><h2 id="fuentes">Fuentes y lecturas recomendadas</h2>%s</section>' % md(inner))
        raise SystemExit("Bloque desconocido: " + kind)
    src = re.sub(r"^:::(\w+)([^\n]*)\n(.*?)\n:::\s*$", block, src, flags=re.S | re.M)

    # figures:  !fig key | pie de foto
    def fig(m):
        key, cap = m.group(1).strip(), m.group(2).strip()
        return stash('<figure>%s<figcaption>%s %s</figcaption></figure>' % (
            picture(key, sizes="(min-width: 1080px) 680px, 100vw", w=1200, ratio=(16, 10), fallback=CAT[a["cat"]]["name"], cat=a["cat"]),
            e(cap) + ("." if cap and not cap.endswith(".") else ""), credit(key)))
    src = re.sub(r"^!fig\s+([\w\-]+)\s*\|\s*(.*)$", fig, src, flags=re.M)

    out = md(src)
    for k, v in blocks.items():
        out = out.replace("<p>%s</p>" % k, v).replace(k, v)
    out = out.replace("<p>", '<p class="lead">', 1)
    out = out.replace("==", "")  # safety

    toc = []

    def h2(m):
        inner = m.group(1)
        if 'id="' in m.group(0):
            return m.group(0)
        hid = slugify(inner)
        toc.append((hid, re.sub(r"<[^>]+>", "", inner)))
        return '<h2 id="%s">%s</h2>' % (hid, inner)
    out = re.sub(r"<h2>(.*?)</h2>", h2, out)

    # in-content ad slot before the third h2 (reserved, hidden until AdSense is enabled)
    parts = out.split("<h2 ")
    if len(parts) > 3:
        parts[3] = '__AD__' + parts[3]
        out = "<h2 ".join(parts).replace("<h2 __AD__", '<div class="ad-slot" data-slot="article-inline" aria-hidden="true"></div><h2 ')
    # marker highlights: ==texto==
    out = re.sub(r"\+\+(.+?)\+\+", r"<mark>\1</mark>", out)
    return out, toc


def plain_text(a):
    t = re.sub(r"^:::.*$|^!fig.*$", " ", a["src"], flags=re.M)
    t = re.sub(r"\[\[([a-z0-9\-]+)\|([^\]]+)\]\]", r"\2", t)
    t = re.sub(r"\[\[[^\]]+\]\]", " ", t)
    t = re.sub(r"<[^>]+>|[#*_>|`+]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


# ------------------------------------------------------------------ layout
def nav_items(active):
    items = [("index.html", "Inicio", "inicio"), ("articulos.html", "Artículos", "articulos"),
             ("categorias.html", "Categorías", "categorias"), ("sobre-nosotros.html", "Sobre nosotros", "sobre"),
             ("contacto.html", "Contacto", "contacto")]
    return items, active


def head(title, desc, root, canonical, og_image=None, og_type="website", jsonld=None, noindex=False, extra=""):
    full_title = title if (title.endswith(SITE["name"]) or title.startswith(SITE["name"])) else "%s · %s" % (title, SITE["name"])
    img = og_image or img_url("hero", 1200, 630)
    ld = ""
    if jsonld:
        for block in (jsonld if isinstance(jsonld, list) else [jsonld]):
            ld += '<script type="application/ld+json">%s</script>\n' % json.dumps(block, ensure_ascii=False)
    return f"""<!doctype html>
<html lang="{SITE['lang']}" data-root="{root}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(full_title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{e(canonical)}">
{'<meta name="robots" content="noindex, follow">' if noindex else '<meta name="robots" content="index, follow, max-image-preview:large">'}
<meta property="og:site_name" content="{e(SITE['name'])}">
<meta property="og:locale" content="{SITE['locale']}">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{e(canonical)}">
<meta property="og:image" content="{e(img)}">
<meta name="twitter:card" content="summary_large_image">
{('<meta name="twitter:site" content="%s">' % e(SITE['twitter'])) if SITE.get('twitter') else ''}
<meta name="theme-color" content="#f3f5f4" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0e1312" media="(prefers-color-scheme: dark)">
<link rel="icon" href="{root}favicon.svg" type="image/svg+xml">
<link rel="alternate" type="application/rss+xml" title="{e(SITE['name'])}" href="{root}feed.xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preconnect" href="https://images.unsplash.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="{root}assets/css/styles.css?v={VERSION}">
<script>(function(d){{d.classList.add('js');try{{var t=localStorage.getItem('ma_theme');if(t)d.setAttribute('data-theme',t)}}catch(e){{}}}})(document.documentElement);</script>
{extra}{ld}</head>
<body>
<a class="skip-link" href="#main">Saltar al contenido</a>
"""


def header(root, active):
    items, _ = nav_items(active)
    lis = "".join('<li><a class="nav__link" href="%s%s"%s>%s</a></li>' % (
        root, href, ' aria-current="page"' if key == active else "", label) for href, label, key in items)
    return f"""<header class="site-header">
  <div class="wrap site-header__inner">
    <a class="logo" href="{root}index.html" aria-label="{e(SITE['name'])}, ir al inicio">{LOGO}<span class="logo__text">Mente <em>Abierta</em></span></a>
    <nav class="nav" id="site-nav" aria-label="Principal"><ul class="nav__list">{lis}</ul></nav>
    <div class="header-actions">
      <button class="icon-btn" type="button" data-open-search aria-label="Buscar artículos (tecla /)">{ICON['search']}</button>
      <button class="icon-btn theme-toggle" type="button" aria-label="Cambiar tema claro u oscuro">{ICON['moon']}{ICON['sun']}</button>
      <button class="icon-btn menu-toggle" type="button" aria-controls="site-nav" aria-expanded="false" aria-label="Abrir menú">{ICON['menu']}</button>
    </div>
  </div>
</header>
"""


def footer(root):
    cats = "".join('<li><a href="%scategoria/%s.html">%s</a></li>' % (root, s, e(n)) for s, n, _ in CATEGORIES[:6])
    cats2 = "".join('<li><a href="%scategoria/%s.html">%s</a></li>' % (root, s, e(n)) for s, n, _ in CATEGORIES[6:])
    return f"""<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div>
        <a class="logo" href="{root}index.html">{LOGO}<span class="logo__text">Mente <em>Abierta</em></span></a>
        <p>Revista digital independiente de curiosidades, ciencia, historia y cultura. Artículos originales, revisados y con fuentes.</p>
      </div>
      <div><h2>Secciones</h2><ul>{cats}</ul></div>
      <div><h2>Más temas</h2><ul>{cats2}</ul></div>
      <div><h2>La revista</h2><ul>
        <li><a href="{root}articulos.html">Todos los artículos</a></li>
        <li><a href="{root}sobre-nosotros.html">Sobre nosotros</a></li>
        <li><a href="{root}contacto.html">Contacto</a></li>
        <li><a href="{root}aviso-legal.html">Aviso legal</a></li>
        <li><a href="{root}privacidad.html">Política de privacidad</a></li>
        <li><a href="{root}cookies.html">Política de cookies</a></li>
        <li><a href="{root}terminos.html">Términos y condiciones</a></li>
        <li><a href="{root}creditos-imagenes.html">Créditos de imágenes</a></li>
        <li><button class="linklike" type="button" data-open-cookies>Configurar cookies</button></li>
      </ul></div>
    </div>
    <div class="footer-bottom">
      <span>© <span data-year>2026</span> {e(SITE['name'])}. Todos los derechos reservados.</span>
      <span><a href="{root}feed.xml">RSS</a> · Hecho con curiosidad</span>
    </div>
  </div>
</footer>
"""


def chrome_end(root):
    return f"""<div class="search-dialog" hidden role="dialog" aria-modal="true" aria-label="Buscar en {e(SITE['name'])}">
  <div class="search-panel">
    <form action="{root}buscar.html" method="get" role="search">
      {ICON['search']}
      <label class="visually-hidden" for="search-input">Buscar artículos</label>
      <input id="search-input" name="q" type="search" placeholder="Buscar artículos, temas, lugares…" autocomplete="off">
      <button class="icon-btn" type="button" data-close-search aria-label="Cerrar búsqueda"><kbd>Esc</kbd></button>
    </form>
    <div class="search-results" aria-live="polite"></div>
  </div>
</div>
<div class="cookie" hidden role="region" aria-label="Aviso de cookies">
  <h2>Tu privacidad</h2>
  <p>Usamos cookies técnicas necesarias para que la web funcione. Con tu permiso, también usaremos cookies de publicidad para financiar el proyecto. Más información en la <a href="{root}cookies.html">política de cookies</a>.</p>
  <div class="cookie__prefs" hidden>
    <label><input type="checkbox" checked disabled> Necesarias (siempre activas)</label>
    <label><input type="checkbox" id="consent-ads"> Publicidad personalizada (Google AdSense)</label>
    <button class="btn btn--sm" type="button" data-consent="save">Guardar preferencias</button>
  </div>
  <div class="cookie__actions">
    <button class="btn btn--sm btn--ghost" type="button" data-consent="none">Rechazar</button>
    <button class="btn btn--sm btn--ghost" type="button" data-consent="config">Configurar</button>
    <button class="btn btn--sm" type="button" data-consent="all">Aceptar</button>
  </div>
</div>
<button class="to-top" type="button" aria-label="Volver arriba">{ICON['up']}</button>
<script src="{root}assets/js/config.js?v={VERSION}"></script>
<script src="{root}assets/js/search-index.js?v={VERSION}" defer></script>
<script src="{root}assets/js/main.js?v={VERSION}" defer></script>
</body>
</html>
"""


def page(root, active, title, desc, canonical, body, **kw):
    return head(title, desc, root, canonical, **kw) + header(root, active) + '<main id="main" tabindex="-1">\n' + body + "\n</main>\n" + footer(root) + chrome_end(root)


def breadcrumbs(root, trail):
    lis = []
    for label, href in trail:
        if href:
            lis.append('<li><a href="%s%s">%s</a></li>' % (root, href, e(label)))
        else:
            lis.append('<li aria-current="page">%s</li>' % e(label))
    return '<nav class="breadcrumbs" aria-label="Migas de pan"><ol>%s</ol></nav>' % "".join(lis)


def breadcrumb_ld(trail):
    items = []
    for i, (label, href) in enumerate(trail, 1):
        it = {"@type": "ListItem", "position": i, "name": label}
        if href:
            it["item"] = SITE["url"] + "/" + href
        items.append(it)
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items}


# ------------------------------------------------------------------ components
def card(a, root, variant="", sizes="(min-width: 980px) 380px, (min-width: 600px) 50vw, 100vw", eager=False, show_dek=True):
    c = CAT[a["cat"]]
    url = "%sarticulos/%s.html" % (root, a["slug"])
    if variant == "row":
        return f"""<article class="card card--row" data-cat="{a['cat']}">
  {picture(a['image'], sizes='150px', w=400, ratio=(1, 1), fallback=c['name'], cat=a['cat'], link=url, alt='')}
  <div class="card__body">
    <div class="card__meta"><a class="chip" data-cat="{a['cat']}" href="{root}categoria/{c['slug']}.html">{e(c['name'])}</a><span>{a['read']} min</span></div>
    <h3 class="card__title"><a href="{url}">{e(a['title'])}</a></h3>
  </div>
</article>"""
    lead = variant == "lead"
    tag = "h2" if lead else "h3"
    return f"""<article class="card{' card--lead' if lead else ''}" data-cat="{a['cat']}" data-date="{a['date'].isoformat()}" data-read="{a['read']}">
  {picture(a['image'], sizes=sizes, w=1200 if lead else 900, ratio=(16, 11) if lead else (3, 2), eager=eager, fallback=c['name'], cat=a['cat'], link=url)}
  <div class="card__meta"><a class="chip" data-cat="{a['cat']}" href="{root}categoria/{c['slug']}.html">{e(c['name'])}</a><time datetime="{a['date'].isoformat()}">{fdate(a['date'], True)}</time></div>
  <{tag} class="card__title"><a href="{url}">{e(a['title'])}</a></{tag}>
  {('<p class="card__dek">%s</p>' % e(a['dek'])) if show_dek else ''}
  <div class="card__foot"><span>{a['read']} min de lectura</span><span class="card__read">Leer {ICON['arrow']}</span></div>
</article>"""


def newsletter(root):
    return ""


def share_bar(a, cls=""):
    url = "%s/articulos/%s.html" % (SITE["url"], a["slug"])
    u = e(url.replace(":", "%3A").replace("/", "%2F"))
    t = e(a["title"].replace(" ", "%20"))
    return f"""<div class="share {cls}" aria-label="Compartir">
  <span>Compartir</span>
  <a href="https://twitter.com/intent/tweet?url={u}&amp;text={t}" target="_blank" rel="noopener" aria-label="Compartir en X">{ICON['x']}<span class="visually-hidden">X</span></a>
  <a href="https://www.facebook.com/sharer/sharer.php?u={u}" target="_blank" rel="noopener" aria-label="Compartir en Facebook">{ICON['fb']}<span class="visually-hidden">Facebook</span></a>
  <a href="https://api.whatsapp.com/send?text={t}%20{u}" target="_blank" rel="noopener" aria-label="Compartir en WhatsApp">{ICON['wa']}<span class="visually-hidden">WhatsApp</span></a>
  <a href="https://www.linkedin.com/sharing/share-offsite/?url={u}" target="_blank" rel="noopener" aria-label="Compartir en LinkedIn">{ICON['in']}<span class="visually-hidden">LinkedIn</span></a>
  <button type="button" data-copy-link data-url="{e(url)}">{ICON['link']}<span>Copiar enlace</span></button>
</div>"""


# ------------------------------------------------------------------ pages
def build_article(a, articles, by_slug, prev_a, next_a):
    root = "../"
    c = CAT[a["cat"]]
    body_html, toc = render_body(a, by_slug, root)
    related = [by_slug[s] for s in a["related"] if s in by_slug][:3]
    if len(related) < 3:
        extra = [x for x in articles if x["cat"] == a["cat"] and x["slug"] != a["slug"] and x not in related]
        extra += [x for x in articles if x["slug"] != a["slug"] and x not in related and x not in extra]
        related += extra[: 3 - len(related)]
    more_cat = [x for x in articles if x["cat"] == a["cat"] and x["slug"] != a["slug"]][:4]
    if not more_cat:
        more_cat = [x for x in articles if x["slug"] != a["slug"]][:4]
    canonical = "%s/articulos/%s.html" % (SITE["url"], a["slug"])
    trail = [("Inicio", "index.html"), (c["name"], "categoria/%s.html" % c["slug"]), (a["title"], None)]
    ld = [{
        "@context": "https://schema.org", "@type": "Article", "headline": a["title"], "description": a["dek"],
        "image": [img_url(a["image"], 1600, 900)], "datePublished": a["date"].isoformat(),
        "dateModified": (a["updated"] or a["date"].isoformat()),
        "author": {"@type": "Organization", "name": SITE["author"], "url": SITE["url"] + "/sobre-nosotros.html"},
        "publisher": {"@type": "Organization", "name": SITE["name"], "logo": {"@type": "ImageObject", "url": SITE["url"] + "/favicon.svg"}},
        "mainEntityOfPage": canonical, "articleSection": c["name"], "inLanguage": SITE["lang"], "wordCount": a["words"],
    }, breadcrumb_ld(trail)]
    toc_html = "".join('<li><a href="#%s">%s</a></li>' % (hid, e(t)) for hid, t in toc if hid != "fuentes")
    more_html = "".join('<li><a href="%s.html">%s</a></li>' % (x["slug"], e(x["title"])) for x in more_cat)
    pager = '<nav class="pager" aria-label="Más artículos">'
    pager += ('<a class="prev" href="%s.html"><span>← Anterior</span><strong>%s</strong></a>' % (prev_a["slug"], e(prev_a["title"]))) if prev_a else "<span></span>"
    pager += ('<a class="next" href="%s.html"><span>Siguiente →</span><strong>%s</strong></a>' % (next_a["slug"], e(next_a["title"]))) if next_a else "<span></span>"
    pager += "</nav>"
    hero_img = picture(a["image"], cls="media", sizes="(min-width: 1240px) 1180px, 100vw", w=1600, ratio=(21, 10), eager=True, fallback=c["name"], cat=a["cat"])
    body = f"""<div class="progress" role="progressbar" aria-label="Progreso de lectura" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0"><div class="progress__bar"></div></div>
<article>
  <div class="wrap">
    <header class="article-head">
      {breadcrumbs(root, trail)}
      <a class="chip enter" data-cat="{a['cat']}" href="{root}categoria/{c['slug']}.html">{e(c['name'])}</a>
      <h1 class="enter enter-2">{e(a['title'])}</h1>
      <p class="dek enter enter-3">{e(a['dek'])}</p>
      <div class="byline enter enter-4">
        <span class="byline__who"><span class="avatar" aria-hidden="true">{SITE['author_initials']}</span><span>Por <strong>{e(SITE['author'])}</strong></span></span>
        <span><time datetime="{a['date'].isoformat()}">{fdate(a['date'])}</time></span>
        <span>{a['read']} min de lectura</span>
      </div>
    </header>
    <figure class="article-hero enter-fade">
      {hero_img}
      <figcaption>{e(IMAGES[a['image']][1])}. {credit(a['image'])}</figcaption>
    </figure>
    <div class="article-layout">
      <div>
        {share_bar(a)}
        <div class="prose" data-article-body style="margin-top:2em">
          {body_html}
        </div>
        <div class="tags">{''.join('<span class="chip chip--plain">%s</span>' % e(k.strip()) for k in a['keywords'].split(',')[:5] if k.strip())}</div>
        {share_bar(a, 'share--end')}
      </div>
      <aside class="article-aside" aria-label="Navegación del artículo">
        {('<nav class="toc" aria-label="En este artículo"><h2>En este artículo</h2><ol>%s</ol></nav>' % toc_html) if toc_html else ''}
        <div class="ad-slot ad-slot--aside" data-slot="article-aside" aria-hidden="true"></div>
        <div class="aside-more"><h2>Más de {e(c['name'])}</h2><ul>{more_html}</ul></div>
      </aside>
    </div>
  </div>
</article>
<section class="section"><div class="wrap">
  <div class="section__head"><div><p class="eyebrow">Sigue leyendo</p><h2 class="section__title">También te puede interesar</h2></div></div>
  <div class="grid grid--3 reveal-stagger">{''.join(card(x, root) for x in related)}</div>
  <div style="margin-top:48px">{pager}</div>
</div></section>"""
    return page(root, "articulos", a["title"], a["dek"], canonical, body,
                og_image=img_url(a["image"], 1200, 630), og_type="article", jsonld=ld,
                extra='<meta property="article:published_time" content="%s">\n<meta property="article:section" content="%s">\n' % (a["date"].isoformat(), e(c["name"])))


def build_home(articles, facts):
    root = ""
    featured = [a for a in articles if a["featured"]][:4]
    if len(featured) < 4:
        featured += [a for a in articles if a not in featured][: 4 - len(featured)]
    lead, side = featured[0], featured[1:4]
    latest = [a for a in articles if a not in featured][:6]
    longreads = sorted([a for a in articles if a not in featured and a not in latest], key=lambda x: -x["read"])[:3]
    counts = {s: sum(1 for a in articles if a["cat"] == s) for s in CAT}
    avg = round(sum(a["read"] for a in articles) / len(articles))
    f0 = facts[0]
    chips = "".join('<a class="chip" data-cat="%s" href="categoria/%s.html">%s <small>%d</small></a>' % (s, s, e(CAT[s]["name"]), counts[s]) for s in CAT)
    tiles = "".join('<a class="cat-tile" data-cat="%s" href="categoria/%s.html"><h3>%s</h3><p>%s</p><span>%d artículos</span></a>' % (
        s, s, e(CAT[s]["name"]), e(CAT[s]["desc"]), counts[s]) for s in CAT)
    ld = {"@context": "https://schema.org", "@type": "WebSite", "name": SITE["name"], "url": SITE["url"] + "/",
          "description": SITE["description"], "inLanguage": SITE["lang"],
          "potentialAction": {"@type": "SearchAction", "target": SITE["url"] + "/buscar.html?q={search_term_string}", "query-input": "required name=search_term_string"}}
    body = f"""<section class="hero"><div class="wrap hero__grid">
  <div>
    <div class="hero__kicker enter"><span class="rule" aria-hidden="true"></span><span class="eyebrow">{e(SITE['tagline'])}</span></div>
    <h1 class="hero__title enter enter-2">Descubre algo <span class="mark-anim">nuevo</span> cada día</h1>
    <p class="hero__lead enter enter-3">Historias, ciencia, tecnología, curiosidades y conocimientos que merece la pena descubrir. Artículos originales, contrastados y escritos para leerse con calma.</p>
    <div class="hero__actions enter enter-4">
      <a class="btn" href="articulos.html">Explorar artículos {ICON['arrow']}</a>
      <a class="btn btn--ghost" href="categorias.html">Ver categorías</a>
    </div>
    <div class="hero__stats enter enter-5">
      <div><strong>{len(articles)}</strong><span>artículos publicados</span></div>
      <div><strong>{len(CAT)}</strong><span>categorías</span></div>
      <div><strong>{avg} min</strong><span>de lectura media</span></div>
    </div>
  </div>
  <figure class="hero__figure enter-fade">
    {picture('hero', cls='media parallax', sizes='(min-width: 860px) 45vw, 100vw', w=1200, ratio=(4, 5), eager=True, fallback='Mente Abierta')}
    <a class="hero__badge" href="articulos/{f0['u'].split('/')[-1]}" style="text-decoration:none"><b>¿Sabías que…?</b>{e(f0['t'])}</a>
    <figcaption><span>El conocimiento empieza con una pregunta.</span><span>{credit('hero')}</span></figcaption>
  </figure>
</div></section>

<section class="section--tight"><div class="wrap">
  <div class="section__head"><div><p class="eyebrow">Selección de la redacción</p><h2 class="section__title">Artículos destacados</h2></div>
  <a class="link-arrow" href="articulos.html">Todos los artículos {ICON['arrow']}</a></div>
  <div class="featured">
    {card(lead, root, 'lead', sizes='(min-width: 900px) 58vw, 100vw')}
    <div class="featured__side reveal-stagger">{''.join(card(x, root, 'row') for x in side)}</div>
  </div>
</div></section>

<section class="section--tight"><div class="wrap">
  <p class="eyebrow" style="margin-bottom:14px">Explora por tema</p>
  <nav class="cat-strip" aria-label="Categorías">{chips}</nav>
</div></section>

<section class="section"><div class="wrap">
  <div class="section__head"><div><p class="eyebrow">Recién publicado</p><h2 class="section__title">Últimos artículos</h2></div></div>
  <div class="grid grid--3 reveal-stagger">{''.join(card(x, root) for x in latest)}</div>
  <div style="margin-top:40px;text-align:center"><a class="btn btn--ghost" href="articulos.html">Ver más artículos {ICON['arrow']}</a></div>
</div></section>

<div class="wrap"><div class="ad-slot ad-slot--leader" data-slot="home-mid" aria-hidden="true"></div></div>

<section class="section--tight"><div class="wrap">
  <div class="fact-band reveal" data-fact>
    <div><p class="eyebrow">El dato del día</p><div class="fact-band__num">{e(f0['n'])}</div></div>
    <div><p class="fact-band__text">{e(f0['t'])}</p><a class="link-arrow" href="{f0['u']}"><span>Leer: {e(f0['a'])}</span> {ICON['arrow']}</a></div>
  </div>
  <script type="application/json" id="facts-data">{json.dumps(facts, ensure_ascii=False)}</script>
</div></section>

<section class="section"><div class="wrap">
  <div class="section__head"><div><p class="eyebrow">Once secciones</p><h2 class="section__title">Explora por categorías</h2><p class="section__sub">Cada sección reúne artículos sobre un mismo tipo de pregunta. Empieza por la que más te llame.</p></div></div>
  <div class="cat-tiles reveal-stagger">{tiles}</div>
</div></section>

<section class="section section--alt"><div class="wrap">
  <div class="section__head"><div><p class="eyebrow">Para leer con calma</p><h2 class="section__title">Lecturas largas del fin de semana</h2></div></div>
  <div class="grid grid--3 reveal-stagger">{''.join(card(x, root) for x in longreads)}</div>
</div></section>
"""
    return page(root, "inicio", SITE["name"] + " · " + SITE["tagline"], SITE["description"], SITE["url"] + "/", body, jsonld=ld)


def build_articles_page(articles):
    root = ""
    counts = {s: sum(1 for a in articles if a["cat"] == s) for s in CAT}
    chips = '<button class="chip chip--plain" type="button" data-filter="todas" aria-pressed="true">Todas <small>%d</small></button>' % len(articles)
    chips += "".join('<button class="chip" type="button" data-cat="%s" data-filter="%s" aria-pressed="false">%s <small>%d</small></button>' % (s, s, e(CAT[s]["name"]), counts[s]) for s in CAT)
    cards = []
    for i, a in enumerate(articles):
        cards.append(card(a, root))
        if i == 5:
            pass
    trail = [("Inicio", "index.html"), ("Artículos", None)]
    body = f"""<section class="page-head"><div class="wrap">
  {breadcrumbs(root, trail)}
  <h1 class="enter">Todos los artículos</h1>
  <p class="enter enter-2">{len(articles)} lecturas sobre ciencia, historia, tecnología, psicología y los rincones más sorprendentes del planeta. Filtra por tema o ordénalas a tu gusto.</p>
</div></section>
<section class="section--tight" style="padding-top:0"><div class="wrap">
  <div class="toolbar">
    <div class="cat-strip" role="group" aria-label="Filtrar por categoría">{chips}</div>
    <div style="display:flex;gap:12px;align-items:center">
      <span class="toolbar__count" aria-live="polite">{len(articles)} artículos</span>
      <label class="visually-hidden" for="sort">Ordenar</label>
      <select class="select" id="sort"><option value="recientes">Más recientes</option><option value="cortos">Lectura corta primero</option><option value="largos">Lectura larga primero</option></select>
    </div>
  </div>
  <div class="grid grid--3" data-listing>{''.join(cards)}</div>
  <div class="ad-slot" data-slot="listing" aria-hidden="true"></div>
</div></section>"""
    return page(root, "articulos", "Todos los artículos", "Biblioteca completa de Mente Abierta: artículos de curiosidades, ciencia, historia, tecnología, psicología, cultura y lugares sorprendentes.",
                SITE["url"] + "/articulos.html", body, jsonld=breadcrumb_ld(trail))


def build_categories_page(articles):
    root = ""
    blocks = []
    for s in CAT:
        items = [a for a in articles if a["cat"] == s]
        links = "".join('<li><a href="articulos/%s.html">%s</a></li>' % (a["slug"], e(a["title"])) for a in items[:3])
        blocks.append(f"""<a class="cat-tile" data-cat="{s}" href="categoria/{s}.html"><h3>{e(CAT[s]['name'])}</h3><p>{e(CAT[s]['desc'])}</p><span>{len(items)} artículos · Ver sección →</span></a>""")
    trail = [("Inicio", "index.html"), ("Categorías", None)]
    body = f"""<section class="page-head"><div class="wrap">
  {breadcrumbs(root, trail)}
  <h1 class="enter">Categorías</h1>
  <p class="enter enter-2">Once secciones para explorar el mundo a tu ritmo. Cada una agrupa artículos que responden a un mismo tipo de curiosidad.</p>
</div></section>
<section class="section--tight" style="padding-top:0"><div class="wrap"><div class="cat-tiles reveal-stagger">{''.join(blocks)}</div></div></section>
<section class="section"><div class="wrap">
  <div class="section__head"><div><p class="eyebrow">Para empezar</p><h2 class="section__title">Lo último de la revista</h2></div></div>
  <div class="grid grid--3 reveal-stagger">{''.join(card(a, root) for a in articles[:3])}</div>
</div></section>"""
    return page(root, "categorias", "Categorías", "Explora Mente Abierta por secciones: curiosidades, tecnología, ciencia, historia, mundo, psicología, cultura, lugares sorprendentes, inventos, misterios históricos y datos interesantes.",
                SITE["url"] + "/categorias.html", body, jsonld=breadcrumb_ld(trail))


def build_category(slug, articles):
    root = "../"
    c = CAT[slug]
    items = [a for a in articles if a["cat"] == slug]
    others = "".join('<a class="chip" data-cat="%s" href="%s.html">%s</a>' % (s, s, e(CAT[s]["name"])) for s in CAT if s != slug)
    suggestions = [a for a in articles if a["cat"] != slug][:3]
    trail = [("Inicio", "index.html"), ("Categorías", "categorias.html"), (c["name"], None)]
    body = f"""<section class="page-head" data-cat="{slug}"><div class="wrap">
  {breadcrumbs(root, trail)}
  <span class="chip enter" data-cat="{slug}">Sección</span>
  <h1 class="enter enter-2" style="margin-top:14px">{e(c['name'])}</h1>
  <p class="enter enter-3">{e(c['desc'])}</p>
</div></section>
<section class="section--tight" style="padding-top:0"><div class="wrap">
  <div class="toolbar"><span class="toolbar__count">{len(items)} {'artículo' if len(items) == 1 else 'artículos'}</span></div>
  <div class="grid grid--3 reveal-stagger">{''.join(card(a, root) for a in items)}</div>
  <div class="ad-slot" data-slot="listing" aria-hidden="true"></div>
</div></section>
<section class="section"><div class="wrap">
  <div class="section__head"><div><p class="eyebrow">Cambia de tema</p><h2 class="section__title">Más artículos</h2></div></div>
  <div class="grid grid--3 reveal-stagger">{''.join(card(a, root) for a in suggestions)}</div>
  <p class="eyebrow" style="margin:48px 0 14px">Otras categorías</p>
  <nav class="cat-strip" aria-label="Otras categorías">{others}</nav>
</div></section>"""
    return page(root, "categorias", c["name"], "%s Artículos de la sección %s en Mente Abierta." % (c["desc"], c["name"]),
                "%s/categoria/%s.html" % (SITE["url"], slug), body, jsonld=breadcrumb_ld(trail))


def build_search_page():
    root = ""
    trail = [("Inicio", "index.html"), ("Buscar", None)]
    body = f"""<section class="page-head"><div class="wrap" data-search-page>
  {breadcrumbs(root, trail)}
  <h1>Buscar</h1>
  <form role="search" style="margin-top:24px;max-width:640px">
    <div class="form-row">
      <label class="visually-hidden" for="q">Buscar artículos</label>
      <input class="input" id="q" name="q" type="search" placeholder="Por ejemplo: Venus, memoria, Egipto…" autocomplete="off">
      <button class="btn" type="submit">{ICON['search']} Buscar</button>
    </div>
  </form>
  <div class="toolbar" style="margin-top:32px"><span class="toolbar__count" aria-live="polite"></span></div>
  <div class="search-list grid" style="gap:28px"></div>
  <noscript><p>El buscador necesita JavaScript. Puedes explorar todos los artículos en <a href="articulos.html">la biblioteca</a>.</p></noscript>
</div></section>"""
    return page(root, "", "Buscar", "Busca entre todos los artículos de Mente Abierta.", SITE["url"] + "/buscar.html", body, noindex=True)


def build_static(fname, articles):
    raw = open(os.path.join(CONTENT, "paginas", fname), encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.S)
    meta = dict((k.strip(), v.strip()) for k, v in (l.split(":", 1) for l in m.group(1).splitlines() if ":" in l))
    content = fill_owner(m.group(2))
    content = content.replace("{{EMAIL_RAW}}", e(OWNER.get("EMAIL", "")))
    content = content.replace("{{SITE_URL}}", e(SITE["url"])).replace("{{SITE_NAME}}", e(SITE["name"]))
    content = content.replace("{{N_ARTICLES}}", str(len(articles))).replace("{{N_CATS}}", str(len(CAT)))
    if "{{IMAGE_CREDITS}}" in content:
        rows = []
        used = {}
        for a in articles:
            used.setdefault(a["image"], a)
            for k in re.findall(r"^!fig\s+([\w\-]+)", a["src"], re.M):
                used.setdefault(k, a)
        for k, a in used.items():
            _, alt, author, url = IMAGES[k]
            rows.append('<tr><td><a href="articulos/%s.html">%s</a></td><td>%s</td><td><a href="%s" rel="noopener" target="_blank">%s</a></td></tr>' % (
                a["slug"], e(a["title"]), e(alt), e(url), e(author)))
        _, alt, author, url = IMAGES["hero"]
        rows.insert(0, '<tr><td><a href="index.html">Portada</a></td><td>%s</td><td><a href="%s" rel="noopener" target="_blank">%s</a></td></tr>' % (e(alt), e(url), e(author)))
        content = content.replace("{{IMAGE_CREDITS}}", '<div class="table-wrap"><table class="prose" style="max-width:none"><thead><tr><th>Dónde se usa</th><th>Imagen</th><th>Autor</th></tr></thead><tbody>%s</tbody></table></div>' % "".join(rows))
    trail = [("Inicio", "index.html"), (meta["title"], None)]
    active = meta.get("nav", "")
    wide = meta.get("layout", "") == "wide"
    body = f"""<section class="page-head"><div class="wrap">
  {breadcrumbs('', trail)}
  <h1 class="enter">{e(meta['h1'] if 'h1' in meta else meta['title'])}</h1>
  {('<p class="enter enter-2">%s</p>' % e(meta['lead'])) if meta.get('lead') else ''}
</div></section>
<section class="section--tight" style="padding-top:0"><div class="wrap"><div class="{'' if wide else 'doc'}">{content}</div></div></section>"""
    return page("", active, meta["title"], meta["description"], "%s/%s" % (SITE["url"], fname), body,
                jsonld=breadcrumb_ld(trail), noindex=meta.get("noindex") == "true")


def build_404(articles):
    body = f"""<section class="notfound"><div class="wrap">
  <p class="big" aria-hidden="true">404</p>
  <h1 style="font-size:var(--step-3);margin-top:16px">Esta página no existe (o se ha perdido como la Biblioteca de Alejandría)</h1>
  <p style="margin-top:14px;color:var(--ink-2);max-width:56ch">Puede que el enlace esté mal escrito o que el artículo haya cambiado de dirección. Prueba a buscarlo o vuelve a la portada.</p>
  <div class="hero__actions"><button class="btn" type="button" data-open-search>{ICON['search']} Buscar un artículo</button><a class="btn btn--ghost" href="/index.html">Ir a la portada</a></div>
</div></section>
<section class="section"><div class="wrap"><div class="section__head"><h2 class="section__title">Quizá buscabas…</h2></div>
<div class="grid grid--3">{''.join(card(a, '/') for a in articles[:3])}</div></div></section>"""
    return page("/", "", "Página no encontrada", "La página que buscas no existe.", SITE["url"] + "/404.html", body, noindex=True)


# ------------------------------------------------------------------ main
def main():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(os.path.join(OUT, "articulos"))
    os.makedirs(os.path.join(OUT, "categoria"))
    shutil.copytree(os.path.join(BASE, "assets"), os.path.join(OUT, "assets"))

    adir = os.path.join(CONTENT, "articulos")
    articles = [parse_article(os.path.join(adir, f)) for f in sorted(os.listdir(adir)) if f.endswith(".md")]
    articles.sort(key=lambda a: (a["date"], a["slug"]), reverse=True)
    by_slug = {a["slug"]: a for a in articles}
    for a in articles:
        if a["cat"] not in CAT:
            raise SystemExit("Categoría desconocida en %s" % a["slug"])
        if a["image"] not in IMAGES:
            raise SystemExit("Imagen desconocida en %s" % a["slug"])

    def w(rel, content):
        p = os.path.join(OUT, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(content)

    for i, a in enumerate(articles):
        prev_a = articles[i + 1] if i + 1 < len(articles) else None
        next_a = articles[i - 1] if i > 0 else None
        w("articulos/%s.html" % a["slug"], build_article(a, articles, by_slug, prev_a, next_a))

    facts = json.load(open(os.path.join(CONTENT, "datos-del-dia.json"), encoding="utf-8"))
    for f in facts:
        if f["u"].split("/")[-1].replace(".html", "") not in by_slug:
            raise SystemExit("Dato del día apunta a un artículo inexistente: " + f["u"])
    w("index.html", build_home(articles, facts))
    w("articulos.html", build_articles_page(articles))
    w("categorias.html", build_categories_page(articles))
    for s in CAT:
        w("categoria/%s.html" % s, build_category(s, articles))
    w("buscar.html", build_search_page())
    for fname in sorted(os.listdir(os.path.join(CONTENT, "paginas"))):
        if fname.endswith(".html"):
            w(fname, build_static(fname, articles))
    w("404.html", build_404(articles))
    w("favicon.svg", FAVICON)

    # search index
    idx = [{"t": a["title"], "d": a["dek"], "c": CAT[a["cat"]]["name"], "s": a["cat"], "k": a["keywords"],
            "u": "articulos/%s.html" % a["slug"], "i": img_url(a["image"], 200, 200), "r": a["read"],
            "b": plain_text(a)[:1800]} for a in articles]
    w("assets/js/search-index.js", "window.MA_INDEX=" + json.dumps(idx, ensure_ascii=False, separators=(",", ":")) + ";")

    # sitemap / robots / rss / ads.txt
    today = date.today().isoformat()
    urls = [("", today, "1.0"), ("articulos.html", today, "0.8"), ("categorias.html", today, "0.6")]
    urls += [("categoria/%s.html" % s, today, "0.6") for s in CAT]
    urls += [("articulos/%s.html" % a["slug"], a["updated"] or a["date"].isoformat(), "0.9") for a in articles]
    urls += [(p, today, "0.3") for p in ["sobre-nosotros.html", "contacto.html", "privacidad.html", "cookies.html", "aviso-legal.html", "terminos.html", "creditos-imagenes.html"]]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sm += "".join("  <url><loc>%s/%s</loc><lastmod>%s</lastmod><priority>%s</priority></url>\n" % (SITE["url"], u, d, p) for u, d, p in urls)
    sm += "</urlset>\n"
    w("sitemap.xml", sm)
    w("robots.txt", "User-agent: *\nAllow: /\nDisallow: /buscar.html\n\nSitemap: %s/sitemap.xml\n" % SITE["url"])
    w("ads.txt", "# Cuando Google apruebe tu cuenta, sustituye esta línea por la que te indique AdSense, por ejemplo:\n# google.com, pub-0000000000000000, DIRECT, f08c47fec0942fa0\n")
    items = "".join("""<item><title>%s</title><link>%s/articulos/%s.html</link><guid>%s/articulos/%s.html</guid><pubDate>%s</pubDate><category>%s</category><description>%s</description></item>\n""" % (
        e(a["title"]), SITE["url"], a["slug"], SITE["url"], a["slug"], a["date"].strftime("%a, %d %b %Y 08:00:00 +0200"), e(CAT[a["cat"]]["name"]), e(a["dek"])) for a in articles)
    w("feed.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel><title>%s</title><link>%s/</link><description>%s</description><language>es-es</language>\n%s</channel></rss>\n' % (
        e(SITE["name"]), SITE["url"], e(SITE["description"]), items))

    w(".htaccess", "ErrorDocument 404 /404.html\nAddDefaultCharset UTF-8\n<IfModule mod_expires.c>\nExpiresActive On\nExpiresByType text/css \"access plus 1 month\"\nExpiresByType application/javascript \"access plus 1 month\"\nExpiresByType image/svg+xml \"access plus 1 month\"\n</IfModule>\n")

    total_words = sum(a["words"] for a in articles)
    print("OK: %d artículos (%d palabras, media %d), %d categorías" % (len(articles), total_words, total_words // len(articles), len(CAT)))
    for a in articles:
        print("  %-38s %-22s %4d palabras  %2d min" % (a["slug"], a["cat"], a["words"], a["read"]))


if __name__ == "__main__":
    main()
