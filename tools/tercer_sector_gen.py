#!/usr/bin/env python3
"""Afegeix a Vic i al Prat la part «Rutes des d'entitats del Tercer Sector Social» al curs
«Quan cuidar-nos és una tasca col·lectiva» (course `cuidar`) de data/vic.json i data/el-prat.json.

Font: tools/tercer_sector.tsv (còpia dels fulls de Drive «Enllaços Wikiloc - Vic i El Prat de
Llobregat», «Descripcions breus de les entitats…» i «Rutes … - Taula Tercer Sector (final)»;
els fulls són la font de veritat). Les coordenades dels fulls venien amb separadors de milers
(4.192.785 = 41,92785) i aquí ja són decimals. Es pot tornar a executar: substitueix la part.

Numeració: a la web continua la del curs (Vic 17–35, El Prat 8–20). Als fulls, als mapes de
My Maps i als títols de Wikiloc les rutes s'anomenen amb el número antic (Vic 2–20, El Prat 16–28);
`web_n = n + offset`. Els mapes es lliguen per entitat (la capa del mapa porta el nom de l'entitat).
"""
import csv, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
COURSE = "cuidar"
rows = list(csv.DictReader((ROOT / "tools/tercer_sector.tsv").open(encoding="utf-8"), delimiter="\t"))

MAPS = {  # ciutat → [(mid, rutes amb el número dels fulls)]
    "Vic": [("1EeIYqI3O4yHLdjO6YXLfvP3Sjb9LBno", range(2, 9)), ("1xkX8907B53DRrZD-Ek5HxoPPrnutX9A", range(9, 16)), ("1mqIFwoBL7D1hGrLIsusDCvdk90EXZWg", range(16, 21))],
    "El Prat de Llobregat": [("1IE-2mk4z3Zqp-VGCz36IwpE1-9UgCLY", range(16, 23)), ("1f7j0KnkWPQlTHQ_cK7XfbOLkpqIbqN8", range(23, 29))],
}
NOTES = {
    ("Vic", 3): "Té un tram de camí sense asfaltar (al voltant del 19 % del recorregut).",
    ("El Prat de Llobregat", 21): "Passa per una zona industrial i a prop de la carretera de l'Aviació: vigila el trànsit.",
    ("El Prat de Llobregat", 28): "Passa per una zona industrial i a prop de la carretera de l'Aviació: vigila el trànsit.",
}
CFG = {
    "Vic": dict(file="vic", nom="Vic", de="de Vic", ciutat_adr="Vic", offset=15,
        first_title="Rutes des dels equipaments comunitaris", summary="35 rutes des d'equipaments i entitats socials",
        block="Hi ha dos tipus de rutes: 16 rutes curtes, d'1,8 a 2 km, que surten d'equipaments comunitaris, i 19 rutes més llargues, de 3,7 a 4,2 km, que surten d'entitats del Tercer Sector Social. Totes són circulars i tornen al punt de sortida."),
    "El Prat de Llobregat": dict(file="el-prat", nom="el Prat de Llobregat", de="del Prat de Llobregat", ciutat_adr="el Prat de Llobregat", offset=-8,
        first_title="Rutes des dels equipaments municipals", summary="20 rutes des d'equipaments i entitats socials",
        block="Hi ha dos tipus de rutes: 7 rutes que surten d'equipaments municipals i 13 rutes circulars, de 3,7 a 4,6 km, que surten d'entitats del Tercer Sector Social. Totes comencen i acaben al mateix lloc."),
}

def cat_km(s):
    return f"{float(s):.1f}".replace(".", ",")

for ciutat, cfg in CFG.items():
    rs = sorted((r for r in rows if r["ciutat"] == ciutat), key=lambda r: int(r["n"]))
    off = cfg["offset"]
    kms = [float(r["km"]) for r in rs]
    path = ROOT / f"data/{cfg['file']}.json"
    d = json.loads(path.read_text(encoding="utf-8"))
    maps, routes = [], []
    for mid, rng in MAPS[ciutat]:
        sub = [r for r in rs if int(r["n"]) in rng]
        lat = sum(float(r["lat"]) for r in sub) / len(sub)
        lon = sum(float(r["lon"]) for r in sub) / len(sub)
        a, b = min(rng) + off, max(rng) + off
        maps.append({"mid": mid, "title": f"{cfg['nom']} · entitats del Tercer Sector Social, rutes {a}-{b}",
                     "ll": f"{lat:.4f},{lon:.4f}", "z": 14, "label": f"Rutes {a} a {b}", "routes": [n + off for n in rng]})
    for r in rs:
        km = float(r["km"])
        x = {"n": int(r["n"]) + off, "name": r["entitat"],
             "info": f"{cat_km(r['km'])} km aprox. · {round(km*12)}–{round(km*15)} min caminant · circular",
             "address": f"{r['adreca']}, {cfg['ciutat_adr']}"}
        note = NOTES.get((ciutat, int(r["n"])))
        if note: x["note"] = note
        x["desc"] = r["descripcio"]
        x["wikiloc"] = r["wikiloc"]
        routes.append(x)
    n_new = len(routes)
    lo, hi = cat_km(min(kms)), cat_km(max(kms))
    tmin, tmax = 5*round(min(kms)*12/5), 5*round(max(kms)*15/5)
    block = next(b for b in d["blocks"] if b["course"] == COURSE)
    if "parts" in block:
        first = block["parts"][0]
    else:
        first = {"id": "equipaments", "title": cfg["first_title"], "nav": cfg["first_title"], "text": block["text"], "groups": block["groups"]}
    new = {"id": "tercer-sector", "title": "Rutes des d'entitats del Tercer Sector Social", "nav": "Entitats del Tercer Sector Social",
        "text": f"{n_new} rutes circulars, de {lo} a {hi} km (uns {tmin}–{tmax} minuts caminant), que surten d'una entitat del Tercer Sector Social {cfg['de']} i hi tornen. Són un temps per caminar i reflexionar: portar a la vida quotidiana el que has après al curs «Quan cuidar-nos és una tasca col·lectiva», adonar-te de com et sents i pensar en petites accions que contribueixin al teu benestar i al de les persones que t'envolten. Tria l'entitat que et quedi més a prop i camina-hi amb calma.",
        "notice": {"title": "Traçats orientatius", "html": [
            "Els traçats s'han reconstruït sobre OpenStreetMap a partir de l'adreça de cada entitat: no són traçats oficials. Camina amb atenció al trànsit i a l'estat dels camins.",
            "Més propostes i recursos a <a href=\"https://elarasocial.com/\" target=\"_blank\" rel=\"noopener\">elarasocial.com</a>."]},
        "groups": [{"id": "tercer-sector-rutes", "title": f"Les {n_new} rutes", "maps": maps, "routes": routes}]}
    block["parts"] = [first, new]
    block.pop("groups", None)
    block["text"] = cfg["block"]
    block["summary"] = cfg["summary"]
    path.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(ciutat, n_new, "rutes", lo, "-", hi, "km; web", routes[0]["n"], "-", routes[-1]["n"])
