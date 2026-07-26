#!/usr/bin/env python3
"""Render the parallel reading view from the TEI file.

Reads othello-bilingual.tei.xml — not the intermediate JSON — so that the
output doubles as a check that the encoding carries everything a reader needs.

The commentary stays out of the way: a note shows only as a small mark at the
edge of the line it belongs to, and opens as a card in front of the text, so
that nothing shifts while reading. Inside a note, the technical terms explain
themselves when the mouse rests on them.
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
OUT = ROOT / "othello-bilingual.html"

TEI = "http://www.tei-c.org/ns/1.0"
NS = {"t": TEI, "xml": "http://www.w3.org/XML/1998/namespace"}
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"
XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"

KIND_LABEL = {
    "attribution": "abweichende Sprecherzuweisung",
    "en-only": "nur im englischen Zeugen",
    "de-only": "nur im deutschen Zeugen",
    "grouped": "unterschiedlich gegliedert",
}

CSS = """
.bar { position: sticky; top: 0; z-index: 20; background: var(--bg);
       border-bottom: 1px solid var(--rule); padding: .5rem 0; }
.bar .row { display: flex; gap: 1.3rem; align-items: center; flex-wrap: wrap;
            font-size: .76rem; font-family: system-ui, sans-serif; color: var(--muted); }
.bar label { display: inline-flex; gap: .35rem; align-items: center; cursor: pointer; }
.bar input { accent-color: var(--accent); }
nav.scenes { overflow-x: auto; white-space: nowrap; padding-top: .3rem;
             font-size: .76rem; font-family: system-ui, sans-serif; }
nav.scenes a { color: var(--muted); text-decoration: none; margin-right: .8rem; }
nav.scenes a:hover { color: var(--accent); }

section.intro { padding: 1.8rem 0 2rem; border-bottom: 1px solid var(--rule); }
section.intro h2 { font-size: 1.05rem; font-variant: small-caps; letter-spacing: .06em;
                   color: var(--accent); margin: 1.8rem 0 .4rem; }
section.intro p { max-width: 42em; }
section.intro .foot { margin: .4rem 0 0; }

h2.scene { font-size: .95rem; font-variant: small-caps; letter-spacing: .08em;
           margin: 3rem 0 .2rem; padding-top: 1rem; border-top: 2px solid var(--rule); }
h2.scene span { color: var(--muted); font-variant: normal; letter-spacing: 0;
                font-size: .85em; }
.pair { position: relative; display: grid; grid-template-columns: 1fr 1fr;
        gap: 0 2.4rem; padding: .5rem 0;
        border-bottom: 1px solid color-mix(in srgb, var(--rule) 40%, transparent); }
.pair.divergent { background: var(--mark); }
.col { min-width: 0; }
.speaker { font-size: .7rem; font-variant: small-caps; letter-spacing: .07em;
           color: var(--accent); display: block; margin-bottom: .1rem; }
.l, .p { margin: 0; position: relative; }
.p { margin-bottom: .35rem; }
.l { text-indent: -1.2em; padding-left: 1.2em; }

/* Zeilennummern: erst auf Wunsch, dann in der Spaltenmarge */
.ln { display: none; }
body.show-ln .col { padding-left: 2.9rem; }
body.show-ln .ln { display: block; position: absolute; left: -2.9rem; top: .12rem;
                   width: 2.4rem; text-align: right; text-indent: 0;
                   font: 400 .66rem/1.6 system-ui, sans-serif; color: var(--muted);
                   opacity: .7; }
.l:target, .p:target { background: color-mix(in srgb, var(--accent) 16%, transparent);
                       border-radius: 3px; }
.stage { font-style: italic; color: var(--muted); font-size: .88em; }
.stage.scene-level { display: block; margin: .8rem 0 .2rem; }
.flag { grid-column: 1 / -1; font-size: .66rem; letter-spacing: .05em;
        color: var(--accent); margin-top: .2rem; font-family: system-ui, sans-serif; }

/* Die Marke: klein, am Rand, ohne Einfluss auf den Satzspiegel */
.mark { position: absolute; right: -2.6rem; top: .45rem; min-width: 2.2rem;
        padding: 0; border: 0; background: none; cursor: pointer; line-height: 1;
        text-align: left; color: var(--muted);
        font: 400 .72rem/1 system-ui, sans-serif; opacity: .6; }
