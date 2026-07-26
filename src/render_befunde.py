#!/usr/bin/env python3
"""Render the page of quantitative findings.

Everything countable about the two witnesses in one place: the tables the
commentary refers to, and those notes on the play as a whole that rest on a
count rather than on a reading. Each carries the query that produced it, so a
reader can rerun it.
"""

from __future__ import annotations

import html
import json
import sys
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lookup import plain, speeches  # noqa: E402
from page import HINWEIS_HERKUNFT, gloss_span, page  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
DOC = ROOT / "othello-bilingual.tei.xml"
OUT = ROOT / "befunde.html"

TEI = "http://www.tei-c.org/ns/1.0"
NS = {"t": TEI, "xml": "http://www.w3.org/XML/1998/namespace"}
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"

KIND_LABEL = {
    "parallel": "Sprechakt zu Sprechakt",
    "attribution": "abweichende Sprecherzuweisung",
    "en-only": "nur im englischen Zeugen",
    "de-only": "nur im deutschen Zeugen",
    "grouped": "unterschiedlich gegliedert",
}

CSS = """
section.block { margin: 2.4rem 0; padding-top: 1.1rem; border-top: 2px solid var(--rule); }
section.block h2 { font-size: 1.05rem; font-variant: small-caps; letter-spacing: .06em;
                   color: var(--accent); margin: 0 0 .5rem; }
section.block p { max-width: 46em; }
table.zahlen { border-collapse: collapse; margin: 1rem 0 .6rem; font-size: .86rem;
               min-width: min(100%, 34rem); }
table.zahlen th, table.zahlen td { padding: .28rem .9rem .28rem 0; text-align: left;
                                   border-bottom: 1px solid var(--rule); }
table.zahlen th { font-variant: small-caps; letter-spacing: .05em; color: var(--muted);
                  font-weight: 400; font-size: .76rem; }
table.zahlen td.num { text-align: right; font-variant-numeric: tabular-nums;
                      padding-right: 1.6rem; }
table.zahlen tr.sum td { font-weight: 600; border-top: 2px solid var(--rule); }
.abfrage { font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
           font-size: .76rem; color: var(--muted); background: var(--note-bg);
           padding: .35rem .6rem; border-radius: 3px; display: inline-block;
           margin-top: .3rem; }
.beleg { margin-top: .8rem; font-size: .8rem; color: var(--muted); max-width: 46em; }
.beleg .art { font-variant: small-caps; letter-spacing: .06em; color: var(--accent); }
.tabellen { display: flex; flex-wrap: wrap; gap: 1.5rem 3rem; }
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


def table(head: tuple[str, ...], rows: list[tuple], total: tuple | None = None) -> str:
    def cells(row, tag="td"):
        out = []
        for i, value in enumerate(row):
            cls = ' class="num"' if i and tag == "td" else ""
            out.append(f"<{tag}{cls}>{html.escape(str(value))}</{tag}>")
        return "".join(out)

    body = "".join(f"<tr>{cells(r)}</tr>" for r in rows)
    if total:
        body += f'<tr class="sum">{cells(total)}</tr>'
    return (f'<table class="zahlen"><tr>{cells(head, "th")}</tr>{body}</table>')


def counts() -> dict:
    """The tables, recomputed from the intermediate files."""
    en = json.loads((BUILD / "en.json").read_text(encoding="utf-8"))
    de = json.loads((BUILD / "de.json").read_text(encoding="utf-8"))
    al = json.loads((BUILD / "align.json").read_text(encoding="utf-8"))

    sp_count: Counter = Counter()
    wd_count: Counter = Counter()
    form_count: dict[str, Counter] = {}
    low = groups = 0
    for act in en["acts"]:
        for scene in act["scenes"]:
            for c in scene["content"]:
                if c["type"] != "sp":
                    continue
                sp_count[c["speaker"].rstrip(".")] += 1
                wd_count[c["speaker"].rstrip(".")] += len(plain(c).split())
                for g in c["content"]:
                    if g["type"] in ("verse", "prose"):
                        groups += 1
                        low += g.get("certainty") == "low"
                        form_count.setdefault(c["who"], Counter())[g["type"]] += 1

    kinds: Counter = Counter()
    for sc in al["scenes"]:
        for link in sc["links"]:
            kinds[link["kind"]] += 1

    scene_len = []
    for act_en, act_de in zip(en["acts"], de["acts"]):
        for s_en, s_de in zip(act_en["scenes"], act_de["scenes"]):
            e = sum(len(plain(c).split()) for c in s_en["content"] if c["type"] == "sp")
            d = sum(len(plain(c).split()) for c in s_de["content"] if c["type"] == "sp")
            scene_len.append((f"{act_en['n']},{s_en['n']}", e, d,
                              f"{d / e:.2f}" if e else "—"))

    stage_en = sum(1 for a in en["acts"] for s in a["scenes"] for c in s["content"]
                   if c["type"] == "stage") + sum(
        1 for a in en["acts"] for s in a["scenes"] for c in s["content"]
        if c["type"] == "sp" for g in c["content"] if g["type"] == "stage")
    stage_de = sum(1 for a in de["acts"] for s in a["scenes"] for c in s["content"]
                   if c["type"] == "stage") + sum(
        1 for a in de["acts"] for s in a["scenes"] for c in s["content"]
        if c["type"] == "sp" for g in c["content"] if g["type"] == "stage")

    return {
        "sp": sp_count, "wd": wd_count, "form": form_count,
        "kinds": kinds, "scene_len": scene_len,
        "low": low, "groups": groups,
        "stage_en": stage_en, "stage_de": stage_de,
        "words_en": sum(wd_count.values()),
        "words_de": sum(len(plain(c).split()) for a in de["acts"] for s in a["scenes"]
                        for c in s["content"] if c["type"] == "sp"),
    }


def main() -> None:
    root = ET.parse(DOC).getroot()
    glossary = read_glossary(root)
    c = counts()

    notes = []
    for div in root.iter(f"{{{TEI}}}div"):
        if div.get("type") != "commentary" or div.get("subtype") != "befunde":
            continue
        beleg = div.find("t:note[@type='beleg']", NS)
        beleg_html = ""
        if beleg is not None:
            art = html.escape(text_of(beleg.find("t:label", NS)))
            body = " ".join(text_of(p) for p in beleg.findall("t:p", NS))
            beleg_html = (f'<p class="beleg"><span class="art">Beleg — {art}</span><br>'
                          f"{html.escape(body)}</p>")
        notes.append((int(div.get("n") or 0),
                      f'<section class="block" id="{div.get(XML_ID)}">'
                      f'<h2>{html.escape(text_of(div.find("t:head", NS)))}</h2>'
                      + "".join(f"<p>{render_prose(p, glossary)}</p>"
                                for p in div.findall("t:p", NS))
                      + beleg_html + "</section>"))
    notes.sort()

    speakers = sorted(c["wd"].items(), key=lambda x: -x[1])[:14]
    t_speakers = table(
        ("Figur", "Reden", "Wörter", "Anteil"),
        [(name, c["sp"][name], words, f"{words / c['words_en']:.1%}")
         for name, words in speakers],
        ("alle Figuren", sum(c["sp"].values()), c["words_en"], "100 %"))

    form_rows = []
    for who, cnt in sorted(c["form"].items(), key=lambda x: -sum(x[1].values())):
        total = sum(cnt.values())
        if total < 8:
            continue
        form_rows.append((who, cnt["verse"], cnt["prose"], f"{cnt['prose'] / total:.0%}"))
    t_form = table(("Figur (ID)", "Vers", "Prosa", "Prosa-Anteil"), form_rows)

    t_links = table(("Art der Verknüpfung", "Anzahl"),
                    [(KIND_LABEL.get(k, k), v) for k, v in c["kinds"].most_common()],
                    ("alle Verknüpfungen", sum(c["kinds"].values())))

    t_scenes = table(("Szene", "Wörter englisch", "Wörter deutsch", "Verhältnis"),
                     c["scene_len"],
                     ("gesamt", c["words_en"], c["words_de"],
                      f"{c['words_de'] / c['words_en']:.2f}"))

    head = """<header class="title">
  <h1>Befunde</h1>
  <p class="sub">Was sich an den beiden Textzeugen auszählen lässt — und was die
     Zahlen nicht hergeben</p>
