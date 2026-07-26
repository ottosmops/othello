#!/usr/bin/env python3
"""Check every anchor, lemma and piece of evidence in data/notes.json.

A note is sound when
  * its locator ("find" / "find_de") occurs in exactly one aligned pair of the
    given act and scene,
  * its English lemma occurs in the English speeches of that pair,
  * its German lemma occurs in the German speeches of that pair,
  * it states how its claim is backed ("belegart" and "beleg"), and every id in
    "refs" exists in data/bibliographie.json.

Failures print the actual text of the pair so the lemma can be corrected.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lookup import find, norm  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
NOTES = ROOT / "data" / "notes.json"
BIBLIO = ROOT / "data" / "bibliographie.json"

BELEGARTEN = {"textzeuge", "auszählung", "literatur"}


def resolve(note: dict) -> tuple[dict | None, str]:
    """Return (hit, error) for a note's anchor."""
    side = "de" if "find_de" in note else "en"
    needle = note.get("find_de") or note.get("find")
    if not needle:
        return None, "kein Anker (find/find_de fehlt)"
    hits = [h for h in find(needle, side)
            if h["act"] == note["act"] and h["scene"] == note["scene"]]
    if not hits:
        loose = find(needle, side)
        where = ", ".join(f"{h['act']}.{h['scene']}" for h in loose) or "nirgends"
        return None, f"Anker nicht in {note['act']}.{note['scene']} gefunden (steht in: {where})"
    if len(hits) > 1:
        return None, f"Anker mehrdeutig ({len(hits)} Treffer in der Szene)"
    return hits[0], ""


def check_beleg(note: dict, known_refs: set[str]) -> int:
    """Every note must say what backs it, and point at real bibliography ids."""
    bad = 0
    if note.get("belegart") not in BELEGARTEN:
        print(f"[{note['id']}] belegart fehlt oder unbekannt: {note.get('belegart')!r}")
        bad += 1
    if not note.get("beleg"):
        print(f"[{note['id']}] beleg fehlt")
        bad += 1
    for ref in note.get("refs", []):
        if ref not in known_refs:
            print(f"[{note['id']}] refs zeigt ins Leere: {ref}")
            bad += 1
    return bad


def main() -> int:
    data = json.loads(NOTES.read_text(encoding="utf-8"))
    biblio = json.loads(BIBLIO.read_text(encoding="utf-8"))
    known_refs = {e["id"] for e in biblio["eintraege"]}

    bad = 0
    for note in data["notes"]:
        bad += check_beleg(note, known_refs)
        if note.get("scope") == "play":
            if not note.get("title") or not note.get("note"):
                print(f"[{note['id']}] Titel oder Text fehlt")
                bad += 1
            continue
        hit, err = resolve(note)
        if err:
            print(f"[{note['id']}] {err}")
            bad += 1
            continue
        assert hit is not None
        for key, field in (("lemma_en", "en_text"), ("lemma_de", "de_text")):
            lemma = note.get(key)
            if lemma and norm(lemma) not in norm(hit[field]):
                print(f"[{note['id']}] {key} nicht belegt: {lemma!r}")
                print(f"    {field}: {hit[field][:400]}")
                bad += 1
        if not note.get("note"):
            print(f"[{note['id']}] Kommentartext fehlt")
            bad += 1

    arten: dict[str, int] = {}
    for note in data["notes"]:
        arten[note.get("belegart", "?")] = arten.get(note.get("belegart", "?"), 0) + 1
    total = len(data["notes"])
    print(f"\n{total} Anmerkungen, {bad} Beanstandungen")
    print("Belegarten: " + ", ".join(f"{k}={v}" for k, v in sorted(arten.items())))
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
