#!/usr/bin/env python3
"""Shared shell for the three HTML pages of the edition.

Reading view, source list and concordance use the same typography, the same
colours in light and dark, and the same navigation, so that they read as one
publication rather than three exports.
"""

from __future__ import annotations

import html

PAGES = [
    ("index.html", "Start"),
    ("einleitung.html", "Einleitung"),
    ("othello-bilingual.html", "Ausgabe"),
    ("befunde.html", "Befunde"),
    ("konkordanz.html", "Konkordanz"),
    ("quellen.html", "Quellen"),
]

BASE_CSS = """
:root {
  --bg: #fbfaf7; --fg: #1c1b19; --muted: #6b6659; --rule: #ddd8cc;
  --accent: #7a3b2e; --mark: #f4ede1; --note-bg: #f6f2ea; --chip: #ece5d7;
}
@media (prefers-color-scheme: dark) {
  :root { --bg: #16150f; --fg: #e8e4d9; --muted: #9c9585; --rule: #33302a;
          --accent: #d99a86; --mark: #232016; --note-bg: #1e1c15; --chip: #2b2820; }
}
:root[data-theme="dark"] {
  --bg: #16150f; --fg: #e8e4d9; --muted: #9c9585; --rule: #33302a;
  --accent: #d99a86; --mark: #232016; --note-bg: #1e1c15; --chip: #2b2820;
}
:root[data-theme="light"] {
  --bg: #fbfaf7; --fg: #1c1b19; --muted: #6b6659; --rule: #ddd8cc;
  --accent: #7a3b2e; --mark: #f4ede1; --note-bg: #f6f2ea; --chip: #ece5d7;
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--fg);
       font: 16px/1.55 "Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif; }
.wrap { max-width: 1180px; margin: 0 auto; padding: 0 1.4rem 6rem; }
a { color: var(--accent); }
h1 { font-size: 1.9rem; margin: 0 0 .3rem; font-weight: 600; }
.sub { margin: 0; color: var(--muted); font-style: italic; }
.sans { font-family: system-ui, -apple-system, sans-serif; }

header.title { padding: 3rem 0 1.6rem; }
header.title dl { display: grid; grid-template-columns: max-content 1fr;
                  gap: .3rem 1.2rem; margin: 1.5rem 0 0; font-size: .82rem;
                  color: var(--muted); }
header.title dt { font-variant: small-caps; letter-spacing: .04em; }
header.title dd { margin: 0; }

nav.pages { display: flex; gap: 1.1rem; padding: .7rem 0; font-size: .78rem;
            font-family: system-ui, sans-serif; border-bottom: 1px solid var(--rule);
            border-top: 1px solid var(--rule); }
nav.pages a { color: var(--muted); text-decoration: none; }
nav.pages a.here { color: var(--accent); font-weight: 600; }
nav.pages a:hover { color: var(--accent); }

.hinweis { background: var(--note-bg); border-left: 3px solid var(--accent);
           padding: .8rem 1rem; margin: 1.6rem 0; font-size: .85rem;
           max-width: 52em; }
.hinweis b { font-weight: 600; }

footer { margin-top: 3.5rem; padding-top: 1.2rem; border-top: 1px solid var(--rule);
         font-size: .78rem; color: var(--muted); }

/* Popups: die erste Regel versteckt auch dort, wo popover unbekannt ist. */
[popover] { display: none; border: 1px solid var(--rule); background: var(--bg);
            color: var(--fg); border-radius: 5px; padding: 1.2rem 1.4rem;
            max-width: 36rem; box-shadow: 0 20px 60px rgba(0,0,0,.3);
            font-size: .87rem; }
[popover]:popover-open { display: block; }
[popover].fallback-open { display: block !important; position: fixed; top: 50%;
                          left: 50%; transform: translate(-50%, -50%); z-index: 60; }
[popover]::backdrop { background: rgba(0,0,0,.4); }
[popover] .close { position: absolute; top: .3rem; right: .55rem; border: 0;
                   background: none; color: var(--muted); font-size: 1.2rem;
                   cursor: pointer; line-height: 1; }

/* Glossar: Erklärung beim Überfahren */
.gloss { border-bottom: 1px dotted var(--accent); cursor: help; position: relative; }
.gloss > .tip { display: none; position: absolute; left: 0; top: 1.5em; z-index: 70;
                width: max(18rem, 22vw); max-width: 90vw; background: var(--bg);
                color: var(--fg); border: 1px solid var(--accent); border-radius: 4px;
                padding: .6rem .8rem; font-size: .78rem; line-height: 1.45;
                font-style: normal; box-shadow: 0 10px 30px rgba(0,0,0,.25); }
.gloss > .tip b { display: block; font-variant: small-caps; letter-spacing: .06em;
                  color: var(--accent); margin-bottom: .2rem; }
.gloss:hover > .tip, .gloss:focus > .tip, .gloss:focus-within > .tip { display: block; }
@media (max-width: 700px) { .gloss > .tip { left: auto; right: 0; } }
"""

