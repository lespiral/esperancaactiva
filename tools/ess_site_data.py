#!/usr/bin/env python3
"""Posa a la web (data/ de lespiral/esperancaactiva) les 147 rutes de l'economia social i solidària
(curs «Quan sostenir la vida es fa difícil», bloc "dia") a partir de ess_routes.json (ess_extract.py).
Ús: python3 -I ess_site_data.py ess_routes.json CARPETA_DEL_REPOSITORI"""
import json, math, os, re, sys, collections, unicodedata
from collections import OrderedDict as OD

ROUTES, REPO = sys.argv[1], sys.argv[2]
DATA = os.path.join(REPO, "data")
R = json.load(open(ROUTES, encoding="utf-8"))


def dumps(obj):
    out = json.dumps(obj, ensure_ascii=False, indent=2)
    pat = re.compile(r'\[\n\s+((?:(?:-?\d+|"[^"\n]{0,40}"),\n\s+)*(?:-?\d+|"[^"\n]{0,40}"))\n\s+\]')
    return pat.sub(lambda m: "[" + ", ".join(x.strip() for x in m.group(1).split(",\n")) + "]", out) + "\n"


def slugify(s):
    s = s.replace("l·l", "ll").replace("L·L", "LL")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def ap(s):
    return s.replace("’", "'")


def join_i(xs):
    xs = list(xs)
    return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " i " + xs[-1]


def lower_article(mun):
    """«El Prat de Llobregat» → «el Prat de Llobregat» dins d'una adreça."""
    return re.sub(r"^(El|La|Els|Les|L')(?=[ ']|[A-ZÀ-Ú])", lambda m: m.group(1).lower(), mun)


def km_txt(km):
    return f"{km:.2f}".replace(".", ",")


def mins(t):
    a, b = re.match(r"(\d+)–(\d+)", t).groups()
    return int(a), int(b)


# ---------- pàgines ----------
CITY = {"Barcelona": "barcelona", "el Prat de Llobregat": "el-prat", "L’Hospitalet de Llobregat": "l-hospitalet",
        "Olot": "olot", "Vic": "vic"}
# (pàgina del pla, slug, nom, títol, icona, ciutat amb pàgina pròpia dins el territori)
TERR = [
    ("Alt Pirineu i Aran", "alt-pirineu-i-aran", "Alt Pirineu i Aran", "Caminar per l'Alt Pirineu i Aran", "tree", None),
    ("Anoia, Penedès i Garraf", "anoia-penedes-i-garraf", "Anoia, Penedès i Garraf", "Caminar per l'Anoia, el Penedès i el Garraf", "plant", None),
    ("Baix Llobregat", "baix-llobregat", "Baix Llobregat", "Caminar pel Baix Llobregat", "map", "el-prat"),
    ("Barcelonès Nord", "barcelones-nord", "Barcelonès Nord", "Caminar pel Barcelonès Nord", "buildings", None),
    ("Camp de Tarragona", "camp-de-tarragona", "Camp de Tarragona", "Caminar pel Camp de Tarragona", "sun", None),
    ("Catalunya Central", "catalunya-central", "Catalunya Central", "Caminar per la Catalunya Central", "footprints", "vic"),
    ("Maresme", "maresme", "Maresme", "Caminar pel Maresme", "globe", None),
    ("Ponent", "ponent", "Ponent", "Caminar per Ponent", "sun", None),
    ("Terres de l’Ebre", "terres-de-l-ebre", "Terres de l'Ebre", "Caminar per les Terres de l'Ebre", "plant", None),
    ("Terres Gironines", "terres-gironines", "Terres Gironines", "Caminar per les Terres Gironines", "tree", "olot"),
    ("Vallès Occidental", "valles-occidental", "Vallès Occidental", "Caminar pel Vallès Occidental", "map", None),
    ("Vallès Oriental", "valles-oriental", "Vallès Oriental", "Caminar pel Vallès Oriental", "footprints", None),
]
SHORT = {"el-prat": "el Prat", "vic": "Vic", "olot": "Olot"}
CITY_NAME = {"el-prat": "El Prat de Llobregat", "vic": "Vic", "olot": "Olot"}

