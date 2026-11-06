# Web de Camins d'Esperança [Activa]

Web estàtica dels cursos i les rutes a peu de Camins d'Esperança [Activa] (L'Espiral i Elara Social).
Es publica amb GitHub Pages des de la carpeta `docs/`.

## On és cada cosa

- `data/site.json`: tots els textos (inici, cursos, preguntes, peu de pàgina, contacte, enllaços de Thinkific).
- `data/barcelona.json`, `data/el-prat.json`, `data/olot.json`, `data/vic.json`: les rutes de cada ciutat, agrupades per curs, amb els mapes de My Maps (`mid`, centre `ll` i zoom `z`).
- `src/templates/`: les plantilles de les pàgines.
- `src/site.css` i `src/site.js`: l'aspecte i el menú del mòbil.
- `src/img/`: el logo i altres imatges.
- `docs/`: la web generada. No s'edita a mà: es torna a generar.

## Com es fa un canvi

1. Canvia el text o la ruta al fitxer de `data/`.
2. Genera la web: `python3 build.py`. L'adreça pública i si surt als cercadors es configuren a `data/site.json`, a `publish`. Quan hi hagi domini propi: canvia-hi `url`, crea el fitxer `CNAME` amb el domini i torna a generar la web.
3. Desa i puja els canvis. GitHub Pages actualitza la web en un o dos minuts.

## Infografies animades

Són a `src/templates/infografies/` (una per fitxer, copiada del bloc INICI–FINAL de la carpeta de Drive «Infografies web») i es posen a les plantilles amb `{% include %}`. Fan servir els colors i les lletres de `site.css`, s'animen quan surten a la pantalla i, amb «reduir moviment», surten ja acabades.

- Inici: `esperanca-activa` (sota la capçalera), `com-funciona` i `7-passes` (sense `curs`).
- Els cursos: `cursos`. L'enllaç de base és `{{ root }}`; el text de «Camina per la teva ciutat» surt de `cities` de `data/site.json`, i el 4t curs n'agafa la frase de la targeta i si està «Properament».
- Cada curs: `capcalera-curs` (`{% with escena = course.key %}`) i `7-passes` (`{% with curs = course.key %}`). A sota de l'espiral, la llista de les 7 passes en text, plegada.
- Les ciutats i cada ciutat: `ciutats`, `llegir-ruta` (`#com-llegir-una-ruta`) i `abans-de-sortir`, dins la macro `before_walk` de `parts.html`, amb la llista en text plegada.
- Preguntes: `i-despres`, dins la resposta de «Què passa quan acabo?» (tercer element de la pregunta a `data/site.json`), i `iniciativa`, a «Una iniciativa de», abans del contacte.
- `cami` no es fa servir.
- Canvis fets al codi de les infografies: a `7-passes`, 16 px de marge al mòbil perquè la passa 7 no es talli; a `iniciativa`, el botó de la Prescripció Social ara és la signatura de L'Espiral i Elara Social.

## Enllaços als cursos de Thinkific

- El camp `thinkific` de cada curs (a `data/site.json`) porta directament al formulari d'inscripció, sense passar per la pàgina de presentació de Thinkific: `https://espiral-elara-social.thinkific.com/enroll/<número del curs>`. El número és el del botó «Inscripció gratuïta» de la pàgina del curs a Thinkific.
- Un curs que encara no està obert porta `"soon": true`: té pàgina a la web i surt a les targetes i a la infografia dels cursos amb la marca «Properament», però cap botó porta a Thinkific. Quan s'obri, n'hi ha prou de treure `"soon": true` i tornar a generar la web.

## Afegir una ciutat

1. Copia un fitxer de `data/` (per exemple `olot.json`) amb el nom de la ciutat nova (`girona.json`) i omple-hi les rutes i els mapes.
2. A `data/site.json`, a `cities`, afegeix-hi la ciutat (`slug`, `name`, `region`, `icon`), en ordre alfabètic. Sortirà sola als desplegables i a les targetes.
3. Genera la web.

