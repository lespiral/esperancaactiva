#!/usr/bin/env python3
"""Amposta (Terres de l'Ebre) i Tarragona (Camp de Tarragona) · curs «Quan el món et preocupa» · rutes des de miradors.
Llegeix tools/miradors_pc.tsv (còpia del full de Drive «Rutes per ciutat i curs», pestanya «Rutes», files 296–308) i afegeix
un bloc `mon` a data/terres-de-l-ebre.json i data/camp-de-tarragona.json, amb una secció per ciutat (com la resta de pobles
d'aquestes pàgines). Alacant, que no és a Catalunya, no hi és: de moment només surt a la .org."""
import csv, json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
rows = list(csv.DictReader((ROOT / "tools" / "miradors_pc.tsv").open(encoding="utf-8"), delimiter="\t"))
km = lambda k: f"{float(k.replace(',', '.')):.2f}".replace(".", ",")
CONF = {
    "Amposta": ("terres-de-l-ebre", "amposta-miradors", "40.7140,0.5810", 12),
    "Tarragona": ("camp-de-tarragona", "tarragona-miradors", "41.1189,1.2445", 13),
}


def route(r):
    return {"n": int(r["n"]), "name": r["name"], "start": "Inici i final: " + r["name"],
            "info": f'{km(r["km"])} km · {r["caminar"]} min caminant · {r["pausas"]} min amb pauses · {r["tipus"]}',
            "wikiloc": "https://www.wikiloc.com/wikiloc/view.do?id=" + r["wikiloc"]}


for city, (slug, sid, ll, z) in CONF.items():
    rs = [r for r in rows if r["ciutat"] == city]
    assert rs and len({r["mid"] for r in rs}) == 1
    n = len(rs)
    kms = [float(r["km"].replace(",", ".")) for r in rs]
    ida = [r["n"] for r in rs if r["tipus"] != "circular"]
    text = (f"{n} rutes curtes (de {km(str(min(kms)))} a {km(str(max(kms)))} km) que surten d'un mirador. Mira el món des d'on ets, escolta l'àudio, "
            "camina i torna al mateix lloc, però des d'un lloc intern diferent, amb una mirada diferent. "
            "Els traçats estan reconstruïts sobre OpenStreetMap i encara no s'han revisat a peu: revisa l'estat del camí abans d'anar-hi.")
    if len(ida) == n:
        text += " Totes són d'anada i tornada, no circulars."
    elif ida:
        text += (f" La ruta {ida[0]} és d'anada i tornada, no circular." if len(ida) == 1
                 else f" Les rutes {', '.join(ida)} són d'anada i tornada, no circulars.")
    block = {
        "course": "mon", "text": text, "summary": f"{n} rutes des de miradors",
        "notice": {"title": "Accessibilitat i seguretat", "html": [
            "Els temps són aproximats: caminant a un ritme tranquil i amb pauses per descansar. Alguns camins tenen escales o pendents i no són adaptats per a cadires de rodes ni cotxets.",
            "El mirador és només el punt de referència del recorregut. Més informació a <a href=\"https://elarasocial.com/\" target=\"_blank\" rel=\"noopener\">elarasocial.com</a>."]},
        "groups": [{"id": f"quan-el-mon-{slug.split('-')[0]}-miradors", "title": city,
                    "maps": [{"mid": rs[0]["mid"], "ll": ll, "z": z, "title": f"{city} · miradors (rutes {rs[0]['n']}–{rs[-1]['n']})",
                              "label": f"Rutes {rs[0]['n']} a {rs[-1]['n']} · Miradors"}],
                    "sections": [{"title": city, "id": sid, "route_prefix": sid, "nav": f"{city} (miradors)",
                                  "routes": [route(r) for r in rs]}]}],
    }
    p = ROOT / "data" / f"{slug}.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    d["blocks"] = [b for b in d["blocks"] if b["course"] != "mon"] + [block]
    # Resum del territori: «5 rutes de l'economia social i solidària i 166 de centres educatius en 52 municipis.»
    # passa a «… solidària, 166 de centres educatius i 5 de miradors en 52 municipis.»
    base = re.sub(r", (\d+ de centres educatius) i \d+ de miradors", r" i \1", d["summary"])
    pre, post = base.rsplit(" en ", 1)
    head, last = pre.rsplit(" i ", 1)
    d["summary"] = f"{head}, {last} i {n} de miradors en {post}"
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("ok")
