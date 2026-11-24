// Camins d'Esperança [Activa] · menú del mòbil, enllaços directes a seccions i desplegables per anar a una ciutat o un districte
(function () {
  var bar = document.querySelector('.topbar');
  var btn = document.querySelector('.menu-btn');
  if (bar && btn) {
    btn.addEventListener('click', function () {
      var open = bar.classList.toggle('is-open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      btn.setAttribute('aria-label', open ? 'Tanca el menú' : 'Obre el menú');
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && bar.classList.contains('is-open')) { btn.click(); btn.focus(); }
    });
  }

  // Si l'adreça porta a una ruta (p. ex. /vic/#quan-el-mon-ruta-5), obre el desplegable que la conté
  function openTarget() {
    var id = decodeURIComponent(location.hash.slice(1));
    if (!id) return;
    var el = document.getElementById(id);
    if (!el) return;
    var d = el.closest('details');
    var opened = false;
    while (d) { if (!d.open) { d.open = true; opened = true; } d = d.parentElement && d.parentElement.closest('details'); }
    if (el.tagName === 'DETAILS' && !el.open) { el.open = true; opened = true; }
    if (opened) el.scrollIntoView();
  }
  window.addEventListener('hashchange', openTarget);
  openTarget();

  // Desplegables «Vés directament a…»: porten a la ciutat, el districte o el mapa triat, dins la mateixa pàgina
  Array.prototype.forEach.call(document.querySelectorAll('select[data-jump]'), function (sel) {
    sel.addEventListener('change', function () {
      var id = sel.value;
      var el = id && document.getElementById(id);
      if (!el) return;
      if (decodeURIComponent(location.hash.slice(1)) === id) el.scrollIntoView();
      else location.hash = id;
      // El focus va al lloc triat (a l'enllaç de la ciutat, si n'hi ha), perquè el teclat i els lectors de pantalla continuïn des d'allà
      var f = el.querySelector('.card__link') || el;
      if (f === el) { el.setAttribute('tabindex', '-1'); el.setAttribute('data-jump-target', ''); }
      try { f.focus({ preventScroll: true }); } catch (e) { f.focus(); }
      sel.value = '';
    });
  });

  // Desplegables que porten a una altra pàgina (p. ex. «Vés directament al teu poble»)
  Array.prototype.forEach.call(document.querySelectorAll('select[data-go]'), function (sel) {
    sel.addEventListener('change', function () {
      if (sel.value) location.href = sel.value;
    });
  });

  // Menú «Tria on vols caminar», per nivells (a la .cat, província › comarca › poble o ciutat).
  // Al mòbil es va pas a pas, amb el camí a dalt; a l'ordinador es veuen totes les columnes alhora.
  function each(list, fn) { Array.prototype.forEach.call(list, fn); }
  function fold(s) {
    s = String(s || '');
    if (s.normalize) s = s.normalize('NFD').replace(/[̀-ͯ]/g, '');
    return s.replace(/[’`´]/g, "'").replace(/·/g, '').toLowerCase().trim();
  }
  each(document.querySelectorAll('[data-placenav]'), function (nav) {
    var L = JSON.parse(nav.getAttribute('data-labels'));
    var box = nav.querySelector('.placenav__box');
    var title = nav.querySelector('.placenav__title');
    var crumbs = nav.querySelector('.placenav__crumbs ol');
    var input = nav.querySelector('.placenav__input');
    var results = nav.querySelector('.placenav__results');
    var resTitle = nav.querySelector('.placenav__restitle');
    var resList = nav.querySelector('.placenav__reslist');
    var none = nav.querySelector('.placenav__none');
    var cols = nav.querySelectorAll('.placenav__col');
    var lists = nav.querySelectorAll('ul[data-list]');
    var btns = nav.querySelectorAll('button[data-open]');
    var towns = nav.querySelectorAll('ul[data-list] a');
    var path = [];  // les llistes obertes sota la primera, p. ex. ["barcelona", "barcelona--baix-llobregat"]

    function list(id) { return nav.querySelector('ul[data-list="' + id + '"]'); }
    function crumb(text, upto, here) {
      var li = document.createElement('li');
      var el = document.createElement(here ? 'span' : 'button');
      el.textContent = text;
      if (here) {
        el.className = 'placenav__here';
        el.setAttribute('aria-current', 'location');
      } else {
        el.type = 'button';
        el.className = 'placenav__crumb';
        el.addEventListener('click', function () { go(path.slice(0, upto)); });
      }
      li.appendChild(el);
      crumbs.appendChild(li);
    }
    function render() {
      var level = path.length;
      nav.setAttribute('data-level', level);
      each(lists, function (u) {
        var d = +u.getAttribute('data-depth');
        u.classList.toggle('is-open', d === 0 || path[d - 1] === u.getAttribute('data-list'));
      });
      each(btns, function (b) {
        var on = path.indexOf(b.getAttribute('data-open')) !== -1;
        b.classList.toggle('is-current', on);
        b.setAttribute('aria-expanded', on ? 'true' : 'false');
      });
      each(cols, function (c) {
        var d = +c.getAttribute('data-depth');
        c.classList.toggle('is-active', d === level);
        var hint = c.querySelector('.placenav__hint');
        if (hint) hint.classList.toggle('is-shown', d > level);
      });
      title.textContent = L.levels[level];
      crumbs.textContent = '';
      crumb(L.root, 0, level === 0);
      path.forEach(function (id, k) { crumb(list(id).getAttribute('data-name'), k + 1, k === level - 1); });
    }
    function go(p) {
      path = p;
      render();
      // Pas a pas, la llista nova substitueix l'anterior: es torna a dalt del quadre i el focus va al títol del pas
      if (nav.classList.contains('is-steps')) {
        if (box.getBoundingClientRect().top < 0) box.scrollIntoView();
        try { title.focus({ preventScroll: true }); } catch (e) { title.focus(); }
      }
    }
    each(btns, function (b) {
      b.addEventListener('click', function () {
        var d = +b.closest('ul').getAttribute('data-depth');
        go(path.slice(0, d).concat(b.getAttribute('data-open')));
      });
    });
    // Columnes si hi caben (uns 240 px cada una); si no, pas a pas
    function fit() { nav.classList.toggle('is-steps', nav.clientWidth / cols.length < 240); }
    fit();
    window.addEventListener('resize', fit);

    // Cercador: pobles i ciutats pel nom o per la comarca i la província
    function search() {
      var raw = input.value.trim();
      var q = fold(raw);
      nav.classList.toggle('is-searching', !!q);
      results.hidden = !q;
      if (!q) return;
      resTitle.textContent = L.results.replace('{q}', raw);
      resList.textContent = '';
      var found = [];
      each(towns, function (a) {
        var name = fold(a.querySelector('.placenav__name').textContent);
        var where = a.getAttribute('data-where');
        if (name.indexOf(q) === -1 && fold(where).indexOf(q) === -1) return;
        var key = name.replace(/^(el|la|els|les|los|las|l') ?/, '');
        var rank = key.indexOf(q) === 0 || name.indexOf(q) === 0 ? 0 : (name.indexOf(q) !== -1 ? 1 : 2);
        found.push({ a: a, where: where, key: key, rank: rank });
      });
      // Primer els que es diuen així (Tarragona) i després els de la comarca o la província; en ordre alfabètic, sense l'article
      found.sort(function (x, y) { return x.rank - y.rank || (x.key < y.key ? -1 : (x.key > y.key ? 1 : 0)); });
      found.forEach(function (f) {
        var c = f.a.cloneNode(true);
        var sub = c.querySelector('.placenav__sub');
        sub.textContent = f.where + ' · ' + sub.textContent;
        var li = document.createElement('li');
        li.appendChild(c);
        resList.appendChild(li);
      });
      none.hidden = resList.children.length > 0;
    }
    input.addEventListener('input', search);
    input.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') {
        var first = resList.querySelector('a');
        if (first) { e.preventDefault(); location.href = first.href; }
      } else if (e.key === 'Escape' && input.value) {
        input.value = '';
        search();
      }
    });
    nav.querySelector('.placenav__clear').addEventListener('click', function () {
      input.value = '';
      search();
      input.focus();
    });
    render();
    search();
  });
})();

// Cerca per ubicació o adreça: mostra, per curs, les rutes que comencen més a prop (dades a assets/rutas.json)
(function () {
  var box = document.querySelector('[data-nearby]');
  if (!box) return;
  var L = JSON.parse(box.getAttribute('data-labels'));
  var root = box.getAttribute('data-root') || '';
  var only = box.getAttribute('data-course');
  var max = parseInt(box.getAttribute('data-max'), 10) || 3;
  var locBtn = box.querySelector('.nearby__locate');
  var form = box.querySelector('.nearby__addr');
  var input = box.querySelector('.nearby__input');
  var status = box.querySelector('.nearby__status');
  var out = box.querySelector('.nearby__results');
  var lang = document.documentElement.lang || 'es';
  var data = null, loading = null;

  function load() {
    if (data) return Promise.resolve(data);
    if (!loading) loading = fetch(box.getAttribute('data-src')).then(function (r) { if (!r.ok) throw new Error('rutas'); return r.json(); }).then(function (d) { data = d; return d; });
    return loading;
  }
  function km(lat1, lon1, lat2, lon2) {
    var r = Math.PI / 180, dl = (lat2 - lat1) * r, dn = (lon2 - lon1) * r;
    var a = Math.sin(dl / 2) * Math.sin(dl / 2) + Math.cos(lat1 * r) * Math.cos(lat2 * r) * Math.sin(dn / 2) * Math.sin(dn / 2);
    return 12742 * Math.asin(Math.sqrt(a));
  }
  function fmt(d) {
    var t = d < 1 ? (Math.max(10, Math.round(d * 100) * 10)) + ' m' : (d < 10 ? d.toFixed(1) : String(Math.round(d))) + ' km';
    return t.replace('.', ',');
  }
  function say(t) { status.textContent = t || ''; }
  function busy(on) { box.classList.toggle('is-busy', on); locBtn.disabled = on; }
  function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }

  function show(lat, lon, where) {
    load().then(function (d) {
      out.textContent = '';
      var head = el('h4', 'nearby__restitle', L.results.replace('{where}', where));
      head.tabIndex = -1;
      out.appendChild(head);
      d.courses.forEach(function (c, ci) {
        if (only && c.k !== only) return;
        var list = [];
        d.routes.forEach(function (r) { if (r[2] === ci) list.push({ r: r, d: km(lat, lon, r[0], r[1]) }); });
        if (!list.length) return;
        list.sort(function (a, b) { return a.d - b.d; });
        var sec = el('section', 'nearby__course');
        if (c.t) {
          var h = el('h5', 'nearby__coursename');
          var ca = el('a', null, c.t); ca.href = root + c.s + '/';
          h.appendChild(ca); sec.appendChild(h);
        }
        if (list[0].d > 40) sec.appendChild(el('p', 'nearby__far', L.far.replace('{d}', fmt(list[0].d))));
        var ul = el('ul', 'nearby__list');
        list.slice(0, max).forEach(function (x) {
          var r = x.r, li = el('li', 'nearby__item');
          var body = el('div', 'nearby__body');
          body.appendChild(el('strong', 'nearby__name', r[6]));
          body.appendChild(el('span', 'nearby__meta', r[4] + ' · ' + L.away.replace('{d}', fmt(x.d))));
          li.appendChild(body);
          var links = el('div', 'nearby__links');
          var a1 = el('a', 'nearby__link', L.go); a1.href = root + r[3] + '/#' + r[5]; links.appendChild(a1);
          if (r[7]) { var a2 = el('a', 'nearby__link nearby__link--map', L.map); a2.href = 'https://www.google.com/maps/d/viewer?mid=' + encodeURIComponent(r[7]); a2.target = '_blank'; a2.rel = 'noopener'; links.appendChild(a2); }
          li.appendChild(links);
          ul.appendChild(li);
        });
        sec.appendChild(ul);
        out.appendChild(sec);
      });
      out.appendChild(el('p', 'nearby__note', L.note));
      out.hidden = false;
      say('');
      busy(false);
      head.focus({ preventScroll: true });
      if (head.scrollIntoView) head.scrollIntoView({ block: 'nearest' });
    }).catch(function () { busy(false); say(L.network); });
  }

  locBtn.addEventListener('click', function () {
    if (!navigator.geolocation) { say(L.unsupported); return; }
    busy(true); say(L.locating);
    load();
    navigator.geolocation.getCurrentPosition(function (p) {
      show(p.coords.latitude, p.coords.longitude, L.here);
    }, function () { busy(false); say(L.denied); }, { enableHighAccuracy: false, timeout: 15000, maximumAge: 300000 });
  });

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var q = input.value.trim();
    if (!q) { input.focus(); return; }
    busy(true); say(L.searching);
    load();
    fetch('https://nominatim.openstreetmap.org/search?format=jsonv2&limit=1&countrycodes=es&accept-language=' + encodeURIComponent(lang) + '&q=' + encodeURIComponent(q))
      .then(function (r) { if (!r.ok) throw new Error('geo'); return r.json(); })
      .then(function (res) {
        if (!res || !res.length) { busy(false); say(L.notfound); return; }
        var where = String(res[0].display_name || q).split(', ').slice(0, 3).join(', ');
        show(parseFloat(res[0].lat), parseFloat(res[0].lon), where);
      })
      .catch(function () { busy(false); say(L.network); });
  });

  // Enllaç amb l'adreça ja escrita (p. ex. des d'elarasocial.com): /ciutats/?q=Vic omple el camp i fa la cerca
  try {
    var pre = new URLSearchParams(location.search).get('q');
    if (pre && pre.trim() && pre.length <= 200) {
      input.value = pre.trim();
      if (form.requestSubmit) form.requestSubmit(); else form.dispatchEvent(new Event('submit', { cancelable: true }));
    }
  } catch (e) {}
})();

// Filtre d'entitats (subpàgines amb moltes rutes): amaga les rutes que no coincideixen amb el text
(function () {
  Array.prototype.forEach.call(document.querySelectorAll('[data-rfilter]'), function (box) {
    var input = box.querySelector('.rfilter__input'), status = box.querySelector('.rfilter__status');
    var section = box.closest('section') || document;
    var tpl = box.getAttribute('data-count') || '{n}', empty = box.getAttribute('data-empty') || '';
    function norm(s) { return String(s).normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase(); }
    var items = Array.prototype.map.call(section.querySelectorAll('li.route'), function (li) {
      var n = li.querySelector('.route__name');
      return { li: li, t: norm(n ? n.textContent.replace(/^Ruta \d+:\s*/, '') : li.textContent) };
    });
    var groups = Array.prototype.map.call(section.querySelectorAll('.group'), function (g) {
      return { g: g, d: g.querySelector('details.routes'), open: g.querySelector('details.routes') && g.querySelector('details.routes').open, items: items.filter(function (x) { return g.contains(x.li); }) };
    });
    function run() {
      var q = norm(input.value.trim()), total = 0;
      groups.forEach(function (g) {
        var hits = 0;
        g.items.forEach(function (x) { var ok = !q || x.t.indexOf(q) !== -1; x.li.hidden = !ok; if (ok) hits++; });
        total += hits;
        g.g.hidden = !!q && !hits;
        if (g.d) g.d.open = q ? hits > 0 : g.open;
      });
      status.textContent = q ? (total ? tpl.replace('{n}', total) : empty) : '';
    }
    input.addEventListener('input', run);
  });
})();

/* Lletres: l'ona dels títols s'obre en arribar-hi i el títol de la capçalera surt paraula a paraula */
(function () {
  var hs = document.querySelectorAll('main h2[id^="h-"], .health__h2');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); } }); }, { threshold: .6 });
    Array.prototype.forEach.call(hs, function (h) { io.observe(h); });
  } else Array.prototype.forEach.call(hs, function (h) { h.classList.add('is-in'); });
  var h1 = document.querySelector('.pagehead h1');
  if (h1 && !(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches)) {
    var words = h1.textContent.trim().split(/\s+/);
    h1.textContent = '';
    words.forEach(function (w, i) {
      var sp = document.createElement('span'); sp.className = 'w'; sp.style.setProperty('--i', i); sp.textContent = w;
      h1.appendChild(sp); if (i < words.length - 1) h1.appendChild(document.createTextNode(' '));
    });
    h1.classList.add('is-split');
  }
})();

/* Mapes de Google My Maps: només es carreguen si la persona ho accepta (es recorda al navegador) */
(function () {
  var KEY = 'ea-consent-mapes', st = null;
  try { st = localStorage.getItem(KEY); } catch (e) {}
  var banner = document.getElementById('consent');
  var frames = document.querySelectorAll('iframe[data-src]');
  function save(v) { try { localStorage.setItem(KEY, v); } catch (e) {} }
  function load() {
    Array.prototype.forEach.call(frames, function (f) {
      if (!f.getAttribute('src')) { f.setAttribute('loading', 'lazy'); f.setAttribute('src', f.getAttribute('data-src')); }
      var c = f.parentNode.querySelector('.map__consent'); if (c) c.hidden = true;
    });
  }
  document.addEventListener('click', function (e) {
    var b = e.target.closest ? e.target.closest('[data-consent]') : null;
    if (!b) return;
    var a = b.getAttribute('data-consent');
    if (a === 'accept') { save('yes'); load(); if (banner) banner.hidden = true; }
    else if (a === 'reject') { var was = st === 'yes'; save('no'); st = 'no'; if (banner) banner.hidden = true; if (was) location.reload(); }
    else if (a === 'open' && banner) { banner.hidden = false; }
  });
  if (st === 'yes') load();
  else if (st === null && frames.length && banner) banner.hidden = false;
})();
