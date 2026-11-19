#!/usr/bin/env python3
"""Rutes des d'entitats del Tercer Sector Social de Berga, Olot, Ripoll i la Seu d'Urgell
(32 rutes, curs `cuidar`). Crea data/berga.json, data/ripoll.json i data/la-seu-d-urgell.json (pàgines
de ciutat), afegeix el bloc `cuidar` a data/olot.json, posa les ciutats a data/site.json › cities i a
data/comarques.json, i escriu els punts d'inici a data/inicis.json. Es pot tornar a executar.

Font: tools/tts_comarcals.tsv (codi, entitat, km, lat/lon d'inici, id de Wikiloc, descripció, adreça), fet
dels CSV de Drive «rutes_<població>.csv» (carpeta Ciutats › <població> › Taula del Tercer Sector), del CSV
«Wikiloc - Taula del Tercer Sector - Berga, Olot, Ripoll i la Seu d'Urgell» i del document de
descripcions. Les observacions internes (trànsit, camins de terra, locals compartits) no es publiquen.
"""
import csv, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
rows = list(csv.DictReader((ROOT / "tools/tts_comarcals.tsv").open(encoding="utf-8"), delimiter="\t"))

CITIES = {
 "OLO": dict(file="olot", nom="Olot", de="d'Olot", maps=[("1y1Ep2kCk2pB1clUc_4cRfVaOWKl5VFg", 1, 7)]),
 "BER": dict(file="berga", nom="Berga", de="de Berga", region="Berguedà", icon="tree", comarca=["Berguedà", "Barcelona"],
             maps=[("1uf3qwwi-ESqp5GNFA7V9w1GszSieiBY", 1, 7)]),
 "RIP": dict(file="ripoll", nom="Ripoll", de="de Ripoll", region="Ripollès", icon="bank", comarca=["Ripollès", "Girona"],
             maps=[("1zHC0MZLMFQJSoASvPHkelTg_h0WmKO8", 1, 6)]),
 "SEU": dict(file="la-seu-d-urgell", nom="La Seu d'Urgell", de="de la Seu d'Urgell", region="Alt Urgell", icon="footprints", comarca=["Alt Urgell", "Lleida"],
             maps=[("1PWP6nlux9IPCir6tinzLg8O0jW0jUGo", 1, 6), ("1xq8OP3A4-BL5oeJjLDu___G8JarAEMg", 7, 12)]),
}

def cat_km(s): return f"{float(s):.1f}".replace(".", ",")

site_p, com_p, ini_p = ROOT / "data/site.json", ROOT / "data/comarques.json", ROOT / "data/inicis.json"
site = json.loads(site_p.read_text(encoding="utf-8"))
com = json.loads(com_p.read_text(encoding="utf-8"))
inicis = json.loads(ini_p.read_text(encoding="utf-8"))

def dump_inicis(d):  # mateix format que ja té el fitxer: una pàgina per bloc, una ruta per línia
    return "{\n" + ",\n".join(json.dumps(k, ensure_ascii=False) + ":{\n" + ",\n".join(f"{json.dumps(i)}:{json.dumps(c)}" for i, c in v.items()) + "\n}" for k, v in d.items()) + "\n}\n"

