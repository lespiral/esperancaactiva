#!/usr/bin/env python3
"""Rutes del curs «Quan cuidar-nos és una tasca col·lectiva» (bloc `cuidar`) des de centres educatius públics:
451 centres de 17 comarques (Alt Camp, Alt Urgell, Berguedà, Cerdanya, Conca de Barberà, Garrigues, Garrotxa, Moianès,
Pallars Jussà, Pallars Sobirà, Pla de l'Estany, Priorat, Ribera d'Ebre, Ripollès, Segarra, Solsonès i Terra Alta).

- Berga, Ripoll, Olot i la Seu d'Urgell (pàgines pròpies): part nova «Rutes des de centres educatius» al bloc `cuidar`
  (la resta del bloc no es toca; només es refan el `summary` i el `text` del bloc, pels comptes).
- La resta, a la pàgina de territori que toca: bloc `cuidar` nou, un grup per mapa de My Maps i una secció per municipi.
- Escriu també els punts d'inici a data/inicis.json i els municipis nous a data/comarques.json. Es pot tornar a executar.

Font: tools/centres_educatius.tsv, fet dels registres de la carpeta AFA_Catalunya (registre_global_publics.csv: nom, municipi,
comarca, adreça, km i minuts; registre_mymaps_publicats.csv: enllaç de cada mapa; registre_wikiloc_publicats.csv + ids de Wikiloc
del perfil Espiral.ElaraSocial). Temps: caminada = km × 12–15 min; amb pauses = +10 / +20 min arrodonit a 5. Adreça només on el
registre en dona una amb carrer (les abreviacions «p.», «Ajuntament», «Zona Escolar», «Finca…» no es publiquen). El tipus de
centre de la frase (`desc`) es treu del nom. Els traçats són reconstruïts sobre OpenStreetMap i no s'han revisat a peu; si el
registre diu que un tram es fa d'anada i tornada, la ruta ho diu a la línia d'info (sense nota).
"""
import csv, json, math, pathlib, re, unicodedata
from collections import OrderedDict, defaultdict
from urllib.parse import urlparse, parse_qs

ROOT = pathlib.Path(__file__).resolve().parent.parent
rows = list(csv.DictReader((ROOT / "tools/centres_educatius.tsv").open(encoding="utf-8"), delimiter="\t"))
ANCHOR = "quan-cuidar-nos"
PID = "centres-educatius"
LINK = "Més propostes i recursos a <a href=\"https://elarasocial.com/\" target=\"_blank\" rel=\"noopener\">elarasocial.com</a>."
NOTICE = {"title": "Traçats orientatius", "html": [
    "Els traçats s'han reconstruït sobre OpenStreetMap a partir de la ubicació de cada centre: no són traçats oficials i no s'han revisat a peu. "
    "Algunes rutes tornen per una part del mateix camí (la fitxa de cada ruta ho diu). Camina amb atenció al trànsit i a l'estat dels camins. "
    "El centre només és el punt de sortida de la ruta: no l'organitza ni la recomana.", LINK]}
TXT = "Surten de centres educatius públics (escoles, instituts, llars d'infants, escoles de música i d'adults): espais on la gent aprèn, es troba i fa comunitat. Tria el centre que tinguis més a prop i fes-hi el temps de reflexió de cada passa. El centre només és el punt de sortida de la ruta: no l'organitza ni la recomana."
CITY_FILE = {"berga": "berga", "ripoll": "ripoll", "olot": "olot", "seu": "la-seu-d-urgell"}
CITY_NAME = {"berga": "Berga", "ripoll": "Ripoll", "olot": "Olot", "seu": "la Seu d'Urgell"}
CITY_DE = {"berga": "de Berga", "ripoll": "de Ripoll", "olot": "d'Olot", "seu": "de la Seu d'Urgell"}


def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def ckm(x, dec=2): return f"{float(x):.{dec}f}".replace(".", ",")
def cuina(lo, hi): return f"de {ckm(lo)} a {ckm(hi)} km" if round(lo, 2) != round(hi, 2) else f"d'{ckm(lo)} km"
def mid(url): return parse_qs(urlparse(url).query)["mid"][0]


def info(r):
    rep = int(r["repeteix"])
    return (f"{ckm(r['km'])} km · {r['cam_min']}–{r['cam_max']} min caminant · {r['pau_min']}–{r['pau_max']} min amb pauses · "
            + ("circular amb tram d'anada i tornada" if rep else "circular"))


