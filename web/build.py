#!/usr/bin/env python3
"""Construit la version web (HTML) des notes à partir des sources LaTeX.

Usage :  python3 web/build.py [dossier_de_sortie]   (défaut : _site)

Étapes :
  1. copie les sources dans un dossier temporaire (tes fichiers ne sont jamais modifiés) ;
  2. contourne deux limites de plasTeX :
       - les « _ » dans les \\label/\\ref d'équations (lus comme indices en mode math),
       - les « \\\\ » à l'intérieur de \\substack{...} ;
  3. génère la bibliographie (bibtex) à partir de references.bib ;
  4. lance plasTeX sur web.tex ;
  5. remet les « \\\\ » dans le HTML et ajoute un lien vers le PDF.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / "_site").resolve()
SEP = r"\substacksep"  # marqueur temporaire, remplacé par \\ dans le HTML

REF_CMDS = r"label|ref|eqref|cref|Cref|crefrange|Crefrange|autoref|nameref|pageref"


def fix_refs(text: str) -> str:
    """eq:foo_bar -> eq:foo-bar dans les arguments des commandes de référence."""
    return re.sub(
        r"\\(" + REF_CMDS + r")\*?\{([^}]*)\}",
        lambda m: m.group(0).replace(m.group(2), m.group(2).replace("_", "-")),
        text,
    )


def fix_substack(text: str) -> str:
    """Remplace \\\\ par un marqueur dans chaque \\substack{...} (accolades équilibrées)."""
    out, i, key = [], 0, r"\substack"
    while True:
        j = text.find(key, i)
        if j < 0:
            out.append(text[i:])
            return "".join(out)
        k = j + len(key)
        while k < len(text) and text[k].isspace():
            k += 1
        if k >= len(text) or text[k] != "{":
            out.append(text[i:k])
            i = k
            continue
        depth, e = 0, k
        while e < len(text):
            if text[e] == "\\":
                e += 2
                continue
            if text[e] == "{":
                depth += 1
            elif text[e] == "}":
                depth -= 1
                if depth == 0:
                    break
            e += 1
        body = text[k + 1 : e].replace("\\\\", SEP + " ")
        out.append(text[i:k] + "{" + body + "}")
        i = e + 1


def main() -> None:
    work = Path(tempfile.mkdtemp(prefix="web-build-"))
    src = work / "src"
    shutil.copytree(ROOT, src, ignore=shutil.ignore_patterns(".git", "_site", "*.pdf"))

    for tex in src.rglob("*.tex"):
        t = tex.read_text(encoding="utf-8")
        tex.write_text(fix_substack(fix_refs(t)), encoding="utf-8")

    # Bibliographie : toutes les entrées de references.bib, style plain.
    (src / "web.aux").write_text(
        "\\citation{*}\n\\bibstyle{plain}\n\\bibdata{references}\n", encoding="utf-8"
    )
    subprocess.run(["bibtex", "web"], cwd=src, check=False)

    if OUT.exists():
        shutil.rmtree(OUT)
    subprocess.run(
        [
            "plastex",
            f"--dir={OUT}",
            "--split-level=1",
            "--packages-dirs=web",
            "--toc-depth=3",
            "--toc-non-files",
            "--localtoc-level=1",
            "web.tex",
        ],
        cwd=src,
        check=True,
    )

    pdf_link = '<a class="pdf-link" href="main.pdf">Download PDF</a>'
    head_extra = (
        '<link rel="preconnect" href="https://fonts.googleapis.com" />\n'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />\n'
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Literata:'
        'ital,opsz,wght@0,7..72,400;0,7..72,600;0,7..72,700;1,7..72,400;1,7..72,600&display=swap" />\n'
        '<link rel="stylesheet" href="styles/site.css" />\n'
    )
    shutil.copy(ROOT / "web" / "style.css", OUT / "styles" / "site.css")
    for html in OUT.glob("*.html"):
        h = html.read_text(encoding="utf-8")
        h = h.replace(SEP, r"\\")
        h = h.replace("</head>", head_extra + "</head>", 1)
        h = h.replace("</header>", pdf_link + "\n</header>", 1)
        html.write_text(h, encoding="utf-8")

    pdf = ROOT / "main.pdf"
    if pdf.exists():
        shutil.copy(pdf, OUT / "main.pdf")
    (OUT / ".nojekyll").touch()
    shutil.rmtree(work, ignore_errors=True)
    print(f"Site généré dans {OUT}")


if __name__ == "__main__":
    main()