</header>"""

    hinweis = (
        '<div class="hinweis"><b>Wie gezählt wird.</b> Grundlage sind die beiden '
        'eingelesenen Textzeugen dieser Ausgabe. Gezählt werden Wörter als '
        'durch Leerzeichen getrennte Zeichenketten, Sprechakte als '
        '<code>sp</code>-Elemente, Wortvorkommen mit einem Wortgrenzen-Muster '
        '(<code>\\bhonest\\w*\\b</code>), das auch Ableitungen erfasst. '
        'Regieanweisungen zählen mit, wenn sie in der Quelle stehen; '
        'stillschweigend ergänzt wurde keine. Zwei Einschränkungen sind '
        'wichtig: Die Vers/Prosa-Unterscheidung des englischen Zeugen ist '
        'erschlossen, nicht überliefert, und deutsche Wörter werden in der '
        '<i>verknüpften</i> Rede gezählt — sie stehen dem englischen Wort '
        'gegenüber, ohne es zwingend zu übersetzen.</div>')

    tables = f"""
<section class="block" id="redeanteile">
  <h2>Redeanteile</h2>
  {t_speakers}
  <span class="abfrage">python3 src/observe.py share</span>
</section>
<section class="block" id="vers-prosa">
  <h2>Vers und Prosa je Figur (englischer Zeuge)</h2>
  <p>Die Zuordnung ist aus dem Zeilenmaß der Transkription erschlossen;
     {c['low']} von {c['groups']} Redegruppen ({c['low'] / c['groups']:.1%})
     beruhen auf der Kontextregel und sind in der TEI-Datei mit
     <code>cert="low"</code> markiert.</p>
  {t_form}
  <span class="abfrage">python3 src/observe.py form</span>
</section>
<section class="block" id="verknuepfungen">
  <h2>Verknüpfung der beiden Zeugen</h2>
  <p>Regieanweisungen: {c['stage_en']} englisch, {c['stage_de']} deutsch.</p>
  {t_links}
  <span class="abfrage">python3 src/align.py</span>
</section>
<section class="block" id="szenen">
  <h2>Umfang der Szenen</h2>
  <p>Verhältnis der Wortzahlen, deutsch zu englisch. Werte unter 1,00 zeigen,
     wo Baudissin verdichtet.</p>
  {t_scenes}
  <span class="abfrage">python3 src/observe.py ratio</span>
</section>"""

    body = (f'<div class="hinweis">{HINWEIS_HERKUNFT}</div>{hinweis}'
            + "".join(n for _, n in notes) + tables)

    footer = ('Alle Zahlen sind mit den Skripten dieser Ausgabe reproduzierbar. '
              'Die Wortfelder des englischen Textes stehen in der '
              '<a href="konkordanz.html">Konkordanz</a>, die Quellen unter '
              '<a href="quellen.html">Quellen</a>.')

    OUT.write_text(page("Othello — Befunde", "befunde.html", head, body,
                        CSS, "", footer), encoding="utf-8")
    print(f"{OUT.name}: {OUT.stat().st_size / 1024:.0f} kB, "
          f"{len(notes)} Texte, 4 Tabellen")


if __name__ == "__main__":
    main()