pages = collections.defaultdict(list)
for r in R:
    pages[r["page"]].append(r)
assert set(pages) == {t[0] for t in TERR} | set(CITY), set(pages) ^ ({t[0] for t in TERR} | set(CITY))

ANCHOR = "quan-sostenir"
PREFIX = "Rutes d'Esperança Activa - "


# Noms i textos que l'Aleix ha corregit a mà (els mapes encara diuen el nom antic).
FIX = {
    "Alba Jussà": ("Cooperativa La Teia (abans «Alba Jussà»)",
                   "La Cooperativa La Teia acompanya persones i famílies amb serveis de suport individualitzat i projectes d’inclusió social i laboral."),
}


def route_obj(r):
    ents = list(r["entities"])
    principal = ap(r["layer"].split(" - ", 1)[1])
    ents.sort(key=lambda e: 0 if ap(e["name"]) == principal or principal.startswith(ap(e["name"])) else 1)
    ents = [dict(e, name=FIX[e["name"]][0], desc=FIX[e["name"]][1]) if e["name"] in FIX else e for e in ents]
    o = OD(n=r["number"], name=ap(join_i(e["name"] for e in ents)))
    a, b = mins(r["time"])
    o["info"] = f"{km_txt(r['km'])} km · {a}–{b} min caminant · circular"
    o["address"] = f"{r['address']}, {lower_article(ap(r['seat_municipality']))}"
    o["desc"] = " ".join(clean_descs(ents))
    return o


def clean_desc(d):
    """Treu les notes de font de les fitxes («Font actual: … (consulta: …).»)."""
    return re.sub(r"\s*Font actual:[^)]*\)\.?", "", d).strip()


SKIP = {"Espai Llavors SCCL"}   # mateixa llibreria que Llibreria Llavors: el text es repetia


def clean_descs(ents):
    names = {e["name"] for e in ents}
    out = []
    for e in ents:
        if e["name"] in SKIP and len(names) > 1:
            continue
        d = clean_desc(e["desc"])
        if d not in out:
            out.append(d)
    return out


def view(rs):
    """Centre (una mica al nord, per la barra del títol del mapa) i zoom perquè hi càpiguen les rutes."""
    x0 = min(r["bbox"][0] for r in rs); y0 = min(r["bbox"][1] for r in rs)
    x1 = max(r["bbox"][2] for r in rs); y1 = max(r["bbox"][3] for r in rs)
    lat = (y0 + y1) / 2; lon = (x0 + x1) / 2
    W, H = 600, 300
    zx = math.log2(W * 360 / (256 * max(x1 - x0, 1e-4)))
    zy = math.log2(H * 360 * math.cos(math.radians(lat)) / (256 * max(y1 - y0, 1e-4)))
    z = max(8, min(15, math.floor(min(zx, zy))))
    lat += 35 * 360 * math.cos(math.radians(lat)) / (256 * 2 ** z)
    return f"{lat:.4f},{lon:.4f}", z


def time_range(rs):
    lo = min(mins(r["time"])[0] for r in rs); hi = max(mins(r["time"])[1] for r in rs)
    return lo, hi


def km_range(rs):
    ks = [r["km"] for r in rs]
    lo, hi = f"{min(ks):.1f}".replace(".", ","), f"{max(ks):.1f}".replace(".", ",")
    if lo == hi:
        return ("d'" if lo[0] in "18" else "de ") + f"{lo} km"
    return ("d'" if lo[0] in "18" else "de ") + f"{lo} a {hi} km"


def block_text(rs):
    n = len(rs)
    lo, hi = time_range(rs)
    multi = any(len(r["entities"]) > 1 for r in rs)
    if n == 1:
        t = (f"Una ruta circular curta, {km_range(rs)} (uns {lo}–{hi} minuts caminant), que surt d'una entitat de "
             "l'economia social i solidària i hi torna. Comença i acaba al carrer, davant de l'entitat: no cal entrar-hi.")
        if multi:
            t += " Al mateix lloc hi ha diverses entitats."
        return t
    t = (f"{n} rutes circulars curtes, {km_range(rs)} (uns {lo}–{hi} minuts caminant), que surten d'una entitat de "
         "l'economia social i solidària i hi tornen: cooperatives, associacions i fundacions que treballen per "
         "l'habitatge, la feina, la cultura o les cures. Comencen i acaben al carrer, davant de l'entitat: no cal entrar-hi.")
    if multi:
        t += " En alguns punts hi ha diverses entitats al mateix lloc."
    return t


