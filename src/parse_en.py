#!/usr/bin/env python3
"""Parse the Project Gutenberg plain-text Othello (PG #1531) into the shared
intermediate JSON format used by the alignment and TEI stages.

Source conventions observed in PG #1531:
  * act headings    ``ACT I`` … ``ACT V`` (all caps, on their own line)
  * scene headings  ``SCENE I. Venice. A street.``
  * speaker labels  ``IAGO.`` (all caps, own line, block-initial)
  * stage business  ``[_Exit._]`` — whole block, or inline at the head of a line
  * blocks are separated by blank lines; a text block that does not open with a
    speaker label continues the preceding speech.

Verse/prose is not marked in the source. The typesetting is, however,
diagnostic: verse follows the metrical line of the Globe/Moby text, prose is
hard-wrapped by the transcribers at a fixed measure. See ``classify_form``.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "sources" / "pg1531_othello_en.txt"
OUT = ROOT / "build" / "en.json"

ROMAN = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6}

RE_ACT = re.compile(r"^ACT ([IVX]+)$")
RE_SCENE = re.compile(r"^SCENE ([IVX]+)\.\s*(.*)$")
RE_SPEAKER = re.compile(r"^[A-Z][A-Z’'. \-]*\.?$")
RE_STAGE_FULL = re.compile(r"^\[_?(.+?)_?\]$")
# Stage business can sit anywhere in a line: "Good night to everyone.
# [_To Brabantio._] And, noble signior, …". The trailing full stop inside the
# brackets is not always there ("[_To Bianca_]").
RE_STAGE_ANYWHERE = re.compile(r"\[_(.+?)_\]")
# Song is set in the transcribers' italics, which may run across several lines:
# an underscore opens at the start of the song and closes at its end.
RE_ITALIC = re.compile(r"_")
# Entrances are set unbracketed in this transcription, unlike exits.
RE_STAGE_BARE = re.compile(r"^(Enter|Re-enter|Exeunt|Exit)\b.*\.$", re.S)
# …as are a few descriptive directions, which have to be listed.
STAGE_BARE_EXTRA = {
    "Brabantio appears above at a window.",
    "The Duke and Senators sitting at a table; Officers attending.",
    "Desdemona in bed asleep; a light burning.",
}
RE_WITHIN = re.compile(r"^\[_Within\._\]\s*(.+)$")

# Speaker labels are all-caps, but so are a few shouted verse lines. Only these
# labels actually occur as speech openers in PG #1531; the inventory is checked
# against the parse result below.
KNOWN_SPEAKERS = {
    "OTHELLO", "IAGO", "DESDEMONA", "CASSIO", "EMILIA", "RODERIGO", "BRABANTIO",
    "LODOVICO", "MONTANO", "BIANCA", "GRATIANO", "DUKE", "CLOWN", "MESSENGER",
    "HERALD", "SAILOR", "SENATOR", "FIRST SENATOR", "SECOND SENATOR",
    "FIRST GENTLEMAN", "SECOND GENTLEMAN", "THIRD GENTLEMAN", "FOURTH GENTLEMAN",
    "FIRST OFFICER", "SECOND OFFICER", "OFFICER", "GENTLEMAN", "MUSICIAN",
    "FIRST MUSICIAN", "GENTLEMEN", "ALL", "BOTH", "SERVANT", "ATTENDANT",
    "SENATORS", "OFFICERS", "DUKE AND SENATORS",
}

# Compound labels ("DUKE and SENATORS.") are kept as they stand and given a
# multi-valued @who, as TEI provides for.
RE_COMPOUND = re.compile(r"^([A-Z][A-Z’'. \-]*?) and ([A-Z][A-Z’'. \-]*)\.$")

# Normalised character ids, shared with the German side (see parse_de.py).
ID_MAP = {
    "OTHELLO": "othello", "IAGO": "iago", "DESDEMONA": "desdemona",
    "CASSIO": "cassio", "EMILIA": "emilia", "RODERIGO": "roderigo",
    "BRABANTIO": "brabantio", "LODOVICO": "lodovico", "MONTANO": "montano",
    "BIANCA": "bianca", "GRATIANO": "gratiano", "DUKE": "duke",
    "CLOWN": "clown", "MESSENGER": "messenger", "HERALD": "herald",
    "SAILOR": "sailor", "SENATOR": "senator", "FIRST SENATOR": "senator1",
    "SECOND SENATOR": "senator2", "FIRST GENTLEMAN": "gentleman1",
    "SECOND GENTLEMAN": "gentleman2", "THIRD GENTLEMAN": "gentleman3",
    "FOURTH GENTLEMAN": "gentleman4", "FIRST OFFICER": "officer1",
    "SECOND OFFICER": "officer2", "OFFICER": "officer",
    "GENTLEMAN": "gentleman", "MUSICIAN": "musician",
    "FIRST MUSICIAN": "musician", "GENTLEMEN": "gentlemen", "ALL": "all",
    "BOTH": "both", "SERVANT": "servant", "ATTENDANT": "attendant",
    "SENATORS": "senators", "OFFICERS": "officers", "[WITHIN]": "voice",
}

# Line measures observed in PG #1531: prose is wrapped at ~70 characters, verse
# is set line-for-line and stays below ~58. Between the two lies a band in which
# a short speech cannot be told apart on typography alone.
VERSE_MAX = 58
PROSE_MIN = 62


def classify_form(lines: list[str]) -> str:
    """Guess verse vs prose from the transcribers' line measure.

    Returns ``"prose"``, ``"verse"`` or ``"?"`` when the typography does not
    decide — typically a one- or two-line speech whose lines fall inside the
    band both settings share. Undecided speeches are resolved from their
    context in :func:`resolve_undecided`.
    """
    body = [l for l in lines if l.strip()]
    if not body:
        return "?"
    lengths = sorted(len(l) for l in body)
    longest = lengths[-1]
    if longest >= PROSE_MIN:
        return "prose"
    if len(body) >= 3 and lengths[len(lengths) // 2] <= VERSE_MAX:
        return "verse"
    if len(body) >= 3:
        return "prose"
    # One or two short lines: could be either a verse line or the tail of a
    # wrapped prose speech.
    return "?"


def resolve_undecided(scene: dict) -> None:
    """Settle ``"?"`` speeches from the nearest decided neighbours in the scene.

    Verse and prose come in stretches in this play (the drinking scene, the
    clown scenes, Iago's prose seductions). Where both neighbours agree the
    undecided speech takes their form; where they disagree, or at the edges of
    a scene, it defaults to verse, which is the unmarked case in the source.
    """
    groups = [
        g
        for c in scene["content"]
        if c["type"] == "sp"
        for g in c["content"]
        if g["type"] in ("verse", "prose", "?")
    ]
    decided = [i for i, g in enumerate(groups) if g["type"] != "?"]
    for i, g in enumerate(groups):
        if g["type"] != "?":
            continue
        before = max((d for d in decided if d < i), default=None)
        after = min((d for d in decided if d > i), default=None)
        forms = {groups[d]["type"] for d in (before, after) if d is not None}
        if len(forms) == 1:
            g["type"] = forms.pop()
        else:
            g["type"] = "verse"  # the unmarked case
            g["certainty"] = "low"


def parse() -> dict:
    text = SRC.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    start = text.index("\nACT I\n", 1500)
    end = text.index("*** END OF THE PROJECT GUTENBERG")
    body = text[start:end]

    acts: list[dict] = []
    act = scene = sp = None
    pending_stage: list[str] = []

    def flush_stage(target: dict | None) -> None:
        """Attach buffered stage directions to *target* (scene or speech)."""
        nonlocal pending_stage
        if pending_stage and target is not None:
            for s in pending_stage:
                target["content"].append({"type": "stage", "text": s})
        pending_stage = []

    for raw_block in re.split(r"\n\s*\n", body):
        block = [l.rstrip() for l in raw_block.split("\n") if l.strip()]
        if not block:
            continue
        head = block[0].strip()

        m = RE_ACT.match(head)
        if m and len(block) == 1:
            flush_stage(scene)
            assert acts or m.group(1) == "I"
            act = {"n": ROMAN[m.group(1)], "head": head, "scenes": []}
            acts.append(act)
            scene = sp = None
            continue

        m = RE_SCENE.match(head)
        if m and len(block) == 1 and act is not None:
            flush_stage(scene)
            scene = {
                "n": ROMAN[m.group(1)],
                "head": head,
                "setting": m.group(2).strip(),
                "content": [],
            }
            act["scenes"].append(scene)
            sp = None
            continue

        if scene is None:  # front matter before ACT I
            continue

        m = RE_STAGE_FULL.match(head)
        if m and len(block) == 1:
            pending_stage.append(m.group(1).rstrip("."))
            continue

        joined = " ".join(l.strip() for l in block)
        if RE_STAGE_BARE.match(joined) or joined in STAGE_BARE_EXTRA:
            pending_stage.append(joined.rstrip("."))
            continue

        m = RE_WITHIN.match(head)
        if m:
            # A cry from offstage: speech, but with no character to assign it to.
            flush_stage(scene)
            sp = {"type": "sp", "speaker": "[Within.]", "who": "voice",
                  "content": [{"type": "stage", "text": "Within"}]}
            scene["content"].append(sp)
            add_speech_lines(sp, [m.group(1)] + block[1:])
            continue

        name = head.rstrip(".")
        compound = RE_COMPOUND.match(head)
        if compound:
            parts = [p.strip().rstrip(".") for p in compound.groups()]
            is_speech = all(p in KNOWN_SPEAKERS for p in parts)
            who = " ".join(ID_MAP.get(p, p.lower()) for p in parts)
        else:
            is_speech = RE_SPEAKER.match(head) is not None and name in KNOWN_SPEAKERS
            who = ID_MAP.get(name, re.sub(r"\W+", "", name.lower()))

        if is_speech:
            flush_stage(scene)
            sp = {
                "type": "sp",
                "speaker": head,
                "who": who,
                "content": [],
            }
            scene["content"].append(sp)
            add_speech_lines(sp, block[1:])
            continue

        # No speaker label: continuation of the current speech, with any
        # buffered stage direction belonging inside it.
        if sp is not None:
            flush_stage(sp)
            add_speech_lines(sp, block)
        else:  # stray text before the first speech = opening stage business
            pending_stage.append(" ".join(block))

    flush_stage(scene)
    for a in acts:
        for s in a["scenes"]:
            resolve_undecided(s)
    return {"acts": acts}


def split_line(line: str, italic: bool) -> tuple[dict, bool]:
    """Turn one source line into parts, and say whether italics stay open.

    The result keeps a plain ``text`` — the spoken words, without the stage
    cues — so that quoting and alignment see only what is said, and ``parts``,
    which preserves the order of speech and stage business for the encoding.
    """
    parts: list[dict] = []
    pos = 0
    for m in RE_STAGE_ANYWHERE.finditer(line):
        if m.start() > pos:
            parts.append({"text": line[pos:m.start()]})
        parts.append({"stage": m.group(1).rstrip(".")})
        pos = m.end()
    if pos < len(line):
        parts.append({"text": line[pos:]})

    # Italics: walk the markers, alternating the state, then drop them.
    for part in parts:
        if "text" not in part:
            continue
        segments = RE_ITALIC.split(part["text"])
        state, marked = italic, False
        for i, segment in enumerate(segments):
            if i:
                state = not state
            if segment.strip() and state:
                marked = True
        italic = state
        part["text"] = "".join(segments)
        if marked:
            part["italic"] = True

    parts = [p for p in parts if p.get("stage") or p.get("text", "").strip()]
    for part in parts:
        if "text" in part:
            part["text"] = part["text"].strip()
    text = " ".join(p["text"] for p in parts if "text" in p).strip()
    return {"parts": parts, "text": text}, italic


def add_speech_lines(sp: dict, lines: list[str]) -> None:
    """Append a run of source lines to *sp*, splitting off inline stage cues."""
    lines = [l.strip() for l in lines if l.strip()]
    if not lines:
        return
    form = classify_form(lines)
    group = {"type": form, "lines": []}
    italic = False
    for line in lines:
        parsed, italic = split_line(line, italic)
        group["lines"].append(parsed)
    sp["content"].append(group)


def main() -> None:
    doc = parse()
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")

    speeches = words = stages = 0
    unknown = set()
    for a in doc["acts"]:
        for s in a["scenes"]:
            for c in s["content"]:
                if c["type"] == "sp":
                    speeches += 1
                    for g in c["content"]:
                        if g["type"] in ("verse", "prose"):
                            words += sum(len(l.get("text", "").split()) for l in g["lines"])
                        else:
                            stages += 1
                    if any(w not in ID_MAP.values() for w in c["who"].split()):
                        unknown.add(c["speaker"])
                else:
                    stages += 1
    print(f"acts={len(doc['acts'])} "
          f"scenes={sum(len(a['scenes']) for a in doc['acts'])} "
          f"speeches={speeches} stages={stages} words={words}")
    if unknown:
        print("unmapped speakers:", sorted(unknown), file=sys.stderr)


if __name__ == "__main__":
    main()
