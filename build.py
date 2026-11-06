#!/usr/bin/env python3
"""Genera la web estàtica de Camins d'Esperança [Activa] a la carpeta docs/.

Ús:  python3 build.py

L'adreça pública de la web i si ha de sortir als cercadors es configuren a
data/site.json, a "publish": {"url": ..., "index": true/false}.

Els textos són a data/site.json i les rutes a data/<ciutat>.json.
"""
import json, os, re, shutil, sys, time, unicodedata
from pathlib import Path
from urllib.parse import quote
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup

ROOT = Path(__file__).resolve().parent
DATA, SRC, OUT = ROOT / "data", ROOT / "src", ROOT / "docs"

from urllib.parse import urlparse

ICONS = json.loads((SRC / "icons.json").read_text(encoding="utf-8"))


def icon(name, cls=None):
    vb = ICONS.get(name + "__vb", "0 0 256 256")
    c = "i" + (" " + cls if cls else "")
    return Markup(f'<svg class="{c}" viewBox="{vb}" fill="currentColor" aria-hidden="true" focusable="false">{ICONS[name]}</svg>')


def slugify(s):
    s = s.replace("l·l", "ll").replace("L·L", "LL")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def map_viewer(mid):
    return "https://www.google.com/maps/d/viewer?mid=" + quote(mid, safe="")


def assign_maps(g, routes):
    """Cada ruta porta l'enllaç al mapa de My Maps on és (botó «Obre el mapa»).
    Si el grup té un sol mapa, totes hi són. Si en té diversos, cada mapa diu
    quines rutes té amb "routes": [1, 2, ...]."""
    maps = g.get("maps") or []
    for r in routes:
        if len(maps) == 1:
            m = maps[0]
        else:
            # "routes" pot dir el número de la ruta (5) o el seu id ("barri-sants-ruta-2")
            found = [m for m in maps if r["n"] in (m.get("routes") or []) or r.get("id") in (m.get("routes") or [])]
            assert len(found) == 1, f"la ruta {r['n']} de «{g['title']}» ha de ser en un sol mapa (posa-la a \"routes\" del mapa)"
            m = found[0]
        r["map_url"] = map_viewer(m["mid"])
        r["map_title"] = m["title"]


# Desplegable «Vés directament a…»: surt dins d'un bloc de curs quan hi ha
# com a mínim aquests mapes o districtes per triar.
ZONES_MIN = 3
ZONES_TEXT = {
    # tipus: (etiqueta, primera opció, enllaç sota cada mapa per tornar al desplegable)
    "zona": ("Vés directament a la teva zona", "Tria una zona", "Canvia de zona"),
    "mapa": ("Vés directament al mapa", "Tria un mapa", "Canvia de mapa"),
}


def add_zones(b, groups, course, cfg, pid=None):
    """Si un bloc (o una part d'un bloc) té molts mapes, hi posa un desplegable per
    saltar al districte, la zona o el mapa. Diversos grups (p. ex. un per districte):
    cada grup és una opció (o cada districte, si el grup en té diversos). Un sol grup
    amb diversos mapes: cada mapa és una opció. Amb "zones": {"by": "district"} al
    bloc, una opció per districte (camp "district" de cada grup). Els textos es poden
    canviar amb "zones" a la ciutat o al bloc: {"label": ..., "placeholder": ..., "back": ...}."""
    options, targets = [], []
    if len(groups) > 1 and cfg.get("by") == "district":
        # Diversos grups per districte (p. ex. un per mapa): una opció per districte,
        # que porta al primer grup; cada mapa té l'enllaç per tornar al desplegable.
        kind = "zona"
        for g in groups:
            d = g.get("district") or g["title"]
            if d not in [o[0] for o in options]:
                options.append((d, g["id"]))
            if g["maps"]:
                targets.append((g["maps"][0], g["title"]))
    elif len(groups) > 1:
        kind = "zona"
        for g in groups:
            if g.get("sections"):
                options += [(s["title"], g["id"]) for s in g["sections"]]
            else:
                options.append((g["title"], g["id"]))
            if g["maps"]:
                targets.append((g["maps"][0], g["title"]))
    elif groups and len(groups[0]["maps"]) > 1:
        kind = "mapa"
        for m in groups[0]["maps"]:
            name = m.get("zone") or m.get("label") or m["title"]
            m["id"] = m.get("id") or f"{course['anchor']}-{slugify(name)}"
            options.append((name, m["id"]))
            targets.append((m, name))
    else:
        return
    if len(options) < ZONES_MIN:
        return
    label, placeholder, back = ZONES_TEXT[kind]
    pid = pid or f"{course['anchor']}-tria"
    b["zones"] = {"id": pid, "label": cfg.get("label", label), "placeholder": cfg.get("placeholder", placeholder), "options": options}
    for m, name in targets:
        m["label"] = m.get("label") or name   # cada mapa amb el seu nom a sobre
        m["back"] = {"href": pid, "text": cfg.get("back", back)}


