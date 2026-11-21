#!/usr/bin/env python3
"""Afegeix `desc` (una frase) a les 15 rutes de «sostenir» de les comarques. Idempotent."""
import json, sys
D = {
"Cal Blanxart": "Cal Blanxart és una cooperativa d'habitatge en cessió d'ús que rehabilita un gran edifici del casc antic de Berga com a projecte de ciutat, amb espais comunitaris i per a entitats.",
"Fundació Horitzó": "La Fundació Horitzó treballa per la salut mental al Berguedà: ofereix acompanyament i projectes d'inserció laboral a persones amb problemes de salut mental o en risc d'exclusió.",
"Vidàlia (Cal Vidal, Puig-reig)": "Vidàlia és una cooperativa d'habitatge que rehabilita la colònia tèxtil de Cal Vidal, a Puig-reig, i hi viu en comunitat, amb espais i tasques compartits.",
"La Lluerna": "La Lluerna és la llibreria cooperativa de Ripoll, que organitza clubs de lectura i activitats culturals al Ripollès.",
"Fundació MAP": "La Fundació MAP és l'entitat del Ripollès que atén persones amb discapacitat i ho combina amb formació i feina des d'una empresa d'economia social.",
"Obrador Ricolta (Beget, Camprodon)": "L'Obrador Ricolta és una cooperativa que ha tornat el forn de pa a Beget i que també treballa la comunicació i el disseny des de l'economia social i solidària.",
"Integra Pirineus": "Integra Pirineus és una fundació que acompanya cap a la feina persones amb discapacitat intel·lectual o trastorn de salut mental, vinculada a la gestió forestal de la Muntanya d'Alinyà.",
"La Granja de la Fageda": "La Fageda és una cooperativa de la Garrotxa que elabora productes làctics, com els iogurts, i dona feina a persones amb trastorn mental.",
"La Fageda (plaça Major de Santa Pau)": "La Fageda és una cooperativa de la Garrotxa que elabora productes làctics, com els iogurts, i dona feina a persones amb trastorn mental.",
"Sambucus": "Sambucus és una cooperativa de Manlleu que porta un restaurant de cuina de mercat al mercat municipal i conrea plantes aromàtiques i medicinals.",
"Cooperativa Sequoia": "Sequoia és una cooperativa d'habitatge en cessió d'ús on viu una comunitat que s'autogestiona, amb hort, forn de pa i activitats culturals.",
"Osonament": "Osonament és una entitat que treballa per la prevenció i l'atenció a la salut mental a Torelló i la Vall del Ges, amb activitats comunitàries i de rehabilitació.",
"Olost i Santa Creu Sostenible": "Olost i Santa Creu Sostenible és una cooperativa que fa de comunitat energètica local: veïnes i veïns gestionen i comparteixen energia renovable.",
"Balenyà Sostenible": "Balenyà Sostenible és una cooperativa i comunitat energètica sense ànim de lucre, que també treballa perquè les persones vulnerables tinguin accés a l'energia.",
"Taradell Sostenible": "Taradell Sostenible és una cooperativa que fa de comunitat energètica local: veïnes i veïns gestionen i comparteixen energia renovable.",
}
n=0
def walk(o):
    global n
    if isinstance(o,dict):
        if o.get("name") in D and "info" in o and "desc" not in o:
            o["desc"]=D[o["name"]]; n+=1
        for v in o.values(): walk(v)
    elif isinstance(o,list):
        for v in o: walk(v)
for f in ["berga","ripoll","la-seu-d-urgell","olot","catalunya-central"]:
    p=f"data/{f}.json"; d=json.load(open(p,encoding="utf-8"))
    # només dins els blocs del curs "dia"
    for b in d.get("blocks",[]):
        if b.get("course")=="dia": walk(b)
    json.dump(d,open(p,"w",encoding="utf-8"),ensure_ascii=False,indent=2); open(p,"a").write("\n")
print(n,"desc afegides")
