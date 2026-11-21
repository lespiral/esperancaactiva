#!/usr/bin/env python3
"""Rutes del curs «Quan sostenir la vida es fa difícil» (bloc `dia`) des de cooperatives i entitats d'economia
solidària: Berga (3), Ripoll (3), la Seu d'Urgell (1), Olot (2) i Osona (6, a la pàgina de la Catalunya Central,
per municipi). Només AFEGEIX: les rutes que ja hi eren (les 3 d'Olot, les 8 de la Catalunya Central, la de Vic)
es queden tal qual. Escriu també els punts d'inici a data/inicis.json. Es pot tornar a executar.

Font: tools/sostenir_comarcals.tsv, fet de les fitxes (fitxes_*_sostenir.md) i dels KML de cada ciutat a Drive.
Adreça només on la fitxa en dona una; les observacions d'accessibilitat de la fitxa es publiquen com a nota.
"""
import csv, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
rows = list(csv.DictReader((ROOT / "tools/sostenir_comarcals.tsv").open(encoding="utf-8"), delimiter="\t"))
by = {}
for r in rows:
    by.setdefault(r["ciutat"], []).append(r)

MAPS = {"berga": "1Jb5n5zbO4zR0tAEuFPHsl9k3CDD1mLk", "ripoll": "1RVZqOlQNlK7fOk5a2v4xBfemvnqp5HI",
        "seu": "1ro-2RoWoXAH6YccM--zvnfeXR7UFu1U", "olot": "1pJz5IBuIboQkVKpSS1B9VXXTmDEaZKE",
        "osona": "1MFsFJaw1_t1G1H0K4wYnDMKxgKw655E"}
FILE = {"berga": "berga", "ripoll": "ripoll", "seu": "la-seu-d-urgell", "olot": "olot", "osona": "catalunya-central"}
NOM = {"berga": "Berga", "ripoll": "Ripoll", "seu": "la Seu d'Urgell", "olot": "Olot", "osona": "Osona"}
PID = "cooperatives-i-economia-solidaria"
GID = "cooperatives-rutes"
ANCHOR = "quan-sostenir"
LINK = "Més propostes i recursos a <a href=\"https://elarasocial.com/\" target=\"_blank\" rel=\"noopener\">elarasocial.com</a>."
NOTICE = {"title": "Traçats orientatius", "html": [
    "Els traçats s'han reconstruït sobre OpenStreetMap a partir de la ubicació de cada cooperativa o entitat: no són traçats oficials, i els punts de sortida són aproximats. Camina amb atenció al trànsit i a l'estat dels camins.", LINK]}
TEXT = ("Surten de cooperatives i d'entitats d'economia solidària: espais on les persones treballen i es relacionen cooperant en lloc de competir. "
        "Tria la que tinguis més a prop i fes-hi el temps de reflexió de cada passa.")


def ckm(s, dec=2): return f"{float(s):.{dec}f}".replace(".", ",")


def route(r, n):
    x = {"n": n, "name": r["nom"],
         "info": f"{ckm(r['km'])} km · {r['cam_min']}–{r['cam_max']} min caminant · {r['pau_min']}–{r['pau_max']} min amb pauses · circular"}
    if r["adreca"]: x["address"] = r["adreca"]
    if r["nota"]: x["note"] = r["nota"]
    x["wikiloc"] = f"https://ca.wikiloc.com/wikiloc/view.do?id={r['wikiloc']}"
    return x


def dump_inicis(d):
    return "{\n" + ",\n".join(json.dumps(k, ensure_ascii=False) + ":{\n" + ",\n".join(f"{json.dumps(i)}:{json.dumps(c)}" for i, c in v.items()) + "\n}" for k, v in d.items()) + "\n}\n"


def ll_of(rs):
    n = len(rs)
    return f"{sum(float(r['lat']) for r in rs) / n:.4f},{sum(float(r['lon']) for r in rs) / n:.4f}"


def put_inicis(inicis, slug, ids, after_prefix):
    cur = inicis.setdefault(slug, {})
    ids = {k: v for k, v in ids.items()}
    keys = [k for k in cur if k.startswith(after_prefix)] if after_prefix else []
    last = max(keys, key=lambda k: list(cur).index(k)) if keys else None
    new = {}
    for k, v in cur.items():
        if k not in ids: new[k] = v
        if k == last: new.update(ids)
    if last is None: new.update(ids)
    inicis[slug] = new


ini_p = ROOT / "data/inicis.json"
inicis = json.loads(ini_p.read_text(encoding="utf-8"))

