#!/usr/bin/env python3
"""Rutes del curs «Quan el món et preocupa» (bloc `mon`) per a Berga (2), Ripoll (4), la Seu d'Urgell (2) i Olot (2).
Berga/Ripoll/la Seu: bloc nou. Olot: substitueix el bloc provisional («Encara no hi ha rutes…»). Vic no es toca.
Escriu també els punts d'inici a data/inicis.json (clau quan-el-mon-ruta-N). Idempotent.
Font: KML de Drive («Quan el món et preocupa»); temps, origen i accessibilitat de la descripció de cada KML.
"""
import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
WL = "https://www.wikiloc.com/wikiloc/view.do?id="
PARK = "Circuit urbà curt per parcs i carrers; travessa amb atenció els carrers amb trànsit."
LINK = "Més propostes i recursos a <a href=\"https://elarasocial.com/\" target=\"_blank\" rel=\"noopener\">elarasocial.com</a>."
NOTICE = {"title": "Traçats i punts d'inici", "html": [
    "Els traçats oficials són simplificats: els quilòmetres poden diferir lleugerament dels de les webs d'origen. Als circuits de parc, el traçat és reconstruït sobre OpenStreetMap i el punt d'inici és aproximat. Camina amb atenció al trànsit i a l'estat dels camins.", LINK]}
C = {
"berga": ("berga", "Berga", "1wMbfTmTqIfcwvtpCxH1aTiQwcd8IKDY", "un sender fins al santuari de Queralt i un circuit pels parcs", [
  ("A Queralt per les capelles", "Plaça de Sant Francesc, Berga", "7,50", "90–112", "100–130", "297505733", "42.10395,1.84430",
   "Pujada continuada fins al santuari de Queralt, amb trams per camins que poden no estar asfaltats. Porta aigua i calçat adequat. El track oficial surt uns 120 m al nord de la plaça."),
  ("Parc del Pla de l'Alemany", "Parc del Pla de l'Alemany, Berga", "1,94", "23–29", "35–50", "297506623", "42.09800,1.84085", PARK + " Alguns trams tenen pendent suau.")]),
"ripoll": ("ripoll", "Ripoll", "1YjyjUS6aLBZhyJuGR28pZl_Q61-S1LI", "tres senders i un circuit pel Parc Temàtic del Pirineu", [
  ("Ruta arquitectònica de Ripoll", "Plaça de l'Abat Oliba, Ripoll", "1,82", "22–27", "30–45", "297506338", "42.20114,2.19022",
   "Recorregut urbà pel nucli de Ripoll, amb algun tram amb pendent i carrers amb trànsit que cal travessar amb atenció."),
  ("Font del Clot dels Vents – Font dels Pintors", "Plaça de l'Abat Oliba, Ripoll", "7,42", "89–111", "100–130", "297506001", "42.20110,2.19019",
   "Camins i corriols que poden no estar asfaltats, amb trams amb pendent. Porta aigua i calçat còmode, i no beguis aigua de les fonts si no n'indiquen la potabilitat. El GPX d'origen anomena la primera font «Clot dels Verns»."),
  ("Mirador de Santa Maria del Catllar", "Raval de Barcelona, Ripoll", "9,38", "113–141", "125–160", "297506200", "42.19991,2.18727",
   "Camins de muntanya que poden no estar asfaltats, amb trams amb pendent i poca ombra. Porta aigua, calçat adequat i comprova el temps abans de sortir."),
  ("Parc Temàtic del Pirineu i ribera del Ter", "Parc Temàtic del Pirineu, Ripoll", "1,85", "22–28", "30–50", "297506454", "42.19597,2.19375",
   PARK + " Pel tram de la ribera del riu, vigila el terra si ha plogut.")]),
"seu": ("la-seu-d-urgell", "la Seu d'Urgell", "1U4ydgxRRUmOug_3JDM3r6TdNYpotObU", "un sender per la ribera del Segre i un circuit pels parcs", [
  ("Volta al Segre des del Parc Olímpic del Segre", "Parc Olímpic del Segre, la Seu d'Urgell", "8,72", "105–131", "115–150", "297504734", "42.35878,1.47328",
   "Camins vora el riu, amb algun tram amb pujades (desnivell acumulat de 142 m) i poca ombra. Porta aigua i protecció solar, i comprova l'estat dels camins abans de sortir."),
  ("Parc de la Boixadera", "Parc de la Boixadera, la Seu d'Urgell", "1,95", "23–29", "35–50", "297506734", "42.35665,1.45163", PARK)]),
"olot": ("olot", "Olot", "1DhKBnpVjSynhhWsJ7IarbbArii2AFjw", "un sender pels volcans del Montsacopa i del Montolivet i un circuit pel Parc Nou", [
  ("Volcans del Montsacopa i del Montolivet", "Plaça de Clarà, Olot", "8,25", "99–124", "110–145", "297506852", "42.18081,2.48604",
   "Pujades als dos volcans (desnivell acumulat de 328 m) i camins que poden no estar asfaltats. Segons Ohgarrotxa, l'accés a la pedrera del Montsacopa està tancat per un despreniment: comprova'n l'estat abans de sortir."),
  ("Parc Nou", "Parc Nou, Olot", "1,62", "19–24", "30–45", "297507038", "42.17180,2.47884", PARK + " Alguns trams del parc poden tenir pendent.")]),
}
ini_p = ROOT / "data/inicis.json"
inicis = json.loads(ini_p.read_text(encoding="utf-8"))
for key, (slug, nom, mid, que, rs) in C.items():
    p = ROOT / f"data/{slug}.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    old = next((b for b in d["blocks"] if b["course"] == "mon"), None)
    if old and "groups" in old:
        print(nom, ": ja hi és"); continue
    n = len(rs)
    routes = []
    for i, (name, addr, km, c, pa, wl, ll, note) in enumerate(rs):
        routes.append({"n": i + 1, "name": name, "info": f"{km} km · {c} min caminant · {pa} min amb pauses · circular",
                       "address": addr, "note": note, "wikiloc": WL + wl})
    lat = sum(float(r[6].split(",")[0]) for r in rs) / n; lon = sum(float(r[6].split(",")[1]) for r in rs) / n
    kms = [float(r[2].replace(",", ".")) for r in rs]
    b = {"course": "mon",
         "text": (f"{n} rutes circulars: {que}. Surten d'un lloc concret de la ciutat i hi tornen. "
                  "Tria la que s'adapti al teu dia i fes-hi el temps de reflexió de cada passa."),
         "summary": f"{n} rutes: senders i parcs", "notice": NOTICE,
         "groups": [{"title": f"Les {n} rutes", "maps": [{"mid": mid, "title": f"{nom[0].upper()+nom[1:]} · parcs, camins i senders",
                     "ll": f"{lat:.4f},{lon:.4f}", "z": 13, "label": f"{n} rutes"}], "routes": routes}]}
    if old: d["blocks"][d["blocks"].index(old)] = b
    else: d["blocks"].append(b)
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    cur = inicis.setdefault(slug, {})
    for r in routes:
        cur[f"quan-el-mon-ruta-{r['n']}"] = rs[r["n"] - 1][6]
    print(nom, n, "rutes")
def dump(d):
    return "{\n" + ",\n".join(json.dumps(k, ensure_ascii=False) + ":{\n" + ",\n".join(f"{json.dumps(i)}:{json.dumps(c)}" for i, c in v.items()) + "\n}" for k, v in d.items()) + "\n}\n"
ini_p.write_text(dump(inicis), encoding="utf-8")
