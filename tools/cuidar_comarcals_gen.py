#!/usr/bin/env python3
"""Rutes del curs «Quan cuidar-nos és una tasca col·lectiva» des de biblioteques i centres cívics i culturals:
Berga (3), Ripoll (3), la Seu d'Urgell (4), Olot (4) i Vic (1). Afegeix al bloc `cuidar` de cada ciutat una
part nova (la resta del bloc no es toca: les rutes de la Taula del Tercer Sector, o els equipaments de Vic, es
queden igual) i escriu els punts d'inici a data/inicis.json. Es pot tornar a executar.

Font: tools/cuidar_comarcals.tsv, fet del document de Drive «Info per a la web - curs cuidar-nos (rutes
biblioteques i centres).md» (enllaç del mapa, km, temps, Wikiloc, fitxes) i dels KML de la subcarpeta
«Biblioteques i centres (cuidar-nos)» de cada ciutat (punt d'inici). Només hi ha adreça on la fitxa en dona una
de comprovada; les observacions d'accessibilitat de la fitxa es publiquen com a nota de la ruta.
"""
import csv, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
rows = list(csv.DictReader((ROOT / "tools/cuidar_comarcals.tsv").open(encoding="utf-8"), delimiter="\t"))
by = {}
for r in rows:
    by.setdefault(r["ciutat"], []).append(r)

MAPS = {"berga": "11O2_OfH97sTK4YRgM6SDa2owJfhi-ms", "ripoll": "1_pk-FTwvRoVTeEV15oa83zf496Wl4zw",
        "seu": "1FIqJw2JrT7P1_wqNNBq17R5sVCIAUC0", "olot": "1prNciU5HmnasbsXxDXvHlWudcav7J34",
        "vic": "1jZ8jJ5wiPsmKa2mWo0g7VCS7jZiVaHU"}
FILE = {"berga": "berga", "ripoll": "ripoll", "seu": "la-seu-d-urgell", "olot": "olot", "vic": "vic"}
NOM = {"berga": "Berga", "ripoll": "Ripoll", "seu": "la Seu d'Urgell", "olot": "Olot", "vic": "Vic"}
DE = {"berga": "de Berga", "ripoll": "de Ripoll", "seu": "de la Seu d'Urgell", "olot": "d'Olot", "vic": "de Vic"}
PID = "biblioteques-i-centres"
LINK = "Més propostes i recursos a <a href=\"https://elarasocial.com/\" target=\"_blank\" rel=\"noopener\">elarasocial.com</a>."
TTS = "Rutes des d'entitats del Tercer Sector Social"


def ckm(s, dec=2): return f"{float(s):.{dec}f}".replace(".", ",")


def route(r, n):
    x = {"n": n, "name": r["nom"],
         "info": f"{ckm(r['km'])} km · {r['cam_min']}–{r['cam_max']} min caminant · {r['pau_min']}–{r['pau_max']} min amb pauses · circular"}
    if r["adreca"]: x["address"] = r["adreca"]
    if r["nota"]: x["note"] = r["nota"]
    x["wikiloc"] = f"https://www.wikiloc.com/wikiloc/view.do?id={r['wikiloc']}"
    return x


def dump_inicis(d):
    return "{\n" + ",\n".join(json.dumps(k, ensure_ascii=False) + ":{\n" + ",\n".join(f"{json.dumps(i)}:{json.dumps(c)}" for i, c in v.items()) + "\n}" for k, v in d.items()) + "\n}\n"


def cuina(lo, hi):
    return f"de {ckm(lo)} a {ckm(hi)} km" if lo != hi else f"d'{ckm(lo)} km"


ini_p = ROOT / "data/inicis.json"
inicis = json.loads(ini_p.read_text(encoding="utf-8"))
ANCHOR = "quan-cuidar-nos"