for key, rs in by.items():
    slug = FILE[key]
    path = ROOT / f"data/{slug}.json"
    d = json.loads(path.read_text(encoding="utf-8"))
    rs = sorted(rs, key=lambda r: r["codi"])
    n = len(rs)
    kms = [float(r["km"]) for r in rs]
    ids = {}
    if key == "osona":
        b = next(b for b in d["blocks"] if b["course"] == "dia")
        if any(g["id"] == "osona-rutes" for g in b["groups"]):
            print("Osona: ja hi és; res a fer"); continue
        secs, order = {}, []
        for r in rs:
            secs.setdefault(r["seccio"], []).append(r)
        sections = []
        for sec, srs in secs.items():
            sid = {"Torelló": "torello-osonament"}.get(sec)
            s = {"title": sec}
            if sid: s["id"] = sid; s["nav"] = "Torelló · Osonament"   # «nav»: l'etiqueta al desplegable «Vés directament al teu poble» (si no, hi hauria dos «Torelló»)
            s["routes"] = [route(x, i + 1) for i, x in enumerate(srs)]
            sections.append(s)
            import unicodedata, re
            sl = sid or re.sub(r"[^a-z0-9]+", "-", unicodedata.normalize("NFKD", sec).encode("ascii", "ignore").decode().lower()).strip("-")
            for i, x in enumerate(srs):
                ids[f"{sl}-ruta-{i + 1}"] = f"{x['lat']},{x['lon']}"
        b["groups"].append({"id": "osona-rutes", "title": "Osona", "maps": [{
            "mid": MAPS[key], "title": "Osona · cooperatives i economia solidària", "ll": ll_of(rs), "z": 10,
            "label": f"{n} rutes des de cooperatives i economia solidària"}], "sections": sections})
        allr = [r for g in b["groups"] for s in g["sections"] for r in s["routes"]]
        mun = sum(len(g["sections"]) for g in b["groups"])
        allkm = [float(r["info"].split(" km")[0].replace(",", ".")) for r in allr]
        b["summary"] = f"{len(allr)} rutes des de l'economia social"
        b["text"] = (f"{len(allr)} rutes circulars curtes, d'{ckm(min(allkm), 1)} a {ckm(max(allkm), 1)} km, que surten d'una entitat de l'economia social i solidària o d'una cooperativa i hi tornen: "
                     "cooperatives, associacions i fundacions que treballen per l'habitatge, la feina, la cultura, l'alimentació o les cures. Comencen i acaben al carrer, davant de l'entitat: no cal entrar-hi.")
        d["summary"] = f"{len(allr)} rutes de l'economia social i solidària en {mun} municipis."
        d["intro"] = d["intro"]
        put_inicis(inicis, slug, ids, None)
    else:
        b = next((b for b in d["blocks"] if b["course"] == "dia"), None)
        if b is None:
            routes = [route(r, i + 1) for i, r in enumerate(rs)]
            b = {"course": "dia",
                 "text": (f"1 ruta circular curta, d'{ckm(kms[0])} km, que surt d'una cooperativa o d'una entitat d'economia solidària i hi torna. Comença i acaba al carrer, davant de l'entitat: no cal entrar-hi."
                          if n == 1 else
                          f"{n} rutes circulars curtes, de {ckm(min(kms))} a {ckm(max(kms))} km, que surten d'una cooperativa o d'una entitat d'economia solidària i hi tornen. Comencen i acaben al carrer, davant de l'entitat: no cal entrar-hi."),
                 "summary": f"{n} {'ruta' if n == 1 else 'rutes'} des de cooperatives i economia solidària",
                 "notice": NOTICE,
                 "groups": [{"title": "La ruta" if n == 1 else f"Les {n} rutes", "maps": [{
                     "mid": MAPS[key], "title": f"{d['name']} · cooperatives i economia solidària", "ll": ll_of(rs), "z": 14,
                     "label": f"{n} {'ruta' if n == 1 else 'rutes'} des de cooperatives i economia solidària"}], "routes": routes}]}
            # el bloc `dia` va darrere dels que ja hi eren (l'ordre dels cursos el posa build.py)
            d["blocks"].append(b)
            ids = {f"{ANCHOR}-ruta-{x['n']}": f"{r['lat']},{r['lon']}" for x, r in zip(routes, rs)}
        elif key != "olot":
            print(NOM[key], ": ja hi és; res a fer"); continue
        else:   # Olot: el bloc passa a tenir dues parts; la que hi era es queda igual (grup, rutes, mapa)
            if any(p.get("id") == PID for p in b.get("parts", [])):
                print(NOM[key], ": ja hi és; res a fer"); continue
            old_g = b.pop("groups")
            old_routes = [r for g in old_g for r in g["routes"]]
            nmax = max(r["n"] for r in old_routes)
            routes = [route(r, nmax + i + 1) for i, r in enumerate(rs)]
            old_kms = [float(r["info"].split(" km")[0].replace(",", ".")) for r in old_routes]
            p0 = {"id": "economia-social", "title": "Rutes des d'entitats de l'economia social i solidària", "nav": "Economia social i solidària",
                  "text": "Surten d'entitats de l'economia social i solidària que comparteixen seu: les tres rutes surten del mateix lloc. Tria la que tinguis més a prop i fes-hi el temps de reflexió de cada passa.",
                  "groups": old_g, "tele": True}
            p1 = {"id": PID, "title": "Rutes des de cooperatives i economia solidària", "nav": "Cooperatives i economia solidària", "text": TEXT,
                  "notice": NOTICE, "groups": [{"id": GID, "title": f"Les {n} rutes", "maps": [{
                      "mid": MAPS[key], "title": f"{d['name']} · cooperatives i economia solidària", "ll": ll_of(rs), "z": 11,
                      "label": f"{n} rutes des de cooperatives i economia solidària", "routes": [x["n"] for x in routes]}], "routes": routes}],
                  "tele": True}
            b["parts"] = [p0, p1]
            tot = len(old_routes) + n
            b["summary"] = f"{tot} rutes des de l'economia social, cooperatives i entitats solidàries"
            b["text"] = (f"Hi ha dos tipus de rutes: {len(old_routes)} rutes, de {ckm(min(old_kms), 1)} a {ckm(max(old_kms), 1)} km, que surten d'entitats de l'economia social i solidària, "
                         f"i {n} rutes més curtes, d'{ckm(min(kms))} a {ckm(max(kms))} km, que surten de cooperatives. Totes són circulars i tornen al punt de sortida.")
            ids = {f"{ANCHOR}-ruta-{x['n']}": f"{r['lat']},{r['lon']}" for x, r in zip(routes, rs)}
        put_inicis(inicis, slug, ids, ANCHOR + "-ruta-")
    path.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(NOM[key], n, "rutes noves")

ini_p.write_text(dump_inicis(inicis), encoding="utf-8")
