#!/usr/bin/env python3
"""Render the front page.

The entry point for the published edition: what it is, what it rests on, and
where to go. The figures are read out of the finished files, so the page cannot
promise more than the edition contains.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parent))
from page import page  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "othello-bilingual.tei.xml"
OUT = ROOT / "index.html"

TEI = "http://www.tei-c.org/ns/1.0"
NS = {"t": TEI, "xml": "http://www.w3.org/XML/1998/namespace"}

CSS = """
.karten { display: grid; grid-template-columns: repeat(auto-fit, minmax(15rem, 1fr));
          gap: 1rem; margin: 2rem 0; }
.karten a { display: block; padding: 1.1rem 1.2rem; border: 1px solid var(--rule);
            border-radius: 5px; text-decoration: none; color: inherit;
            background: var(--note-bg); }
.karten a:hover { border-color: var(--accent); }
.karten .t { font-weight: 600; color: var(--accent); display: block;
             margin-bottom: .3rem; }
.karten .d { font-size: .85rem; color: var(--muted); }
.kennzahlen { display: grid; grid-template-columns: repeat(auto-fit, minmax(9rem, 1fr));
              gap: 1rem 1.5rem; margin: 2rem 0; padding: 1.2rem 0;
              border-top: 1px solid var(--rule); border-bottom: 1px solid var(--rule); }
.kennzahlen div { text-align: left; }
.kennzahlen .z { font-size: 1.5rem; font-weight: 600; color: var(--accent);
                 font-variant-numeric: tabular-nums; }
.kennzahlen .b { font-size: .74rem; color: var(--muted);
                 font-family: system-ui, sans-serif; }
section.start { margin: 2.4rem 0; }
section.start h2 { font-size: 1rem; font-variant: small-caps; letter-spacing: .06em;
                   color: var(--accent); margin-bottom: .4rem; }
section.start p { max-width: 46em; }
"""


def main() -> None:
    root = ET.parse(DOC).getroot()
    n_sp = sum(1 for _ in root.iter(f"{{{TEI}}}sp"))
    n_link = sum(1 for _ in root.iter(f"{{{TEI}}}link"))
    n_ann = sum(1 for _ in root.iter(f"{{{TEI}}}annotation"))
    n_intro = sum(1 for d in root.iter(f"{{{TEI}}}div")
                  if d.get("type") == "commentary")
    kon = json.loads((ROOT / "build" / "konkordanz.json").read_text(encoding="utf-8"))
    n_beleg = sum(f["gesamt"] for f in kon["felder"])
    n_bez = len(json.loads((ROOT / "data" / "bezuege.json")
                           .read_text(encoding="utf-8"))["bezuege"])
    abw = sum(1 for link in root.iter(f"{{{TEI}}}link")
              if link.get("type") != "parallel")

    head = """<header class="title">
  <h1>Othello, der Mohr von Venedig</h1>
  <p class="sub">Englisch–deutsche Parallelausgabe mit Stellenkommentar ·
     Shakespeare 1604 / Baudissin 1832</p>
</header>"""

    karten = [
        ("einleitung.html", "Einleitung",
         "Neun Texte: Überlieferung des englischen Textes, Baudissins Übersetzung, "
         "Wieland, Cinthios Novelle, die Farbfrage, die doppelte Zeit, die "
         "Wirkungsgeschichte von Coleridge bis Bradley."),
        ("othello-bilingual.html", "Die Ausgabe",
         "Beide Fassungen nebeneinander, Sprechakt für Sprechakt verknüpft. "
         "Anmerkungen als Randnummern, Zeilennummern zuschaltbar, Abweichungen "
         "zwischen den Zeugen markiert."),
        ("befunde.html", "Befunde",
         "Was sich auszählen lässt: Redeanteile, Vers und Prosa je Figur, die "
         "Arten der Verknüpfung, der Umfang der Szenen — jeweils mit der Abfrage, "
         "die die Zahl erzeugt."),
        ("konkordanz.html", "Konkordanz",
         "Zwölf Wortfelder des englischen Textes. Jede Stelle in ihrer Zeile, mit "
         "Kontext und Sprung in den Paralleltext; für vier Felder ist geprüft, "
         "auf wen sich jede Nennung bezieht."),
        ("quellen.html", "Quellen",
         "Die beiden Textzeugen mit Überlieferungskette und Rechtsstand, die "
         "zitierte Literatur — und was geprüft und verworfen wurde, mit "
         "Begründung."),
    ]

    zahlen = [
        (f"{n_sp:,}".replace(",", " "), "Sprechakte, zweisprachig"),
        (f"{n_link:,}".replace(",", " "), f"Verknüpfungen, davon {abw} Abweichungen"),
        (f"{n_ann + n_intro}", "Anmerkungen, jede mit Beleg"),
        (f"{n_beleg:,}".replace(",", " "), "Konkordanzbelege"),
        (f"{n_bez}", "Stellen mit geprüftem Bezug"),
    ]

    body = f"""