NEW_CITIES = []
for pre, cfg in CITIES.items():
    rs = sorted((r for r in rows if r["codi"].startswith(pre)), key=lambda r: r["codi"])
    n = len(rs); assert n == sum(b - a + 1 for _, a, b in cfg["maps"]), (pre, n)
    kms = [float(r["km"]) for r in rs]
    lo, hi = cat_km(min(kms)), cat_km(max(kms))
    tmin, tmax = 5 * round(min(kms) * 12 / 5), 5 * round(max(kms) * 15 / 5)
    routes, maps = [], []
    for i, r in enumerate(rs, 1):
        assert int(r["codi"][-3:]) == i
        km = float(r["km"])
        x = {"n": i, "name": r["entitat"], "info": f"{cat_km(r['km'])} km aprox. · {round(km*12)}–{round(km*15)} min caminant · circular"}
        if r["adreca"].strip(): x["address"] = r["adreca"].strip()
        x["desc"] = r["descripcio"]
        x["wikiloc"] = f"https://www.wikiloc.com/wikiloc/view.do?id={r['wikiloc']}"
        routes.append(x)
        inicis.setdefault("olot" if pre == "OLO" else cfg["file"], {})
    for k, (mid, a, b) in enumerate(cfg["maps"], 1):
        sub = rs[a - 1:b]
        lat = sum(float(r["lat"]) for r in sub) / len(sub); lon = sum(float(r["lon"]) for r in sub) / len(sub)
        suf = f" ({k}/{len(cfg['maps'])})" if len(cfg["maps"]) > 1 else ""
        label = f"Rutes {a} a {b}" if len(cfg["maps"]) > 1 else f"{n} rutes des d'entitats del Tercer Sector Social"
        maps.append({"mid": mid, "title": f"{cfg['nom']} · entitats del Tercer Sector Social{suf}", "ll": f"{lat:.4f},{lon:.4f}", "z": 14,
                     "label": label, "routes": list(range(a, b + 1))})
    block = {"course": "cuidar",
        "text": f"{n} rutes circulars, " + (f"d'uns {lo} km" if lo == hi else f"de {lo} a {hi} km") + f" (uns {tmin}–{tmax} minuts caminant), que surten d'una entitat del Tercer Sector Social {cfg['de']} i hi tornen: una ruta per entitat. Són un temps per caminar i reflexionar: portar a la vida quotidiana el que has après al curs «Quan cuidar-nos és una tasca col·lectiva», adonar-te de com et sents i pensar en petites accions que contribueixin al teu benestar i al de les persones que t'envolten. Tria l'entitat que et quedi més a prop i camina-hi amb calma.",
        "summary": f"{n} rutes des d'entitats del Tercer Sector Social",
        "notice": {"title": "Traçats orientatius", "html": [
            "Els traçats s'han reconstruït sobre OpenStreetMap a partir de la ubicació de cada entitat: no són traçats oficials. Camina amb atenció al trànsit i a l'estat dels camins.",
            "Més propostes i recursos a <a href=\"https://elarasocial.com/\" target=\"_blank\" rel=\"noopener\">elarasocial.com</a>."]},
        "groups": [{"title": f"Les {n} rutes", "maps": maps, "routes": routes}]}
    path = ROOT / f"data/{cfg['file']}.json"
    if pre == "OLO":
        d = json.loads(path.read_text(encoding="utf-8"))
        i = next(i for i, b in enumerate(d["blocks"]) if b["course"] == "cuidar")
        d["blocks"][i] = block
        d["summary"] = "23 rutes curtes i circulars, des dels CAP, l'hospital, places, ponts i parcs, des de l'economia social i des d'entitats del Tercer Sector Social."
        slug = "olot"
    else:
        d = {"slug": cfg["file"], "name": cfg["nom"], "region": cfg["region"],
             "summary": f"{n} rutes circulars des d'entitats del Tercer Sector Social.",
             "intro": "Rutes a peu per fer el temps de reflexió de cada passa. Cada curs té les seves rutes: tria el teu i camina.",
             "blocks": [block]}
        slug = cfg["file"]
        NEW_CITIES.append((slug, cfg))
    path.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    ids = {f"quan-cuidar-nos-ruta-{r['n']}": f"{rs[r['n']-1]['lat']},{rs[r['n']-1]['lon']}" for r in routes}
    inicis[slug] = {**{k: v for k, v in inicis.get(slug, {}).items() if not k.startswith("quan-cuidar-nos-")}, **ids}
    print(cfg["nom"], n, "rutes", lo, "-", hi, "km")

# site.json › cities i comarques.json: només s'hi afegeixen les línies noves (no es reescriu el fitxer)
st, ct = site_p.read_text(encoding="utf-8"), com_p.read_text(encoding="utf-8")
for slug, cfg in NEW_CITIES:
    if f'"slug": "{slug}"' not in st:
        line = f'    {{"slug": "{slug}", "name": "{cfg["nom"]}", "region": "{cfg["region"]}", "icon": "{cfg["icon"]}"}}'
        lines = st.split("\n"); a = next(i for i, l in enumerate(lines) if l.startswith('  "cities": ['))
        b = next(i for i in range(a + 1, len(lines)) if lines[i].startswith("  ]"))
        items = [l.rstrip(",") for l in lines[a + 1:b]] + [line]
        items.sort(key=lambda l: json.loads(l.strip())["name"].lower().replace("'", "!"))
        lines[a + 1:b] = [l + ("," if k < len(items) - 1 else "") for k, l in enumerate(items)]
        st = "\n".join(lines)
    if f'"{cfg["nom"]}":' not in ct:
        entries = ct.split("\n"); a = next(i for i, l in enumerate(entries) if l.startswith('  "Amposta"'))
        b = next(i for i, l in enumerate(entries) if l.strip() == "}")
        import re, unicodedata
        key = lambda n: re.sub(r"[^a-z0-9]+", "", unicodedata.normalize("NFKD", re.sub(r"^(El|La|Els|Les|L') ?", "", n)).encode("ascii", "ignore").decode().lower())
        new = f'  {json.dumps(cfg["nom"], ensure_ascii=False)}: {json.dumps(cfg["comarca"], ensure_ascii=False)},'
        pos = next((k for k in range(a, b) if key(json.loads("{" + entries[k].rstrip(",") + "}").popitem()[0]) > key(cfg["nom"])), b)
        entries.insert(pos, new)
        last = next(k for k in range(len(entries) - 1, -1, -1) if entries[k].startswith('  "'))
        entries = [l.rstrip(",") if k == last else l for k, l in enumerate(entries)]
        ct = "\n".join(entries)
site_p.write_text(st, encoding="utf-8"); com_p.write_text(ct, encoding="utf-8")
ini_p.write_text(dump_inicis(inicis), encoding="utf-8")
