#!/usr/bin/env python3
"""
Buildscript voor de LeefstijlLab-pagina's.

Bouwt alle pagina's vanuit de templates in deze map (_bron/) en schrijft ze
naar de juiste submappen van de repo. Fonts worden gesubset uit de zips in
"Brand Assets" en base64-embed in elke pagina.

Gebruik (vanuit een omgeving met python3, fonttools en brotli):
    python3 build.py

Verwachte mappenstructuur:
    LeefstijlLab/
      Brand Assets/            (font-zips, logo's)
      Style Guide/             (Webflow-export met logo-svg)
      Graphics/0. Fundament/svg/  (pov- en bouwstenen-graphics)
      github-pages/            (deze repo)
        _bron/                 (deze map: templates + dit script)
"""
import base64
import pathlib
import re
import shutil
import tempfile
import zipfile

BRON = pathlib.Path(__file__).resolve().parent
REPO = BRON.parent
LL = REPO.parent  # LeefstijlLab-map met Brand Assets, Style Guide, Graphics

BRAND = LL / "Brand Assets"
STYLE = LL / "Style Guide"
GFX = LL / "Graphics" / "0. Fundament" / "svg"

UNICODES = "U+0020-007E,U+00A0-00FF,U+2013,U+2014,U+2018,U+2019,U+201C,U+201D,U+2026,U+2192,U+2193,U+20AC"


def subset_fonts() -> dict:
    """Pak de font-zips uit en subset naar base64-woff2 per gewicht."""
    from fontTools.subset import main as subset

    tmp = pathlib.Path(tempfile.mkdtemp())
    for zipnaam in ["Staatliches-20250304T160044Z-001.zip", "Red_Hat_Display-20250304T160048Z-001.zip"]:
        with zipfile.ZipFile(BRAND / zipnaam) as z:
            z.extractall(tmp)

    jobs = {
        "STAAT": tmp / "Staatliches/Staatliches-Regular.ttf",
        "RHDREG": tmp / "Red_Hat_Display/static/RedHatDisplay-Regular.ttf",
        "RHDMED": tmp / "Red_Hat_Display/static/RedHatDisplay-Medium.ttf",
        "RHDSB": tmp / "Red_Hat_Display/static/RedHatDisplay-SemiBold.ttf",
        "RHDBOLD": tmp / "Red_Hat_Display/static/RedHatDisplay-Bold.ttf",
    }
    fonts = {}
    for token, ttf in jobs.items():
        out = tmp / f"{token}.woff2"
        subset([str(ttf), f"--unicodes={UNICODES}", "--flavor=woff2", f"--output-file={out}", "--layout-features=*"])
        fonts[token] = base64.b64encode(out.read_bytes()).decode()
    shutil.rmtree(tmp, ignore_errors=True)
    return fonts


def strip_xml(svg_tekst: str) -> str:
    return re.sub(r"<\?xml[^>]*\?>", "", svg_tekst).strip()


def graphic(pad: pathlib.Path) -> str:
    """Brand-graphic (1200x900) responsief maken voor inline gebruik."""
    return strip_xml(pad.read_text()).replace('width="1200" height="900"', "", 1)


def main():
    fonts = subset_fonts()
    logo = strip_xml((STYLE / "67c85e5ef1ddd11c73b6c5bc_Leefstyl Lab Logo.svg").read_text())
    logo = logo.replace("<svg ", '<svg class="logo" ', 1)

    paginas = [
        ("template-landing.html", "landingspagina/index.html", {"@@IJSBERG@@": graphic(GFX / "ijsberg.svg")}),
        ("template-opleiding.html", "opleiding/index.html", {
            "@@POV@@": graphic(GFX / "leefstijllab-pov.svg"),
            "@@BOUW@@": graphic(GFX / "bouwstenen.svg"),
        }),
        ("template-modules.html", "modules/index.html", {"@@BOUW@@": graphic(GFX / "bouwstenen.svg")}),
        ("template-coaches.html", "coaches/index.html", {}),
        ("template-coach-profiel.html", "coaches/profiel.html", {}),
        ("template-connect.html", "connect/index.html", {}),
    ]

    for tpl, doel, extra in paginas:
        html = (BRON / tpl).read_text()
        for token, waarde in fonts.items():
            html = html.replace(f"@@{token}@@", waarde)
        html = html.replace("@@LOGO@@", logo)
        for token, waarde in extra.items():
            html = html.replace(token, waarde)
        (REPO / doel).parent.mkdir(parents=True, exist_ok=True)
        (REPO / doel).write_text(html)
        print(f"  {doel} ({len(html):,} bytes)")

    # coachdata is een gedeeld runtime-bestand, geen template
    shutil.copy(BRON / "coaches-data.js", REPO / "coaches" / "data.js")
    print("  coaches/data.js")
    print("Klaar. Commit en push de repo om te publiceren.")


if __name__ == "__main__":
    main()
