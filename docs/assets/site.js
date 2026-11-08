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

  // Menú «Tria on vols caminar»: província › comarca › poble o ciutat.
  // Al mòbil es va pas a pas, amb el camí a dalt; a l'ordinador es veuen les tres columnes alhora.
  var narrow = window.matchMedia('(max-width: 759px)');
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
    var provBtns = nav.querySelectorAll('button[data-prov]');
    var comBtns = nav.querySelectorAll('button[data-com]');
    var comLists = nav.querySelectorAll('ul[data-prov]');
    var townLists = nav.querySelectorAll('ul[data-com]');
    var towns = nav.querySelectorAll('ul[data-com] a');
    var state = { prov: '', com: '' };

    function mark(btns, attr, value) {
      each(btns, function (b) {
        var on = b.getAttribute(attr) === value;
        b.classList.toggle('is-current', on);
        b.setAttribute('aria-expanded', on ? 'true' : 'false');
      });
    }
    function crumb(text, prov, com, here) {
      var li = document.createElement('li');
      var el = document.createElement(here ? 'span' : 'button');
      el.textContent = text;
      if (here) {
        el.className = 'placenav__here';
        el.setAttribute('aria-current', 'location');
      } else {
        el.type = 'button';
        el.className = 'placenav__crumb';
        el.addEventListener('click', function () { go(prov, com); });
      }
      li.appendChild(el);
      crumbs.appendChild(li);
    }
    function render() {
      var level = !state.prov ? 0 : (!state.com ? 1 : 2);
      nav.setAttribute('data-level', level);
      mark(provBtns, 'data-prov', state.prov);
      mark(comBtns, 'data-com', state.com);
      each(comLists, function (u) { u.classList.toggle('is-open', u.getAttribute('data-prov') === state.prov); });
      each(townLists, function (u) { u.classList.toggle('is-open', u.getAttribute('data-com') === state.com); });
      title.textContent = L.levels[level];
      crumbs.textContent = '';
      crumb(L.root, '', '', level === 0);
      if (state.prov) crumb(nav.querySelector('ul[data-prov="' + state.prov + '"]').getAttribute('data-name'), state.prov, '', level === 1);
      if (state.com) crumb(nav.querySelector('ul[data-com="' + state.com + '"]').getAttribute('data-name'), state.prov, state.com, true);
    }
    function go(prov, com) {
      state.prov = prov; state.com = com;
      render();
      // Al mòbil, la llista nova substitueix l'anterior: es torna a dalt del quadre i el focus va al títol del pas
      if (narrow.matches) {
        if (box.getBoundingClientRect().top < 0) box.scrollIntoView();
        try { title.focus({ preventScroll: true }); } catch (e) { title.focus(); }
      }
    }
    each(provBtns, function (b) {
      b.addEventListener('click', function () { go(b.getAttribute('data-prov'), ''); });
    });
    each(comBtns, function (b) {
      b.addEventListener('click', function () { go(b.getAttribute('data-com').split('--')[0], b.getAttribute('data-com')); });
    });

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