def route(r, n):
    x = {"n": n, "name": r["nom"], "info": info(r)}
    if r["adreca"]: x["address"] = r["adreca"]
    x["desc"] = r["desc"]
    if r["wikiloc"]: x["wikiloc"] = f"https://ca.wikiloc.com/wikiloc/view.do?id={r['wikiloc']}"   # 17004992: només a My Maps
    return x


def zoom(rs):
    la = [float(r["lat"]) for r in rs]; lo = [float(r["lon"]) for r in rs]
    span = max(max(la) - min(la), (max(lo) - min(lo)) * 0.75)
    for lim, z in ((0.02, 14), (0.04, 13), (0.08, 12), (0.16, 11), (0.32, 10), (0.64, 9)):
        if span < lim: return z
    return 8


def ll_of(rs):
    la = [float(r["lat"]) for r in rs]; lo = [float(r["lon"]) for r in rs]
    return f"{(max(la) + min(la)) / 2:.4f},{(max(lo) + min(lo)) / 2:.4f}"


def map_meta(maprows):
    """Dades del mapa de My Maps (totes les rutes del mapa, també les d'altres pobles)."""
    r0 = maprows[0]
    i, n = re.search(r"mapa (\d+) de (\d+)", r0["mapa"]).groups()
    return {"mid": mid(r0["mapa_url"]), "title": r0["mapa"], "ll": ll_of(maprows), "z": zoom(maprows),
            "label": f"{r0['comarca']} · mapa {int(i)} de {int(n)}"}


by_map = defaultdict(list)
for r in rows: by_map[r["mapa"]].append(r)
for v in by_map.values(): v.sort(key=lambda r: int(r["capa"]))
by_page = defaultdict(list)
for r in rows: by_page[r["pagina"]].append(r)


def map_order(r):
    return (r["comarca"], int(re.search(r"mapa (\d+) de", r["mapa"]).group(1)))


def dump_inicis(d):
    return "{\n" + ",\n".join(json.dumps(k, ensure_ascii=False) + ":{\n" + ",\n".join(f"{json.dumps(i)}:{json.dumps(c)}" for i, c in v.items()) + "\n}" for k, v in d.items()) + "\n}\n"


ini_p = ROOT / "data/inicis.json"
inicis = json.loads(ini_p.read_text(encoding="utf-8"))


def put_inicis(page, ids):
    cur = inicis.setdefault(page, {})
    for k in [k for k in ids if k in cur]: pass
    inicis[page] = {k: v for k, v in cur.items() if k not in ids} | ids


def titol_grup(muns):
    if len(muns) <= 2: return " i ".join(muns)
    rest = len(muns) - 2
    return f"{muns[0]}, {muns[1]} i {rest} {'municipi' if rest == 1 else 'municipis'} més"


# ---------- Pàgines de territori ----------
def territory(page):
    path = ROOT / f"data/{page}.json"
    d = json.loads(path.read_text(encoding="utf-8"))
    blk = next((b for b in d["blocks"] if b["course"] == "cuidar"), None)
    have = {g["maps"][0]["mid"] for g in blk["groups"]} if blk else set()
    rs = [r for r in by_page[page] if mid(r["mapa_url"]) not in have]   # els mapes que ja hi són no es toquen
    if not rs:
        print(page, ": ja hi és; res a fer"); return None
    if blk:
        old_mun = {s["title"] for g in blk["groups"] for s in g["sections"]}
        assert not old_mun & {r["municipi"] for r in rs}, "municipi en un mapa nou i en un d'antic"
    groups, used, ids = [], {}, {}
    for mp in sorted({r["mapa"] for r in rs}, key=lambda m: map_order(by_map[m][0])):
        here = [r for r in by_map[mp] if r["pagina"] == page]
        secs = OrderedDict()
        for r in here: secs.setdefault(r["municipi"], []).append(r)
        sections = []
        for mun, srs in secs.items():
            base = f"{slug(mun)}-{PID}"
            k = used.get(mun, 0)
            s = {"title": mun}
            if k == 0:
                s["id"] = base; first = 1
            else:
                s["id"] = f"{base}-{k + 1}"; s["route_prefix"] = base; s["nav"] = f"{mun} (mapa {re.search(r'mapa (\d+) de', mp).group(1).lstrip('0')})"
                first = sum(1 for _ in range(0)) + used_n[mun] + 1
            used_n[mun] = (used_n.get(mun, 0)) + len(srs)
            used[mun] = k + 1
            s["routes"] = [route(r, first + i) for i, r in enumerate(srs)]
            for i, r in enumerate(srs):
                ids[f"{s.get('route_prefix') or s['id']}-ruta-{first + i}"] = f"{r['lat']},{r['lon']}"
            sections.append(s)
        meta = map_meta(by_map[mp])
        groups.append({"id": f"{PID}-{slug(here[0]['comarca'])}-{int(re.search(r'mapa (\d+) de', mp).group(1))}",
                       "title": titol_grup(list(secs)), "maps": [meta], "sections": sections})
    allr = [x for g in groups for s in g["sections"] for x in s["routes"]]
    n = len(allr)
    kms = [float(x["info"].split(" km")[0].replace(",", ".")) for x in allr]
    tmin = min(int(re.search(r"(\d+)–\d+ min caminant", x["info"]).group(1)) for x in allr)
    tmax = max(int(re.search(r"\d+–(\d+) min caminant", x["info"]).group(1)) for x in allr)
    if blk:   # mapes nous a un bloc que ja existeix: s'afegeixen els grups, ordenats per comarca i número de mapa
        blk["groups"] += groups
        gkey = lambda g: (re.sub(r"-\d+$", "", g["id"]), int(re.search(r"-(\d+)$", g["id"]).group(1)))
        blk["groups"].sort(key=gkey)
        tot = sum(len(s["routes"]) for g in blk["groups"] for s in g["sections"])
        blk["summary"] = f"{tot} rutes des de centres educatius"
        return d, blk, ids, True
    b = {"course": "cuidar",
         "text": TXT,
         "summary": f"{n} rutes des de centres educatius", "notice": NOTICE, "groups": groups}
    return d, b, ids, False


