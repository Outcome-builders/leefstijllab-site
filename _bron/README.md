# Bronbestanden LeefstijlLab-pagina's

De pagina's in deze repo worden gegenereerd vanuit de templates in deze map.
De `@@TOKEN@@`-placeholders (fonts, logo, graphics) worden bij het bouwen
vervangen door `build.py`.

Werkwijze bij aanpassingen:

1. Pas de betreffende `template-*.html` aan (of `coaches-data.js` voor coachdata)
2. Draai `python3 build.py` (vereist: fonttools + brotli, `pip install fonttools brotli`)
3. Commit en push; GitHub Pages deployt automatisch (soms 1-15 min vertraging)

Bewerk de gegenereerde `index.html`-bestanden niet rechtstreeks: die worden
overschreven bij de volgende build.

Uitzonderingen (geen template): `boeklancering/index.html` en de root
`index.html` zijn met de hand geschreven; `landingspagina/assets/roel-cover.jpg`
is een gegenereerde compositie (portret + dominostenen-watermerk).
