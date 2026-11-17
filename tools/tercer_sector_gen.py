#!/usr/bin/env python3
"""Afegeix a Vic i al Prat la part «Rutes des d'entitats del Tercer Sector Social»
(curs «Quan sostenir la vida es fa difícil») a data/vic.json i data/el-prat.json.

Font: tools/tercer_sector.tsv (còpia dels fulls de Drive «Enllaços Wikiloc - Vic i El Prat de
Llobregat», «Descripcions breus de les entitats…» i «Rutes … - Taula Tercer Sector (final)»;
els fulls són la font de veritat). Les coordenades dels fulls venien amb separadors de milers
(4.192.785 = 41,92785) i aquí ja són decimals. Es pot tornar a executar: substitueix la part.
"""
import csv, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
rows = list(csv.DictReader((ROOT / "tools/tercer_sector.tsv").open(encoding="utf-8"), delimiter="\t"))

MAPS = {  # ciutat → [(mid, rutes, títol)]
    "Vic": [("1EeIYqI3O4yHLdjO6YXLfvP3Sjb9LBno", range(2, 9)), ("1xkX8907B53DRrZD-Ek5HxoPPrnutX9A", range(9, 16)), ("1mqIFwoBL7D1hGrLIsusDCvdk90EXZWg", range(16, 21))],
    "El Prat de Llobregat": [("1IE-2mk4z3Zqp-VGCz36IwpE1-9UgCLY", range(16, 23)), ("1f7j0KnkWPQlTHQ_cK7XfbOLkpqIbqN8", range(23, 29))],
}
NOTES = {
    ("Vic", 3): "Té un tram de camí sense asfaltar (al voltant del 19 % del recorregut).",
    ("El Prat de Llobregat", 21): "Passa per una zona industrial i a prop de la carretera de l'Aviació: vigila el trànsit.",
    ("El Prat de Llobregat", 28): "Passa per una zona industrial i a prop de la carretera de l'Aviació: vigila el trànsit.",
}
CFG = {
    "Vic": dict(file="vic", nom="Vic", de="de Vic", total=20, label="19 rutes des d'entitats del Tercer Sector Social",
        summary="20 rutes des d'entitats socials",
        block="Hi ha dos tipus de rutes: 1 ruta curta, d'1,9 km, que surt d'una entitat de l'economia social i solidària, i 19 rutes més llargues, de 3,7 a 4,2 km, que surten d'entitats del Tercer Sector Social. Totes són circulars i tornen al punt de sortida."),
    "El Prat de Llobregat": dict(file="el-prat", nom="el Prat de Llobregat", de="del Prat de Llobregat", total=28, label="13 rutes des d'entitats del Tercer Sector Social",
        summary="28 rutes des d'entitats socials",
        block="Hi ha dos tipus de rutes: 15 rutes curtes, d'1,6 a 2,1 km, que surten d'entitats de l'economia social i solidària, i 13 rutes més llargues, de 3,7 a 4,6 km, que surten d'entitats del Tercer Sector Social. Totes són circulars i tornen al punt de sortida."),
}

def cat_km(s):
    return f"{float(s):.1f}".replace(".", ",")

for ciutat, cfg in CFG.items():
    rs = [r for r in rows if r["ciutat"] == ciutat]
    rs.sort(key=lambda r: int(r["n"]))
    kms = [float(r["km"]) for r in rs]
    path = ROOT / f"data/{cfg['file']}.json"
    d = json.loads(path.read_text(encoding="utf-8"))
    maps, routes = [], []
    for mid, rng in MAPS[ciutat]:
        sub = [r for r in rs if int(r["n"]) in rng]
        lat = sum(float(r["lat"]) for r in sub) / len(sub)
        lon = sum(float(r["lon"]) for r in sub) / len(sub)
        a, b = min(rng), max(rng)
        maps.append({"mid": mid, "title": f"{cfg['nom']} · entitats del Tercer Sector Social, rutes {a}-{b}",
                     "ll": f"{lat:.4f},{lon:.4f}", "z": 14, "label": f"Rutes {a} a {b}", "routes": list(rng)})
    for r in rs:
        x = {"n": int(r["n"]), "name": r["entitat"], "info": f"{cat_km(r['km'])} km aprox. · circular"}
        n = NOTES.get((ciutat, int(r["n"])))
        if n: x["note"] = n
        x["desc"] = r["descripcio"]
        x["wikiloc"] = r["wikiloc"]
        routes.append(x)
    n_new = len(routes)
    lo, hi = cat_km(min(kms)), cat_km(max(kms))
    block = next(b for b in d["blocks"] if b["course"] == "dia")
    if "parts" in block:
        first = block["parts"][0]
    else:
        first = {"id": "economia-social", "title": "Rutes des de l'economia social", "text": block["text"], "groups": block["groups"]}
    new = {"id": "tercer-sector", "title": "Rutes des d'entitats del Tercer Sector Social", "nav": "Entitats del Tercer Sector Social",
        "text": f"{n_new} rutes circulars, de {lo} a {hi} km (aproximadament d'1 h a 1 h 15 caminant), que surten d'una entitat del Tercer Sector Social {cfg['de']} i hi tornen. Són un temps per caminar i reflexionar: portar a la vida quotidiana el que has après al curs «Quan sostenir la vida es fa difícil», adonar-te de com et sents i pensar en petites accions que contribueixin al teu benestar i al de les persones que t'envolten. Tria l'entitat que et quedi més a prop i camina-hi amb calma.",
        "notice": {"title": "Traçats orientatius", "html": [
            "Els traçats s'han reconstruït sobre OpenStreetMap a partir de l'adreça de cada entitat: no són traçats oficials. Camina amb atenció al trànsit i a l'estat dels camins.",
            "Més propostes i recursos a <a href=\"https://elarasocial.com/\" target=\"_blank\" rel=\"noopener\">elarasocial.com</a>."]},
        "groups": [{"id": "tercer-sector-rutes", "title": f"Les {n_new} rutes", "maps": maps, "routes": routes}]}
    for k in ("nav",):
        first.setdefault(k, first["title"])
    block["parts"] = [first, new]
    block.pop("groups", None)
    block["text"] = cfg["block"]
    block["summary"] = cfg["summary"]
    path.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(ciutat, n_new, "rutes", lo, "-", hi, "km")
