"""Correctifs plasTeX pour la version web (charge par usepackage{webfixes} dans web/preamble-web.tex)."""
from plasTeX import Command


class substack(Command):
    # Garde substack tel quel dans le source envoye a MathJax.
    args = 'content'


class substacksep(Command):
    # Marqueur insere par web/build.py a la place des doubles barres obliques
    # dans substack ; il est remplace dans le HTML final.
    pass


class leavevmode(Command):
    pass
