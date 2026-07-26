#!/usr/bin/env python3
"""Align the English and German speeches scene by scene.

Both witnesses share the act/scene division of the received text, so the
alignment problem is confined to a single scene at a time. Within a scene the
speeches are aligned with Needleman-Wunsch over the sequence of speaking
characters, with the relative length of the speeches as a tie-breaker. Adjacent
gaps whose neighbour has the same speaker are folded into n:1 / 1:n links, which
is how the real divergences show up: Baudissin occasionally runs two short
replies together, and the two witnesses disagree about a handful of half-lines.

Output: build/align.json plus a quality report on stdout.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"

MATCH = 3.0        # same speaker
MISMATCH = -2.0    # different speaker (still possible: minor-role naming)
GAP = -2.5


def speeches(scene: dict) -> list[dict]:
    return [c for c in scene["content"] if c["type"] == "sp"]


def words(sp: dict) -> int:
    return sum(
        len(l.get("text", "").split())
        for g in sp["content"]
        if g["type"] in ("verse", "prose")
        for l in g["lines"]
    )


def score(a: dict, b: dict) -> float:
    """Similarity of two speeches: speaker identity plus a length signal.

    @who may hold several ids (collective speakers such as "DUKE and
    SENATORS"), so identity is measured on the sets: a partial overlap still
    scores positively.
    """
    wa_, wb_ = set(a["who"].split()), set(b["who"].split())
    if wa_ == wb_:
        base = MATCH
    elif wa_ & wb_:
        base = 1.0
    else:
        base = MISMATCH
    wa, wb = words(a), words(b)
    if wa and wb:
        ratio = min(wa, wb) / max(wa, wb)
        base += 0.5 * (ratio - 0.5)  # ±0.25, enough to break ties only
    return base


def needleman_wunsch(xs: list[dict], ys: list[dict]) -> list[tuple[int | None, int | None]]:
    n, m = len(xs), len(ys)
    f = [[0.0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        f[i][0] = f[i - 1][0] + GAP
    for j in range(1, m + 1):
        f[0][j] = f[0][j - 1] + GAP
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            f[i][j] = max(
                f[i - 1][j - 1] + score(xs[i - 1], ys[j - 1]),
                f[i - 1][j] + GAP,
                f[i][j - 1] + GAP,
            )
    pairs: list[tuple[int | None, int | None]] = []
    i, j = n, m
    while i > 0 or j > 0:
        if i > 0 and j > 0 and abs(f[i][j] - (f[i - 1][j - 1] + score(xs[i - 1], ys[j - 1]))) < 1e-9:
            pairs.append((i - 1, j - 1))
            i, j = i - 1, j - 1
        elif i > 0 and abs(f[i][j] - (f[i - 1][j] + GAP)) < 1e-9:
            pairs.append((i - 1, None))
            i -= 1
        else:
            pairs.append((None, j - 1))
            j -= 1
    pairs.reverse()
    return pairs


def fold_gaps(pairs, xs, ys):
    """Turn gap+match runs by the same speaker into n:m links.

    ``[(3, None), (4, 7)]`` with the same speaker in English 3 and 4 becomes
    ``([3, 4], [7])`` — one German speech answering two English ones.
    """
    links: list[dict] = []
    for en, de in pairs:
        if en is not None and de is not None:
            links.append({"en": [en], "de": [de]})
            continue
        side, idx = ("en", en) if en is not None else ("de", de)
        seq = xs if side == "en" else ys
        prev = links[-1] if links else None
        merged = False
        # attach to the neighbouring link if that link's speech on the same side
        # is by the same character
        if prev and prev[side] and seq[prev[side][-1]]["who"] == seq[idx]["who"]:
            prev[side].append(idx)
            merged = True
        if not merged:
            links.append({"en": [], "de": []})
            links[-1][side] = [idx]
    # a second pass pulls unattached gaps into the following link when it is by
    # the same speaker
    out = []
    for link in links:
        if link["en"] and link["de"]:
            out.append(link)
            continue
        side = "en" if link["en"] else "de"
        seq = xs if side == "en" else ys
        if out and out[-1][side] and seq[out[-1][side][-1]]["who"] == seq[link[side][0]]["who"]:
            out[-1][side].extend(link[side])
        else:
            out.append(link)
    return out


def main() -> None:
    en = json.loads((BUILD / "en.json").read_text(encoding="utf-8"))
    de = json.loads((BUILD / "de.json").read_text(encoding="utf-8"))

    assert len(en["acts"]) == len(de["acts"]) == 5
    result = {"scenes": []}
    stats = {"1:1": 0, "n:m": 0, "en_only": 0, "de_only": 0, "speaker_clash": 0,
             "form_agree": 0, "form_clash": 0}
    clashes = []

    for a_en, a_de in zip(en["acts"], de["acts"]):
        assert len(a_en["scenes"]) == len(a_de["scenes"]), (
            f"scene count differs in act {a_en['n']}")
        for s_en, s_de in zip(a_en["scenes"], a_de["scenes"]):
            xs, ys = speeches(s_en), speeches(s_de)
            links = fold_gaps(needleman_wunsch(xs, ys), xs, ys)
            for link in links:
                if link["en"] and link["de"]:
                    if len(link["en"]) == len(link["de"]) == 1:
                        stats["1:1"] += 1
                        link["kind"] = "parallel"
                        x, y = xs[link["en"][0]], ys[link["de"][0]]
                        if x["who"] != y["who"]:
                            stats["speaker_clash"] += 1
                            link["kind"] = "attribution"
                            clashes.append(
                                f"{a_en['n']}.{s_en['n']}: {x['speaker']} / {y['speaker']}")
                        fx = {g["type"] for g in x["content"]} - {"stage"}
                        fy = {g["type"] for g in y["content"]} - {"stage"}
                        if fx and fy:
                            stats["form_agree" if fx == fy else "form_clash"] += 1
                    else:
                        stats["n:m"] += 1
                        link["kind"] = "grouped"
                elif link["en"]:
                    stats["en_only"] += 1
                    link["kind"] = "en-only"
                else:
                    stats["de_only"] += 1
                    link["kind"] = "de-only"
            result["scenes"].append({
                "act": a_en["n"], "scene": s_en["n"],
                "en_head": s_en["head"], "de_head": s_de["head"],
                "links": links,
            })

    (BUILD / "align.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")

    total = stats["1:1"] + stats["n:m"] + stats["en_only"] + stats["de_only"]
    print(f"links={total}  1:1={stats['1:1']}  n:m={stats['n:m']}  "
          f"only-EN={stats['en_only']}  only-DE={stats['de_only']}")
    print(f"speaker clashes in 1:1 links: {stats['speaker_clash']}")
    print(f"verse/prose: agree={stats['form_agree']} clash={stats['form_clash']} "
          f"({stats['form_agree'] / max(1, stats['form_agree'] + stats['form_clash']):.1%})")
    for c in clashes[:20]:
        print("  clash:", c)


if __name__ == "__main__":
    main()
