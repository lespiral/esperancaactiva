#!/usr/bin/env python3
"""El Prat · curs «Quan el món et preocupa» · part «Rutes des de miradors» (rutes 10–20).
Llegeix tools/miradors.tsv (fitxes i punts d'inici del Drive «Quan el món et preocupa - Miradors»)
i escriu la part «miradors» al bloc `mon` de data/el-prat.json (la substitueix si ja hi és)."""
import csv, json, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
rows = list(csv.DictReader(open(ROOT / "tools" / "miradors.tsv", encoding="utf-8"), delimiter="\t"))
assert len(rows) == 11

MAPS = {
    "1": {"mid": "18pPCufXmv8FoBgf99Gx91UwjnTFTJVw", "title": "El Prat · miradors (mapa 1/2, rutes 10–15)", "ll": "41.2990,2.1050", "z": 13},
    "2": {"mid": "16mQxhetAJQGNKLZgvVGHiRGUEL67nk8", "title": "El Prat · miradors (mapa 2/2, rutes 16–20)", "ll": "41.3050,2.1245", "z": 14},
}
TITLES = {"1": "Miradors · mapa 1 (rutes 10–15)", "2": "Miradors · mapa 2 (rutes 16–20)"}

def route(r):
    return {
        "n": int(r["n"]),
        "name": r["name"],
        "start": "Inici i final: " + r["name"],
        "info": f'{r["km"]} km · {r["caminant"]} min caminant · {r["pauses"]} min amb pauses · {r["tipus"]}',
        "desc": r["desc"],
        "note": "Accessibilitat i seguretat: " + r["access"],
        "dest": r["dest"],
        "wikiloc": "https://www.wikiloc.com/wikiloc/view.do?id=" + r["wikiloc"],
    }

groups = []
for k in ("1", "2"):
    groups.append({
        "id": f"miradors-{k}",
        "title": TITLES[k],
        "maps": [MAPS[k]],
        "routes": [route(r) for r in rows if r["mapa"] == k],
    })

part = {
    "id": "miradors",
    "title": "Rutes des de miradors",
    "nav": "Rutes des de miradors",
    "text": ("11 rutes curtes (de 0,4 a 1,7 km) que surten d'un mirador i hi tornen. Mira el món des d'on ets, escolta l'àudio, "
             "camina i torna al mateix lloc, però des d'un lloc intern diferent, amb una mirada diferent. "
             "Els traçats estan reconstruïts sobre OpenStreetMap i encara no s'han revisat a peu: "
             "revisa l'estat del camí i les normes d'accés dels espais naturals abans d'anar-hi."),
    "groups": groups,
}

p = ROOT / "data" / "el-prat.json"
d = json.load(open(p, encoding="utf-8"))
b = next(b for b in d["blocks"] if b["course"] == "mon")
b["parts"] = [x for x in b["parts"] if x["id"] != "miradors"] + [part]
b["text"] = ("Hi ha tres tipus de rutes: 9 rutes pels espais naturals del Delta del Llobregat (el riu, les llacunes, la platja i el Parc Agrari), "
             "17 circuits urbans curts, de 10 a 15 minuts caminant, que surten de places, parcs i jardins de tots els barris del Prat, "
             "i 11 rutes curtes que surten d'un mirador. Abans d'anar als espais naturals, comprova els horaris d'obertura.")
b["summary"] = "9 rutes pel Delta, 17 circuits urbans i 11 des de miradors"
json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
open(p, "a").write("\n")

# Punts d'inici per a la cerca per ubicació (data/inicis.json: una línia per ruta)
pi = ROOT / "data" / "inicis.json"
txt = pi.read_text(encoding="utf-8")
ini = json.loads(txt)
for r in rows:
    pref = "miradors-" + r["mapa"]
    lat, lon = r["dest"].split(",")
    ini["el-prat"][f"{pref}-ruta-{r['n']}"] = f"{float(lat):.5f},{float(lon):.5f}"
out = "{\n" + ",\n".join('"%s":{\n%s\n}' % (k, ",\n".join('"%s":"%s"' % (a, b) for a, b in v.items())) for k, v in ini.items()) + "\n}"
pi.write_text(out + ("\n" if txt.endswith("\n") else ""), encoding="utf-8")
print("ok")
