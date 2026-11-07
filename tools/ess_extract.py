#!/usr/bin/env python3
"""Extreu les rutes de l'economia social dels KML de ChatGPT (checkpoint) i el registre de My Maps.
Ús: python3 -I ess_extract.py CARPETA_CHECKPOINT SORTIDA.json"""
import json, re, sys, glob, os, html

CK, OUT = sys.argv[1], sys.argv[2]

# mid de cada mapa (Registre_My_Maps_Esperanca_Activa.xlsx, 07/11/2026)
MIDS = {
    "MAP-001": "19vFO9pO_kcWzw7hYgYgrk233Yft_0LI", "MAP-002": "1qcCfGSqPYmlvZytkHwRzELBcX7mVpDU",
    "MAP-003": "1m0sU9PJMKSuPcTS0nGQK_uJBirVn1rQ", "MAP-004": "1PuTKkU2klocMaps4ZTuFu0ot2jMK2ZM",
    "MAP-005": "1W773X6yIb9MEePoQVGrX3NQM4t0i7HM", "MAP-006": "14enq1iKQMDC4ENJ0trYAuD-VwRkoDWc",
    "MAP-007": "15-vsuygTPfderVDCp7w1pbs4pptXbyc", "MAP-008": "1D-EvgOZulK9hZcSh-V2oxDxkbJNP0PM",
    "MAP-009": "1Rjycc3vfv69bgdp83ROVRvFt22hTrHE", "MAP-010": "1E_2hWdYRxZIfF4PNAUehlUH-uk0R1qk",
    "MAP-011": "1cXr3zTl_RWtnwBwvpo7L-VrL62KXUyc", "MAP-012": "1LtyhGM7AfXpcFiOFBuDeABV3idqXCSQ",
    "MAP-013": "1msr3FA-K3JTUZGirWKfGPRhxidB8kOM", "MAP-014": "1v120S7Tp9Biz3tW89dgHIw7_AosAiYw",
    "MAP-015": "1Hm-KVicCx9MVexFnTeh84K2-QUot1qI", "MAP-016": "1Lk8Q49hAzzm1RbMjmqGJH90QJ7msKqo",
    "MAP-017": "1QwUDDhxFKpy-1Phrn6-CDeHTELTl-Fs", "MAP-018": "1DINJUWHd8-ujf2WqVBvCi3_e5865bUU",
    "MAP-019": "1t2gJjh1dKINQvtav9HvuxoonhercRgI", "MAP-020": "1oISpOH0r3sAczopfV_CJ7TSuyl0mR28",
    "MAP-021": "1peDJBg3Q9nYO8_5zQADPhbbHD0SnqMw", "MAP-022": "1AJ05l21sQ6iyq-cnBlKhhQUsziq2WZk",
    "MAP-023": "1ByM3sgpT6L_zRhiucPoLw0x5SEGpjr4", "MAP-024": "19C5B7AQ1L6l-jT4FGtGWpoOTlzY6SEM",
}
for k, v in MIDS.items():
    assert len(v) == 32, k
# els que també són al checkpoint han de coincidir
for p in json.load(open(os.path.join(CK, "progress.json"), encoding="utf-8")):
    assert MIDS[p["code"]] == p["mid"], p["code"]

manifest = json.load(open(os.path.join(CK, "manifest.json"), encoding="utf-8"))
plan = json.load(open(os.path.join(CK, "plan_data_revised.json"), encoding="utf-8"))
seats = {s["id"]: s for s in plan["seats"]}


