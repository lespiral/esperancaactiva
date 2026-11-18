#!/usr/bin/env python3
"""Genera data/barcelona-taula.json (subpàgina /barcelona/taula-tercer-sector/, 698 rutes d'entitats de la
Taula del Tercer Sector Social, curs `cuidar`) i les entrades de data/inicis.json d'aquesta pàgina.

Font: tools/taula_tercer_sector.tsv (codi D0X-TTS-NNN, entitat, km, id de Wikiloc, punt d'inici llegit del
KML de cada mapa de My Maps, descripció del full «Taula Tercer Sector - Entitats amb ubicació física»).
Cap contacte, web ni xarxa d'entitat. Es pot tornar a executar."""
import csv, json, pathlib, re, unicodedata

ROOT = pathlib.Path(__file__).resolve().parent.parent
SLUG = "barcelona/taula-tercer-sector"
rows = {r["codi"]: r for r in csv.DictReader((ROOT / "tools/taula_tercer_sector.tsv").open(encoding="utf-8"), delimiter="\t")}

DISTRICTES = {  # codi: (nom, [(mid, nombre de rutes)])
 "D01": ("Ciutat Vella", [("1ASIs46BYHX7cLp1n0FoEnRTfwt4fzvo",10),("17RrEdMhuNR94t_O9Kk93_WUPrBVzvPU",10),("18ME8_8plsVS0fOPCaNEK4UZI1udvIVU",10),("1vM6rRw4u4KsLgBljXgSYWskO3oM0D1w",10),("1UgCN3D6ivBVNntXaUXKz6wM1Cd8lRp4",10),("1bNc0LdFbDeNEQ2cr8jLiwMFtVWbsO7M",10),("1GHdqE-JcJV8dfsOtsdgqiE7gAnQxlP4",10),("1cHebh-Vq75jztvrx6oUzAeS2FdIiSGM",10),("1iQ9fH-4enE2SkK9bB2BNE1zk4_CB8fs",10),("1zXzngmvFX6V3tH7NA_Dl-HcaTKp90L4",10),("1z5DyIvrlfBN9ekkmzba6JNLS4T-q70c",10)]),
 "D02": ("Eixample", [("1Q_LePvX5gr8u0Ehl5GzpDiHNqQcejdA",10),("1H_lUKplqb0OoW1DvZD68Q3T4QsUQ08Y",10),("1yjNrSkfMHa3C6QMuswhfdFjZtNaYqbk",10),("1ucA8P3T-duRMMXYFhxTW0uF4vYFaeSY",10),("1MjDzeoZkP5QuUnNPMgp2bIBY-D5pjnc",10),("1SCrV1ZwVBB6aTMHDtMa6feGSaKvrQXo",10),("1_HnlosRJcheKaGsqq1wyMWKqjFzyOIQ",10),("1z-E1ARfzD_hVWPuXSrx13oZY1xi7QhI",10),("19ncbOh3200prR6wHHLHXEhwSt7-GlnY",10),("1QDWVGXxKHHm4NeSkGt9gjLk2bjQefPA",10),("1FpxAVIEtS4DaCqhxASNII-WfHFWJklE",10),("1iJOyDyBAqaeeONmepMLILuZ4VVgyJRA",10),("15P2Bz3SQqgXL_0og7dMN4gVTR3Peb0M",10),("1yLsJHLwOpObFhfHBBu60WAPMSLWKww0",4)]),
 "D03": ("Sants-Montjuïc", [("1bvAGs40NfW0TvFMqlECFU0rRbKhbftU",9),("1_PzzDXzeJ74uPJSGOcQie5n7r61vuXk",9),("1574iQkk5APxnCDcnnI4KbLGwNtWmjbU",9),("1BM0keHPoFkcHJseW0bRcPetrldlOajU",9),("1F8fHummLoG2l0bdhuX9_kMiJlQuaut0",9),("1mzzio4-q6rz30-3uNKXs356EhX2pc9g",8),("1iFzVZCulotCPnFsQcVVI_9sTh-b0Ckk",8)]),
 "D04": ("Les Corts", [("1lHB24SQX4yAEhLyZQfPy0srYkH-oypw",10),("14Uumqjj3KB_QSBghNM69af2XSNb6U-Y",10),("1Lq7-5cWWBjO7eBeFlY5lyor8caknLn0",10)]),
 "D05": ("Sarrià-Sant Gervasi", [("1aYqcEFQPWIN4wIyzhsQiXF5brahdJWw",10),("1mLRVqjH7hDarNvyWJ9bPnDNUnwbeLqs",10),("1F50ntNi59-haDbzpJzlG7DroZR2lAxw",10),("1oD7SX2KVozyz7IZCWDnrPxJvNUoVuJ8",9),("1yXx31APXLAMvZwKYfK7w_6o3o8me0nY",9),("1hhYUSpPn9Uq38U5nu5w8SfZbOAenj6A",9),("1wCAi66c62q0WVxsm_Jpsm7kzaFsYv9M",9),("17VuOOnUtOCaEuO2N3kmkrr958wA8lnU",9)]),
 "D06": ("Gràcia", [("1BHxY0tksCXQ8XhaFf-rXsoqw9_PCUVA",10),("13A_SjyM40WcF1Mk2WT200vejhOWlRNM",10),("1f4I-OC5xo1gD3x1TqilgUYzQ0sIS9uM",10),("1UBpGT9hyLVVulcpX8ymbtEudbRuTUw4",10),("1ikKMv6DGoMzI9ZhjWPdq0Z_zX0ba4js",10),("188_aeHyqoLc3twxK0-AjoesvpZpsnGc",10),("1tH7uYnxw_8bOWbQAykk3Y1iwIXpxSb4",8)]),
 "D07": ("Horta-Guinardó", [("14VTnmLAemsEymy_uqzlw3UMfHIYm5v8",10),("1rwQI2kV1_6k_V_Qbo5CgqQGBCh43jG4",9),("1ZmdEuIaK9z7lM2L8hPbOZAVi1s2lPiI",9),("1I9QsnRsM0r5ssZ5S8wqr9pmky8FhXqk",9),("1Oo63thXntvMbIs24okqcsKKRIhz19Sw",9),("1EamiHq_SNj-xs0Yn0_No4Iza4nOI6Z8",9)]),
 "D08": ("Nou Barris", [("1QVoeD5e3B1cWIXdDj5vo-g8zd0YDKjg",10),("1dbPgNz_xLsdY89OSPXmhSMdNyiZmhjw",10),("1YFn8NWbeBpimEZM8BZ7FFoRck2HQ3tI",10),("1MF-icqyk2HDgOWn8x_weUt6LvW_b8pg",6)]),
 "D09": ("Sant Andreu", [("12N5prz9-peBVULnclNywZUJDgyxfZJU",10),("1kpt4EshzZSvvdJt-D87eKkgVQan4m1o",10),("1BYJl6DLH7SFxarQwNpyKWAWBXHYUSek",10),("1zfCsSFANogTU8daqNKF7Ghli4tZk5Q0",10),("1A0ilzdvqlb2QdrDT-euKEpXtaw2On1g",10),("1VBta90jr2czScwHcnxNnb908RjzzmIs",3)]),
 "D10": ("Sant Martí", [("1NeZ_XybMO64PKHT14mJQu24NKbTHV10",10),("1bStZtKqjWTf1ZqmjTO2CAWJGxQHl3pI",10),("1TgGv4EGUkdQaiMeUMZSKliCROf4TY4U",10),("1Lk3PFW8ZNQlVnB3o0ed6oroBFJI2R8c",10),("1163MjqDhz6uM_iR52aP9R6pV-qeXySY",10),("10TpFxTEJbxgq-jWnApQu-yEDF44_NmQ",10),("1P86oyclJIAIEWPkUkJ7Bex4yDvIsMPI",10),("12HEtisZ_IpaXK14SESiu2Jp_nzg9gLE",6)]),
}