site = json.loads((DATA / "site.json").read_text(encoding="utf-8"))
SITE_URL = site["publish"]["url"].rstrip("/") + "/"
NOINDEX = not site["publish"].get("index", False)
BASE = urlparse(SITE_URL).path or "/"   # p. ex. /esperancaactiva/ a GitHub Pages, / amb domini propi
courses = {c["key"]: c for c in site["courses"]}

# HTML fields (written by us in site.json) are trusted markup
site["safety_html"] = Markup(site["safety_html"])
bw = site["before_walk"]
bw_html = Markup("<p>{}</p><ul class=\"ticks\">{}</ul>").format(
    bw["intro"], Markup("").join(Markup("<li>{}</li>").format(i) for i in bw["list"]))
fp = site["faq_page"]
fp["contact_html"] = Markup(fp["contact_html"])
for s in fp["sections"]:
    s["id"] = slugify(s["title"])
    # Cada pregunta: [pregunta, resposta] o [pregunta, resposta, infografia] (p. ex. "i-despres": la infografia surt dins la resposta)
    s["items"] = [(it[0], bw_html if it[1] == "__before_walk__" else Markup(f"<p>{it[1]}</p>"), slugify(it[0]), it[2] if len(it) > 2 else None) for it in s["items"]]
site["home"]["faq"] = [(q, Markup("<p>{}</p>").format(a)) for q, a in site["home"]["faq"]]

def process_groups(groups, course):
    """Posa els ids als grups, als districtes o barris i a les rutes, i l'enllaç al
    mapa de cada ruta. Torna el nombre de rutes."""
    total = 0
    for g in groups:
        if g.get("sections"):
            g["id"] = g.get("id") or slugify(g["title"])
            for s in g["sections"]:
                s["id"] = s.get("id") or slugify(s["title"])
                # Si un barri continua en un altre mapa, la secció nova porta un id propi
                # (barri-sants-2) i les rutes mantenen el del barri (barri-sants-ruta-6).
                prefix = s.get("route_prefix") or s["id"]
                for r in s["routes"]:
                    r["id"] = f"{prefix}-ruta-{r['n']}"
                assign_maps(g, s["routes"])
            g["count"] = sum(len(s["routes"]) for s in g["sections"])
        else:
            g["id"] = g.get("id") or (f"{course['anchor']}-rutes" if len(groups) == 1 else slugify(g["title"]))
            # Un sol grup: /vic/#quan-el-mon-ruta-5. Diversos grups (p. ex. un per districte): /barcelona/#cap-gracia-ruta-6
            prefix = course["anchor"] if len(groups) == 1 else g["id"]
            for r in g["routes"]:
                r["id"] = f"{prefix}-ruta-{r['n']}"
            assign_maps(g, g["routes"])
            g["count"] = len(g["routes"])
        total += g["count"]
    return total


# Cities
cities = []
summaries = {}
course_summaries = {k: {} for k in courses}
for c in site["cities"]:
    if not c.get("slug"):
        continue
    city = json.loads((DATA / f"{c['slug']}.json").read_text(encoding="utf-8"))
    city.setdefault("title", f"Caminar per {city['name']}")
    city["icon"] = c["icon"]
    by_course = {b["course"]: b for b in city["blocks"]}
    blocks = []
    for key, course in courses.items():
        b = by_course.get(key, {"course": key, "text": f"Encara no hi ha rutes d'aquest curs a {city['name']}. Mentrestant, pots fer el temps de reflexió de cada passa caminant a prop de casa o en un lloc tranquil."})
        b = dict(b, course=course)
        # Un bloc pot tenir diverses parts, cada una amb el seu títol, text, avís,
        # grups i desplegable (Barcelona «Quan la vida»: rutes des dels CAP i rutes
        # «Caminant fem salut»). Sense "parts", el bloc és una sola part sense títol.
        parts = b.get("parts") or [{"groups": b.get("groups") or []}]
        total = 0
        for i, p in enumerate(parts):
            assert i == 0 or p.get("id") and p.get("title"), "cada part, a partir de la segona, necessita id i title"
            p["count"] = process_groups(p["groups"], course)
            total += p["count"]
            if p.get("notice"):
                p["notice"] = dict(p["notice"], html=[Markup(h) for h in p["notice"]["html"]])
            # La primera part manté el desplegable del curs (#quan-la-vida-tria); les altres, el seu (#caminant-fem-salut-tria)
            cfg = dict(city.get("zones") or {}, **(b.get("zones") or {}), **(p.get("zones") or {}))
            add_zones(p, p["groups"], course, cfg, pid=None if i == 0 else f"{p['id']}-tria")
        b["parts"] = parts
        b["groups"] = [g for p in parts for g in p["groups"]]
        b["total"] = total
        b["summary"] = b.get("summary") or ("Encara no hi ha rutes d'aquest curs" if not total else f"{total} rutes")
        course_summaries[key][city["slug"]] = {"text": b["summary"] if total else "Encara no hi ha rutes d'aquest curs. Pots caminar a prop de casa.", "has": bool(total)}
        blocks.append(b)
    # Primer els cursos que tenen rutes en aquesta ciutat; després, els que encara no en tenen
    city["blocks"] = [b for b in blocks if b["total"]] + [b for b in blocks if not b["total"]]
    summaries[city["slug"]] = {"text": city["summary"], "has": True}
    cities.append(city)