def n_rutes(n):
    return "1 ruta" if n == 1 else f"{n} rutes"


def groups_for(rs, sections_by=None, sec_prefix=""):
    """Un grup per mapa. sections_by: "municipality" o "district" (seccions), o None (llista)."""
    bymap = OD()
    for r in sorted(rs, key=lambda r: (r["map"], r["order"])):
        bymap.setdefault(r["map"], []).append(r)
    N = len(bymap)
    groups = []
    for k, (code, mrs) in enumerate(bymap.items(), 1):
        ll, z = view(mrs)
        title = ap(mrs[0]["map_title"][len(PREFIX):] if mrs[0]["map_title"].startswith(PREFIX) else mrs[0]["map_title"])
        if sections_by:
            names = list(OD.fromkeys(ap(r[sections_by]) for r in mrs))
            gtitle = join_i(names)
        else:
            gtitle = "La ruta" if len(mrs) == 1 else f"Les {len(mrs)} rutes"
        label = (f"{gtitle} · mapa {k} de {N}" if N > 1 else f"{n_rutes(len(mrs))} des de l'economia social")
        g = OD()
        g["id"] = f"{ANCHOR}-mapa-{k}" if N > 1 else f"{ANCHOR}-rutes"
        g["title"] = gtitle
        g["maps"] = [OD(mid=mrs[0]["mid"], title=title, ll=ll, z=z, label=label)]
        if sections_by:
            secs = OD()
            for r in mrs:
                secs.setdefault(ap(r[sections_by]), []).append(r)
            g["sections"] = []
            for name, srs in secs.items():
                s = OD(title=name)
                if sec_prefix:
                    s["id"] = f"{sec_prefix}{slugify(name)}"
                s["routes"] = [route_obj(r) for r in sorted(srs, key=lambda r: r["number"])]
                g["sections"].append(s)
        else:
            g["routes"] = [route_obj(r) for r in sorted(mrs, key=lambda r: r["number"])]
        groups.append(g)
    return groups


def dia_block(rs, **kw):
    b = OD(course="dia", text=block_text(rs), summary=f"{n_rutes(len(rs))} des de l'economia social")
    if kw.get("zones"):
        b["zones"] = kw.pop("zones")
    b["groups"] = groups_for(rs, **kw)
    return b


def set_block(path, block, summary=None):
    s = open(path, encoding="utf-8").read()
    city = json.loads(s, object_pairs_hook=OD)
    city["blocks"] = [b for b in city["blocks"] if b["course"] != "dia"] + [block]
    if summary:
        city["summary"] = summary
    open(path, "w", encoding="utf-8").write(dumps(city))


# ---------- territoris ----------
site_terr = []
for page, slug, name, title, icon, city in TERR:
    rs = pages[page]
    muns = list(OD.fromkeys(ap(r["municipality"]) for r in sorted(rs, key=lambda r: (r["map"], r["order"]))))
    comarques = list(OD.fromkeys(r["comarca"] for r in sorted(rs, key=lambda r: (r["map"], r["order"]))))
    # Una sola comarca: els municipis (p. ex. Barcelonès Nord); si no, les comarques
    region = join_i(sorted(muns, key=lambda m: slugify(re.sub(r"^(El|La|Els|Les|L') ?", "", m))) if len(comarques) == 1 else comarques) + (f" (sense {SHORT[city]})" if city else "")
    t = OD(slug=slug, name=name, kind="territory", title=title, region=name,
           summary=f"{n_rutes(len(rs))} de l'economia social i solidària en {len(muns)} {'municipi' if len(muns) == 1 else 'municipis'}.",
           intro="Rutes a peu per fer el temps de reflexió de cada passa, des d'entitats de l'economia social i solidària.")
    if city:
        crs = pages[{v: k for k, v in CITY.items()}[city]]
        t["see_also"] = [OD(text=f"{CITY_NAME[city]} té pàgina pròpia, amb {n_rutes(len(crs))} d'aquest curs.", city=city, course="dia")]
    t["zones"] = OD(by="section", label="Vés directament al teu poble", placeholder="Tria un poble", back="Canvia de poble")
    t["blocks"] = [dia_block(rs, sections_by="municipality")]
    open(os.path.join(DATA, f"{slug}.json"), "w", encoding="utf-8").write(dumps(t))
    site_terr.append(OD(slug=slug, name=name, region=region, icon=icon))
    print(f"{slug}: {len(rs)} rutes, {len(muns)} municipis, {len(t['blocks'][0]['groups'])} mapes · {region}")

