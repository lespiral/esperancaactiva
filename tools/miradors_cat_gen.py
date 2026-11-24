#!/usr/bin/env python3
"""Curs «Quan el món et preocupa» (bloc `mon`) · 181 rutes des de miradors de Catalunya (rutes 1021–1228 i 1229–1271 del full de Drive
«Rutes per ciutat i curs», pestanya «Rutes», files 361–605; sense els pobles del País Valencià i de les Illes Balears, que només surten a la .org).
Llegeix tools/miradors_cat.tsv. Afegeix un grup per mapa de My Maps i una secció per municipi al bloc `mon` de la pàgina de territori
(no toca les seccions que ja hi són, com Amposta i Tarragona); Berga, que té pàgina pròpia, rep un grup nou al seu bloc `mon`.
Afegeix els municipis nous a data/comarques.json. Es pot tornar a executar. Coordenades dels municipis: aproximades (només per centrar el mapa)."""
import csv, json, re, unicodedata
from collections import OrderedDict, defaultdict
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
rows = list(csv.DictReader((ROOT / "tools/miradors_cat.tsv").open(encoding="utf-8"), delimiter="\t"))
PAGE = {"Selva": "terres-gironines", "Baix Empordà": "terres-gironines", "Alt Empordà": "terres-gironines", "Ripollès": "terres-gironines",
        "Cerdanya": "alt-pirineu-i-aran", "Alt Urgell": "alt-pirineu-i-aran", "Aran": "alt-pirineu-i-aran", "Pallars Jussà": "alt-pirineu-i-aran",
        "Alta Ribagorça": "alt-pirineu-i-aran", "Solsonès": "catalunya-central", "Segrià": "ponent", "Noguera": "ponent",
        "Baix Llobregat": "baix-llobregat", "Osona": "catalunya-central", "Vallès Oriental": "valles-oriental", "Bages": "catalunya-central",
        "Berguedà": "catalunya-central", "Moianès": "catalunya-central", "Garraf": "anoia-penedes-i-garraf", "Alt Penedès": "anoia-penedes-i-garraf",
        "Baix Penedès": "anoia-penedes-i-garraf", "Vallès Occidental": "valles-occidental", "Barcelonès": "barcelones-nord", "Maresme": "maresme",
        "Tarragonès": "camp-de-tarragona", "Priorat": "camp-de-tarragona", "Baix Camp": "camp-de-tarragona", "Alt Camp": "camp-de-tarragona",
        "Conca de Barberà": "camp-de-tarragona", "Baix Ebre": "terres-de-l-ebre", "Montsià": "terres-de-l-ebre", "Ribera d'Ebre": "terres-de-l-ebre",
        "Terra Alta": "terres-de-l-ebre"}
km = lambda k: f"{float(str(k).replace(',', '.')):.2f}".replace(".", ",")
slug = lambda s: re.sub(r"[^a-z0-9]+", "-", unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()).strip("-")
LINK = "<a href=\"https://elarasocial.com/\" target=\"_blank\" rel=\"noopener\">elarasocial.com</a>"
NOTICE = {"title": "Accessibilitat i seguretat", "html": [
    "Els traçats estan reconstruïts sobre OpenStreetMap a partir de la ubicació de cada mirador i no s'han revisat a peu: són orientatius. "
    "Els temps són aproximats, caminant a un ritme tranquil i amb pauses per descansar. Alguns camins tenen escales o pendents i no són adaptats per a cadires de rodes ni cotxets. "
    "Camina amb atenció al trànsit i a l'estat dels camins.",
    f"El mirador és només el punt de referència del recorregut. Més informació a {LINK}."]}


def route(r):
    rec = r["tipus"].lower()
    return {"n": int(r["n"]), "name": r["name"], "start": "Inici i final: " + r["name"],
            "info": f'{km(r["km"])} km · {r["caminar"].replace(" min", "")} min caminant · {r["pausas"].replace(" min", "")} min amb pauses · {rec}',
            "wikiloc": "https://www.wikiloc.com/wikiloc/view.do?id=" + r["wikiloc"]}