def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

def cat_km(s): return f"{float(s):.1f}".replace(".", ",")

groups, inicis, kms = [], {}, []
for dc, (nom, maps) in DISTRICTES.items():
    n0 = 1
    for k, (mid, cnt) in enumerate(maps, 1):
        codes = [f"{dc}-TTS-{n:03d}" for n in range(n0, n0 + cnt)]
        assert all(c in rows for c in codes), codes
        gid = f"{slug(nom)}-{k}"
        pts = [tuple(map(float, rows[c]["inici"].split(","))) for c in codes]
        lat = sum(p[0] for p in pts) / cnt; lon = sum(p[1] for p in pts) / cnt
        routes = []
        for n, c in zip(range(n0, n0 + cnt), codes):
            r = rows[c]; km = float(r["km"]); kms.append(km)
            x = {"n": n, "name": r["entitat"], "info": f"{cat_km(r['km'])} km aprox. · {round(km*12)}–{round(km*15)} min caminant · circular"}
            if r["adreca"].strip(): x["address"] = r["adreca"].strip()
            if r["descripcio"].strip(): x["desc"] = r["descripcio"].strip()
            x["wikiloc"] = f"https://www.wikiloc.com/wikiloc/view.do?id={r['wikiloc']}"
            routes.append(x)
            inicis[f"{gid}-ruta-{n}"] = r["inici"]
        a, b = n0, n0 + cnt - 1
        groups.append({"id": gid, "title": f"{nom} · rutes {a} a {b}", "district": nom,
            "maps": [{"mid": mid, "title": f"Barcelona · {nom} · Taula del Tercer Sector ({k}/{len(maps)})",
                      "ll": f"{lat:.4f},{lon:.4f}", "z": 14, "label": f"{nom}: rutes {a} a {b}"}],
            "routes": routes})
        n0 += cnt
    assert n0 - 1 == sum(c for _, c in maps)