## Desplegables «Vés directament a…»

- A Inici, a Les ciutats i a cada pàgina de curs hi ha un desplegable que porta a la targeta de la ciutat triada (`#ciutat-olot`).
- Dins d'una ciutat, si un bloc de curs té 3 mapes o més (o 3 districtes o més), surt un desplegable abans dels mapes que porta al districte, la zona o el mapa triat. Sota el nom de cada mapa hi ha un enllaç per tornar al desplegable.
- Si el bloc té diversos grups (un per districte), cada districte és una opció. Si té un sol grup amb diversos mapes (Vic, parcs), cada mapa és una opció i el nom surt de `label` (o de `zone`, si el mapa en té).
- Si el bloc té un grup per mapa i diversos mapes per districte (Barcelona, parcs i jardins), amb `"zones": {"by": "district"}` al bloc el desplegable mostra un districte per opció (camp `district` de cada grup) i porta al primer mapa del districte.
- Un bloc pot tenir diverses parts (`"parts"`), cada una amb `id`, `title`, `nav` (el text de l'enllaç a dalt del bloc), `text`, un avís opcional (`"notice": {"title": ..., "html": [paràgrafs]}`), els seus `groups` i el seu desplegable. Barcelona «Quan la vida» en té dues: les rutes des dels CAP i les rutes «Caminant fem salut», que no surten d'un CAP i porten l'avís. La primera part manté el desplegable del curs (`#quan-la-vida-tria`); les altres en tenen un de propi (`#caminant-fem-salut-tria`).
- Els textos es poden canviar a la ciutat o al bloc amb `"zones": {"label": ..., "placeholder": ..., "back": ...}` (Barcelona: «Vés directament al teu districte»). El mínim de mapes és `ZONES_MIN` a `build.py`.

## Adreces directes (per enllaçar des de Thinkific)

Cada bloc de curs d'una ciutat té una adreça pròpia:

- `/barcelona/#quan-la-vida` (rutes des dels CAP i rutes «Caminant fem salut»; cada part té la seva adreça: `/barcelona/#rutes-cap` i `/barcelona/#caminant-fem-salut`), `/barcelona/#quan-cuidar-nos` (equipaments comunitaris), `/barcelona/#quan-el-mon` (parcs i jardins)
- `/el-prat/#quan-la-vida`, `/el-prat/#quan-cuidar-nos`, `/el-prat/#quan-el-mon`
- `/vic/#quan-la-vida` (rutes des dels CAP i hospitals, 24 a 28), `/vic/#quan-cuidar-nos` (rutes des dels equipaments comunitaris, 1 a 16, amb numeració pròpia), `/vic/#quan-el-mon`
- `/olot/#quan-la-vida` (rutes des dels CAP i l'hospital, 1 a 4, i rutes saludables PAFES, 5 a 13)

I cada ruta, la seva (el desplegable s'obre sol):

- `/vic/#quan-el-mon-ruta-5`, `/vic/#quan-la-vida-ruta-24`, `/vic/#quan-cuidar-nos-ruta-3`, `/el-prat/#quan-la-vida-ruta-12`, `/olot/#quan-la-vida-ruta-2`
- Barcelona, rutes «Caminant fem salut» (Quan la vida), per districte: `/barcelona/#ciutat-vella-ruta-1`, `/barcelona/#gracia-ruta-3`. Fins al 6 de novembre de 2026 eren a «Quan cuidar-nos»: les adreces no han canviat.
- Barcelona, equipaments comunitaris (Quan cuidar-nos): un districte `/barcelona/#equipaments-gracia` (el seu mapa; Sant Martí en té dos: `/barcelona/#equipaments-sant-marti` i `/barcelona/#equipaments-sant-marti-mapa-2`), un barri `/barcelona/#equipaments-el-raval` i una ruta `/barcelona/#equipaments-el-raval-ruta-2`. Les rutes es numeren per barri, com als mapes.
- Barcelona, rutes des dels CAP (Quan la vida): `/barcelona/#cap-gracia-ruta-6`; el mapa i el desplegable d'un districte: `/barcelona/#cap-gracia`
- Barcelona, parcs i jardins (Quan el món): un districte `/barcelona/#parcs-gracia` (el seu primer mapa), un mapa `/barcelona/#parcs-eixample-mapa-3`, un barri `/barcelona/#barri-la-vila-de-gracia` i una ruta `/barcelona/#barri-el-raval-ruta-1`. Les rutes es numeren per barri, com als mapes. Si un barri continua al mapa següent, les seves rutes mantenen l'adreça del barri (`/barcelona/#barri-el-fort-pienc-ruta-10`).

Altres: `/vic/#quan-el-mon-rutes-21-a-23` i `/vic/#quan-cuidar-nos-rutes-9-a-16` (un mapa de Vic), `/vic/#quan-el-mon-rutes` (la llista de rutes), `/barcelona/#sants-montjuic-i-les-corts` (un grup de districtes), `/preguntes/#es-realment-gratuit` (una pregunta).

## El botó «Obre el mapa»

Cada ruta té un botó que obre, a pantalla completa, el mapa de My Maps on és (amb totes les rutes d'aquell mapa). Si un grup té un sol mapa, totes les rutes hi van. Si en té diversos, cada mapa diu quines rutes té amb `"routes": [1, 2, ...]` (com Vic «Quan el món», el Prat «Quan la vida» i Olot «Quan la vida»); si en falta alguna, `build.py` avisa. El camp `dest` de les rutes ja no es fa servir.

## Dades

Les rutes vénen de la web de Google Sites (publicada el 3 de novembre de 2026), que es va fer amb el full «Rutes per ciutat i curs» i els GPX. No s'han d'inventar dades: si en falta alguna, es deixa marcada amb `[PENDENT]`.

Les 65 rutes de Barcelona des dels equipaments comunitaris («Quan cuidar-nos és una tasca col·lectiva», 6 de novembre de 2026) vénen del full «Rutes Barcelona - Prescripció social» (pestanyes «Rutes» i «Mapes») i de les fitxes dels 11 mapes de My Maps: el nom i l'adreça del punt d'inici, els km, el temps caminant i amb pauses i, de l'apartat «Accessibilitat i seguretat», només els avisos que no són de tots els recorreguts (escales, desnivell, parcs amb horari). Les 42 rutes que abans eren en aquest curs són ara a «Quan la vida», en una part pròpia: són una adaptació dels itineraris urbans «Caminant fem salut» publicats al Canal Salut (https://canalsalut.gencat.cat/.content/_Vida_saludable/Activitat_fisica/Rutes_saludables/rutes-pel-districte.pdf).

Les 16 rutes de Vic des dels equipaments comunitaris («Quan cuidar-nos és una tasca col·lectiva», 6 de novembre de 2026) vénen de les fitxes dels 2 mapes de My Maps «Rutes d’Esperança Activa - Vic · equipaments comunitaris» (rutes 1–8 i 9–16): el nom i l’adreça del punt d’inici, els km, el temps caminant i amb pauses i, de l’apartat «Accessibilitat i seguretat», els trams de terra, d’escales o per carretera i els pendents. Tenen numeració pròpia (1 a 16), diferent de la dels parcs (1 a 23) i de la dels CAP i hospitals (24 a 28).

Les 261 rutes de Barcelona pels parcs i jardins («Quan el món et preocupa», 5 de novembre de 2026) vénen del full «Rutes Barcelona - Parcs i jardins» (pestanyes «Rutes» i «Mapes») i de les fitxes dels 31 mapes de My Maps: el nom i l'adreça del punt d'inici, els km i el temps caminant i amb pauses. De les observacions del full només s'hi posen les que serveixen a qui camina (horaris, pendents, on comença la ruta).