used_n = {}
SEE = {"catalunya-central": ["berga"], "alt-pirineu-i-aran": ["seu"], "terres-gironines": ["olot", "ripoll"]}
TERR_REGION = {
    "alt-pirineu-i-aran": "Alt Urgell (sense la Seu d'Urgell), Alta Ribagorça, Cerdanya, Pallars Jussà i Pallars Sobirà",
    "catalunya-central": "Bages, Berguedà (sense Berga), Lluçanès, Moianès, Osona (sense Vic) i Solsonès",
    "terres-de-l-ebre": "Baix Ebre, Montsià, Ribera d'Ebre i Terra Alta",
    "terres-gironines": "Alt Empordà, Garrotxa (sense Olot), Gironès, Pla de l'Estany, Ripollès (sense Ripoll) i Selva",
}
for page in ("alt-pirineu-i-aran", "catalunya-central", "camp-de-tarragona", "ponent", "terres-de-l-ebre", "terres-gironines"):
    used_n.clear()
    res = territory(page)
    if res is None: continue
    d, b, ids, extended = res
    if not extended:
        b["see_also"] = [{"text": f"{CITY_NAME[c][0].upper() + CITY_NAME[c][1:]} té pàgina pròpia, amb {sum(1 for r in by_page[c])} rutes d'aquest curs.", "city": c if c != "seu" else "la-seu-d-urgell", "course": "cuidar"}
                         for c in SEE.get(page, [])]
        if not b["see_also"]: del b["see_also"]
        d["blocks"].append(b)
    ess = sum(len(s["routes"]) for bl in d["blocks"] if bl["course"] == "dia" for g in bl["groups"] for s in g["sections"])
    nmun = len({s["title"] for bl in d["blocks"] for g in bl["groups"] for s in g.get("sections", [])})
    ncur = sum(len(s["routes"]) for g in b["groups"] for s in g["sections"])
    d["summary"] = f"{ess} rutes de l'economia social i solidària i {ncur} de centres educatius en {nmun} municipis."
    d["intro"] = "Rutes a peu per fer el temps de reflexió de cada passa, des d'entitats de l'economia social i solidària i de centres educatius."
    if page in TERR_REGION and not extended: d["region"] = TERR_REGION[page]
    (ROOT / f"data/{page}.json").write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    put_inicis(page, ids)
    print(page, ncur, "rutes (total del bloc),", len({s['title'] for g in b['groups'] for s in g['sections']}), "municipis")

# ---------- Pàgines de ciutat ----------
LABEL = {"tercer-sector": "d'entitats del Tercer Sector Social", "biblioteques-i-centres": "de biblioteques i centres cívics i culturals",
         PID: "de centres educatius públics"}
