#!/usr/bin/env python3
"""Rutes del curs «Quan la vida et desborda» de Berga (7), Ripoll (5), la Seu d'Urgell (6) i les 4 rutes
saludables (PAFES) de Vic (29–32). Afegeix el bloc `vida` a data/berga.json, data/ripoll.json i
data/la-seu-d-urgell.json, afegeix una part nova (PAFES) al bloc `vida` de data/vic.json i escriu els punts
d'inici a data/inicis.json. No toca les rutes 24–28 de Vic ni res d'Olot. Es pot tornar a executar.

Font: tools/vida_comarcals.tsv, fet de les fitxes («fitxes_<ciutat>.md»), dels fulls «Rutes <ciutat>» i dels
KML de Drive (Camins d'Esperança Activa › Ciutats › <ciutat>). Les fitxes dels mapes no es publiquen aquí.
"""
import csv, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
rows = list(csv.DictReader((ROOT / "tools/vida_comarcals.tsv").open(encoding="utf-8"), delimiter="\t"))
by = {}
for r in rows:
    by.setdefault(r["ciutat"], []).append(r)

MAPS = {"berga": "1XmQmYnFC_EK2-LRxX2cadCpp2kdgokM", "ripoll": "1NeDDXgfNGn828qgCvKZhVlBHDAeB9bY",
        "seu": "1ct73EgldXilDi_ET7lWdbUkbkq2BvRw", "vic": "1B0gtXK-UcQSKiee-XKxNL5yREkSly0Q"}
FILE = {"berga": "berga", "ripoll": "ripoll", "seu": "la-seu-d-urgell", "vic": "vic"}
NOM = {"berga": "Berga", "ripoll": "Ripoll", "seu": "la Seu d'Urgell", "vic": "Vic"}
LINK = "Més propostes i recursos a <a href=\"https://elarasocial.com/\" target=\"_blank\" rel=\"noopener\">elarasocial.com</a>."


def ckm(s, dec=2): return f"{float(s):.{dec}f}".replace(".", ",")


def route(r):
    x = {"n": int(r["n"]), "name": r["nom"],
         "info": f"{ckm(r['km'])} km · {r['cam_min']}–{r['cam_max']} min caminant · {r['pau_min']}–{r['pau_max']} min amb pauses · circular"}
    if r["adreca"]: x["address"] = r["adreca"]
    notes = []
    if r["nota"]: notes.append(r["nota"])
    if r["alt_min"]:
        notes.append(f"Desnivell d'uns {int(r['alt_max']) - int(r['alt_min'])} m, entre els {r['alt_min']} i els {r['alt_max']} m d'altitud.")
    if notes: x["note"] = " ".join(notes)
    x["wikiloc"] = f"https://www.wikiloc.com/wikiloc/view.do?id={r['wikiloc']}"
    return x


def centre(rs):
    return f"{sum(float(r['lat']) for r in rs) / len(rs):.4f},{sum(float(r['lon']) for r in rs) / len(rs):.4f}"


def rang(rs):
    kms = [float(r["km"]) for r in rs]
    return ckm(min(kms)), ckm(max(kms)), min(int(r["cam_min"]) for r in rs), max(int(r["cam_max"]) for r in rs)


PAFES = "rutes saludables del PAFES (Pla d'Activitat Física, Esport i Salut)"
CIUTAT = {  # text de la intro de cada bloc: qui són les rutes que no són PAFES
    "berga": ("3", "surten del CAP, de l'hospital i del CSMA de Berga", "Les rutes 1 a 3", "Les rutes 4 a 7", "de Berga"),
    "ripoll": ("1", "surt del CAP del Ripollès", "La ruta 1", "Les rutes 2 a 5", "de Ripoll"),
    "seu": ("2", "surten del CAP i de la Fundació Sant Hospital de la Seu d'Urgell", "Les rutes 1 i 2", "Les rutes 3 a 6", "de la Seu d'Urgell"),
}
ORIGIN = {
    "berga": "del CAP, de l'hospital, del CSMA i de carrers i passejos de Berga",
    "ripoll": "del CAP del Ripollès i de carrers de Ripoll",
    "seu": "del CAP, de la Fundació Sant Hospital i del passeig de Joan Brudieu, a la Seu d'Urgell",
    "vic": "dels CAP, dels hospitals i de carrers i places de Vic",
}
CREDIT = {
    "berga": "Les rutes 4 a 7 segueixen les rutes saludables del PAFES (Pla d'Activitat Física, Esport i Salut) de Berga.",
    "ripoll": "Les rutes 2 a 5 segueixen les rutes saludables del PAFES (Pla d'Activitat Física, Esport i Salut) de Ripoll.",
    "seu": "Les rutes 3 a 6 segueixen les rutes saludables del PAFES (Pla d'Activitat Física, Esport i Salut) de la Seu d'Urgell.",
    "vic": "Les rutes 29 a 32 segueixen les rutes saludables del PAFES (Pla d'Activitat Física, Esport i Salut) de Vic.",
}
SUMMARY_CITY = {
    "berga": "14 rutes circulars: des del CAP, l'hospital i el CSMA, de rutes saludables i des d'entitats del Tercer Sector Social.",
    "ripoll": "11 rutes circulars: des del CAP, de rutes saludables i des d'entitats del Tercer Sector Social.",
    "seu": "18 rutes circulars: des del CAP i l'hospital, de rutes saludables i des d'entitats del Tercer Sector Social.",
}
SUMMARY_BLOCK = {
    "berga": "7 rutes des del CAP, l'hospital, el CSMA i rutes saludables",
    "ripoll": "5 rutes des del CAP i rutes saludables",
    "seu": "6 rutes des del CAP, l'hospital i rutes saludables",
}


