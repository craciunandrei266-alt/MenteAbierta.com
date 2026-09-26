# -*- coding: utf-8 -*-
"""
Crea MenteAbierta.html: TODA la web en un único archivo que se abre con doble clic
en cualquier navegador (Chrome, Edge, Firefox, Safari), sin descomprimir carpetas.
Uso:  python3 build.py && python3 bundle.py
"""
import base64
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
PUB = os.path.join(BASE, "public")
OUT = os.path.join(BASE, "MenteAbierta.html")


def read(rel):
    return open(os.path.join(PUB, rel), encoding="utf-8").read()


def page_parts(html):
    title = re.search(r"<title>(.*?)</title>", html, re.S).group(1)
    desc_m = re.search(r'<meta name="description" content="(.*?)">', html)
    main = re.search(r'<main id="main" tabindex="-1">\n?(.*)\n?</main>', html, re.S).group(1)
    return {"t": title, "d": desc_m.group(1) if desc_m else "", "m": main}


def main():
    pages = {}
    for dp, _, fs in os.walk(PUB):
        for f in fs:
            if f.endswith(".html"):
                rel = os.path.relpath(os.path.join(dp, f), PUB).replace(os.sep, "/")
                pages[rel] = page_parts(read(rel))

    shell = read("index.html")
    css = read("assets/css/styles.css")
    fav = "data:image/svg+xml;base64," + base64.b64encode(read("favicon.svg").encode()).decode()

    shell = re.sub(r'<link rel="stylesheet" href="assets/css/styles\.css[^"]*">', lambda m: "<style>\n" + css + "\n</style>", shell)
    shell = shell.replace('href="favicon.svg"', 'href="%s"' % fav)
    shell = re.sub(r'<link rel="alternate"[^>]*>\n', "", shell)

    def inline(name):
        return "<script>\n" + read("assets/js/" + name).replace("</script", "<\\/script") + "\n</script>"

    data = json.dumps(pages, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    router = ROUTER.replace("__PAGES__", data)
    scripts = "\n".join([inline("config.js"), inline("search-index.js"), "<script>window.MA_SPA=true;</script>", inline("main.js"), router])
    shell = re.sub(r'<script src="assets/js/config\.js[^"]*"></script>\n<script src="assets/js/search-index\.js[^"]*" defer></script>\n<script src="assets/js/main\.js[^"]*" defer></script>',
                   lambda m: scripts, shell)
    assert "assets/js/main.js" not in shell, "no se pudieron incrustar los scripts"
    open(OUT, "w", encoding="utf-8").write(shell)
    print("OK: %s (%d páginas, %.0f KB)" % (OUT, len(pages), os.path.getsize(OUT) / 1024))


ROUTER = r"""<script>
(function () {
  "use strict";
  var P = __PAGES__;
  var current = "index.html";
  var mainEl = document.getElementById("main");
  var metaDesc = document.querySelector('meta[name="description"]');

  function resolve(base, href) {
    if (!href || /^(https?:|mailto:|tel:|javascript:|data:|blob:)/i.test(href)) return null;
    var frag = "", q = "", i = href.indexOf("#");
    if (i > -1) { frag = href.slice(i + 1); href = href.slice(0, i); }
    i = href.indexOf("?");
    if (i > -1) { q = href.slice(i + 1); href = href.slice(0, i); }
    if (!href) return frag ? { key: current, frag: frag, q: "" , same: true } : null;
    var parts = href.charAt(0) === "/" ? href.slice(1).split("/") : base.split("/").slice(0, -1).concat(href.split("/"));
    var out = [];
    parts.forEach(function (p) { if (p === "..") out.pop(); else if (p && p !== ".") out.push(p); });
    var key = out.join("/") || "index.html";
    if (!P[key]) {
      var alt = href.replace(/^(\.\.\/)+/, "").replace(/^\//, "");
      key = P[alt] ? alt : (/\.html$/.test(key) ? "404.html" : null);
      if (!key) return null;
    }
    return { key: key, frag: frag, q: q };
  }

  function section(key) {
    if (key.indexOf("articulos/") === 0) return "articulos.html";
    if (key.indexOf("categoria/") === 0) return "categorias.html";
    return key;
  }

  function render(key, q, frag) {
    var pg = P[key] || P["404.html"];
    current = P[key] ? key : "404.html";
    if (window.MA_closeSearch) { var d = document.querySelector(".search-dialog"); if (d && d.classList.contains("is-open")) window.MA_closeSearch(true); }
    if (window.MA_closeMenu) window.MA_closeMenu();
    mainEl.innerHTML = pg.m;
    document.title = pg.t.replace(/&amp;/g, "&").replace(/&quot;/g, '"').replace(/&#x27;/g, "'");
    if (metaDesc) metaDesc.setAttribute("content", pg.d);
    var sec = section(current);
    Array.prototype.forEach.call(document.querySelectorAll(".nav__link"), function (a) {
      var r = resolve("index.html", a.getAttribute("href"));
      if (r && r.key === sec) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current");
    });
    window.MA_ROUTE_QUERY = null;
    if (q) { var m = /(?:^|&)q=([^&]*)/.exec(q); window.MA_ROUTE_QUERY = m ? decodeURIComponent(m[1].replace(/\+/g, " ")) : ""; }
    var target = frag && document.getElementById(frag);
    if (target) target.scrollIntoView(); else window.scrollTo(0, 0);
    if (window.MA_initPage) window.MA_initPage();
  }

  function go(r) {
    var h = "#/" + r.key + (r.q ? "?" + r.q : "");
    if (location.hash === h) render(r.key, r.q, r.frag);
    else location.hash = h;
  }

  function fromHash() {
    var h = location.hash;
    if (h.indexOf("#/") !== 0) { if (current !== "index.html") render("index.html"); return; }
    var r = resolve("index.html", h.slice(2));
    if (r) render(r.key, r.q, r.frag);
  }

  document.addEventListener("click", function (e) {
    if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    var a = e.target.closest ? e.target.closest("a[href]") : null;
    if (!a || a.target === "_blank") return;
    var base = a.closest("#main") ? current : "index.html";
    var r = resolve(base, a.getAttribute("href"));
    if (!r) return;
    e.preventDefault();
    if (r.same) { var t = document.getElementById(r.frag); if (t) t.scrollIntoView({ behavior: "smooth" }); return; }
    go(r);
  });

  var dialogForm = document.querySelector(".search-panel form");
  if (dialogForm) dialogForm.addEventListener("submit", function (e) {
    e.preventDefault();
    var v = (document.getElementById("search-input") || {}).value || "";
    go({ key: "buscar.html", q: "q=" + encodeURIComponent(v) });
  });

  window.addEventListener("hashchange", fromHash);
  if (location.hash.indexOf("#/") === 0) fromHash();
})();
</script>"""

if __name__ == "__main__":
    main()
