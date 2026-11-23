#!/usr/bin/env python3
"""Barcelona · curs «Quan el món et preocupa» · part «Rutes des de miradors» (rutes 301–310, sense la 306 de moment).
Llegeix tools/miradors_barcelona.tsv (fitxes i KML del Drive «Barcelona - Quan el món et preocupa - Miradors»)
i, a data/barcelona.json, passa els grups de parcs del bloc `mon` a una primera part «Rutes des de parcs i jardins»
(els ids de grup i de ruta no canvien) i hi afegeix la part «miradors». Punts d'inici a data/inicis.json."""
import csv, json
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
rows = list(csv.DictReader((ROOT / "tools" / "miradors_barcelona.tsv").open(encoding="utf-8"), delimiter="\t"))
assert [r["n"] for r in rows] == ["301", "302", "303", "304", "305", "307", "308", "309", "310"]  # la 306 queda fora

MAP = {"mid": "1qOSBu3dnmFtr3cNJ58QMq-8stufWk04", "ll": "41.3830,2.1620", "z": 12,
       "title": "Barcelona · miradors (rutes 301–310)", "label": "Rutes 301 a 310 · Miradors"}
km = lambda k: f"{float(k.replace(',', '.')):.2f}".replace(".", ",")

def route(r):
    note = "Accessibilitat i seguretat: " + r["access"] + (" " + r["extra"] if r["extra"] else "")
    return {
        "n": int(r["n"]), "name": r["name"],
        "start": "Inici i final: " + r["name"],
        "info": f'{km(r["km"])} km · {r["caminar"]} min caminant · {r["pausas"]} min amb pauses · circular',
        "desc": r["desc"], "note": note,
        "wikiloc": "https://www.wikiloc.com/wikiloc/view.do?id=" + r["wikiloc"],
    }

part = {
    "id": "miradors", "title": "Rutes des de miradors", "nav": "Rutes des de miradors",
    "text": ("9 rutes curtes (d'1,1 a 1,4 km) que surten d'un mirador i hi tornen. Mira el món des d'on ets, escolta l'àudio, "
             "camina i torna al mateix lloc, però des d'un lloc intern diferent, amb una mirada diferent. "
             "Els traçats estan reconstruïts sobre OpenStreetMap i encara no s'han revisat a peu: "
             "revisa l'estat del camí abans d'anar-hi."),
    "notice": {"title": "Accessibilitat i seguretat", "html": [
        "Els temps són aproximats: caminant a un ritme tranquil i amb pauses per descansar. Alguns camins tenen escales o pendents i no són adaptats per a cadires de rodes ni cotxets.",
        "El mirador és només el punt de referència del recorregut. Més informació a <a href=\"https://elarasocial.com/\" target=\"_blank\" rel=\"noopener\">elarasocial.com</a>."]},
    "groups": [{"id": "miradors-rutes", "title": "Les 9 rutes", "maps": [MAP], "routes": [route(r) for r in rows]}],
}

p = ROOT / "data" / "barcelona.json"
d = json.loads(p.read_text(encoding="utf-8"))
b = next(b for b in d["blocks"] if b["course"] == "mon")
if "parts" not in b:
    b["parts"] = [{"id": "parcs", "title": "Rutes des de parcs i jardins", "nav": "Rutes des de parcs i jardins", "groups": b.pop("groups")}]
b["parts"] = [x for x in b["parts"] if x["id"] != "miradors"] + [part]
b["text"] = ("261 rutes curtes i circulars pels parcs i jardins dels 10 districtes de la ciutat, d'entre 1,7 i 2,2 km (uns 20–30 minuts caminant). "
             "Surten d'un parc, un jardí o una plaça i hi tornen. Tria el teu districte, busca el teu barri i fes-hi el temps de reflexió de cada passa. "
             "A part, hi ha 9 rutes més curtes que surten d'un mirador.")
b["summary"] = "270 rutes: 261 pels parcs i jardins i 9 des de miradors"
d["summary"] = "456 rutes repartides pels 10 districtes de la ciutat."
p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

pi = ROOT / "data" / "inicis.json"
txt = pi.read_text(encoding="utf-8"); ini = json.loads(txt)
for r in rows:
    ini["barcelona"][f"quan-el-mon-ruta-{r['n']}"] = r["dest"]
pi.write_text("{\n" + ",\n".join('"%s":{\n%s\n}' % (k, ",\n".join('"%s":"%s"' % (a, c) for a, c in v.items())) for k, v in ini.items()) + "\n}" + ("\n" if txt.endswith("\n") else ""), encoding="utf-8")
print("ok")