for key, rs in by.items():
    slug = FILE[key]
    path = ROOT / f"data/{slug}.json"
    d = json.loads(path.read_text(encoding="utf-8"))
    b = next(b for b in d["blocks"] if b["course"] == "cuidar")
    # 1) les parts que ja hi eren (la primera sense id/títol: passa a tenir-ne, i només això)
    if "parts" not in b:
        first = {"groups": b.pop("groups")}
        b["parts"] = [first]
    old = [p for p in b["parts"] if p.get("id") != PID]
    old_routes = [r for p in old for g in p["groups"] for r in g["routes"]]
    nmax = max(r["n"] for r in old_routes)
    if len(old) == 1 and not old[0].get("id"):   # Berga, Ripoll, la Seu, Olot: la part de la Taula del Tercer Sector
        p0 = old[0]
        p0.update({"id": "tercer-sector", "title": TTS, "nav": "Entitats del Tercer Sector Social"})
        if b.get("text") and "text" not in p0:
            p0["text"] = b["text"]            # el text de presentació que ja hi havia al bloc, tal qual
        if b.get("notice") and "notice" not in p0:
            p0["notice"] = b.pop("notice")    
        # ordre de claus net: id, title, nav, text, notice, groups
        old[0] = {k: p0[k] for k in ("id", "title", "nav", "text", "notice", "groups") if k in p0}
    # 2) la part nova
    rs = sorted(rs, key=lambda r: r["codi"])
    routes = [route(r, nmax + i + 1) for i, r in enumerate(rs)]
    n = len(rs)
    kms = [float(r["km"]) for r in rs]
    tmin, tmax = min(int(r["cam_min"]) for r in rs), max(int(r["cam_max"]) for r in rs)
    ll = f"{sum(float(r['lat']) for r in rs) / n:.4f},{sum(float(r['lon']) for r in rs) / n:.4f}"
    if n == 1:
        text = (f"1 ruta circular d'{ckm(kms[0])} km (de {tmin} a {tmax} minuts caminant), que surt d'un centre cívic i cultural {DE[key]} i hi torna. "
                "És un temps per caminar i reflexionar: portar a la vida quotidiana el que has après al curs «Quan cuidar-nos és una tasca col·lectiva», "
                "adonar-te de com et sents i pensar en petites accions que contribueixin al teu benestar i al de les persones que t'envolten. Camina-hi amb calma.")
    else:
        text = (f"{n} rutes circulars, {cuina(min(kms), max(kms))} (de {tmin} a {tmax} minuts caminant), que surten d'una biblioteca o d'un centre cívic i cultural {DE[key]} i hi tornen: una ruta per equipament. "
                "Són un temps per caminar i reflexionar: portar a la vida quotidiana el que has après al curs «Quan cuidar-nos és una tasca col·lectiva», "
                "adonar-te de com et sents i pensar en petites accions que contribueixin al teu benestar i al de les persones que t'envolten. Tria l'equipament que et quedi més a prop i camina-hi amb calma.")
    part = {"id": PID, "title": "Rutes des de biblioteques i centres cívics i culturals",
            "nav": "Biblioteques i centres", "text": text,
            "notice": {"title": "Traçats orientatius", "html": [
                "Els traçats s'han reconstruït sobre OpenStreetMap a partir de la ubicació de cada equipament: no són traçats oficials. Camina amb atenció al trànsit i a l'estat dels camins.", LINK]},
            "groups": [{"id": "biblioteques-i-centres-rutes", "title": f"Les {n} rutes" if n > 1 else "La ruta", "maps": [{
                "mid": MAPS[key], "title": f"{d['name']} · biblioteques i centres cívics i culturals", "ll": ll, "z": 14,
                "label": f"{n} rutes des de biblioteques i centres" if n > 1 else "1 ruta des d'un centre cívic i cultural",
                "routes": [x["n"] for x in routes]}], "routes": routes}]}
    b["parts"] = old + [part]
    total = len(old_routes) + n
    if key == "vic":
        b["summary"] = f"{total} rutes des d'equipaments, biblioteques, centres i entitats socials"
        b["text"] = ("Hi ha tres tipus de rutes: 16 rutes curtes, d'1,8 a 2 km, que surten d'equipaments comunitaris; 1 ruta d'1,2 km, que surt d'un centre cívic i cultural; "
                     "i 19 rutes més llargues, de 3,7 a 4,2 km, que surten d'entitats del Tercer Sector Social. Totes són circulars i tornen al punt de sortida.")
    else:
        b["summary"] = f"{total} rutes des d'entitats del Tercer Sector Social, biblioteques i centres"
        b["text"] = (f"Hi ha dos tipus de rutes: {len(old_routes)} rutes, de 2,4 a 2,6 km, que surten d'entitats del Tercer Sector Social, "
                     f"i {n} rutes més curtes, {cuina(min(kms), max(kms))}, que surten de biblioteques i centres cívics i culturals. Totes són circulars i tornen al punt de sortida.")
    path.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # punts d'inici: just darrere de l'últim «quan-cuidar-nos-ruta-N» de la pàgina, sense moure res més
    cur = inicis.setdefault(slug, {})
    ids = {f"{ANCHOR}-ruta-{x['n']}": f"{r['lat']},{r['lon']}" for x, r in zip(routes, rs)}
    last = max((k for k in cur if k.startswith(ANCHOR + "-ruta-")), key=lambda k: list(cur).index(k))
    new = {}
    for k, v in cur.items():
        if k not in ids: new[k] = v
        if k == last: new.update(ids)
    inicis[slug] = new
    print(NOM[key], n, "rutes noves; n =", routes[0]["n"], "–", routes[-1]["n"])

ini_p.write_text(dump_inicis(inicis), encoding="utf-8")