n = sum(len(g["routes"]) for g in groups)
assert n == 698 == len(rows), n
lo, hi = cat_km(min(kms)), cat_km(max(kms))
data = {"slug": SLUG, "name": "Barcelona · Taula del Tercer Sector", "region": "Barcelonès",
  "title": "Rutes des d'entitats del Tercer Sector Social de Barcelona",
  "summary": f"{n} rutes des d'entitats del Tercer Sector Social",
  "intro": "Rutes circulars a peu que surten d'entitats del Tercer Sector Social de Barcelona, dels 10 districtes. Tria el teu districte o busca una entitat pel nom.",
  "blocks": [{"course": "cuidar",
    "text": f"{n} rutes circulars, de {lo} a {hi} km (uns {5*round(min(kms)*12/5)}–{5*round(max(kms)*15/5)} minuts caminant), que surten d'una entitat del Tercer Sector Social de Barcelona i hi tornen: una ruta per entitat. Són un temps per caminar i reflexionar: portar a la vida quotidiana el que has après al curs «Quan cuidar-nos és una tasca col·lectiva», adonar-te de com et sents i pensar en petites accions que contribueixin al teu benestar i al de les persones que t'envolten. Tria el districte, busca l'entitat que et quedi més a prop i camina-hi amb calma.",
    "summary": f"{n} rutes des d'entitats del Tercer Sector Social",
    "zones": {"by": "district"},
    "filter": {"label": "Busca una entitat", "placeholder": "Escriu el nom de l'entitat", "empty": "Cap entitat coincideix amb la cerca.", "count": "{n} entitats"},
    "see_also": [{"text": "Torna a Barcelona", "href": "barcelona/#quan-cuidar-nos"}],
    "notice": {"title": "Traçats orientatius", "html": [
      "Els traçats s'han reconstruït sobre OpenStreetMap a partir de l'adreça de cada entitat: no són traçats oficials. Camina amb atenció al trànsit i a l'estat dels camins.",
      "Més propostes i recursos a <a href=\"https://elarasocial.com/\" target=\"_blank\" rel=\"noopener\">elarasocial.com</a>."]},
    "groups": groups}]}
(ROOT / "data/barcelona-taula.json").write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
ip = ROOT / "data/inicis.json"
d = json.loads(ip.read_text(encoding="utf-8")); d[SLUG] = inicis
def dump(d):  # mateix format que ja té el fitxer: una pàgina per bloc, una ruta per línia
    return "{\n" + ",\n".join(json.dumps(k, ensure_ascii=False) + ":{\n" + ",\n".join(f"{json.dumps(i)}:{json.dumps(c)}" for i, c in v.items()) + "\n}" for k, v in d.items()) + "\n}\n"
ip.write_text(dump(d), encoding="utf-8")
print(n, "rutes", len(groups), "mapes", lo, "-", hi, "km")