.mark:hover, .mark:focus { color: var(--accent); opacity: 1; }
.mark + .mark { top: 1.6rem; }
body.no-notes .mark { display: none; }
@media (max-width: 900px) {
  .mark { position: static; display: inline-block; margin-right: .3rem; opacity: .8; }
  .mark + .mark { margin-left: 0; }
}

/* Die Anmerkung selbst */
.notecard .type { font-size: .66rem; font-variant: small-caps; letter-spacing: .09em;
                  color: var(--accent); }
.notecard .lemmas { font-style: italic; margin: .1rem 0 .5rem; }
.notecard p { margin: .5rem 0 0; }
.notecard .beleg { margin-top: .9rem; padding-top: .7rem;
                   border-top: 1px solid var(--rule); font-size: .8rem;
                   color: var(--muted); }
.notecard .beleg .art { font-variant: small-caps; letter-spacing: .06em;
                        color: var(--accent); }
.notecard .src { margin-top: .5rem; font-size: .78rem; }
.notecard .src b { font-weight: 600; color: var(--fg); }

/* Fließtext-Modus: dieselben Karten, in den Text gestellt */
body.notes-inline .notecard { display: block !important; position: static;
        transform: none; max-width: none; margin: .6rem 0 .4rem;
        box-shadow: none; background: var(--note-bg); border: 0;
        border-left: 3px solid var(--accent); border-radius: 0;
        grid-column: 1 / -1; }
body.notes-inline .notecard .close { display: none; }
body.notes-inline .mark { display: none; }
body.no-notes .notecard { display: none !important; }

section.biblio { margin-top: 3.5rem; padding-top: 1.2rem;
                 border-top: 2px solid var(--rule); }
section.biblio h2 { font-size: .95rem; font-variant: small-caps; letter-spacing: .07em;
                    color: var(--accent); }
@media (max-width: 760px) {
  .pair { grid-template-columns: 1fr; gap: .5rem; }
  .col + .col { padding-top: .5rem; border-top: 1px dotted var(--rule); }
}
@media print { .bar, nav.pages, .mark { display: none; } }
"""

JS = """
const body = document.body;
const swNotes = document.getElementById('sw-notes');
const swInline = document.getElementById('sw-inline');
const swLines = document.getElementById('sw-lines');

function apply() {
  body.classList.toggle('no-notes', !swNotes.checked);
  body.classList.toggle('notes-inline', swInline.checked && swNotes.checked);
  body.classList.toggle('show-ln', swLines.checked);
  swInline.disabled = !swNotes.checked;
  try {
    localStorage.setItem('othello-notes', swNotes.checked ? '1' : '0');
    localStorage.setItem('othello-inline', swInline.checked ? '1' : '0');
    localStorage.setItem('othello-lines', swLines.checked ? '1' : '0');
  } catch (e) {}
}
try {
  if (localStorage.getItem('othello-notes') === '0') swNotes.checked = false;
  if (localStorage.getItem('othello-inline') === '1') swInline.checked = true;
  if (localStorage.getItem('othello-lines') === '1') swLines.checked = true;
} catch (e) {}
swNotes.addEventListener('change', apply);
swInline.addEventListener('change', apply);
swLines.addEventListener('change', apply);
apply();