def dump_inicis(d):  # mateix format que ja té el fitxer: una pàgina per bloc, una ruta per línia
    return "{\n" + ",\n".join(json.dumps(k, ensure_ascii=False) + ":{\n" + ",\n".join(f"{json.dumps(i)}:{json.dumps(c)}" for i, c in v.items()) + "\n}" for k, v in d.items()) + "\n}\n"


ini_p = ROOT / "data/inicis.json"
inicis = json.loads(ini_p.read_text(encoding="utf-8"))

for key, rs in by.items():
    path = ROOT / f"data/{FILE[key]}.json"
    d = json.loads(path.read_text(encoding="utf-8"))
    rs = sorted(rs, key=lambda r: int(r["n"]))
    routes = [route(r) for r in rs]
    slug = FILE[key]
    if key == "vic":
        b = next(b for b in d["blocks"] if b["course"] == "vida")
        assert "groups" in b and [r["n"] for r in b["groups"][0]["routes"]] == [24, 25, 26, 27, 28] or "parts" in b
        lo, hi, tmin, tmax = rang(rs)
        part = {"id": "rutes-saludables", "title": "Rutes saludables PAFES", "nav": "Rutes saludables PAFES",
                "text": f"{len(rs)} rutes circulars, de {lo} a {hi} km (de {tmin} a {tmax} minuts caminant), que surten de carrers, places i un CAP de Vic i segueixen les {PAFES} de la ciutat. Tria la que tinguis més a prop i fes-hi el temps de reflexió de cada passa.",
                "notice": {"title": "Traçats oficials", "html": ["Els traçats són els de les rutes saludables del PAFES de Vic. Camina amb atenció al trànsit i a l'estat dels camins."]},
                "groups": [{"id": "quan-la-vida-pafes", "title": f"Les {len(rs)} rutes", "maps": [{
                    "mid": MAPS[key], "title": "Vic · rutes saludables PAFES", "ll": centre(rs), "z": 14,
                    "label": f"Rutes 29 a 32 · rutes saludables PAFES", "routes": [int(r["n"]) for r in rs]}], "routes": routes}]}
        if "parts" not in b:  # el bloc existent passa a ser la primera part, sense canviar-ne res
            first = {"groups": b.pop("groups")}
            b["parts"] = [first]
        b["parts"] = [p for p in b["parts"] if p.get("id") != "rutes-saludables"] + [part]
        b["origin"] = ORIGIN[key]   # el resum del bloc i el de la ciutat els calcula build.py
        b["credit"] = CREDIT[key]
    else:
        n = len(rs)
        n_cap, quins, r_cap, r_paf, de = CIUTAT[key]
        lo, hi, tmin, tmax = rang(rs)
        reco = f"Els traçats de {r_cap.lower()} s'han reconstruït sobre OpenStreetMap a partir de la ubicació del punt de sortida: no són traçats oficials. Els de {r_paf.lower()} són els de les rutes saludables del PAFES."
        block = {"course": "vida", "origin": ORIGIN[key], "credit": CREDIT[key],
                 "text": f"{n} rutes circulars, de {lo} a {hi} km (de {tmin} a {tmax} minuts caminant). {r_cap} {quins.replace('surten', 'surten').replace('surt ', 'surt ')}. {r_paf} segueixen les {PAFES} {de}. Tria la que tinguis més a prop i fes-hi el temps de reflexió de cada passa.",
                 "summary": SUMMARY_BLOCK[key],
                 "notice": {"title": "Traçats orientatius i oficials", "html": [reco + " Camina amb atenció al trànsit i a l'estat dels camins.", LINK]},
                 "groups": [{"title": f"Les {n} rutes", "maps": [{
                     "mid": MAPS[key], "title": f"{d['name']} · rutes del curs «Quan la vida et desborda»", "ll": centre(rs), "z": 14,
                     "label": f"{n} rutes des del CAP i rutes saludables", "routes": list(range(1, n + 1))}], "routes": routes}]}
        d["blocks"] = [b for b in d["blocks"] if b["course"] != "vida"]
        d["blocks"].insert(0, block)
    path.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    ids = {f"quan-la-vida-ruta-{r['n']}": f"{r['lat']},{r['lon']}" for r in rs}
    cur = inicis.setdefault(slug, {})
    if key == "vic":  # les noves, just darrere de les existents de «vida» (sense moure res més)
        new = {}
        for k, v in cur.items():
            new[k] = v
            if k == "quan-la-vida-ruta-28":
                new.update({i: c for i, c in ids.items() if i not in cur})
        inicis[slug] = {**new, **{i: c for i, c in ids.items() if i in cur}}
    else:
        inicis[slug] = {**ids, **{k: v for k, v in cur.items() if not k.startswith("quan-la-vida-")}}
    print(NOM[key], len(rs), "rutes")

ini_p.write_text(dump_inicis(inicis), encoding="utf-8")
