#!/usr/bin/env python3
"""Render the source list as its own page.

Three sections: the two witnesses the edition prints, the works its commentary
cites, and the sources that were examined and set aside — with the reason. The
last section is the one that keeps the edition honest: it says what was not
used, and why.
"""

from __future__ import annotations

import html
import json
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parent))
from page import page  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "othello-bilingual.tei.xml"
OUT = ROOT / "quellen.html"

TEI = "http://www.tei-c.org/ns/1.0"
NS = {"t": TEI, "xml": "http://www.w3.org/XML/1998/namespace"}
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"

# Geprüft und nicht verwendet. Ausführlich begründet in QUELLEN.md.
VERWORFEN = [
 ("Folger Shakespeare / DraCor-Korpus <code>shake</code>",
  "https://shakespeare.folger.edu",
  "Technisch die beste englische Quelle — TEI mit ausgezeichneter "
  "Vers/Prosa-Unterscheidung und Folger-Zeilenzählung. Steht unter einer "
  "CC-BY-NC-Lizenz und ist damit nicht gemeinfrei; die Anfrage verlangte "
  "ausdrücklich Public-Domain-Quellen."),
 ("Wieland, <i>Othello</i> 1766 (Wikisource)",
  "https://de.wikisource.org/wiki/Othello,_der_Mohr_von_Venedig",
  "Der erste deutsche Othello, gemeinfrei, vollständig transkribiert. Nicht "
  "als Haupttext verwendet, weil Wieland in Prosa übersetzt, kürzt und einer "
  "anderen englischen Vorlage folgt. Für eine dritte Kolumne erste Wahl."),
 ("Internet Shakespeare Editions: Q1 1622 und F1 1623",
  "https://internetshakespeare.uvic.ca/Library/Texts/Oth/",
  "Diplomatische Transkriptionen beider Frühdrucke — die einzige Möglichkeit, "
  "die Quarto/Folio-Differenzen unmittelbar am Text zu prüfen statt aus der "
  "Sekundärliteratur. Nicht eingebunden, weil die Nutzungsbedingungen zu "
  "klären wären. Der nächste Schritt für einen echten textkritischen Apparat."),
 ("Zeno.org",
  "https://www.zeno.org/Literatur/M/Shakespeare,+William",
  "Bietet denselben Baudissin-Text, war beim Aufbau dieser Ausgabe aber nicht "
  "erreichbar. TextGrid stellt dieselbe Textgrundlage besser ausgezeichnet bereit."),
 ("Digitalisate auf archive.org",
  "https://archive.org",
  "Scans der historischen Drucke, gemeinfrei, aber nur mit maschineller "
  "Texterkennung. Für zeichengenaues Arbeiten ohne Nachkorrektur unbrauchbar; "
  "als Faksimile-Beleg für Einzelstellen wertvoll."),
 ("projekt-gutenberg.org / Gutenberg-DE",
  "https://www.projekt-gutenberg.org",
  "Enthält Baudissins Übersetzung; die Nutzungsbedingungen der Website sind "
  "restriktiver als der gemeinfreie Text darunter. Mit DraCor liegt eine "
  "ausdrücklich CC0-lizenzierte Fassung vor."),
]

# Die Stoffquelle, mit Zustand der jeweiligen Digitalisierung.
CINTHIO = [
 ("De gli Hecatommithi, Erstausgabe 1565 (italienisch)",
  "https://archive.org/details/de-gli-hecatommithi-parte-prima",
  "Scan mit Volltexterkennung; die Type macht die Erkennung für Zitate unbrauchbar."),
 ("Gli Ecatommiti, Ausgaben 1833–1854 (italienisch)",
  "https://archive.org/details/bub_gb_py6CLg9ISTAC",
  "Jüngere Drucke, besser lesbar — der praktikable Weg zum Wortlaut."),
 ("Wolstenholme Parr: The Story of the Moor of Venice, London 1795",
  "https://archive.org/details/bim_eighteenth-century_the-story-of-the-moor-of_parr-wolstenholme_1795",
  "Älteste englische Übersetzung der Novelle, gemeinfrei; die Texterkennung "
  "des Scans ist für Zitate unbrauchbar."),
 ("Internet Shakespeare Editions: Cinthio's Tale",
  "https://internetshakespeare.uvic.ca/doc/Cinthio_M/index.html",
  "Moderne englische Übersetzung, gut lesbar; Lizenz gesondert zu klären."),
]