for key, fname in CITY_FILE.items():
    path = ROOT / f"data/{fname}.json"
    d = json.loads(path.read_text(encoding="utf-8"))
    b = next(b for b in d["blocks"] if b["course"] == "cuidar")
    if any(p.get("id") == PID for p in b["parts"]):
        print(CITY_NAME[key], ": ja hi és; res a fer"); continue
    old_routes = [r for p in b["parts"] for g in p["groups"] for r in g["routes"]]
    nmax = max(r["n"] for r in old_routes)
    rs = by_page[key]
    maps = sorted({r["mapa"] for r in rs}, key=lambda m: map_order(by_map[m][0]))
    groups, n, ids, k = [], nmax, {}, 0
    for mp in maps:
        here = sorted([r for r in by_map[mp] if r["pagina"] == key], key=lambda r: int(r["capa"]))
        groups.append(("tmp", mp, here))
    single = len(groups) == 1
    out_groups = []
    for gi, (_, mp, here) in enumerate(groups, 1):
        meta = map_meta(by_map[mp])
        gid = f"{PID}-rutes" if single else f"{PID}-{gi}"
        routes = []
        for r in here:
            n += 1; routes.append(route(r, n))
            ids[f"{ANCHOR}-ruta-{n}" if single else f"{gid}-ruta-{n}"] = f"{r['lat']},{r['lon']}"
        out_groups.append({"id": gid, "title": (f"Les {len(routes)} rutes" if single else f"{meta['label'].split(' · ')[1].capitalize()} ({len(routes)} {'ruta' if len(routes) == 1 else 'rutes'})"),
                           "maps": [meta | {"routes": [x["n"] for x in routes]}], "routes": routes})
    new = [x for g in out_groups for x in g["routes"]]
    nn = len(new)
    kms = [float(x["info"].split(" km")[0].replace(",", ".")) for x in new]
    tmin = min(int(re.search(r"(\d+)–\d+ min caminant", x["info"]).group(1)) for x in new)
    tmax = max(int(re.search(r"\d+–(\d+) min caminant", x["info"]).group(1)) for x in new)
    part = {"id": PID, "title": "Rutes des de centres educatius", "nav": "Centres educatius",
            "text": TXT,
            "notice": NOTICE, "groups": out_groups, "tele": True}
    b["parts"].append(part)
    # text i resum del bloc, pels comptes de cada part
    desc = []
    for p in b["parts"]:
        rr = [r for g in p["groups"] for r in g["routes"]]
        km = [float(r["info"].split(" km")[0].replace(",", ".")) for r in rr]
        assert p["id"] in LABEL, p["id"]
        desc.append((len(rr), km, LABEL[p["id"]]))
    names = ["tres", "dos"]
    frases = [f"{c} {'ruta' if c == 1 else 'rutes'}, {cuina(min(km), max(km))}, que surten {lab}" for c, km, lab in desc]
    b["text"] = f"Hi ha {'tres' if len(desc) == 3 else 'dos'} tipus de rutes: " + ", ".join(frases[:-1]) + " i " + frases[-1] + ". Totes tornen al punt de sortida."
    b["summary"] = f"{sum(c for c, _, _ in desc)} rutes des d'entitats del Tercer Sector Social, biblioteques i centres educatius"
    path.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    cur = inicis.setdefault(fname, {})
    last = max((k for k in cur if k.startswith(ANCHOR + "-ruta-")), key=lambda k: list(cur).index(k))
    newc = {}
    for k, v in cur.items():
        if k not in ids: newc[k] = v
        if k == last: newc.update(ids)
    inicis[fname] = newc
    print(CITY_NAME[key], nn, "rutes noves; n =", new[0]["n"], "–", new[-1]["n"], "· grups:", len(out_groups))

ini_p.write_text(dump_inicis(inicis), encoding="utf-8")

# ---------- comarques.json (menú «Tria on vols caminar») ----------
cp = ROOT / "data/comarques.json"
cd = json.loads(cp.read_text(encoding="utf-8"))
head = {k: v for k, v in cd.items() if k.startswith("_")}
body = {k: v for k, v in cd.items() if not k.startswith("_")}
add = 0
for r in rows:
    v = [r["comarca"], r["provincia"]]
    if r["municipi"] not in body: body[r["municipi"]] = v; add += 1
    elif body[r["municipi"]] != v: print("AVÍS comarca diferent:", r["municipi"], body[r["municipi"]], v)
srt = lambda n: slug(re.sub(r"^(El|La|Els|Les|L') ?", "", n))
cd = head | dict(sorted(body.items(), key=lambda kv: srt(kv[0])))
lines = [f"  {json.dumps(k, ensure_ascii=False)}: {json.dumps(v, ensure_ascii=False)}" for k, v in cd.items()]
cp.write_text("{\n" + ",\n".join(lines) + "\n}\n", encoding="utf-8")
print("comarques.json: +", add, "municipis")