<section class="start">
  <p>Shakespeares Tragödie in zwei gemeinfreien Textzeugen — dem englischen Text
  der Globe-Tradition und Wolf Heinrich Graf Baudissins Übersetzung von 1832 —,
  sprechaktweise verknüpft, deutsch kommentiert und als gültiges TEI P5
  ausgezeichnet. Die Abweichungen zwischen den Fassungen sind nicht geglättet,
  sondern verzeichnet: Baudissins ausgelassene Zoten, die Q/F-Differenzen, die
  abweichenden Sprecherzuweisungen.</p>
</section>

<div class="kennzahlen">
  {''.join(f'<div><div class="z">{z}</div><div class="b">{b}</div></div>' for z, b in zahlen)}
</div>

<div class="karten">
  {''.join(f'<a href="{href}"><span class="t">{t}</span><span class="d">{d}</span></a>'
           for href, t, d in karten)}
</div>

<section class="start">
  <h2>Woher der Kommentar stammt</h2>
  <p>Er ist kein Nachdruck einer vorhandenen Ausgabe, sondern für diese
  Zusammenstellung verfasst — maschinell, von einem Sprachmodell. Was sich
  belegen lässt, ist belegt: Zitate sind automatisch gegen beide Textzeugen
  geprüft, Zahlenangaben am Text ausgezählt, Angaben aus der Literatur im
  Volltext nachgeschlagen. Wo eine Aussage auf keinem dieser drei Wege gesichert
  ist, sagt das die Schaltfläche <i>Beleg</i> an der Anmerkung selbst. Die
  philologischen Urteile sind damit nicht abgesichert — sie gehören geprüft,
  bevor jemand sie zitiert.</p>
</section>

<section class="start">
  <h2>Daten und Nachnutzung</h2>
  <p>Die Ausgabe selbst ist eine TEI-P5-Datei
  (<code>othello-bilingual.tei.xml</code>, gültig gegen <code>tei_all</code>):
  zwei Textzeugen in einer <code>group</code>, das Alignment und der Kommentar im
  <code>standOff</code>, jeder Sprechakt und jede Zeile mit eigener
  <code>xml:id</code>. Kommentar, Bibliographie, Glossar und Bezugsschicht liegen
  daneben als JSON und werden beim Bauen eingesetzt; jedes Zitat wird dabei gegen
  beide Zeugen geprüft, ein falsches bricht den Bau.</p>
  <p>Beide Textzeugen sind gemeinfrei. Kodierung, Alignment, Kommentar und
  Skripte stehen unter
  <a href="https://creativecommons.org/publicdomain/zero/1.0/">CC0 1.0</a>.</p>
</section>"""

    footer = ('Quelltext und Daten: <a href="https://github.com/ottosmops/othello">'
              'github.com/ottosmops/othello</a> · Textzeugen gemeinfrei, '
              'Bearbeitung CC0 1.0')

    OUT.write_text(page("Othello — zweisprachige kommentierte Ausgabe",
                        "index.html", head, body, CSS, "", footer), encoding="utf-8")
    print(f"{OUT.name}: {OUT.stat().st_size / 1024:.0f} kB")


if __name__ == "__main__":
    main()