CSS = """
section.q { margin: 2.4rem 0; padding-top: 1.1rem; border-top: 2px solid var(--rule); }
section.q h2 { font-size: 1.05rem; font-variant: small-caps; letter-spacing: .06em;
               color: var(--accent); margin: 0 0 .4rem; }
section.q > p { max-width: 46em; }
.eintrag { margin: 1.3rem 0; max-width: 52em; }
.eintrag .kurz { font-weight: 600; }
.eintrag .voll { display: block; margin-top: .15rem; }
.eintrag .status { display: block; margin-top: .25rem; font-size: .8rem;
                   color: var(--muted); font-style: italic; }
.eintrag a.url { font-size: .8rem; font-family: system-ui, sans-serif;
                 word-break: break-all; }
.zeuge { background: var(--note-bg); border-left: 3px solid var(--accent);
         padding: .9rem 1.1rem; margin: 1.2rem 0; max-width: 52em; }
.zeuge h3 { margin: 0 0 .3rem; font-size: .95rem; }
.zeuge dl { display: grid; grid-template-columns: max-content 1fr; gap: .2rem 1rem;
            margin: .5rem 0 0; font-size: .84rem; }
.zeuge dt { color: var(--muted); font-variant: small-caps; letter-spacing: .04em; }
.zeuge dd { margin: 0; }
"""


def text_of(el: ET.Element | None) -> str:
    return "".join(el.itertext()).strip() if el is not None else ""


def witness_block(bibl: ET.Element, sprache: str) -> str:
    notes = {n.get("type"): n for n in bibl.findall("t:note", NS)}
    avail = bibl.find("t:availability", NS)
    idnos = [text_of(i) for i in bibl.findall("t:idno", NS)
             if (i.get("type") or "") == "URL"]
    links = " · ".join(f'<a href="{html.escape(u)}">{html.escape(u)}</a>' for u in idnos)
    return f"""<div class="zeuge">
  <h3>{sprache}: {html.escape(text_of(bibl.find('t:title', NS)))}</h3>
  <dl>
    <dt>Verfasser</dt><dd>{html.escape(text_of(bibl.find('t:author', NS)))}</dd>
    <dt>Herausgeber</dt><dd>{html.escape(text_of(bibl.find('t:publisher', NS)))},
        {html.escape(text_of(bibl.find('t:date', NS)))}</dd>
    <dt>Nachweis</dt><dd>{links}</dd>
    <dt>Herkunft</dt><dd>{html.escape(text_of(notes.get('provenance')))}</dd>
    <dt>Rechtsstand</dt><dd>{html.escape(text_of(avail))}</dd>
  </dl>
</div>"""