BASE_JS = """
// Popups: die Popover-API, wo vorhanden, sonst eine schlichte Rückfallebene.
const supportsPopover = HTMLElement.prototype.hasOwnProperty('togglePopover');
if (!supportsPopover) {
  document.querySelectorAll('[data-pop]').forEach(btn => {
    const pop = document.getElementById(btn.dataset.pop);
    if (!pop) return;
    btn.addEventListener('click', e => {
      e.preventDefault();
      document.querySelectorAll('[popover].fallback-open')
              .forEach(p => p.classList.remove('fallback-open'));
      pop.classList.add('fallback-open');
    });
  });
}
document.querySelectorAll('[popover] .close').forEach(b => {
  b.addEventListener('click', () => {
    const pop = b.closest('[popover]');
    if (supportsPopover && pop.hidePopover) { pop.hidePopover(); }
    else { pop.classList.remove('fallback-open'); }
  });
});
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') {
    document.querySelectorAll('[popover].fallback-open')
            .forEach(p => p.classList.remove('fallback-open'));
  }
});
"""

HINWEIS_HERKUNFT = (
    "<b>Woher dieser Kommentar stammt.</b> Er ist kein Nachdruck einer "
    "vorhandenen Ausgabe, sondern für diese Zusammenstellung verfasst — "
    "maschinell, von einem Sprachmodell. Was sich belegen lässt, ist belegt: "
    "Zitate sind automatisch gegen beide Textzeugen geprüft, Zahlenangaben am "
    "Text ausgezählt, Angaben aus der Literatur im Volltext nachgeschlagen. "
    "Wo eine Aussage auf keinem dieser drei Wege gesichert ist, sagt das die "
    "Schaltfläche <i>Beleg</i> an der Anmerkung selbst. Die philologischen "
    "Urteile sind damit nicht abgesichert — sie gehören geprüft, bevor jemand "
    "sie zitiert."
)


def nav(current: str) -> str:
    return '<nav class="pages">' + "".join(
        f'<a href="{href}"{" class=\"here\"" if href == current else ""}>{label}</a>'
        for href, label in PAGES) + "</nav>"


def page(title: str, current: str, head: str, body: str,
         css: str = "", js: str = "", footer: str = "") -> str:
    return f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<style>{BASE_CSS}{css}</style>
</head>
<body>
<div class="wrap">
{head}
{nav(current)}
{body}
<footer>{footer}</footer>
</div>
<script>{BASE_JS}{js}</script>
</body>
</html>"""


def gloss_span(text: str, term: str, explanation: str) -> str:
    """A term with its explanation, shown on hover and on focus."""
    return (f'<span class="gloss" tabindex="0">{text}'
            f'<span class="tip"><b>{html.escape(term)}</b>'
            f'{html.escape(explanation)}</span></span>')