def titol(muns):
    if len(muns) <= 2: return " i ".join(muns)
    rest = len(muns) - 2
    return f"{muns[0]}, {muns[1]} i {rest} {'municipi' if rest == 1 else 'municipis'} més"


def text_of(rs):
    n = len(rs); kms = [x["km"] for x in rs]
    t = (f"{n} rutes curtes (de {km(str(min(kms)))} a {km(str(max(kms)))} km) que surten d'un mirador. Mira el món des d'on ets, escolta l'àudio, "
         "camina i torna al mateix lloc, però des d'un lloc intern diferent, amb una mirada diferent. "
         "Els traçats estan reconstruïts sobre OpenStreetMap i encara no s'han revisat a peu: revisa l'estat del camí abans d'anar-hi.")
    ida = sum(1 for x in rs if x["rec"] != "circular")
    if ida == n: t += " Totes són d'anada i tornada, no circulars."
    elif ida: t += " Algunes són d'anada i tornada, no circulars; la fitxa de cada ruta ho diu."
    return t


for r in rows:
    r["km"] = float(r["km"].replace(",", ".")); r["rec"] = "circular" if r["tipus"].lower() == "circular" else "anada i tornada"
    r["tipus"] = r["rec"]
by_map = defaultdict(list)
for r in rows: by_map[r["mid"]].append(r)
for v in by_map.values(): v.sort(key=lambda r: int(r["n"]))


def map_meta(mid):
    rs = by_map[mid]
    la = [float(r["lat"]) for r in rs]; lo = [float(r["lon"]) for r in rs]
    span = max(max(la) - min(la), (max(lo) - min(lo)) * 0.75)
    z = 8
    for lim, zz in ((0.02, 14), (0.04, 13), (0.08, 12), (0.16, 11), (0.32, 10), (0.64, 9)):
        if span < lim: z = zz; break
    muns = list(OrderedDict.fromkeys(r["mun"] for r in rs))
    return {"mid": mid, "ll": f"{(max(la) + min(la)) / 2:.4f},{(max(lo) + min(lo)) / 2:.4f}", "z": z,
            "title": f"{titol(muns)} · miradors", "label": f"Mapa de miradors · {len(rs)} rutes"}


def groups_for(page_rows):
    out = []
    for mid in sorted({r["mid"] for r in page_rows}, key=lambda m: int(by_map[m][0]["n"])):
        here = [r for r in by_map[mid] if r in page_rows]
        secs = OrderedDict()
        for r in here: secs.setdefault(r["mun"], []).append(r)
        sections = []
        for mun, srs in secs.items():
            base = f"{slug(mun)}-miradors"
            sec = {"title": mun, "id": base + ("-" + mid[:6].lower() if base in used else ""), "routes": [route(r) for r in srs]}
            if base in used: sec["route_prefix"] = base; sec["nav"] = f"{mun} (miradors, mapa {mid[:6]})"
            used.add(base)
            sections.append(sec)
        out.append({"id": "quan-el-mon-miradors-" + mid[:6].lower(), "title": titol(list(secs)), "maps": [map_meta(mid)], "sections": sections})
    return out


used = set()
com_p = ROOT / "data/comarques.json"
com = json.loads(com_p.read_text(encoding="utf-8"))
norm = lambda s: s.lower().replace("’", "'")
cn = {norm(k): k for k in com}
for r in rows:
    k = cn.get(norm(r["mun"]))
    if k: r["mun"] = k       # nom amb la grafia que ja té la web
    else: com[r["mun"]] = [r["comarca"], r["provincia"]]; cn[norm(r["mun"])] = r["mun"]
com_p.write_text("{\n" + ",\n".join(f"  {json.dumps(k, ensure_ascii=False)}: {json.dumps(v, ensure_ascii=False)}" for k, v in com.items()) + "\n}\n", encoding="utf-8")

