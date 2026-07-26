#!/usr/bin/env python3
"""Render the introduction as its own page.

The nine essays on the play as a whole — transmission, translation, source,
reception — read as continuous prose and have no business interrupting the
text. Each keeps its evidence, which opens as a card.
"""

from __future__ import annotations

import html
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parent))
from page import HINWEIS_HERKUNFT, gloss_span, page  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "othello-bilingual.tei.xml"
OUT = ROOT / "einleitung.html"

TEI = "http://www.tei-c.org/ns/1.0"
NS = {"t": TEI, "xml": "http://www.w3.org/XML/1998/namespace"}
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"

CSS = """
article { max-width: 44em; }
article section { margin: 2.4rem 0; }
article h2 { font-size: 1.15rem; font-variant: small-caps; letter-spacing: .05em;
             color: var(--accent); margin: 0 0 .5rem; }
article p { margin: .7rem 0; }
article p:first-of-type::first-line { font-variant: small-caps; }
.beleg-knopf { font: 400 .72rem/1.4 system-ui, sans-serif; color: var(--muted);
               background: var(--chip); border: 1px solid var(--rule);
               border-radius: 999px; padding: .12rem .7rem; cursor: pointer;
               margin-top: .4rem; }
.beleg-knopf:hover { color: var(--accent); border-color: var(--accent); }
.notecard .beleg .art { font-variant: small-caps; letter-spacing: .06em;
                        color: var(--accent); }
.notecard .beleg p { margin: .4rem 0 0; font-size: .84rem; }
.notecard .src { margin-top: .6rem; font-size: .8rem; }
.notecard .src b { font-weight: 600; }
.inhalt { font-size: .82rem; font-family: system-ui, sans-serif; margin: 1.4rem 0;
          columns: 2; column-gap: 2rem; }
.inhalt a { display: block; color: var(--muted); text-decoration: none;
            margin-bottom: .3rem; }
.inhalt a:hover { color: var(--accent); }
@media (max-width: 700px) { .inhalt { columns: 1; } }
"""


def text_of(el: ET.Element | None) -> str:
    return "".join(el.itertext()).strip() if el is not None else ""


def read_glossary(root: ET.Element) -> dict[str, dict]:
    out: dict[str, dict] = {}
    lst = root.find(".//t:list[@xml:id='glossary']", NS)
    if lst is None:
        return out
    label = None
    for child in lst:
        tag = child.tag.split("}")[1]
        if tag == "label":
            label = child
        elif tag == "item" and label is not None:
            out[str(label.get(XML_ID))] = {"begriff": text_of(label),
                                           "erklaerung": text_of(child)}
            label = None
    return out


def read_bibliography(root: ET.Element) -> dict[str, dict]:
    out: dict[str, dict] = {}
    listbibl = root.find(".//t:listBibl[@xml:id='commentary-bibliography']", NS)
    if listbibl is None:
        return out
    for bibl in listbibl.findall("t:bibl", NS):
        notes = bibl.findall("t:note", NS)
        ref = bibl.find("t:ref", NS)
        out[str(bibl.get(XML_ID))] = {
            "nummer": bibl.get("n") or "",
            "kurz": text_of(bibl.find("t:title", NS)),
            "voll": text_of(notes[0]) if notes else "",
            "status": text_of(notes[1]) if len(notes) > 1 else "",
            "url": (ref.get("target") or "") if ref is not None else "",
        }
    return out


def render_prose(el: ET.Element, glossary: dict[str, dict]) -> str:
    parts = []
    if el.text:
        parts.append(html.escape(el.text))
    for child in el:
        if child.tag.split("}")[1] == "term":
            entry = glossary.get((child.get("ref") or "").lstrip("#"))
            label = html.escape(text_of(child))
            parts.append(gloss_span(label, entry["begriff"], entry["erklaerung"])
                         if entry else label)
        if child.tail:
            parts.append(html.escape(child.tail))
    return "".join(parts)


def render_beleg(note: ET.Element | None, biblio: dict[str, dict]) -> str:
    if note is None:
        return ""
    art = html.escape(text_of(note.find("t:label", NS)))
    body = "".join(f"<p>{html.escape(text_of(p))}</p>" for p in note.findall("t:p", NS))
    sources = []
    for ptr in note.findall("t:ptr", NS):
        entry = biblio.get((ptr.get("target") or "").lstrip("#"))
        if not entry:
            continue
        link = (f' <a href="{html.escape(entry["url"])}">Volltext</a>'
                if entry["url"] else "")
        sources.append(f'<div class="src">[{entry["nummer"]}] '
                       f'<b>{html.escape(entry["kurz"])}</b>{link}<br>'
                       f'{html.escape(entry["status"])}</div>')
    return (f'<div class="beleg"><span class="art">Beleg — {art}</span>'
            f'{body}{"".join(sources)}</div>')


def main() -> None:
    root = ET.parse(DOC).getroot()
    glossary = read_glossary(root)
    biblio = read_bibliography(root)

    divs = sorted((d for d in root.iter(f"{{{TEI}}}div")
                   if d.get("type") == "commentary" and d.get("subtype") != "befunde"),
                  key=lambda d: int(d.get("n") or 0))

    sections, cards, toc = [], [], []
    for div in divs:
        head = text_of(div.find("t:head", NS))
        anchor = str(div.get(XML_ID))
        toc.append(f'<a href="#{anchor}">{html.escape(head)}</a>')
        paras = "".join(f"<p>{render_prose(p, glossary)}</p>"
                        for p in div.findall("t:p", NS))
        beleg = div.find("t:note[@type='beleg']", NS)
        knopf = ""
        if beleg is not None:
            card_id = f"n-{anchor}"
            knopf = (f'<button class="beleg-knopf" popovertarget="{card_id}" '
                     f'data-pop="{card_id}">Beleg</button>')
            cards.append(f'<div id="{card_id}" popover class="notecard">'
                         f'<button class="close" aria-label="schließen">×</button>'
                         f'<div class="type">{html.escape(head)}</div>'
                         f'{render_beleg(beleg, biblio)}</div>')
        sections.append(f'<section id="{anchor}"><h2>{html.escape(head)}</h2>'
                        f"{paras}{knopf}</section>")

    head = """<header class="title">
  <h1>Einleitung</h1>
  <p class="sub">Überlieferung, Übersetzung, Stoff und Nachleben — was vor der
     Lektüre zu wissen nützlich ist</p>
</header>"""

    body = (f'<div class="hinweis">{HINWEIS_HERKUNFT}</div>'
            f'<div class="inhalt">{"".join(toc)}</div>'
            f'<article>{"".join(sections)}</article>{"".join(cards)}')

    footer = ('Die Zahlenbefunde stehen unter <a href="befunde.html">Befunde</a>, '
              'die Textseite unter <a href="othello-bilingual.html">Ausgabe</a>. '
              'Unterstrichene Begriffe erklären sich, sobald die Maus darauf ruht.')

    OUT.write_text(page("Othello — Einleitung", "einleitung.html", head, body,
                        CSS, "", footer), encoding="utf-8")
    print(f"{OUT.name}: {OUT.stat().st_size / 1024:.0f} kB, {len(sections)} Texte")


if __name__ == "__main__":
    main()
