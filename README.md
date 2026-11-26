# Notes in Number Theory

Notes de théorie des nombres (Julien Racette).

- **Site web :** https://julienracette.github.io/note_number_theory/
- **PDF :** https://julienracette.github.io/note_number_theory/main.pdf

## Comment ça marche

À chaque `git push` sur `master`, GitHub Actions (`.github/workflows/site.yml`) :

1. compile `main.tex` → `main.pdf` (préambule complet, biber, index) ;
2. convertit les mêmes fichiers `.tex` en site HTML avec [plasTeX](https://plastex.github.io/plastex/) via `web/build.py` (une page par section, MathJax, renvois cliquables) ;
3. publie le tout sur GitHub Pages.

## Ajouter des notes

- **Nouvelle section/chapitre dans une partie existante :** ajoute le `\input{...}` dans le fichier de la partie (`analytic.tex`, `analytic/.../main.tex`, etc.). Rien d'autre à faire : le PDF et le site suivent.
- **Nouvelle partie (`\part`) :** ajoute-la dans `main.tex` *et* dans `web.tex`.
- **Nouvelle macro mathématique :** ajoute-la dans `preamble/macros.tex` *et* dans `web/preamble-web.tex`.
- **Nouveau package :** seulement dans `preamble/package.tex`. Si une commande du package apparaît dans le contenu et casse le site, neutralise-la dans `web/preamble-web.tex`.

## Tester le site en local

```bash
pip install plasTeX
python3 web/build.py          # génère _site/
python3 -m http.server -d _site
```