def parse_kml(path):
    t = open(path, encoding="utf-8").read()
    d = html.unescape(re.search(r"<Placemark>.*?<description>(.*?)</description>", t, re.S).group(1))
    coords = re.search(r"<coordinates>(.*?)</coordinates>", t, re.S).group(1).split()
    pts = [tuple(map(float, c.split(",")[:2])) for c in coords]   # (lon, lat)
    paras = [p.strip() for p in d.split("\n\n") if p.strip()]
    start = next((p for p in paras if p.startswith("Inici i final:")), "")
    ents = []
    try:
        i = next(i for i, p in enumerate(paras) if p.startswith("Sobre l’entitat"))
    except StopIteration:
        i = None
    if i is not None:
        for p in paras[i + 1:]:
            if p.startswith("Distància:"):
                break
            lines = p.split("\n")
            if len(lines) >= 2:
                ents.append({"name": lines[0].strip(), "desc": " ".join(l.strip() for l in lines[1:])})
    if i is not None and not ents:
        # Format de l'Alt Pirineu: «Sobre l'entitat», «Entitat de l'economia…» i el text, en un sol paràgraf
        lines = [l.strip() for l in paras[i].split("\n")]
        if len(lines) > 2:
            ents.append({"name": None, "desc": " ".join(lines[2:])})
    listed = []
    j = next((i for i, p in enumerate(paras) if p.startswith("Entitats d’aquesta seu")), None)
    if j is not None:
        listed = [l.strip() for l in paras[j].split("\n")[1:] if l.strip()]
    return {"start": start, "entities": ents, "listed": listed, "pts": pts}


routes = []
for m in manifest:
    for L in m["layers"]:
        f = os.path.join(CK, m["code"], f"{L['order']:02d}_{L['point']}.kml")
        k = parse_kml(f)
        s = seats[L["point"]]
        for e in k["entities"]:
            if e["name"] is None:
                e["name"] = L["name"].split(" - ", 1)[1]
        lon, lat = k["pts"][0]
        routes.append({
            "map": m["code"], "mid": MIDS[m["code"]], "map_title": m["title"], "page": m["page"],
            "order": L["order"], "number": L["number"], "layer": L["name"], "point": L["point"],
            "municipality": L["municipality"], "district": L.get("district") or "", "comarca": s.get("comarca", ""),
            "km": L["km"], "time": L["time"], "address": s["address"], "seat_municipality": s["municipality"],
            "start": k["start"], "entities": k["entities"], "listed": k["listed"],
            "dest": f"{lat:.5f},{lon:.5f}",
            "bbox": [min(p[0] for p in k["pts"]), min(p[1] for p in k["pts"]), max(p[0] for p in k["pts"]), max(p[1] for p in k["pts"])],
        })

# El Prat: Domingo Recreativos, Heres Social i La Rachola, una ruta cadascuna (registre 07/11/2026)
uiku = next(r for r in routes if r["point"] == "XAC-040")
ents = {e["name"]: e for e in uiku["entities"]}
assert set(ents) == {"Domingo Recreativos SCCL", "Heres Social SCCL", "La Rachola SCCL"}, set(ents)
base = dict(uiku)
uiku.update(entities=[ents["Domingo Recreativos SCCL"]], listed=["Domingo Recreativos SCCL"],
            layer="El Prat de Llobregat 3 - Domingo Recreativos SCCL", km=1.61, time="19–24 minuts")
for order, name, km, time in [(7, "Heres Social SCCL", 2.131, "26–32 minuts"), (8, "La Rachola SCCL", 2.024, "24–30 minuts")]:
    r = dict(base)
    r.update(order=order, number=order, entities=[ents[name]], listed=[name], km=km, time=time,
             layer=f"El Prat de Llobregat {order} - {name}", point=f"XAC-040-{order}")
    routes.append(r)

# Comprovacions
problems = []
for r in routes:
    if not r["entities"]:
        problems.append(("sense «Sobre l'entitat»", r["layer"]))
    elif r["listed"] and [e["name"] for e in r["entities"]] != r["listed"]:
        problems.append(("entitats diferents", r["layer"], r["listed"], [e["name"] for e in r["entities"]]))
print(len(routes), "rutes;", len({r['map'] for r in routes}), "mapes")
for p in problems:
    print("AVÍS:", p)
json.dump(routes, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