// Kommt der Aufruf aus der Konkordanz, gleich die Nummern zeigen.
if (location.hash.startsWith('#l-')) {
  swLines.checked = true;
  apply();
  const ziel = document.getElementById(location.hash.slice(1));
  if (ziel) ziel.scrollIntoView({block: 'center'});
}
"""


def text_of(el: ET.Element | None) -> str:
    return "".join(el.itertext()).strip() if el is not None else ""


def render_speech(sp: ET.Element) -> str:
    """One speech, with a numbered anchor per line so that the concordance and
    any citation can point at the line rather than the whole speech."""
    sp_id = str(sp.get(XML_ID))              # etwa en-1.3.60
    side, rest = sp_id.split("-", 1)
    act, scene = rest.split(".")[:2]
    out = [f'<span class="speaker">{html.escape(text_of(sp.find("t:speaker", NS)))}</span>']

    def zeile(el: ET.Element, cls: str) -> str:
        n = el.get("n") or ""
        anchor = f' id="l-{side}-{act}.{scene}.{n}"' if n else ""
        nummer = f'<span class="ln">{n}</span>' if n else ""
        return f'<div class="{cls}"{anchor}>{nummer}{render_line(el)}</div>'

    for child in sp:
        tag = child.tag.split("}")[1]
        if tag == "speaker":
            continue
        if tag == "stage":
            out.append(f'<span class="stage">[{html.escape(text_of(child))}]</span>')
        elif tag == "lg":
            for line in child.findall("t:l", NS):
                out.append(zeile(line, "l"))
        elif tag == "p":
            out.append(zeile(child, "p"))
    return "".join(out)


def render_line(el: ET.Element) -> str:
    parts = []
    if el.text:
        parts.append(html.escape(el.text))
    for child in el:
        tag = child.tag.split("}")[1]
        if tag == "stage":
            parts.append(f'<span class="stage">[{html.escape(text_of(child))}] </span>')
        elif tag == "hi":
            parts.append(f"<i>{html.escape(text_of(child))}</i>")
        if child.tail:
            parts.append(html.escape(child.tail))
    out = "".join(parts)
    if el.get("rend") == "italic":
        out = f"<i>{out}</i>"
    return out or "&nbsp;"


def render_prose(el: ET.Element, glossary: dict[str, dict]) -> str:
    """A commentary paragraph, with tei:term turned into a hover explanation."""
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
    """What backs a note: the kind of evidence, the wording, the sources."""
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


def render_note_card(el: ET.Element, card_id: str, types: dict[str, str],
                     biblio: dict[str, dict], glossary: dict[str, dict],
                     heading: str = "") -> str:
    body_note = beleg_note = None
    for note in el.findall("t:note", NS):
        if note.get("type") == "beleg":
            beleg_note = note
        else:
            body_note = note
    source = body_note if body_note is not None else el
    kind = ""
    if body_note is not None:
        kind = types.get(f"type-{body_note.get('type')}", body_note.get("type") or "")
    lemmas = " · ".join(
        f'<span lang="{lab.get(XML_LANG, "de")}">{html.escape(text_of(lab))}</span>'
        for lab in source.findall("t:label", NS))
    paras = "".join(f"<p>{render_prose(p, glossary)}</p>"
                    for p in source.findall("t:p", NS))
    head = f'<div class="type">{html.escape(heading or kind)}</div>'
    return (f'<div id="{card_id}" popover class="notecard">'
            f'<button class="close" aria-label="schließen">×</button>'
            f'{head}<div class="lemmas">{lemmas}</div>{paras}'
            f'{render_beleg(beleg_note, biblio)}</div>')


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


def main() -> None:
    root = ET.parse(DOC).getroot()
    biblio = read_bibliography(root)
    glossary = read_glossary(root)
    speeches = {str(sp.get(XML_ID)): sp for sp in root.iter(f"{{{TEI}}}sp")}
    types = {str(i.get(XML_ID)): text_of(i) for i in root.iter(f"{{{TEI}}}interp")}

    preceding_stage: dict[str, list[str]] = {}
    for scene in root.iter(f"{{{TEI}}}div"):
        if scene.get("type") != "scene":
            continue
        pending: list[str] = []
        for child in scene:
            tag = child.tag.split("}")[1]
            if tag == "stage":
                pending.append(text_of(child))
            elif tag == "sp":
                if pending:
                    preceding_stage[str(child.get(XML_ID))] = pending
                    pending = []

    notes_by_target: dict[str, list[ET.Element]] = {}
    for ann in root.iter(f"{{{TEI}}}annotation"):
        first = (ann.get("target") or "").split()[0].lstrip("#")
        notes_by_target.setdefault(first, []).append(ann)

    scene_heads = {str(div.get(XML_ID)): text_of(div.find("t:head", NS))
                   for div in root.iter(f"{{{TEI}}}div")
                   if div.get("type") == "scene"}

    body: list[str] = []
    nav_scenes: list[str] = []
    current_scene = None

    for link in root.iter(f"{{{TEI}}}link"):
        targets = [t.lstrip("#") for t in (link.get("target") or "").split()]
        en_ids = [t for t in targets if t.startswith("en-") and t in speeches]
        de_ids = [t for t in targets if t.startswith("de-") and t in speeches]
        anchor = (en_ids or de_ids)[0]
        act, scene = anchor.split("-")[1].split(".")[:2]
        key = f"{act}.{scene}"
        if key != current_scene:
            current_scene = key
            nav_scenes.append(f'<a href="#s{key}">{act}.{scene}</a>')
            body.append(
                f'<h2 class="scene" id="s{key}">Akt {act}, Szene {scene} '
                f'<span>· {html.escape(scene_heads.get(f"en-sc-{key}", ""))} / '
                f'{html.escape(scene_heads.get(f"de-sc-{key}", ""))}</span></h2>')

        stages_en = preceding_stage.get(en_ids[0], []) if en_ids else []
        stages_de = preceding_stage.get(de_ids[0], []) if de_ids else []
        if stages_en or stages_de:
            body.append('<div class="pair stages">' + "".join(
                '<div class="col">' + "".join(
                    f'<span class="stage scene-level">{html.escape(s)}</span>'
                    for s in side) + "</div>"
                for side in (stages_en, stages_de)) + "</div>")

        kind = link.get("type") or "parallel"
        row = [f'<div class="pair{"" if kind == "parallel" else " divergent"}" '
               f'id="p-{anchor}">']
        for ids in (en_ids, de_ids):
            row.append('<div class="col">')
            row.append("".join(render_speech(speeches[i]) for i in ids))
            if not ids:
                row.append('<span class="stage">— kein Gegenstück —</span>')
            row.append("</div>")
        if kind != "parallel":
            row.append(f'<div class="flag">◆ {KIND_LABEL.get(kind, kind)}</div>')
        for target in targets:
            for ann in notes_by_target.get(target, []):
                card_id = f"n-{ann.get(XML_ID)}"
                nummer = ann.get("n") or "•"
                row.append(f'<button class="mark" popovertarget="{card_id}" '
                           f'data-pop="{card_id}" title="Anmerkung {nummer}" '
                           f'aria-label="Anmerkung {nummer}">[{nummer}]</button>')
                row.append(render_note_card(ann, card_id, types, biblio, glossary))
        row.append("</div>")
        body.append("".join(row))

    src = root.find(".//t:sourceDesc", NS)
    assert src is not None
    sources = []
    for bibl in src.findall(".//t:bibl", NS):
        url = text_of(bibl.find("t:idno", NS))
        sources.append(
            f"<dt>{'Englisch' if bibl.get(XML_ID) == 'src-en' else 'Deutsch'}</dt>"
            f"<dd>{html.escape(text_of(bibl.find('t:title', NS)))}, "
            f"{html.escape(text_of(bibl.find('t:publisher', NS)))} "
            f"{html.escape(text_of(bibl.find('t:date', NS)))} — "
            f'<a href="{html.escape(url)}">{html.escape(url)}</a></dd>')

    n_notes = sum(1 for _ in root.iter(f"{{{TEI}}}annotation"))
    head = f"""<header class="title">
  <h1>Othello, der Mohr von Venedig</h1>
  <p class="sub">Englisch–deutsche Parallelausgabe mit Stellenkommentar ·
     Shakespeare / Baudissin 1832</p>
  <dl>{''.join(sources)}
      <dt>Kommentar</dt><dd>{n_notes} Anmerkungen, deutsch, jede mit Beleg —
      siehe <a href="quellen.html">Quellen</a></dd>
      <dt>Zahlen</dt><dd>die Auszählungen stehen auf der Seite
      <a href="befunde.html">Befunde</a></dd></dl>
