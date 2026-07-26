#!/usr/bin/env python3
"""Parse the DraCor/TextGrid TEI of Baudissin's German Othello (1832) into the
shared intermediate JSON format.

The source is already TEI P5 (div[@type=act] > div[@type=scene] > sp), so this
is mostly a normalisation step: character ids are mapped onto the canonical set
shared with the English side, and page breaks of the print edition are kept as
milestones so the edition can still cite the German pagination.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "sources" / "gersh_othello_de.tei.xml"
OUT = ROOT / "build" / "de.json"

TEI = "http://www.tei-c.org/ns/1.0"
NS = {"t": TEI}

# Baudissin's cast, mapped onto the canonical ids used by parse_en.py.
ID_MAP = {
    "othello": "othello", "jago": "iago", "desdemona": "desdemona",
    "cassio": "cassio", "emilia": "emilia", "rodrigo": "roderigo",
    "lodovico": "lodovico", "brabantio": "brabantio", "herzog": "duke",
    "montano": "montano", "gratiano": "gratiano", "bianca": "bianca",
    "narr": "clown", "erster_senator": "senator1", "zweiter_senator": "senator2",
    "erster_edelmann": "gentleman1", "zweiter_edelmann": "gentleman2",
    "dritter_edelmann": "gentleman3", "vierter_edelmann": "gentleman4",
    "matrose": "sailor", "beamter": "officer", "gerichtsdiener": "officer",
    "bote": "messenger", "musikanten": "musician", "herold": "herald",
    "edelleute": "gentlemen", "alle_i-3": "all", "alle_ii-3": "all",
}

ACT_NUM = {"Erster": 1, "Zweiter": 2, "Dritter": 3, "Vierter": 4, "Fünfter": 5}
SCENE_NUM = {"Erste": 1, "Zweite": 2, "Dritte": 3, "Vierte": 4, "Fünfte": 5}


def tag(el: ET.Element) -> str:
    return el.tag.split("}", 1)[-1]


def canon(who: str | None) -> str:
    if not who:
        return "unknown"
    ids = [ID_MAP.get(w.lstrip("#"), w.lstrip("#")) for w in who.split()]
    return " ".join(ids)


def flat_text(el: ET.Element) -> str:
    """Text content of *el* with page breaks dropped and whitespace normalised."""
    parts: list[str] = []
    for node in el.iter():
        if tag(node) == "pb":
            if node.tail:
                parts.append(node.tail)
            continue
        if node is el and node.text:
            parts.append(node.text)
        elif node is not el:
            if node.text:
                parts.append(node.text)
            if node.tail:
                parts.append(node.tail)
    return re.sub(r"\s+", " ", "".join(parts)).strip()


def page_before(el: ET.Element) -> str | None:
    """Page number of the print edition in force at *el*, if a pb precedes it."""
    return el.get("_page")


def annotate_pages(body: ET.Element) -> None:
    """Stamp every element with the page it appears on (pb is a milestone)."""
    current = None
    for el in body.iter():
        if tag(el) == "pb":
            current = el.get("n")
        elif current:
            el.set("_page", current)


def head_text(div_el: ET.Element) -> str:
    head = div_el.find("t:head", NS)
    assert head is not None and head.text, f"<div> without <head>: {div_el.get('type')}"
    return head.text.strip()


def parse() -> dict:
    tree = ET.parse(SRC)
    body = tree.getroot().find(".//t:body", NS)
    assert body is not None, "no <body> in source TEI"
    annotate_pages(body)

    acts = []
    for act_el in body.findall("t:div", NS):
        head = head_text(act_el)
        act = {
            "n": ACT_NUM[head.split()[0]],
            "head": head,
            "scenes": [],
        }
        acts.append(act)
        for scene_el in act_el.findall("t:div", NS):
            shead = head_text(scene_el)
            scene = {
                "n": SCENE_NUM[shead.split()[0]],
                "head": shead,
                "setting": "",
                "content": [],
            }
            act["scenes"].append(scene)
            settings = []
            for child in scene_el:
                name = tag(child)
                if name == "head":
                    continue
                if name == "stage":
                    txt = flat_text(child)
                    if not scene["content"]:
                        settings.append(txt)
                    scene["content"].append(
                        {"type": "stage", "text": txt, "page": page_before(child)}
                    )
                elif name == "sp":
                    scene["content"].append(parse_sp(child))
            scene["setting"] = " ".join(settings[:1])
    return {"acts": acts}


def parse_sp(sp_el: ET.Element) -> dict:
    speaker_el = sp_el.find("t:speaker", NS)
    label = flat_text(speaker_el) if speaker_el is not None else ""
    # DraCor resolves collective speakers ("ALLE") into the individuals on
    # stage, and gives them scene-bound ids. The edition keeps the printed
    # collective label, so the two witnesses stay comparable.
    who = "all" if label.upper().startswith("ALLE") else canon(sp_el.get("who"))
    sp = {
        "type": "sp",
        "speaker": label,
        "who": who,
        "page": page_before(sp_el),
        "content": [],
    }
    for child in sp_el:
        name = tag(child)
        if name == "speaker":
            continue
        if name == "stage":
            sp["content"].append({"type": "stage", "text": flat_text(child)})
        elif name == "lg":
            lines = [{"text": flat_text(l)} for l in child.findall("t:l", NS)]
            for st in child.findall("t:stage", NS):  # rare: stage inside lg
                lines.append({"stage": flat_text(st), "text": ""})
            sp["content"].append({"type": "verse", "lines": lines})
        elif name == "l":  # single line not wrapped in lg
            sp["content"].append(
                {"type": "verse", "lines": [{"text": flat_text(child)}]}
            )
        elif name == "p":
            sp["content"].append(
                {"type": "prose", "lines": [{"text": flat_text(child)}]}
            )
    return sp


def main() -> None:
    doc = parse()
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")

    speeches = sum(
        1
        for a in doc["acts"]
        for s in a["scenes"]
        for c in s["content"]
        if c["type"] == "sp"
    )
    words = sum(
        len(l.get("text", "").split())
        for a in doc["acts"]
        for s in a["scenes"]
        for c in s["content"]
        if c["type"] == "sp"
        for g in c["content"]
        if g["type"] in ("verse", "prose")
        for l in g["lines"]
    )
    print(f"acts={len(doc['acts'])} "
          f"scenes={sum(len(a['scenes']) for a in doc['acts'])} "
          f"speeches={speeches} words={words}")


if __name__ == "__main__":
    main()
