#!/usr/bin/env python3
"""Afegeix a cada ruta de l'economia social (bloc "dia") l'enllaç a la seva ruta de Wikiloc
(usuari lespiral.elarasocial), a partir de tools/ess_wikiloc.csv.

El CSV surt de «Registre_publicacio_Wikiloc.csv» (Drive, carpeta de ChatGPT, 06/11/2026):
una ruta de Wikiloc per entitat. A la web hi ha una ruta per seu, i el primer nom de la ruta
és l'entitat principal de la seu (la de la capa de My Maps): se n'agafa la ruta de Wikiloc.

Ús (des de l'arrel del repositori): python3 -I tools/ess_wikiloc.py
Cal tornar-lo a executar després de tools/ess_site_data.py, que reescriu els blocs "dia"."""
import csv, glob, json, os, re, sys, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
CSV = os.path.join(ROOT, "tools", "ess_wikiloc.csv")

# Entitats que tenen més d'una ruta a Wikiloc (eren a més d'un ateneu): la que es fa servir.
# XES, GRACER i la Confederació: les dues primeres tenen el mateix GPX (mateix sha256).
PREFER = {
    "Xarxa d'Economia Solidària (XES)": "01-019",
    "Confederació de Cooperatives de Catalunya": "08-024",
    "GRACER": "04-007",
    "Fundació Espigoladors": "03-026",   # la del Baix Llobregat (ruta del Prat)
}


def dumps(obj):   # el mateix format que tools/ess_site_data.py
    out = json.dumps(obj, ensure_ascii=False, indent=2)
    pat = re.compile(r'\[\n\s+((?:(?:-?\d+|"[^"\n]{0,40}"),\n\s+)*(?:-?\d+|"[^"\n]{0,40}"))\n\s+\]')
    return pat.sub(lambda m: "[" + ", ".join(x.strip() for x in m.group(1).split(",\n")) + "]", out) + "\n"


def norm(s):
    s = s.replace("’", "'").lower()
    s = "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


rows = list(csv.DictReader(open(CSV, encoding="utf-8"), delimiter=";"))
by_id = {r["id_entitat"]: r for r in rows}
prefer = {norm(k): v for k, v in PREFER.items()}


def find(route):
    name = norm(route["name"])
    cands = [r for r in rows if name.startswith(norm(r["nom"]))]
    if not cands:
        sys.exit(f"Sense ruta de Wikiloc: {route['name']}")
    best = max(len(norm(r["nom"])) for r in cands)
    cands = [r for r in cands if len(norm(r["nom"])) == best]
    key = norm(cands[0]["nom"])
    if key in prefer:
        return by_id[prefer[key]]
    if len(cands) > 1:
        # la mateixa entitat a diversos llocs: el municipi de l'adreça surt a l'adreça de Wikiloc
        mun = norm(route["address"].rsplit(",", 1)[1]).replace(" ", "-")
        mun = re.sub(r"^(el|la|les|els|l)-", "", mun)
        cands = [r for r in cands if mun in r["url_wikiloc"]]
    if len(cands) != 1:
        sys.exit(f"Ruta de Wikiloc dubtosa ({len(cands)}): {route['name']} · {route['address']}")
    return cands[0]


def routes_in(o):
    if isinstance(o, dict):
        for k, v in o.items():
            if k == "routes" and isinstance(v, list) and v and isinstance(v[0], dict):
                yield from v
            else:
                yield from routes_in(v)
    elif isinstance(o, list):
        for v in o:
            yield from routes_in(v)


total, used = 0, {}
for path in sorted(glob.glob(os.path.join(DATA, "*.json"))):
    if path.endswith("site.json"):
        continue
    d = json.load(open(path, encoding="utf-8"))
    changed = False
    for b in d.get("blocks", []):
        if b.get("course") != "dia":
            continue
        for r in routes_in(b):
            w = find(r)
            used.setdefault(w["id_entitat"], []).append(r["name"])
            new = {}
            for k, v in r.items():
                if k != "wikiloc":
                    new[k] = v
                if k == "desc" or (k == "address" and "desc" not in r):
                    new["wikiloc"] = w["url_wikiloc"]
            if "wikiloc" not in new:
                new["wikiloc"] = w["url_wikiloc"]
            if new != r:
                r.clear(); r.update(new); changed = True
            total += 1
    if changed:
        open(path, "w", encoding="utf-8").write(dumps(d))

dup = {k: v for k, v in used.items() if len(v) > 1}
if dup:
    sys.exit(f"Una ruta de Wikiloc a més d'una ruta de la web: {dup}")
print(f"{total} rutes amb enllaç a Wikiloc")
