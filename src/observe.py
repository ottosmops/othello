#!/usr/bin/env python3
"""Survey the aligned texts for facts a commentary can rest on.

Nothing here interprets. It counts, compares and lists, so that the notes in
data/notes.json can be written from measured findings rather than from
recollection. Every number the commentary states about this edition should be
reproducible with one of these reports.

    python3 src/observe.py ratio      Reden, die Baudissin stark kürzt/dehnt
    python3 src/observe.py word W…    Vorkommen und deutsche Wiedergaben
    python3 src/observe.py rhyme      Reimpaare am Szenenschluss
    python3 src/observe.py form       Vers/Prosa je Figur
    python3 src/observe.py share      Redeanteile
    python3 src/observe.py stage      Regieanweisungen im Vergleich
    python3 src/observe.py songs      Liedstellen
"""

from __future__ import annotations

import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from lookup import load, norm, plain, speeches  # noqa: E402


def pairs():
    """Every aligned pair as (act, scene, kind, en_speech(es), de_speech(es))."""
    en, de, al = load()
    for sc in al["scenes"]:
        E = speeches(en, sc["act"], sc["scene"])
        D = speeches(de, sc["act"], sc["scene"])
        for link in sc["links"]:
            yield (sc["act"], sc["scene"], link["kind"],
                   [E[i] for i in link["en"]], [D[i] for i in link["de"]])


def words(sps) -> int:
    return sum(len(plain(s).split()) for s in sps)


def cmd_ratio(args) -> None:
    """Where the German is markedly shorter or longer than the English."""
    rows = []
    for act, scene, kind, E, D in pairs():
        we, wd = words(E), words(D)
        if we < 12 or not wd:
            continue
        rows.append((wd / we, act, scene, E, D, we, wd))
    rows.sort(key=lambda r: r[0])
    print("### stärkste Kürzungen (deutsch/englisch)")
    for r, act, scene, E, D, we, wd in rows[:15]:
        print(f"{r:.2f}  {act}.{scene}  {E[0]['speaker']} {we}→{wd} Wörter")
        print(f"   EN {plain(E[0])[:220]}")
        print(f"   DE {plain(D[0])[:220]}")
    print("\n### stärkste Dehnungen")
    for r, act, scene, E, D, we, wd in rows[-8:]:
        print(f"{r:.2f}  {act}.{scene}  {E[0]['speaker']} {we}→{wd} Wörter")


def cmd_word(args) -> None:
    """Occurrences of a word and what stands opposite it in German."""
    for word in args:
        hits = []
        for act, scene, kind, E, D in pairs():
            en_text = " ".join(plain(s) for s in E)
            if re.search(rf"\b{word}\w*\b", en_text, re.I):
                for m in re.finditer(rf"\b{word}\w*\b", en_text, re.I):
                    hits.append((act, scene, m.group(0),
                                 en_text[max(0, m.start() - 45):m.start() + 55],
                                 " ".join(plain(s) for s in D)[:150]))
        print(f"\n### {word}: {len(hits)} Belege")
        for act, scene, form, ctx, de in hits[:14]:
            print(f"  {act}.{scene} …{ctx}…")
            print(f"       DE {de}")


def cmd_rhyme(args) -> None:
    """Rhyming couplets: does the German keep the rhyme?"""
    en, de, al = load()
    for a in en["acts"]:
        for s in a["scenes"]:
            sps = [c for c in s["content"] if c["type"] == "sp"]
            if not sps:
                continue
            last = sps[-1]
            lines = [l.get("text", "") for g in last["content"]
                     if g["type"] in ("verse", "prose") for l in g["lines"]]
            if len(lines) >= 2:
                print(f"{a['n']}.{s['n']} EN … {lines[-2]} / {lines[-1]}")
                D = speeches(de, a["n"], s["n"])
                dl = [l.get("text", "") for g in D[-1]["content"]
                      if g["type"] in ("verse", "prose") for l in g["lines"]]
                if len(dl) >= 2:
                    print(f"      DE … {dl[-2]} / {dl[-1]}")


def cmd_form(args) -> None:
    """Verse and prose per character, and where a character switches."""
    counts: dict[str, Counter] = defaultdict(Counter)
    switches = []
    for act, scene, kind, E, D in pairs():
        for s in E:
            forms = {g["type"] for g in s["content"]} - {"stage"}
            for f in forms:
                counts[s["who"]][f] += 1
            if len(forms) > 1:
                switches.append((act, scene, s["speaker"], plain(s)[:90]))
    print("### Vers/Prosa je Figur (englischer Zeuge)")
    for who, c in sorted(counts.items(), key=lambda x: -sum(x[1].values())):
        total = sum(c.values())
        if total < 8:
            continue
        print(f"  {who:12s} Vers {c['verse']:4d}  Prosa {c['prose']:4d}  "
              f"({c['prose'] / total:.0%} Prosa)")
    print(f"\n### Reden mit Wechsel innerhalb der Rede: {len(switches)}")
    for row in switches[:12]:
        print("  ", row)


def cmd_share(args) -> None:
    """Who speaks how much, in speeches and in words."""
    sp_count: Counter = Counter()
    wd_count: Counter = Counter()
    for act, scene, kind, E, D in pairs():
        for s in E:
            sp_count[s["who"]] += 1
            wd_count[s["who"]] += len(plain(s).split())
    total_w = sum(wd_count.values())
    print("### Redeanteile (englischer Zeuge)")
    for who, n in wd_count.most_common(12):
        print(f"  {who:12s} {sp_count[who]:4d} Reden  {n:5d} Wörter  "
              f"{n / total_w:5.1%}")
    print(f"  gesamt: {sum(sp_count.values())} Reden, {total_w} Wörter")


def cmd_stage(args) -> None:
    """Stage directions: how many, and where the witnesses differ in number."""
    en, de, al = load()
    for a_en, a_de in zip(en["acts"], de["acts"]):
        for s_en, s_de in zip(a_en["scenes"], a_de["scenes"]):
            ne = sum(1 for c in s_en["content"] if c["type"] == "stage")
            ne += sum(1 for c in s_en["content"] if c["type"] == "sp"
                      for g in c["content"] if g["type"] == "stage")
            nd = sum(1 for c in s_de["content"] if c["type"] == "stage")
            nd += sum(1 for c in s_de["content"] if c["type"] == "sp"
                      for g in c["content"] if g["type"] == "stage")
            print(f"  {a_en['n']}.{s_en['n']}: EN {ne:3d}  DE {nd:3d}  "
                  f"{'≠' if ne != nd else ''}")


def cmd_songs(args) -> None:
    """Passages the English text marks as song (italics in the source)."""
    for act, scene, kind, E, D in pairs():
        for s in E:
            text = plain(s)
            if "_" in text or re.search(r"\b(sings|Sings)\b", str(s)):
                print(f"{act}.{scene} {s['speaker']}: {text[:200]}")
                print(f"      DE {' '.join(plain(x) for x in D)[:200]}")


COMMANDS = {
    "ratio": cmd_ratio, "word": cmd_word, "rhyme": cmd_rhyme,
    "form": cmd_form, "share": cmd_share, "stage": cmd_stage, "songs": cmd_songs,
}


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(__doc__)
        return
    COMMANDS[sys.argv[1]](sys.argv[2:])


if __name__ == "__main__":
    main()