</header>"""

    body_html = f"""<div class="bar">
  <div class="row">
    <label><input type="checkbox" id="sw-notes" checked> Anmerkungen</label>
    <label><input type="checkbox" id="sw-inline"> im Text statt als Marke</label>
    <label><input type="checkbox" id="sw-lines"> Zeilennummern</label>
    <span>✳ am Zeilenrand öffnet die Anmerkung · ◆ markiert eine Abweichung
      zwischen den Zeugen</span>
  </div>
  <nav class="scenes">{''.join(nav_scenes)}</nav>
</div>
<div class="hinweis kurz">Der Kommentar ist für diese Ausgabe verfasst, nicht
aus einer vorhandenen übernommen; jede Anmerkung nennt ihren Beleg. Die
Einleitung steht auf einer <a href="einleitung.html">eigenen Seite</a>.</div>
{''.join(body)}"""

    footer = ('Erzeugt aus <code>othello-bilingual.tei.xml</code> (TEI P5, gültig '
              'gegen tei_all). Die vollständigen Quellen stehen auf der Seite '
              '<a href="quellen.html">Quellen</a>, die Wortfelder des englischen '
              'Textes in der <a href="konkordanz.html">Konkordanz</a>.')

    OUT.write_text(page("Othello — zweisprachige kommentierte Ausgabe",
                        "othello-bilingual.html", head, body_html, CSS, JS, footer),
                   encoding="utf-8")
    print(f"{OUT.name}: {OUT.stat().st_size / 1024:.0f} kB, {n_notes} Anmerkungen")


if __name__ == "__main__":
    main()
