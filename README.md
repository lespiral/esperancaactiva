# Web de Camins d'Esperança [Activa]

Web estàtica dels cursos i les rutes a peu de Camins d'Esperança [Activa] (L'Espiral i Elara Social).
Es publica amb GitHub Pages des de la carpeta `docs/`.

## On és cada cosa

- `data/site.json`: tots els textos (inici, cursos, preguntes, peu de pàgina, contacte, enllaços de Thinkific).
- `data/barcelona.json`, `data/el-prat.json`, `data/vic.json`: les rutes de cada ciutat, agrupades per curs, amb els mapes de My Maps (`mid`, centre `ll` i zoom `z`).
- `src/templates/`: les plantilles de les pàgines.
- `src/site.css` i `src/site.js`: l'aspecte i el menú del mòbil.
- `src/img/`: el logo i altres imatges.
- `docs/`: la web generada. No s'edita a mà: es torna a generar.

## Com es fa un canvi

1. Canvia el text o la ruta al fitxer de `data/`.
2. Genera la web: `python3 build.py`. L'adreça pública i si surt als cercadors es configuren a `data/site.json`, a `publish`. Quan hi hagi domini propi: canvia-hi `url`, crea el fitxer `CNAME` amb el domini i torna a generar la web.
3. Desa i puja els canvis. GitHub Pages actualitza la web en un o dos minuts.

## Afegir una ciutat

1. Copia un fitxer de `data/` (per exemple `vic.json`) amb el nom nou (`ripoll.json`) i omple-hi les rutes i els mapes.
2. A `data/site.json`, a `cities`, posa-hi el `slug` (`"ripoll"`) i treu `"soon": true`.
3. Genera la web.

## Adreces directes (per enllaçar des de Thinkific)

Cada bloc de curs d'una ciutat té una adreça pròpia:

- `/barcelona/#quan-la-vida` (rutes des dels CAP), `/barcelona/#quan-cuidar-nos`
- `/el-prat/#quan-la-vida`, `/el-prat/#quan-cuidar-nos`, `/el-prat/#quan-el-mon`
- `/vic/#quan-la-vida` (rutes des dels CAP i hospitals, 24 a 28), `/vic/#quan-el-mon`

I cada ruta, la seva (el desplegable s'obre sol):

- `/vic/#quan-el-mon-ruta-5`, `/vic/#quan-la-vida-ruta-24`, `/el-prat/#quan-la-vida-ruta-12`
- Barcelona, per districte: `/barcelona/#ciutat-vella-ruta-1`, `/barcelona/#gracia-ruta-3` (Quan cuidar-nos)
- Barcelona, rutes des dels CAP (Quan la vida): `/barcelona/#cap-gracia-ruta-6`; el mapa i el desplegable d'un districte: `/barcelona/#cap-gracia`

Altres: `/vic/#quan-el-mon-rutes` (la llista de rutes), `/barcelona/#sants-montjuic-i-les-corts` (un grup de districtes), `/preguntes/#es-realment-gratuit` (una pregunta).

## El botó «Obre el mapa»

Cada ruta té un botó que obre, a pantalla completa, el mapa de My Maps on és (amb totes les rutes d'aquell mapa). Si un grup té un sol mapa, totes les rutes hi van. Si en té diversos, cada mapa diu quines rutes té amb `"routes": [1, 2, ...]` (com Vic «Quan el món» i el Prat «Quan la vida»); si en falta alguna, `build.py` avisa. El camp `dest` de les rutes ja no es fa servir.

## Dades

Les rutes vénen de la web de Google Sites (publicada el 3 de novembre de 2026), que es va fer amb el full «Rutes per ciutat i curs» i els GPX. No s'han d'inventar dades: si en falta alguna, es deixa marcada amb `[PENDENT]`.
