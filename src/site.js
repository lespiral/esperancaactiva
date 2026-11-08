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