# Sanity checks
all_ids = []
n_routes = 0
for city in cities:
    ids = []
    for b in city["blocks"]:
        ids.append(b["course"]["anchor"])
        for p in b["parts"]:
            if p.get("id"):
                ids.append(p["id"])
            if p.get("zones"):
                ids.append(p["zones"]["id"])
        for g in b["groups"]:
            ids.append(g["id"])
            ids += [m["id"] for m in g["maps"] if m.get("id")]
            for s in g.get("sections") or [g]:
                if s is not g:
                    ids.append(s["id"])
                for r in s["routes"]:
                    ids.append(r["id"]); n_routes += 1
    dup = {i for i in ids if ids.count(i) > 1}
    assert not dup, f"ids repetits a {city['slug']}: {dup}"

def cities_with_a(names):
    """«a Barcelona, el Prat de Llobregat, Olot i Vic»: la llista de ciutats per a una frase.
    L'article va en minúscula (el Prat) i «a el» es contrau («al Prat») si la llista en comença amb un."""
    names = [re.sub(r"^(El|La|Els|Les|L')(?=[ A-ZÀ-Ý])", lambda m: m.group(1).lower(), n) for n in names]
    s = names[0] if len(names) == 1 else ", ".join(names[:-1]) + " i " + names[-1]
    return re.sub(r"^el ", "al ", re.sub(r"^els ", "als ", s)) if re.match(r"els? ", s) else "a " + s


env = Environment(loader=FileSystemLoader(SRC / "templates"), autoescape=select_autoescape(["html"]), trim_blocks=True, lstrip_blocks=True)
env.globals.update(icon=icon, site=site, noindex=NOINDEX, version=str(int(time.time())),
                   logo=(SRC / "img" / "logo.png").exists(),
                   partners_logo=(SRC / "img" / "lespiral-elara.png").exists(),
                   summaries=summaries, course_summaries=course_summaries,
                   cities_with_a=cities_with_a([c["name"] for c in site["cities"] if c.get("slug")]),
                   h=site["home"], cc=site["course_common"])


PAGES = []


def render(template, path, **ctx):
    depth = len([p for p in path.split("/") if p])
    root = ctx.pop("root", "../" * depth)
    canonical = None if path.endswith(".html") else SITE_URL + (path + "/" if path else "")
    if canonical:
        PAGES.append(canonical)
    html = env.get_template(template).render(root=root, canonical=canonical, **ctx)
    dest = OUT / path / "index.html" if not path.endswith(".html") else OUT / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html, encoding="utf-8")


if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir()

render("home.html", "", section="inici")
render("courses.html", "cursos", section="cursos", page_title="Els cursos", cp=site["courses_page"])
render("cities.html", "ciutats", section="ciutats", page_title="Les ciutats", cp=site["cities_page"])
render("faq.html", "preguntes", section="preguntes", page_title="Preguntes", fp=fp)
for c in site["courses"]:
    render("course.html", c["slug"], section="cursos", page_title=c["title"], page_description=c["subtitle"], course=c)
for city in cities:
    render("city.html", city["slug"], section="ciutats", page_title=city["name"], page_description=city["summary"], city=city)
render("404.html", "404.html", page_title="Pàgina no trobada", root=BASE, base=BASE)

(OUT / "assets").mkdir(exist_ok=True)
shutil.copy(SRC / "site.css", OUT / "assets" / "site.css")
shutil.copy(SRC / "site.js", OUT / "assets" / "site.js")
if (SRC / "img").exists():
    shutil.copytree(SRC / "img", OUT / "assets" / "img")
(OUT / ".nojekyll").write_text("")
if NOINDEX:
    (OUT / "robots.txt").write_text("User-agent: *\nDisallow: /\n")
else:
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}sitemap.xml\n")
    today = time.strftime("%Y-%m-%d")
    urls = "".join(f"  <url><loc>{u}</loc><lastmod>{today}</lastmod></url>\n" for u in PAGES)
    (OUT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n', encoding="utf-8")
if (ROOT / "CNAME").exists():
    shutil.copy(ROOT / "CNAME", OUT / "CNAME")

print(f"Fet: {len(cities)} ciutats, {n_routes} rutes, {sum(len(g['maps']) for c in cities for b in c['blocks'] for g in b['groups'])} mapes. adreça={SITE_URL} cercadors={'no' if NOINDEX else 'sí'}")
