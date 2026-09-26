/* =========================================================
   Mente Abierta — interacción del sitio
   Sin dependencias. Respeta prefers-reduced-motion.
   setupGlobal() se ejecuta una vez; initPage() en cada página
   (también en la versión de archivo único, que cambia de página sin recargar).
   ========================================================= */
(function () {
  "use strict";

  var doc = document.documentElement;
  var CFG = window.MA_CONFIG || {};
  var ROOT = doc.getAttribute("data-root") || "";
  var reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function $(sel, ctx) { return (ctx || document).querySelector(sel); }
  function $$(sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); }
  function store(key, val) {
    try {
      if (val === undefined) return window.localStorage.getItem(key);
      if (val === null) window.localStorage.removeItem(key); else window.localStorage.setItem(key, val);
    } catch (e) { return null; }
  }
  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }
  function norm(s) { return String(s || "").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, ""); }

  /* Page-level state used by the global scroll handler */
  var progress = null, article = null, parallax = [];
  var revealIO = null, tocIO = null;

  /* ======================================================================
     GLOBAL (once)
     ====================================================================== */
  var header = $(".site-header");
  var menuBtn = $(".menu-toggle");
  var nav = $("#site-nav");
  var toTop = $(".to-top");

  function closeMenu() {
    if (!nav) return;
    nav.classList.remove("is-open");
    if (menuBtn) menuBtn.setAttribute("aria-expanded", "false");
  }

  function setupGlobal() {
    /* Theme toggle */
    var themeBtn = $(".theme-toggle");
    if (themeBtn) {
      themeBtn.addEventListener("click", function () {
        var current = doc.getAttribute("data-theme");
        if (!current) current = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
        var next = current === "dark" ? "light" : "dark";
        doc.setAttribute("data-theme", next);
        store("ma_theme", next);
        themeBtn.setAttribute("aria-label", next === "dark" ? "Cambiar a modo claro" : "Cambiar a modo oscuro");
      });
    }

    /* Mobile menu */
    if (menuBtn && nav) {
      menuBtn.addEventListener("click", function () {
        var open = !nav.classList.contains("is-open");
        nav.classList.toggle("is-open", open);
        menuBtn.setAttribute("aria-expanded", String(open));
      });
      $$("a", nav).forEach(function (a) { a.addEventListener("click", closeMenu); });
    }

    /* Scroll-driven UI */
    var ticking = false;
    window.addEventListener("scroll", function () { if (!ticking) { ticking = true; window.requestAnimationFrame(onScroll); } }, { passive: true });
    window.addEventListener("resize", onScroll);
    function onScrollWrap() { ticking = false; }
    function onScroll() {
      var y = window.scrollY || window.pageYOffset;
      if (header) header.classList.toggle("is-scrolled", y > 8);
      if (toTop) toTop.classList.toggle("is-visible", y > 900);
      if (progress && article && document.body.contains(article)) {
        var r = article.getBoundingClientRect();
        var total = r.height - window.innerHeight * .6;
        var done = Math.min(1, Math.max(0, (-r.top + window.innerHeight * .2) / (total > 0 ? total : 1)));
        progress.style.transform = "scaleX(" + done.toFixed(4) + ")";
        progress.parentNode.setAttribute("aria-valuenow", Math.round(done * 100));
      }
      parallax.forEach(function (el) {
        var speed = parseFloat(el.getAttribute("data-parallax")) || .06;
        var rect = el.parentNode.getBoundingClientRect();
        if (rect.bottom < 0 || rect.top > window.innerHeight) return;
        el.style.transform = "translate3d(0," + (rect.top * -speed).toFixed(1) + "px,0) scale(1.08)";
      });
      onScrollWrap();
    }
    window.MA_onScroll = onScroll;

    if (toTop) toTop.addEventListener("click", function () {
      window.scrollTo({ top: 0, behavior: reduceMotion ? "auto" : "smooth" });
      var target = $("#main"); if (target) target.focus({ preventScroll: true });
    });

    /* Delegated buttons (work on any page, now or later) */
    document.addEventListener("click", function (e) {
      var t = e.target.closest ? e.target.closest("[data-open-search],[data-open-cookies],[data-copy-link],[data-copy-text]") : null;
      if (!t) return;
      if (t.hasAttribute("data-open-search")) { openSearch(); return; }
      if (t.hasAttribute("data-open-cookies")) { openCookies(); return; }
      if (t.hasAttribute("data-copy-link")) {
        var url = t.getAttribute("data-url") || window.location.href;
        var label = t.querySelector("span");
        var done = function (ok) { if (label) { var tx = label.textContent; label.textContent = ok ? "Enlace copiado" : "Copia la URL del navegador"; setTimeout(function () { label.textContent = tx; }, 2200); } };
        if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(url).then(function () { done(true); }, function () { done(false); });
        else done(false);
        return;
      }
      if (t.hasAttribute("data-copy-text")) {
        var text = t.getAttribute("data-copy-text");
        if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(function () { t.textContent = "Copiado"; }, function () { t.textContent = "Selecciona y copia"; });
      }
    });

    /* Keyboard */
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") { closeMenu(); if (dialog && dialog.classList.contains("is-open")) closeSearch(); }
      var tag = (document.activeElement && document.activeElement.tagName) || "";
      if (e.key === "/" && !/INPUT|TEXTAREA|SELECT/.test(tag)) { e.preventDefault(); openSearch(); }
    });

    /* Search dialog */
    if (dialog) {
      dialog.addEventListener("click", function (e) { if (e.target === dialog) closeSearch(); });
      $$("[data-close-search]", dialog).forEach(function (b) { b.addEventListener("click", closeSearch); });
      sInput.addEventListener("input", function () { renderDialog(sInput.value); });
      dialog.addEventListener("click", function (e) { if (e.target.closest && e.target.closest("a.result")) closeSearch(true); });
    }

    /* Cookie banner */
    if (banner && CFG.useOwnCookieBanner !== false) {
      if (!readConsent()) showBanner();
      banner.addEventListener("click", function (e) {
        var act = e.target.closest("[data-consent]");
        if (!act) return;
        var v = act.getAttribute("data-consent");
        var prefs = $(".cookie__prefs", banner);
        if (v === "config") { prefs.hidden = !prefs.hidden; return; }
        var adsBox = $("#consent-ads");
        if (v === "all") saveConsent(true);
        if (v === "none") saveConsent(false);
        if (v === "save") saveConsent(adsBox && adsBox.checked);
        hideBanner();
        loadAds();
      });
    }

    $$("[data-year]").forEach(function (el) { el.textContent = new Date().getFullYear(); });
  }

  /* ---------- Search ---------- */
  var dialog = $(".search-dialog");
  var sInput = $("#search-input");
  var sResults = $(".search-results");
  var lastFocus = null;

  function searchIndex(q) {
    var data = window.MA_INDEX || [];
    var terms = norm(q).split(/\s+/).filter(function (t) { return t.length > 1; });
    if (!terms.length) return [];
    var out = [];
    data.forEach(function (it) {
      var title = norm(it.t), dek = norm(it.d), cat = norm(it.c), kw = norm(it.k), body = norm(it.b || "");
      var score = 0, all = true;
      terms.forEach(function (t) {
        var s = 0;
        if (title.indexOf(t) > -1) s += 6;
        if (kw.indexOf(t) > -1) s += 4;
        if (cat.indexOf(t) > -1) s += 3;
        if (dek.indexOf(t) > -1) s += 2;
        if (body.indexOf(t) > -1) s += 1;
        if (!s) all = false;
        score += s;
      });
      if (all && score) out.push({ it: it, score: score });
    });
    out.sort(function (a, b) { return b.score - a.score; });
    return out.map(function (o) { return o.it; });
  }
  function highlight(text, q) {
    var safe = esc(text);
    norm(q).split(/\s+/).filter(function (t) { return t.length > 1; }).forEach(function (t) {
      var n = norm(safe), idx = n.indexOf(t);
      if (idx > -1) safe = safe.slice(0, idx) + "<mark>" + safe.slice(idx, idx + t.length) + "</mark>" + safe.slice(idx + t.length);
    });
    return safe;
  }
  function resultRow(it, q) {
    return '<a class="result" href="' + ROOT + it.u + '"><div class="media" data-cat="' + esc(it.s) + '"><img src="' + esc(it.i) + '" alt="" loading="lazy" width="64" height="64"></div>' +
      '<div><strong>' + (q ? highlight(it.t, q) : esc(it.t)) + '</strong><small>' + esc(it.c) + ' · ' + esc(it.r) + ' min de lectura</small></div></a>';
  }
  function renderDialog(q) {
    if (!sResults) return;
    if (!q.trim()) {
      var picks = (window.MA_INDEX || []).slice(0, 5);
      sResults.innerHTML = '<p class="search-empty">Sugerencias para empezar</p>' + picks.map(function (it) { return resultRow(it); }).join("");
      return;
    }
    var res = searchIndex(q).slice(0, 8);
    if (!res.length) {
      sResults.innerHTML = '<p class="search-empty">No hay artículos que coincidan con «' + esc(q) + '». Prueba con otra palabra, como «historia» o «cerebro».</p>';
      return;
    }
    sResults.innerHTML = res.map(function (it) { return resultRow(it, q); }).join("") +
      '<a class="result" href="' + ROOT + 'buscar.html?q=' + encodeURIComponent(q) + '"><span></span><strong>Ver todos los resultados →</strong></a>';
  }
  function openSearch() {
    if (!dialog) return;
    lastFocus = document.activeElement;
    dialog.hidden = false;
    requestAnimationFrame(function () { dialog.classList.add("is-open"); });
    renderDialog(sInput.value || "");
    setTimeout(function () { sInput.focus(); }, 30);
    document.body.style.overflow = "hidden";
  }
  function closeSearch(skipFocus) {
    if (!dialog) return;
    dialog.classList.remove("is-open");
    document.body.style.overflow = "";
    setTimeout(function () { dialog.hidden = true; }, 260);
    if (lastFocus && skipFocus !== true) lastFocus.focus();
  }
  window.MA_closeSearch = closeSearch;
  window.MA_closeMenu = closeMenu;

  /* ---------- Cookies + AdSense ---------- */
  var CONSENT_KEY = "ma_consent_v1";
  var banner = $(".cookie");
  function readConsent() { try { return JSON.parse(store(CONSENT_KEY) || "null"); } catch (e) { return null; } }
  function saveConsent(ads) { store(CONSENT_KEY, JSON.stringify({ ads: !!ads, date: new Date().toISOString() })); }
  function showBanner() { if (banner) banner.hidden = false; }
  function hideBanner() { if (banner) banner.hidden = true; }
  function openCookies() {
    if (!banner) return;
    var c = readConsent(); var box = $("#consent-ads");
    if (box && c) box.checked = !!c.ads;
    showBanner(); var p = $(".cookie__prefs", banner); if (p) p.hidden = false;
  }
  var adsScriptLoaded = false;
  function loadAds() {
    if (!CFG.adsEnabled || !CFG.adsenseClient || /X{6,}/.test(CFG.adsenseClient)) return;
    var slots = $$(".ad-slot").filter(function (s) { return (CFG.adSlots || {})[s.getAttribute("data-slot")] && !s.querySelector("ins"); });
    if (!slots.length) return;
    doc.classList.add("ads-on");
    var consent = readConsent();
    window.adsbygoogle = window.adsbygoogle || [];
    if (!consent || !consent.ads) window.adsbygoogle.requestNonPersonalizedAds = 1;
    if (!adsScriptLoaded) {
      adsScriptLoaded = true;
      var s = document.createElement("script");
      s.async = true; s.crossOrigin = "anonymous";
      s.src = "https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=" + encodeURIComponent(CFG.adsenseClient);
      document.head.appendChild(s);
    }
    slots.forEach(function (slot) {
      var ins = document.createElement("ins");
      ins.className = "adsbygoogle";
      ins.style.display = "block";
      ins.setAttribute("data-ad-client", CFG.adsenseClient);
      ins.setAttribute("data-ad-slot", CFG.adSlots[slot.getAttribute("data-slot")]);
      ins.setAttribute("data-ad-format", slot.getAttribute("data-format") || "auto");
      ins.setAttribute("data-full-width-responsive", "true");
      slot.appendChild(ins);
      try { window.adsbygoogle.push({}); } catch (e) { /* ignore */ }
    });
  }

  /* ---------- Contact form (FormSubmit) ---------- */
  var FORMSUBMIT = CFG.formEmail ? "https://formsubmit.co/ajax/" + String(CFG.formEmail).trim() : "";
  function showMsg(form, html, isError) {
    var msg = form.querySelector(".form-msg");
    if (!msg) return;
    msg.hidden = false;
    msg.innerHTML = html;
    msg.style.color = isError ? "#c0392b" : "";
  }
  function sendFormSubmit(data) {
    return fetch(FORMSUBMIT, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(data)
    }).then(function (r) { return r.json().catch(function () { return { success: r.ok ? "true" : "false" }; }); })
      .then(function (json) {
        var ok = json && (json.success === true || json.success === "true");
        if (!ok) {
          var m = (json && json.message) || "";
          var err = new Error(m || "FormSubmit error");
          err.activation = /activat/i.test(m);
          throw err;
        }
        return json;
      });
  }
  function wireContact(form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!form.checkValidity()) { form.reportValidity(); return; }
      var data = {};
      new FormData(form).forEach(function (v, k) { data[k] = v; });
      if (data._honey) return;
      var endpoint = CFG.contactEndpoint;
      if (!FORMSUBMIT && !endpoint) {
        showMsg(form, "Ahora mismo no podemos recibir mensajes. Escríbenos a <strong>" + esc(CFG.contactEmail || "") + "</strong>.", true);
        return;
      }
      var site = CFG.siteName || "Mente Abierta";
      data._subject = "[" + site + "] " + (data.motivo || "Mensaje") + " de " + (data.nombre || data.email);
      data._replyto = data.email;
      if (CFG.contactAutoReply) data._autoresponse = CFG.contactAutoReply;
      data._template = "table";
      data.fecha = new Date().toLocaleString("es-ES");
      var btn = form.querySelector("[type=submit]");
      var label = btn ? btn.textContent : "";
      if (btn) { btn.disabled = true; btn.textContent = "Enviando…"; }
      var extra = endpoint ? fetch(endpoint, { method: "POST", body: new FormData(form), mode: "no-cors" }).catch(function () {}) : null;
      Promise.all([FORMSUBMIT ? sendFormSubmit(data) : extra, FORMSUBMIT ? extra : null])
        .then(function () {
          form.reset();
          showMsg(form, "¡Mensaje enviado! Te hemos mandado una copia de confirmación a tu correo y te responderemos lo antes posible.");
        })
        .catch(function (err) {
          if (err && err.activation) {
            showMsg(form, "El formulario se está activando. Si eres el administrador de la web, revisa el correo <strong>" + esc(CFG.formEmail) + "</strong> y pulsa «Activate Form». Después, los envíos funcionarán con normalidad.", true);
          } else {
            showMsg(form, "No hemos podido enviar el mensaje. Revisa tu conexión e inténtalo de nuevo o escríbenos a <strong>" + esc(CFG.contactEmail || "") + "</strong>.", true);
          }
        })
        .then(function () { if (btn) { btn.disabled = false; btn.textContent = label; } });
    });
  }

  /* ======================================================================
     PER PAGE
     ====================================================================== */
  function initPage() {
    var main = $("#main") || document.body;

    progress = $(".progress__bar", main);
    article = $("[data-article-body]", main);
    parallax = reduceMotion ? [] : $$("[data-parallax]", main);

    /* Images: fade in and graceful fallback */
    $$(".media img", main).forEach(function (img) {
      var box = img.closest(".media");
      function fail() { if (box) box.classList.add("is-failed"); }
      if (img.complete) { if (!img.naturalWidth) fail(); return; }
      img.classList.add("is-loading");
      img.addEventListener("load", function () { img.classList.remove("is-loading"); });
      img.addEventListener("error", function () { img.classList.remove("is-loading"); fail(); });
    });

    /* Reveal on scroll (only below the fold; content visible by default) */
    if (revealIO) { revealIO.disconnect(); revealIO = null; }
    if (!reduceMotion && "IntersectionObserver" in window) {
      revealIO = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (!en.isIntersecting) return;
          var el = en.target;
          if (el.classList.contains("reveal-stagger")) {
            Array.prototype.forEach.call(el.children, function (child, i) {
              child.style.transitionDelay = Math.min(i, 8) * 70 + "ms";
              child.classList.remove("is-pending");
            });
          } else {
            el.classList.remove("is-pending");
          }
          revealIO.unobserve(el);
        });
      }, { rootMargin: "0px 0px -8% 0px", threshold: .08 });
      var vh = window.innerHeight;
      $$(".reveal, .reveal-stagger", main).forEach(function (el) {
        if (el.getBoundingClientRect().top < vh * .92) return;
        if (el.classList.contains("reveal-stagger")) {
          Array.prototype.forEach.call(el.children, function (c) { c.classList.add("is-pending"); });
        } else {
          el.classList.add("is-pending");
        }
        revealIO.observe(el);
      });
    }

    /* Table of contents highlight + smooth in-page jumps */
    if (tocIO) { tocIO.disconnect(); tocIO = null; }
    var tocLinks = $$(".toc a", main);
    tocLinks.forEach(function (a) {
      a.addEventListener("click", function (e) {
        var target = document.getElementById(a.getAttribute("href").slice(1));
        if (!target) return;
        e.preventDefault();
        target.scrollIntoView({ behavior: reduceMotion ? "auto" : "smooth", block: "start" });
      });
    });
    if (tocLinks.length && "IntersectionObserver" in window) {
      var map = {};
      tocLinks.forEach(function (a) { map[a.getAttribute("href").slice(1)] = a; });
      tocIO = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (en.isIntersecting) {
            tocLinks.forEach(function (a) { a.classList.remove("is-active"); });
            var link = map[en.target.id]; if (link) link.classList.add("is-active");
          }
        });
      }, { rootMargin: "-20% 0px -70% 0px" });
      tocLinks.map(function (a) { return document.getElementById(a.getAttribute("href").slice(1)); })
        .filter(Boolean).forEach(function (h) { tocIO.observe(h); });
    }

    /* Share links always point to the page the reader is on (only on a real website) */
    var here = /^https?:/.test(window.location.protocol) ? window.location.origin + window.location.pathname : "";
    if (here) {
      var u = encodeURIComponent(here), t = encodeURIComponent(document.title);
      $$(".share", main).forEach(function (bar) {
        $$("a", bar).forEach(function (a) {
          var h = a.getAttribute("href") || "";
          if (h.indexOf("twitter.com") > -1) a.href = "https://twitter.com/intent/tweet?url=" + u + "&text=" + t;
          else if (h.indexOf("facebook.com") > -1) a.href = "https://www.facebook.com/sharer/sharer.php?u=" + u;
          else if (h.indexOf("whatsapp.com") > -1) a.href = "https://api.whatsapp.com/send?text=" + t + "%20" + u;
          else if (h.indexOf("linkedin.com") > -1) a.href = "https://www.linkedin.com/sharing/share-offsite/?url=" + u;
        });
        $$("[data-copy-link]", bar).forEach(function (b) { b.setAttribute("data-url", here); });
      });
    }

    /* Full search page */
    var searchPage = $("[data-search-page]", main);
    if (searchPage) {
      var q0 = window.MA_ROUTE_QUERY != null ? window.MA_ROUTE_QUERY : (new URLSearchParams(window.location.search).get("q") || "");
      var pageInput = $("#q", searchPage);
      var list = $(".search-list", searchPage);
      var count = $(".toolbar__count", searchPage);
      var runPage = function (q) {
        pageInput.value = q;
        if (!q.trim()) { list.innerHTML = ""; count.textContent = "Escribe una palabra para buscar entre " + (window.MA_INDEX || []).length + " artículos."; return; }
        var res = searchIndex(q);
        count.textContent = res.length === 1 ? "1 resultado" : res.length + " resultados";
        list.innerHTML = res.length ? res.map(function (it) {
          return '<article class="card card--row" data-cat="' + esc(it.s) + '"><a class="media" href="' + ROOT + it.u + '" tabindex="-1" aria-hidden="true" data-fallback="' + esc(it.c) + '"><img src="' + esc(it.i) + '" alt="" loading="lazy" width="300" height="300"></a>' +
            '<div class="card__body"><div class="card__meta"><span class="chip" data-cat="' + esc(it.s) + '">' + esc(it.c) + '</span><span>' + it.r + ' min</span></div>' +
            '<h2 class="card__title"><a href="' + ROOT + it.u + '">' + highlight(it.t, q) + '</a></h2><p class="card__dek">' + highlight(it.d, q) + '</p></div></article>';
        }).join("") : '<p class="search-empty">Sin resultados para «' + esc(q) + '». Revisa la ortografía o explora las <a href="' + ROOT + 'categorias.html">categorías</a>.</p>';
      };
      searchPage.querySelector("form").addEventListener("submit", function (e) {
        e.preventDefault();
        var q = pageInput.value;
        if (/^https?:/.test(window.location.protocol) && !window.MA_SPA) {
          try { history.replaceState(null, "", "?q=" + encodeURIComponent(q)); } catch (err) { /* ignore */ }
        }
        runPage(q);
      });
      runPage(q0);
    }

    /* Articles listing: filter + sort */
    var listing = $("[data-listing]", main);
    if (listing) {
      var cards = $$(".card", listing);
      var chips = $$("[data-filter]", main);
      var sortSel = $("#sort", main);
      var countEl = $(".toolbar__count", main);
      var active = "todas";
      var apply = function () {
        var visible = cards.filter(function (c) { return active === "todas" || c.getAttribute("data-cat") === active; });
        cards.forEach(function (c) { c.hidden = visible.indexOf(c) === -1; });
        var mode = sortSel ? sortSel.value : "recientes";
        visible.sort(function (a, b) {
          if (mode === "cortos") return (+a.dataset.read) - (+b.dataset.read);
          if (mode === "largos") return (+b.dataset.read) - (+a.dataset.read);
          return b.dataset.date.localeCompare(a.dataset.date);
        }).forEach(function (c) { listing.appendChild(c); });
        if (countEl) countEl.textContent = visible.length === 1 ? "1 artículo" : visible.length + " artículos";
      };
      chips.forEach(function (ch) {
        ch.addEventListener("click", function () {
          active = ch.getAttribute("data-filter");
          chips.forEach(function (x) { x.setAttribute("aria-pressed", String(x === ch)); });
          apply();
        });
      });
      if (sortSel) sortSel.addEventListener("change", apply);
      apply();
    }

    /* Fact of the day */
    var factEl = $("[data-fact]", main);
    var factData = $("#facts-data", main);
    if (factEl && factData) {
      try {
        var facts = JSON.parse(factData.textContent);
        var now = new Date();
        var day = Math.floor((now - new Date(now.getFullYear(), 0, 0)) / 864e5);
        var f = facts[day % facts.length];
        $(".fact-band__num", factEl).textContent = f.n;
        $(".fact-band__text", factEl).textContent = f.t;
        var link = $(".link-arrow", factEl);
        link.setAttribute("href", ROOT + f.u);
        $("span", link).textContent = "Leer: " + f.a;
      } catch (e) { /* keep server-rendered fact */ }
    }

    /* Contact form */
    $$("form[data-contact]", main).forEach(wireContact);

    loadAds();
    if (window.MA_onScroll) window.MA_onScroll();
  }

  setupGlobal();
  initPage();
  window.MA_initPage = initPage;
})();