# ---------- ciutats ----------
# L'Hospitalet: ciutat nova (només aquest curs de moment)
hrs = pages["L’Hospitalet de Llobregat"]
hosp = OD(slug="l-hospitalet", name="L'Hospitalet de Llobregat", region="Barcelonès",
          summary=f"{n_rutes(len(hrs))} des d'entitats de l'economia social i solidària.",
          intro="Rutes a peu per fer el temps de reflexió de cada passa. Cada curs té les seves rutes: tria el teu i camina.",
          blocks=[dia_block(hrs)])
open(os.path.join(DATA, "l-hospitalet.json"), "w", encoding="utf-8").write(dumps(hosp))

prs, vrs, ors, brs = pages["el Prat de Llobregat"], pages["Vic"], pages["Olot"], pages["Barcelona"]
set_block(os.path.join(DATA, "el-prat.json"), dia_block(prs),
          summary=f"17 circuits urbans, 7 rutes des dels equipaments, 9 pel Delta del Llobregat i {len(prs)} des de l'economia social.")
set_block(os.path.join(DATA, "vic.json"), dia_block(vrs),
          summary="45 rutes curtes i circulars: pels parcs, des dels CAP i hospitals, des dels equipaments comunitaris i des de l'economia social.")
set_block(os.path.join(DATA, "olot.json"), dia_block(ors),
          summary="14 rutes curtes i circulars, des dels CAP, l'hospital, places, ponts i parcs, i des de l'economia social.")
set_block(os.path.join(DATA, "barcelona.json"),
          dia_block(brs, sections_by="district", sec_prefix=f"{ANCHOR}-", zones=OD(by="section")),
          summary=f"{422 + len(brs)} rutes repartides pels 10 districtes de la ciutat.")

# ---------- site.json: territoris i l'Hospitalet ----------
p = os.path.join(DATA, "site.json")
s = open(p, encoding="utf-8").read()
lines = ",\n".join("    " + json.dumps(t, ensure_ascii=False).replace('", "', '", "') for t in site_terr)
s, k = re.subn(r'"territories": \[\n.*?\n  \]', '"territories": [\n' + lines + "\n  ]", s, count=1, flags=re.S)
assert k == 1
if '"slug": "l-hospitalet"' not in s:
    old = '    {"slug": "olot",'
    assert old in s
    s = s.replace(old, '    {"slug": "l-hospitalet", "name": "L\'Hospitalet de Llobregat", "region": "Barcelonès", "icon": "users-three"},\n' + old, 1)
lo, hi = time_range(R)
faq_add = (f" Les rutes de l'economia social i solidària, a Barcelona, l'Hospitalet i molts pobles i ciutats de Catalunya, "
           f"fan {km_range(R)} (uns {lo}–{hi} minuts).")
anchor = " A cada ruta hi trobaràs els quilòmetres i el temps aproximat, caminant i amb pauses."
if "Les rutes de l'economia social i solidària" not in s:
    assert s.count(anchor) == 1
    s = s.replace(anchor, faq_add + anchor)
open(p, "w", encoding="utf-8").write(s)

print(f"Ciutats: Barcelona {len(brs)}, el Prat {len(prs)}, l'Hospitalet {len(hrs)}, Olot {len(ors)}, Vic {len(vrs)}. Total {len(R)}.")
print("FAQ:", faq_add)