for page in sorted({PAGE[r["comarca"]] for r in rows if r["mun"] != "Berga"}):
    pr = [r for r in rows if PAGE[r["comarca"]] == page and r["mun"] != "Berga"]
    p = ROOT / f"data/{page}.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    blk = next((b for b in d["blocks"] if b["course"] == "mon"), None)
    used.clear()
    if blk:
        blk["groups"] = [g for g in blk["groups"] if not g["id"].startswith("quan-el-mon-miradors-")]
        used.update(s.get("route_prefix") or s["id"] for g in blk["groups"] for s in g["sections"])
    else:
        blk = {"course": "mon", "text": "", "summary": "", "notice": NOTICE, "groups": []}
        d["blocks"].append(blk)
    blk["groups"] += groups_for(pr)
    blk["groups"].sort(key=lambda g: min(r["n"] for s in g["sections"] for r in s["routes"]))
    allr = [{"km": float(x["info"].split(" km")[0].replace(",", ".")), "rec": "circular" if x["info"].endswith("circular") and "anada" not in x["info"] else "ida"}
            for g in blk["groups"] for s in g["sections"] for x in s["routes"]]
    blk["text"] = text_of(allr); blk["summary"] = f"{len(allr)} rutes des de miradors"
    cnt = lambda c: sum(len(s["routes"]) for b in d["blocks"] if b["course"] == c for g in b["groups"] for s in g.get("sections", []))
    nmun = len({s["title"] for b in d["blocks"] for g in b["groups"] for s in g.get("sections", [])})
    parts = [f"{cnt('dia')} rutes de l'economia social i solidària"]
    if any(b["course"] == "cuidar" for b in d["blocks"]): parts.append(f"{cnt('cuidar')} de centres educatius")
    parts.append(f"{len(allr)} de miradors")
    d["summary"] = (parts[0] if len(parts) == 1 else ", ".join(parts[:-1]) + " i " + parts[-1]) + f" en {nmun} municipis."
    fonts = ["d'entitats de l'economia social i solidària"] + (["de centres educatius"] if any(b["course"] == "cuidar" for b in d["blocks"]) else []) + ["de miradors"]
    d["intro"] = "Rutes a peu per fer el temps de reflexió de cada passa, des " + ", ".join(fonts[:-1]) + " i " + fonts[-1] + "."
    if page == "alt-pirineu-i-aran" and "Aran" not in d["region"]:
        d["region"] = "Alt Urgell (sense la Seu d'Urgell), Alta Ribagorça, Aran, Cerdanya, Pallars Jussà i Pallars Sobirà"
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(page, len(pr), "rutes noves;", len(allr), "al bloc")

# Berga (pàgina pròpia): grup nou al bloc `mon`
br = [r for r in rows if r["mun"] == "Berga"]
p = ROOT / "data/berga.json"
d = json.loads(p.read_text(encoding="utf-8"))
b = next(b for b in d["blocks"] if b["course"] == "mon")
b["groups"] = [g for g in b["groups"] if g.get("id") != "miradors"]
meta = map_meta(br[0]["mid"]); meta["title"] = "Berga i el Berguedà · miradors"
b["groups"].append({"id": "miradors", "title": f"Les {len(br)} rutes des de miradors", "maps": [meta], "routes": [dict(route(r), n=i + 3) for i, r in enumerate(br)]})
old = sum(len(g["routes"]) for g in b["groups"] if g.get("id") != "miradors")
b["text"] = (f"{old} rutes circulars (un sender fins al santuari de Queralt i un circuit pels parcs) i {len(br)} rutes curtes des de miradors. "
             "Surten d'un lloc concret de la ciutat i hi tornen. Tria la que s'adapti al teu dia i fes-hi el temps de reflexió de cada passa. "
             "Els traçats dels miradors estan reconstruïts sobre OpenStreetMap i encara no s'han revisat a peu.")
b["summary"] = f"{old + len(br)} rutes: senders, parcs i miradors"
p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("Berga", len(br))
