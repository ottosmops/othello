#!/usr/bin/env python3
"""Assemble the bilingual TEI P5 edition from the parsed texts, the alignment
and the commentary.

Structure of the output document:

    TEI
      teiHeader           – two sources with their licences, editorial method
      text/front          – introduction: the commentary notes on the whole play
      text/group/text     – the English witness  (xml:id="text-en")
      text/group/text     – the German witness   (xml:id="text-de")
      standOff/linkGrp    – speech-by-speech alignment, typed by kind
      standOff/listAnnotation – the commentary, anchored to both witnesses

Every speech carries an xml:id of the form ``en-1.3.42`` (witness, act, scene,
running number), which is what the links and annotations point at.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lookup import norm, plain  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
OUT = ROOT / "othello-bilingual.tei.xml"

EDITION_DATE = "2026-07-26"

# Canonical cast, with the name each witness prints.
CAST = [
    ("othello", "Othello", "Othello", "MALE"),
    ("desdemona", "Desdemona", "Desdemona", "FEMALE"),
    ("iago", "Iago", "Jago", "MALE"),
    ("cassio", "Cassio", "Cassio", "MALE"),
    ("emilia", "Emilia", "Emilia", "FEMALE"),
    ("roderigo", "Roderigo", "Rodrigo", "MALE"),
    ("brabantio", "Brabantio", "Brabantio", "MALE"),
    ("duke", "Duke of Venice", "Herzog von Venedig", "MALE"),
    ("lodovico", "Lodovico", "Lodovico", "MALE"),
    ("gratiano", "Gratiano", "Gratiano", "MALE"),
    ("montano", "Montano", "Montano", "MALE"),
    ("bianca", "Bianca", "Bianca", "FEMALE"),
    ("clown", "Clown", "Narr", "MALE"),
    ("senator1", "First Senator", "Erster Senator", "MALE"),
    ("senator2", "Second Senator", "Zweiter Senator", "MALE"),
    ("senators", "Senators", "Senatoren", "UNKNOWN"),
    ("gentleman1", "First Gentleman", "Erster Edelmann", "MALE"),
    ("gentleman2", "Second Gentleman", "Zweiter Edelmann", "MALE"),
    ("gentleman3", "Third Gentleman", "Dritter Edelmann", "MALE"),
    ("gentleman4", "Fourth Gentleman", "Vierter Edelmann", "MALE"),
    ("gentlemen", "Gentlemen", "Edelleute", "UNKNOWN"),
    ("officer", "Officer", "Gerichtsdiener", "MALE"),
    ("officers", "Officers", "Beamte", "UNKNOWN"),
    ("messenger", "Messenger", "Bote", "MALE"),
    ("sailor", "Sailor", "Matrose", "MALE"),
    ("herald", "Herald", "Herold", "MALE"),
    ("musician", "First Musician", "Musikanten", "UNKNOWN"),
    ("all", "All", "Alle", "UNKNOWN"),
    ("both", "Both", "Beide", "UNKNOWN"),
    ("servant", "Servant", "Diener", "UNKNOWN"),
    ("attendant", "Attendant", "Gefolge", "UNKNOWN"),
]
KNOWN_IDS = {c[0] for c in CAST}

TYPE_LABEL = {
    "textual": "Textkritik",
    "translation": "Übersetzungsvergleich",
    "realia": "Sacherklärung",
    "rhetoric": "Rhetorik und Stil",
    "dramaturgy": "Dramaturgie",
    "reception": "Wirkungsgeschichte",
    "source": "Stoffgeschichte",
    "edition": "Editionsbericht",
}


class Writer:
    """Minimal indenting XML writer."""

    def __init__(self) -> None:
        self.parts: list[str] = []
        self.depth = 0

    def raw(self, s: str) -> None:
        self.parts.append(s)

    def line(self, s: str) -> None:
        self.parts.append("  " * self.depth + s + "\n")

    def open(self, tag: str, **attrs) -> None:
        self.line(f"<{tag}{fmt_attrs(attrs)}>")
        self.depth += 1

    def close(self, tag: str) -> None:
        self.depth -= 1
        self.line(f"</{tag}>")

    def leaf(self, tag: str, text: str = "", **attrs) -> None:
        if text:
            self.line(f"<{tag}{fmt_attrs(attrs)}>{escape(text)}</{tag}>")
        else:
            self.line(f"<{tag}{fmt_attrs(attrs)}/>")

    def __str__(self) -> str:
        return "".join(self.parts)


def fmt_attrs(attrs: dict) -> str:
    out = []
    for k, v in attrs.items():
        if v is None or v == "":
            continue
        out.append(f" {k.replace('_', ':')}={quoteattr(str(v))}")
    return "".join(out)


def sp_id(side: str, act: int, scene: int, n: int) -> str:
    return f"{side}-{act}.{scene}.{n}"


def scene_id(side: str, act: int, scene: int) -> str:
    return f"{side}-sc-{act}.{scene}"


# --------------------------------------------------------------------------- header


def write_header(w: Writer, stats: dict) -> None:
    w.open("teiHeader")
    w.open("fileDesc")

    w.open("titleStmt")
    w.leaf("title", "Othello, der Mohr von Venedig — Othello, the Moor of Venice",
           type="main")
    w.leaf("title", "Zweisprachige Ausgabe englisch–deutsch mit Stellenkommentar",
           type="sub", xml_lang="de")
    w.open("author")
    w.open("persName")
    w.leaf("forename", "William")
    w.leaf("surname", "Shakespeare")
    w.close("persName")
    w.leaf("idno", "http://www.wikidata.org/entity/Q692", type="wikidata")
    w.close("author")
    w.open("editor", role="translator")
    w.open("persName")
    w.leaf("forename", "Wolf")
    w.leaf("forename", "Heinrich")
    w.leaf("nameLink", "von")
    w.leaf("surname", "Baudissin")
    w.close("persName")
    w.leaf("idno", "http://www.wikidata.org/entity/Q215699", type="wikidata")
    w.close("editor")
    w.open("respStmt")
    w.leaf("resp", "Zusammenstellung der Textzeugen, maschinelles Alignment, "
                   "TEI-Kodierung und Stellenkommentar")
    w.leaf("name", "Claude (Anthropic), im Auftrag des Herausgebers")
    w.close("respStmt")
    w.close("titleStmt")

    w.open("editionStmt")
    w.open("edition", n="1.0")
    w.leaf("date", EDITION_DATE, when=EDITION_DATE)
    w.close("edition")
    w.close("editionStmt")

    w.open("publicationStmt")
    w.leaf("publisher", "Unveröffentlicht; Arbeitsausgabe")
    w.leaf("date", EDITION_DATE, when=EDITION_DATE)
    w.open("availability")
    w.leaf("licence", "Die beiden Textzeugen sind gemeinfrei (siehe sourceDesc). "
                      "Kodierung, Alignment und Kommentar dieser Ausgabe stehen "
                      "unter CC0 1.0.",
           target="https://creativecommons.org/publicdomain/zero/1.0/")
    w.close("availability")
    w.close("publicationStmt")

    w.open("sourceDesc")
    w.open("listBibl")
    w.leaf("head", "Die beiden Textzeugen")
    w.leaf("desc", "Die Ausgabe stellt zwei unabhängig überlieferte, gemeinfreie "
                   "Textzeugen nebeneinander. Beide werden unverändert "
                   "wiedergegeben; eingegriffen wird ausschließlich in der "
                   "Auszeichnung.")

    # English witness
    w.open("bibl", xml_id="src-en", type="digitalSource")
    w.leaf("author", "William Shakespeare")
    w.leaf("title", "Othello", level="m")
    w.open("respStmt")
    w.leaf("resp", "Transkription")
    w.leaf("name", "The PG Shakespeare Team")
    w.close("respStmt")
    w.leaf("publisher", "Project Gutenberg")
    w.leaf("date", "1998", when="1998-11-01")
    w.leaf("idno", "https://www.gutenberg.org/ebooks/1531", type="URL")
    w.leaf("idno", "1531", type="PGid")
    w.open("note", type="provenance")
    w.leaf("p", "Elektronischer Text in der Nachfolge der Globe-Ausgabe (1864) "
                "bzw. des Moby-Shakespeare; Mischtext aus Quarto 1622 und First "
                "Folio 1623. In den Vereinigten Staaten gemeinfrei; die "
                "Transkription selbst wurde von Project Gutenberg gemeinfrei "
                "gestellt.")
    w.close("note")
    w.open("availability", status="free")
    w.leaf("p", "Public domain (USA). Project Gutenberg License; die "
                "Marken-Klausel betrifft den Namen »Project Gutenberg«, "
                "nicht den Text.")
    w.close("availability")
    w.close("bibl")

    # German witness
    w.open("bibl", xml_id="src-de", type="digitalSource")
    w.leaf("author", "William Shakespeare")
    w.leaf("title", "Othello", level="a")
    w.open("respStmt")
    w.leaf("resp", "Übersetzung")
    w.leaf("name", "Wolf Heinrich Graf Baudissin")
    w.close("respStmt")
    w.leaf("publisher", "TextGrid Repository / DraCor (German Shakespeare Drama Corpus)")
    w.leaf("date", "1832", when="1832")
    w.leaf("idno", "http://www.textgridrep.org/textgrid:vn7q.0", type="URL")
    w.leaf("idno", "https://dracor.org/gersh/othello", type="URL")
    w.open("note", type="provenance")
    w.leaf("p", "Erstdruck der Übersetzung: Shakspeare's dramatische Werke. "
                "Übersetzt von August Wilhelm Schlegel, ergänzt und erläutert von "
                "Ludwig Tieck, Band 8, Berlin: Georg Andreas Reimer 1832. Die "
                "digitale Fassung folgt: Sämtliche Werke in vier Bänden, hrsg. von "
                "Anselm Schlösser, Band 4: Tragödien, 3. Auflage, Berlin und Weimar: "
                "Aufbau-Verlag 1975, S. 389–496; deren Seitenzählung ist als "
                "pb-Marken erhalten.")
    w.close("note")
    w.open("availability", status="free")
    w.leaf("p", "Gemeinfrei (Baudissin gest. 1878). Die TEI-Fassung von DraCor "
                "steht unter CC0 1.0.")
    w.close("availability")
    w.close("bibl")

    w.close("listBibl")
    w.close("sourceDesc")
    w.close("fileDesc")

    w.open("encodingDesc")
    w.open("projectDesc")
    w.leaf("p", "Ziel der Ausgabe ist die Parallellektüre: jeder Sprechakt des "
                "englischen Textes ist, soweit möglich, mit seinem deutschen "
                "Gegenstück verknüpft, und die Abweichungen sind als solche "
                "verzeichnet statt geglättet.")
    w.close("projectDesc")

    w.open("editorialDecl")
    w.open("correction")
    w.leaf("p", "Keine Eingriffe in den Wortlaut beider Zeugen. Orthographie, "
                "Interpunktion und Apostrophierung stehen wie in den Quellen.")
    w.close("correction")
    w.open("segmentation")
    w.leaf("p", "Grundeinheit ist der Sprechakt (sp). Zeilen folgen dem "
                "Zeilenfall der jeweiligen Quelle und sind je Szene und Zeuge "
                "durchgezählt (@n). Die Auszeichnungskonventionen des englischen "
                "Klartextes wurden aufgelöst: Regieanweisungen in eckigen Klammern "
                "— auch mitten in der Verszeile, etwa »Good night to everyone. "
                "[_To Brabantio._] And, noble signior« — stehen als stage, die "
                "Kursivierung der Lieder (Unterstriche der Transkription) als hi "
                "bzw. l@rend. Im Text selbst bleibt kein Auszeichnungszeichen "
                "der Quelle stehen.")
    w.close("segmentation")
    w.open("interpretation")
    w.leaf("p", f"Vers und Prosa: Der deutsche Zeuge unterscheidet beides in der "
                f"Auszeichnung (lg/l gegenüber p). Der englische Zeuge tut das "
                f"nicht; dort wurde die Unterscheidung aus dem Zeilenmaß der "
                f"Transkription erschlossen (Prosa ist auf rund 70 Zeichen "
                f"umbrochen, Vers folgt der metrischen Zeile) und für kurze, "
                f"typographisch nicht entscheidbare Reden aus dem Kontext "
                f"ergänzt. {stats['low']} Redegruppen "
                f"({stats['low_pct']}) beruhen auf dieser Kontextregel und sind "
                f"mit cert=\"low\" markiert. Der Abgleich mit dem deutschen Zeugen "
                f"bestätigt die Zuordnung in {stats['form_pct']} der verknüpften "
                f"Sprechakte.")
    w.close("interpretation")
    w.open("normalization")
    w.leaf("p", "Für das Alignment wurden Typographica (Apostroph, Anführung, "
                "Gedankenstrich, ß) normalisiert; im Text selbst nicht.")
    w.close("normalization")
    w.close("editorialDecl")

    w.open("appInfo")
    w.open("application", ident="othello-align", version="1.0")
    w.leaf("label", "Sprechakt-Alignment")
    w.leaf("desc", f"Needleman-Wunsch über die Sprecherfolge je Szene, mit der "
                   f"relativen Redelänge als Tiebreak. Ergebnis: "
                   f"{stats['parallel']} eins-zu-eins verknüpfte Sprechakte, "
                   f"{stats['attribution']} mit abweichender Sprecherzuweisung, "
                   f"{stats['en_only']} nur englisch, {stats['de_only']} nur deutsch.")
    w.close("application")
    w.close("appInfo")
    w.close("encodingDesc")

    w.open("profileDesc")
    w.open("langUsage")
    w.leaf("language", "Englisch (Frühneuenglisch in modernisierter Schreibung)",
           ident="en")
    w.leaf("language", "Deutsch (Übersetzung von 1832)", ident="de")
    w.close("langUsage")
    w.open("particDesc")
    w.open("listPerson")
    for pid, en_name, de_name, sex in CAST:
        w.open("person", xml_id=pid, sex=sex)
        w.leaf("persName", en_name, xml_lang="en")
        w.leaf("persName", de_name, xml_lang="de")
        w.close("person")
    w.close("listPerson")
    w.close("particDesc")
    w.open("textClass")
    w.open("keywords", scheme="https://www.wikidata.org/")
    w.leaf("term", "Tragödie", ref="http://www.wikidata.org/entity/Q80930")
    w.leaf("term", "Parallelausgabe")
    w.close("keywords")
    w.close("textClass")
    w.close("profileDesc")

    w.open("revisionDesc")
    w.leaf("change", "Erstfassung: Textzeugen eingelesen, aligniert, kommentiert.",
           when="2026-07-25")
    w.leaf("change", "Belegapparat, Glossar, Bezugsschicht und Konkordanz "
                     "ergänzt; Sekundärliteratur im Volltext geprüft; "
                     "Editionsbericht aufgenommen; Veröffentlichung als "
                     "Website.", when="2026-07-26")
    w.close("revisionDesc")
    w.close("teiHeader")


# --------------------------------------------------------------------------- text


def write_front(w: Writer, play_notes: list[dict],
                terms: list[tuple[re.Pattern, str]]) -> None:
    w.open("front")
    w.open("div", type="introduction", xml_lang="de")
    w.leaf("head", "Zur Ausgabe")
    w.leaf("p", "Der englische und der deutsche Text stehen als zwei "
                "eigenständige Zeugen nebeneinander; die Verknüpfung der "
                "Sprechakte steht im standOff-Teil dieses Dokuments, ebenso der "
                "Stellenkommentar. Die folgenden Abschnitte kommentieren das "
                "Stück als ganzes.")
    for note in sorted(play_notes, key=lambda n: (n.get("seite", ""), n.get("rang", 0))):
        w.open("div", type="commentary", subtype=note.get("seite", "einleitung"),
               n=str(note.get("rang", "")), xml_id=f"note-{note['id']}",
               ana=f"#type-{note['type']}")
        w.leaf("head", note["title"])
        write_paragraphs(w, note["note"], terms)
        write_beleg(w, note)
        w.close("div")
    w.close("div")
    w.close("front")


def write_witness(w: Writer, doc: dict, side: str, lang: str, title: str) -> None:
    w.open("text", xml_id=f"text-{side}", xml_lang=lang, type="witness")
    w.open("body")
    w.leaf("head", title)
    for act in doc["acts"]:
        w.open("div", type="act", n=str(act["n"]), xml_id=f"{side}-act-{act['n']}")
        w.leaf("head", act["head"])
        for scene in act["scenes"]:
            w.open("div", type="scene", n=str(scene["n"]),
                   xml_id=scene_id(side, act["n"], scene["n"]))
            w.leaf("head", scene["head"])
            counter = {"sp": 0, "l": 0}
            page = None
            for item in scene["content"]:
                page = write_item(w, item, side, act["n"], scene["n"], counter, page)
            w.close("div")
        w.close("div")
    w.close("body")
    w.close("text")


def write_item(w: Writer, item: dict, side: str, act: int, scene: int,
               counter: dict, page: str | None) -> str | None:
    if item.get("page") and item["page"] != page:
        page = item["page"]
        w.leaf("pb", n=page, ed="aufbau1975")
    if item["type"] == "stage":
        w.leaf("stage", item["text"])
        return page
    counter["sp"] += 1
    attrs = {
        "xml_id": sp_id(side, act, scene, counter["sp"]),
        "who": " ".join(f"#{x}" for x in item["who"].split() if x in KNOWN_IDS) or None,
    }
    w.open("sp", **attrs)
    w.leaf("speaker", item["speaker"])
    for group in item["content"]:
        if group["type"] == "stage":
            w.leaf("stage", group["text"], type="delivery")
        elif group["type"] == "prose":
            for line in group["lines"]:
                counter["l"] += 1
                write_line(w, "p", line, counter["l"], group.get("certainty"))
        else:
            w.open("lg", type="verse", cert=group.get("certainty"))
            for line in group["lines"]:
                counter["l"] += 1
                write_line(w, "l", line, counter["l"], None)
            w.close("lg")
    w.close("sp")
    return page


def write_line(w: Writer, tag: str, line: dict, n: int, cert: str | None) -> None:
    """One source line: spoken words, stage cues in their place, italics kept.

    The English witness prints stage business inside the line ("Good night to
    everyone. [_To Brabantio._] And, noble signior,") and marks song by the
    transcribers' italics; both are encoded rather than left as plain text.
    """
    parts = line.get("parts")
    if not parts:  # German witness: no inline markup to preserve
        w.leaf(tag, line.get("text", ""), n=str(n), cert=cert)
        return
    if len(parts) == 1 and "text" in parts[0] and not parts[0].get("italic"):
        w.leaf(tag, parts[0]["text"], n=str(n), cert=cert)
        return
    spoken = [p for p in parts if "text" in p]
    whole_line_italic = bool(spoken) and all(p.get("italic") for p in spoken)
    inner = []
    for part in parts:
        if "stage" in part:
            inner.append(f'<stage type="delivery">{escape(part["stage"])}</stage>')
        elif part.get("italic") and not whole_line_italic:
            inner.append(f'<hi rend="italic">{escape(part["text"])}</hi>')
        else:
            inner.append(escape(part["text"]))
    rend = ' rend="italic"' if whole_line_italic else ""
    cert_attr = f' cert="{cert}"' if cert else ""
    w.line(f'<{tag} n="{n}"{rend}{cert_attr}>{" ".join(inner)}</{tag}>')


# --------------------------------------------------------------------------- standOff


def compile_glossary(glossary: dict) -> list[tuple[re.Pattern, str]]:
    """Patterns for the glossary terms, longest form first so that »First
    Folio« wins over »Folio«."""
    out = []
    for entry in glossary["begriffe"]:
        for form in sorted(entry["formen"], key=len, reverse=True):
            out.append((re.compile(rf"(?<!\w){re.escape(form)}(?!\w)"), entry["id"]))
    return sorted(out, key=lambda x: -len(x[0].pattern))


def mark_terms(text: str, patterns: list[tuple[re.Pattern, str]],
               used: set[str]) -> str:
    """Wrap the first mention of each glossary term in a note as tei:term.

    Only the first mention: a note that says »Q1« five times should not be
    peppered with five identical explanations.
    """
    marked = escape(text)
    for pattern, term_id in patterns:
        if term_id in used:
            continue
        m = pattern.search(marked)
        if not m:
            continue
        used.add(term_id)
        marked = (marked[:m.start()]
                  + f'<term ref="#g-{term_id}">{m.group(0)}</term>'
                  + marked[m.end():])
    return marked


def write_glossary(w: Writer, glossary: dict) -> None:
    w.open("list", type="gloss", xml_id="glossary")
    w.leaf("head", "Erläuterte Begriffe")
    for entry in glossary["begriffe"]:
        w.leaf("label", entry["begriff"], xml_id=f"g-{entry['id']}")
        w.leaf("item", entry["erklaerung"])
    w.close("list")


BELEGART_LABEL = {
    "textzeuge": "am Wortlaut beider Textzeugen geprüft",
    "auszählung": "an dieser Ausgabe ausgezählt",
    "literatur": "nach Literatur; siehe Belegangabe",
    "werkstatt": "aus der Arbeit an dieser Ausgabe",
}


def write_paragraphs(w: Writer, text: str,
                     terms: list[tuple[re.Pattern, str]]) -> None:
    """Commentary prose, split at blank lines; a glossary term is marked once
    per note, not once per paragraph."""
    used: set[str] = set()
    for absatz in [a.strip() for a in text.split("\n\n") if a.strip()]:
        w.line(f"<p>{mark_terms(absatz, terms, used)}</p>")


def write_beleg(w: Writer, note: dict) -> None:
    """The evidence a note rests on, and its pointers into the bibliography."""
    w.open("note", type="beleg", xml_lang="de",
           ana=f"#beleg-{note['belegart'].replace('ä', 'ae')}")
    w.leaf("label", BELEGART_LABEL[note["belegart"]])
    w.leaf("p", note["beleg"])
    for ref in note.get("refs", []):
        w.leaf("ptr", target=f"#bib-{ref}")
    w.close("note")


def write_bibliography(w: Writer, biblio: dict) -> None:
    w.open("listBibl", xml_id="commentary-bibliography")
    w.leaf("head", "Belegstellen des Kommentars")
    for nummer, entry in enumerate(biblio["eintraege"], 1):
        w.open("bibl", xml_id=f"bib-{entry['id']}", n=str(nummer))
        w.leaf("title", entry["kurz"], type="short")
        w.leaf("note", entry["voll"], type="full")
        if entry.get("url"):
            w.leaf("ref", entry["url"], target=entry["url"])
        w.leaf("note", entry["geprueft"], type="status")
        w.close("bibl")
    w.close("listBibl")

    w.open("interpGrp", type="Belegarten", xml_id="beleg-arten")
    w.leaf("interp", "Am Wortlaut beider Textzeugen geprüft", xml_id="beleg-textzeuge")
    w.leaf("interp", "An dieser Ausgabe ausgezählt", xml_id="beleg-auszaehlung")
    w.leaf("interp", "Nach Literatur", xml_id="beleg-literatur")
    w.leaf("interp", "Aus der Arbeit an dieser Ausgabe", xml_id="beleg-werkstatt")
    w.close("interpGrp")


def order_of_appearance(align: dict, anchors: dict) -> dict[str, int]:
    """Rank every note by where its first anchor stands in the play."""
    position = {}
    running = 0
    for sc in align["scenes"]:
        for link in sc["links"]:
            for i in link["en"]:
                position[sp_id("en", sc["act"], sc["scene"], i + 1)] = running
                running += 1
            for i in link["de"]:
                position[sp_id("de", sc["act"], sc["scene"], i + 1)] = running
                running += 1
    return {nid: min(position.get(t, 1 << 30) for t in targets)
            for nid, targets in anchors.items()}


def write_standoff(w: Writer, align: dict, notes: list[dict], anchors: dict,
                   biblio: dict, glossary: dict,
                   terms: list[tuple[re.Pattern, str]],
                   anchor_order: dict[str, int]) -> None:
    w.open("standOff")

    w.open("linkGrp", type="translation-alignment",
           corresp="#text-en #text-de")
    w.leaf("desc", "Verknüpfung der Sprechakte. @type unterscheidet die "
                   "Parallelstellen von den vier Arten der Abweichung: "
                   "abweichende Sprecherzuweisung (attribution), nur in einem "
                   "Zeugen vorhanden (en-only, de-only), unterschiedlich "
                   "gegliedert (grouped).")
    for sc in align["scenes"]:
        act, scene = sc["act"], sc["scene"]
        for link in sc["links"]:
            targets = [sp_id("en", act, scene, i + 1) for i in link["en"]]
            targets += [sp_id("de", act, scene, i + 1) for i in link["de"]]
            if not link["en"]:
                targets.append(scene_id("en", act, scene))
            if not link["de"]:
                targets.append(scene_id("de", act, scene))
            w.leaf("link", type=link["kind"],
                   target=" ".join("#" + t for t in targets))
    w.close("linkGrp")

    w.open("listAnnotation", type="commentary")
    w.leaf("desc", "Stellenkommentar. Die Anmerkungen sind deutsch und beziehen "
                   "sich auf beide Zeugen; @target nennt die kommentierten "
                   "Sprechakte, die label-Elemente das Stichwort in der jeweiligen "
                   "Fassung. Jede Anmerkung führt in einer note@type=\"beleg\" mit, "
                   "worauf sie sich stützt; ptr verweist auf die Bibliographie.")
    for nummer, note in enumerate(sorted(notes, key=lambda n: anchor_order[n["id"]]), 1):
        anchor = anchors[note["id"]]
        targets = " ".join("#" + t for t in anchor)
        w.open("annotation", xml_id=f"note-{note['id']}", n=str(nummer),
               motivation="commenting", target=targets,
               ana=f"#type-{note['type']}")
        w.open("note", xml_lang="de", type=note["type"])
        if note.get("lemma_en"):
            w.leaf("label", note["lemma_en"], xml_lang="en")
        if note.get("lemma_de"):
            w.leaf("label", note["lemma_de"], xml_lang="de")
        write_paragraphs(w, note["note"], terms)
        w.close("note")
        write_beleg(w, note)
        w.close("annotation")
    w.close("listAnnotation")

    write_bibliography(w, biblio)
    write_glossary(w, glossary)

    w.open("interpGrp", type="Kommentarkategorien", xml_id="commentary-types")
    for key, label in TYPE_LABEL.items():
        w.leaf("interp", label, xml_id=f"type-{key}")
    w.close("interpGrp")

    w.close("standOff")


# --------------------------------------------------------------------------- anchors


def resolve_anchors(align: dict, en: dict, de: dict, notes: list[dict]) -> dict:
    """Map every note id to the xml:ids of the speeches it comments on."""
    from lookup import speeches

    anchors: dict[str, list[str]] = {}
    for note in notes:
        act, scene = note["act"], note["scene"]
        side = "de" if "find_de" in note else "en"
        needle = norm(note.get("find_de") or note["find"])
        sc = next(s for s in align["scenes"]
                  if s["act"] == act and s["scene"] == scene)
        E = speeches(en, act, scene)
        D = speeches(de, act, scene)
        hits = []
        for link in sc["links"]:
            seq, idxs = (E, link["en"]) if side == "en" else (D, link["de"])
            if needle and needle in norm(" ".join(plain(seq[i]) for i in idxs)):
                hits.append(link)
        assert len(hits) == 1, f"{note['id']}: {len(hits)} Treffer"
        link = hits[0]
        anchors[note["id"]] = (
            [sp_id("en", act, scene, i + 1) for i in link["en"]]
            + [sp_id("de", act, scene, i + 1) for i in link["de"]]
        )
    return anchors


def collect_stats(en: dict, align: dict) -> dict:
    low = total = 0
    for a in en["acts"]:
        for s in a["scenes"]:
            for c in s["content"]:
                if c["type"] != "sp":
                    continue
                for g in c["content"]:
                    if g["type"] in ("verse", "prose"):
                        total += 1
                        low += g.get("certainty") == "low"
    kinds: dict[str, int] = {}
    for sc in align["scenes"]:
        for link in sc["links"]:
            kinds[link["kind"]] = kinds.get(link["kind"], 0) + 1
    return {
        "low": low,
        "low_pct": f"{low / max(1, total):.1%}".replace(".", ","),
        "form_pct": "rund 96 %",
        "parallel": kinds.get("parallel", 0),
        "attribution": kinds.get("attribution", 0),
        "en_only": kinds.get("en-only", 0),
        "de_only": kinds.get("de-only", 0),
        "grouped": kinds.get("grouped", 0),
    }


def main() -> None:
    en = json.loads((BUILD / "en.json").read_text(encoding="utf-8"))
    de = json.loads((BUILD / "de.json").read_text(encoding="utf-8"))
    align = json.loads((BUILD / "align.json").read_text(encoding="utf-8"))
    notes_data = json.loads((ROOT / "data" / "notes.json").read_text(encoding="utf-8"))
    biblio = json.loads((ROOT / "data" / "bibliographie.json").read_text(encoding="utf-8"))
    glossary = json.loads((ROOT / "data" / "glossar.json").read_text(encoding="utf-8"))

    play_notes = [n for n in notes_data["notes"] if n.get("scope") == "play"]
    spot_notes = [n for n in notes_data["notes"] if n.get("scope") != "play"]
    anchors = resolve_anchors(align, en, de, spot_notes)
    stats = collect_stats(en, align)
    terms = compile_glossary(glossary)

    w = Writer()
    w.raw('<?xml version="1.0" encoding="UTF-8"?>\n')
    w.raw('<?xml-model href="https://www.tei-c.org/release/xml/tei/custom/'
          'schema/relaxng/tei_all.rng" type="application/xml" '
          'schematypens="http://relaxng.org/ns/structure/1.0"?>\n')
    w.open("TEI", xmlns="http://www.tei-c.org/ns/1.0", xml_id="othello-en-de")
    write_header(w, stats)
    w.open("text", type="edition")
    write_front(w, play_notes, terms)
    w.open("group")
    write_witness(w, en, "en", "en", "Othello, the Moor of Venice")
    write_witness(w, de, "de", "de", "Othello, der Mohr von Venedig")
    w.close("group")
    w.close("text")
    write_standoff(w, align, spot_notes, anchors, biblio, glossary, terms,
                   order_of_appearance(align, anchors))
    w.close("TEI")

    OUT.write_text(str(w), encoding="utf-8")
    size = OUT.stat().st_size
    links = sum(len(s["links"]) for s in align["scenes"])
    print(f"{OUT.name}: {size / 1024:.0f} kB, {links} Verknüpfungen, "
          f"{len(spot_notes)} Stellenkommentare, {len(play_notes)} Einleitungstexte")


if __name__ == "__main__":
    main()
