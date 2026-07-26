#!/usr/bin/env python3
"""Look up an aligned speech pair by a phrase from either text.

    python3 src/lookup.py "beast with two backs"
    python3 src/lookup.py --de "Tier mit zwei Rücken"

Used while writing the commentary, and re-used by build_tei.py to resolve the
anchors of the notes in data/notes.json.
"""

from __future__ import annotations

import json
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"


def load() -> tuple[dict, dict, dict]:
    en = json.loads((BUILD / "en.json").read_text(encoding="utf-8"))
    de = json.loads((BUILD / "de.json").read_text(encoding="utf-8"))
    al = json.loads((BUILD / "align.json").read_text(encoding="utf-8"))
    return en, de, al


def speeches(doc: dict, act: int, scene: int) -> list[dict]:
    a = next(x for x in doc["acts"] if x["n"] == act)
    s = next(x for x in a["scenes"] if x["n"] == scene)
    return [c for c in s["content"] if c["type"] == "sp"]


def plain(sp: dict) -> str:
    return " ".join(
        l.get("text", "")
        for g in sp["content"]
        if g["type"] in ("verse", "prose")
        for l in g["lines"]
    )


def norm(s: str) -> str:
    """Fold the typographic variation that separates a quote from its source."""
    s = unicodedata.normalize("NFC", s)
    for a, b in [("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"'),
                 ("–", "-"), ("—", "-"), ("ß", "ss")]:
        s = s.replace(a, b)
    return " ".join(s.lower().split())


def find(phrase: str, side: str = "en") -> list[dict]:
    """All aligned pairs in which *phrase* occurs on *side*."""
    en, de, al = load()
    needle = norm(phrase)
    hits = []
    for sc in al["scenes"]:
        E = speeches(en, sc["act"], sc["scene"])
        D = speeches(de, sc["act"], sc["scene"])
        for link in sc["links"]:
            seq, idxs = (E, link["en"]) if side == "en" else (D, link["de"])
            text = " ".join(plain(seq[i]) for i in idxs)
            if needle and needle in norm(text):
                hits.append({
                    "act": sc["act"], "scene": sc["scene"], "link": link,
                    "en_idx": link["en"], "de_idx": link["de"],
                    "en_speaker": E[link["en"][0]]["speaker"] if link["en"] else None,
                    "de_speaker": D[link["de"][0]]["speaker"] if link["de"] else None,
                    "en_text": " ".join(plain(E[i]) for i in link["en"]),
                    "de_text": " ".join(plain(D[i]) for i in link["de"]),
                })
    return hits


def main() -> None:
    args = sys.argv[1:]
    side = "en"
    if args and args[0] == "--de":
        side, args = "de", args[1:]
    if not args:
        print(__doc__)
        return
    for hit in find(" ".join(args), side):
        print(f"=== {hit['act']}.{hit['scene']}  EN#{hit['en_idx']} DE#{hit['de_idx']}"
              f"  [{hit['link']['kind']}]")
        print(f"  EN {hit['en_speaker']}: {hit['en_text']}")
        print(f"  DE {hit['de_speaker']}: {hit['de_text']}")


if __name__ == "__main__":
    main()
