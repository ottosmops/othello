#!/usr/bin/env python3
"""Validate the finished edition.

Three checks, in ascending order of interest:
  1. well-formedness,
  2. TEI P5 (RELAX NG, tei_all) via jing, if the schema and jing are present,
  3. referential integrity — every @target, @who, @ana and @corresp must point
     at an xml:id that exists in the document, and every speech must be
     reachable from the alignment.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "othello-bilingual.tei.xml"
RNG = ROOT / "build" / "tei_all.rng"
TEI = "http://www.tei-c.org/ns/1.0"
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"

POINTER_ATTRS = ("target", "who", "ana", "corresp")


def check_schema() -> int:
    if not RNG.exists() or not shutil.which("jing"):
        print("· TEI-Schema übersprungen (jing oder tei_all.rng fehlt)")
        return 0
    proc = subprocess.run(["jing", str(RNG), str(DOC)],
                          capture_output=True, text=True)
    if proc.returncode == 0:
        print("· TEI P5 (tei_all, RELAX NG): gültig")
        return 0
    print("· TEI P5: FEHLER")
    print(proc.stdout[:4000] or proc.stderr[:4000])
    return 1


def check_pointers(root: ET.Element) -> int:
    ids = {el.get(XML_ID) for el in root.iter() if el.get(XML_ID)}
    bad = 0
    seen_targets: set[str] = set()
    for el in root.iter():
        for attr in POINTER_ATTRS:
            value = el.get(attr)
            if not value:
                continue
            for ref in value.split():
                if not ref.startswith("#"):
                    continue  # external URI
                if ref[1:] not in ids:
                    print(f"  ! {el.tag.split('}')[1]}/@{attr} zeigt ins Leere: {ref}")
                    bad += 1
                elif attr == "target":
                    seen_targets.add(ref[1:])
    print(f"· Zeiger: {len(ids)} xml:id, {bad} unauflösbar")

    speeches = {el.get(XML_ID) for el in root.iter(f"{{{TEI}}}sp")}
    unlinked = speeches - seen_targets
    if unlinked:
        print(f"  ! {len(unlinked)} Sprechakte ohne Verknüpfung, "
              f"z. B. {sorted(str(u) for u in unlinked)[:5]}")
        bad += 1
    else:
        print(f"· Alle {len(speeches)} Sprechakte sind verknüpft")
    return 1 if bad else 0


def report(root: ET.Element) -> None:
    def count(tag: str) -> int:
        return sum(1 for _ in root.iter(f"{{{TEI}}}{tag}"))

    links = {}
    for link in root.iter(f"{{{TEI}}}link"):
        links[link.get("type")] = links.get(link.get("type"), 0) + 1
    print(f"· Umfang: {count('sp')} Sprechakte, {count('l')} Verszeilen, "
          f"{count('p') - count('note')} Prosaabschnitte, {count('stage')} "
          f"Regieanweisungen, {count('annotation')} Stellenkommentare")
    print("· Verknüpfungen: " + ", ".join(f"{k}={v}" for k, v in sorted(links.items())))


def main() -> int:
    try:
        tree = ET.parse(DOC)
    except ET.ParseError as exc:
        print(f"· Nicht wohlgeformt: {exc}")
        return 1
    print("· Wohlgeformt: ja")
    root = tree.getroot()
    rc = check_schema()
    rc |= check_pointers(root)
    report(root)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