def main() -> None:
    root = ET.parse(DOC).getroot()
    src = root.find(".//t:sourceDesc", NS)
    assert src is not None
    witnesses = {b.get(XML_ID): b for b in src.findall(".//t:bibl", NS)}

    lit = []
    listbibl = root.find(".//t:listBibl[@xml:id='commentary-bibliography']", NS)
    assert listbibl is not None
    for bibl in listbibl.findall("t:bibl", NS):
        notes = bibl.findall("t:note", NS)
        ref = bibl.find("t:ref", NS)
        url = (ref.get("target") or "") if ref is not None else ""
        lit.append(
            f'<div class="eintrag" id="bib-{bibl.get(XML_ID)}">'
            f'<span class="kurz">[{bibl.get("n") or "?"}] '
            f'{html.escape(text_of(bibl.find("t:title", NS)))}</span>'
            f'<span class="voll">{html.escape(text_of(notes[0]) if notes else "")}</span>'
            + (f'<a class="url" href="{html.escape(url)}">{html.escape(url)}</a>'
               if url else "")
            + f'<span class="status">{html.escape(text_of(notes[1]) if len(notes) > 1 else "")}'
              f"</span></div>")

    def liste(rows):
        return "".join(
            f'<div class="eintrag"><span class="kurz">{kurz}</span>'
            f'<span class="voll">{html.escape(text)}</span>'
            f'<a class="url" href="{html.escape(url)}">{html.escape(url)}</a></div>'
            for kurz, url, text in rows)

    head = """<header class="title">
  <h1>Quellen</h1>
  <p class="sub">Was diese Ausgabe abdruckt, was ihr Kommentar zitiert, und was
     geprüft und beiseitegelegt wurde</p>
</header>"""

    glossar = root.find(".//t:list[@xml:id='glossary']", NS)
    n_gloss = len(glossar.findall("t:label", NS)) if glossar is not None else 0

    body = f"""
<div class="hinweis"><b>Alles hier Abgedruckte ist gemeinfrei.</b> Beide
Textzeugen wie auch die zitierte Sekundärliteratur stehen frei zur Verfügung;
Kodierung, Alignment und Kommentar dieser Ausgabe stehen unter
<a href="https://creativecommons.org/publicdomain/zero/1.0/">CC0 1.0</a>.
Die ausführliche Fassung dieser Liste mit allen Begründungen steht in
<code>QUELLEN.md</code>.</div>

<section class="q" id="zeugen">
  <h2>Die abgedruckten Textzeugen</h2>
  <p>Zwei unabhängig überlieferte Fassungen, unverändert wiedergegeben;
     eingegriffen wurde ausschließlich in der Auszeichnung.</p>
  {witness_block(witnesses['src-en'], 'Englisch')}
  {witness_block(witnesses['src-de'], 'Deutsch')}
</section>

<section class="q" id="literatur">
  <h2>Belegstellen des Kommentars</h2>
  <p>Worauf sich die Anmerkungen stützen. Die Nummern in eckigen Klammern
     werden in den Belegkarten der Anmerkungen zitiert; der Zusatz in Kursive
     sagt jeweils, ob und wofür die Quelle für diese Ausgabe tatsächlich
     eingesehen wurde.</p>
  {''.join(lit)}
</section>

<section class="q" id="cinthio">
  <h2>Die Stoffquelle: Cinthios Novelle</h2>
  <p>Shakespeares Vorlage — die siebte Novelle der dritten Dekade der
     <i>Hecatommithi</i>, Venedig 1565 — ist gemeinfrei und mehrfach
     digitalisiert. Für diese Ausgabe wurde sie nicht ausgewertet; die Angaben
     zum Inhalt im Kommentar sind entsprechend als ungeprüft gekennzeichnet.</p>
  {liste(CINTHIO)}
</section>

<section class="q" id="verworfen">
  <h2>Geprüft und nicht verwendet</h2>
  <p>Diese Liste gehört zur Ausgabe wie die vorige: Sie zeigt, welche
     Alternativen bestanden und woran sie scheiterten.</p>
  {liste(VERWORFEN)}
</section>

<section class="q" id="glossar">
  <h2>Glossar</h2>
  <p>{n_gloss} Fachbegriffe sind im Kommentar erklärt; sie erscheinen dort
     unterstrichen und zeigen ihre Erläuterung, sobald die Maus darauf ruht.
     Maschinenlesbar stehen sie in <code>data/glossar.json</code> und in der
     TEI-Datei als <code>list[@type="gloss"]</code>.</p>
</section>"""

    footer = ('Die vollständige, kommentierte Quellenliste steht in '
              '<code>QUELLEN.md</code>; die Zahlen dieser Ausgabe unter '
              '<a href="befunde.html">Befunde</a>.')
    OUT.write_text(page("Othello — Quellen", "quellen.html", head, body, CSS, "", footer),
                   encoding="utf-8")
    print(f"{OUT.name}: {OUT.stat().st_size / 1024:.0f} kB, "
          f"{len(lit)} Belegstellen, {len(VERWORFEN)} verworfene Quellen")


if __name__ == "__main__":
    main()
