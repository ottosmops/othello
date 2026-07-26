#!/usr/bin/env python3
"""Concordance of the English text, arranged by semantic field.

One index page and one page per field. Every occurrence is shown in the line it
stands in — the verse line as the source sets it, with the line before and after
for context, its number within the scene, the speaker and a link into the
parallel reading view. Nothing is truncated: a field page lists all its places.

The German figures on each page are indicative, not equivalences: they count
word forms in the aligned speech, which need not translate the English word —
Baudissin's »treu« renders both *honest* and *true*. What is exact is the
English side and the reference.

    python3 src/concordance.py   → konkordanz.html, konkordanz-<feld>.html,
                                   build/konkordanz.json
"""

from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lookup import load, plain, speeches  # noqa: E402
from page import page  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
OUT_JSON = BUILD / "konkordanz.json"
OUT_INDEX = ROOT / "konkordanz.html"
BEZUEGE = ROOT / "data" / "bezuege.json"

# Namen, die im englischen Text als Figurenbezeichnung vorkommen. Nur diese
# werden automatisch erkannt; alles andere bleibt ohne Angabe.
NAMEN = {
    "othello": ["Othello"], "iago": ["Iago"], "desdemona": ["Desdemona"],
    "cassio": ["Cassio"], "emilia": ["Emilia"], "roderigo": ["Roderigo"],
    "brabantio": ["Brabantio"], "lodovico": ["Lodovico"], "montano": ["Montano"],
    "bianca": ["Bianca"], "gratiano": ["Gratiano"],
}

FIELDS = [
 {"id": "farbe", "titel": "Farbe, Licht, Dunkel",
  "einleitung": "Das Wortfeld, mit dem die erste Szene über Othello spricht, "
                "bevor er auftritt — und mit dem er in III,3 über sich selbst "
                "spricht. »Fair« ist dabei dreideutig: hell, schön, gerecht.",
  "en": ["black", "fair", "white", "dark", "light", "night"],
  "de": ["schwarz", "weiß", "hell", "dunkel", "Licht", "Nacht", "schön"]},

 {"id": "ehre", "titel": "Ehre, Redlichkeit, Name",
  "einleitung": "»Honest« ist das Leitwort des Stücks und trifft fast immer "
                "Jago. Das Wort deckt Aufrichtigkeit, Standesehre und, bei "
                "Frauen, Keuschheit ab — im Deutschen braucht es dafür ein "
                "halbes Dutzend Wörter.",
  "en": ["honest", "honour", "honor", "reputation", "name", "virtue"],
  "de": ["ehrlich", "redlich", "treu", "brav", "bieder", "Ehre", "Name", "Tugend"]},

 {"id": "teufel", "titel": "Teufel, Hölle, Himmel",
  "einleitung": "Die religiöse Schicht des Stücks. Bemerkenswert ist das "
                "Verhältnis von »heaven« zu »God«: Der Folio-Druck ersetzt "
                "Gottesnamen, Baudissin macht das rückgängig.",
  "en": ["devil", "hell", "heaven", "damn", "soul", "God", "angel", "sin"],
  "de": ["Teufel", "Höll", "Himmel", "verdamm", "Seele", "Gott", "Engel", "Sünde"]},

 {"id": "sehen", "titel": "Sehen, Zeugnis, Beweis",
  "einleitung": "Othello verlangt den »ocular proof«, und die ganze Intrige "
                "besteht darin, ihm etwas zu zeigen. Das Feld verbindet "
                "Wahrnehmung mit Beweisrecht.",
  "en": ["see", "eye", "proof", "prove", "witness", "ocular", "sight", "show"],
  "de": ["sehn", "sehen", "Auge", "Beweis", "beweis", "Zeug", "zeigen", "Anblick"]},

 {"id": "tier", "titel": "Tier, Jagd, Ungeheuer",
  "einleitung": "Jago beschreibt Menschen als Tiere, Othello übernimmt es. "
                "Dazu die Beizjagd (haggard, jesses) und das »monster«, für "
                "das Baudissin drei verschiedene Wörter braucht.",
  "en": ["beast", "monster", "toad", "goat", "ape", "wolf", "dog", "horse",
         "raven", "fly", "haggard"],
  "de": ["Vieh", "Untier", "Scheusal", "Ungeheu", "Kröte", "Ziege", "Affe",
         "Wolf", "Hund", "Roß", "Rabe", "Fliege", "Falk"]},

 {"id": "eifersucht", "titel": "Eifersucht, Verdacht, Betrug",
  "einleitung": "Der Kern der Handlung, sprachlich: vom Verdacht über das "
                "Hörnermotiv bis zum Betrug. »Cuckold« hat im Deutschen keine "
                "geläufige Entsprechung — »Hahnrei« kommt bei Baudissin nicht vor.",
  "en": ["jealous", "jealousy", "suspect", "suspicion", "cuckold", "horn",
         "false", "deceive", "abuse"],
  "de": ["Eifersucht", "eifersücht", "Argwohn", "argwöhn", "Hörner", "gehörnt",
         "falsch", "trüg", "betrüg"]},

 {"id": "zauber", "titel": "Zauber, Gift, Krankheit",
  "einleitung": "Brabantios Anklage lautet auf Zauberei; Jago beschreibt seine "
                "Arbeit als Vergiftung. Beide Register bleiben bis zum Schluss "
                "in Gebrauch.",
  "en": ["witch", "charm", "magic", "spell", "poison", "medicine", "drug",
         "plague", "sick"],
  "de": ["Hexe", "Zauber", "Bann", "Gift", "Arznei", "Trank", "Pest", "krank"]},

 {"id": "handel", "titel": "Handel, Geld, Besitz",
  "einleitung": "Jago rechnet, Rodrigo zahlt, Othello spricht von seiner Ehe "
                "als Kauf. Die Kaufmannssprache ist in diesem venezianischen "
                "Stück nie weit.",
  "en": ["money", "purse", "gold", "jewel", "price", "purchase", "profit",
         "thief", "steal", "rob"],
  "de": ["Geld", "Beutel", "Gold", "Kleinod", "Preis", "Handel", "Gewinn",
         "Dieb", "stehl", "raub"]},

 {"id": "fremde", "titel": "Fremde: Mohr, Türke, Venedig",
  "einleitung": "Die geographische und ethnische Verortung des Stücks — und "
                "die Wörter, mit denen Zugehörigkeit zu- und abgesprochen wird.",
  "en": ["Moor", "Turk", "Ottomite", "Venice", "Venetian", "Cyprus", "stranger",
         "barbarian", "Barbary"],
  "de": ["Mohr", "Türk", "Venedig", "Venetian", "Cypern", "Cyper", "Fremd",
         "Afrikaner", "Barber"]},

 {"id": "frau", "titel": "Frau, Ehe, Unzucht",
  "einleitung": "Von »wife« bis »strumpet«. Die härtesten Wörter des Stücks "
                "stehen im vierten Akt; Baudissin dämpft sie durchweg um eine "
                "Stufe.",
  "en": ["wife", "woman", "maid", "whore", "strumpet", "bawd", "chaste",
         "husband", "marry", "marriage"],
  "de": ["Weib", "Frau", "Gattin", "Mädchen", "Metze", "Dirne", "Hure",
         "Buhler", "Kupplerin", "keusch", "Gatte", "Ehe"]},

 {"id": "krieg", "titel": "Krieg, Dienst, Rang",
  "einleitung": "Othellos Welt vor dem Stück und die Ämter, um die Jago "
                "intrigiert: Leutnant gegen Fähnrich.",
  "en": ["war", "soldier", "captain", "lieutenant", "ancient", "general",
         "service", "sword", "arms"],
  "de": ["Krieg", "Soldat", "Hauptmann", "Leutnant", "Fähndrich", "General",
         "Dienst", "Schwert", "Degen", "Waffen"]},

 {"id": "reden", "titel": "Reden, Schweigen, Wissen",
  "einleitung": "Wer spricht, wer schweigt, wer weiß: das Feld, in dem die "
                "Tragödie sich entscheidet — bis zu Jagos letzter Weigerung.",
  "en": ["speak", "word", "tongue", "silence", "know", "think", "believe",
         "swear", "confess"],
  "de": ["sprech", "sprich", "Wort", "Zunge", "schweig", "still", "wiss",
         "weiß", "denk", "glaub", "schwör", "gesteh"]},
]


def scene_lines(scene: dict) -> list[dict]:
    """Every line of a scene, numbered as the TEI numbers them."""
    out = []
    n = 0
    for c in scene["content"]:
        if c["type"] != "sp":
            continue
        for g in c["content"]:
            if g["type"] not in ("verse", "prose"):
                continue
            for i, line in enumerate(g["lines"]):
                n += 1
                out.append({
                    "n": n,
                    "text": line.get("text", ""),
                    "sprecher": c["speaker"].rstrip("."),
                    "who": c["who"],
                    "form": g["type"],
                    "erste": i == 0,
                    "sp_index": None,  # wird unten gesetzt
                    "sp": c,
                })
    return out


def build() -> dict:
    en, de, al = load()

    # Sprechakt → laufende Nummer in der Szene, für die Verweise ins Lesebild
    sp_number: dict[int, int] = {}
    for act in en["acts"]:
        for scene in act["scenes"]:
            k = 0
            for c in scene["content"]:
                if c["type"] == "sp":
                    k += 1
                    sp_number[id(c)] = k

    # Alle Zeilen mit ihrem Kontext, nach Szene
    zeilen = []
    for act in en["acts"]:
        for scene in act["scenes"]:
            lines = scene_lines(scene)
            for i, line in enumerate(lines):
                line["akt"] = act["n"]
                line["szene"] = scene["n"]
                line["vorher"] = lines[i - 1]["text"] if i else ""
                line["nachher"] = lines[i + 1]["text"] if i + 1 < len(lines) else ""
                line["anker"] = f"en-{act['n']}.{scene['n']}.{sp_number[id(line['sp'])]}"
                zeilen.append(line)

    bez = json.loads(BEZUEGE.read_text(encoding="utf-8"))
    anzeige = bez["anzeige"]
    geprueft = bez["bezuege"]

    result = {"felder": [], "anzeige": anzeige}
    for field in FIELDS:
        by_word: dict[str, list] = {w: [] for w in field["en"]}
        for line in zeilen:
            for word in field["en"]:
                for m in re.finditer(rf"\b{word}\w*\b", line["text"], re.I):
                    # Schlüssel über die belegte Wortform, nicht das Suchwort:
                    # »honesty« steht unter honesty, nicht unter honest.
                    schluessel = (f"{line['akt']}.{line['szene']}.{line['n']}."
                                  f"{m.group(0).lower()}")
                    eintrag = geprueft.get(schluessel)
                    genannt = [wer for wer, formen in NAMEN.items()
                               if any(re.search(rf"\b{f}\b", line["text"]) for f in formen)]
                    by_word[word].append({
                        "form": m.group(0),
                        "bezug": eintrag,
                        "genannt": genannt,
                        "akt": line["akt"], "szene": line["szene"], "zeile": line["n"],
                        "sprecher": line["sprecher"], "form_art": line["form"],
                        "vorher": line["vorher"], "nachher": line["nachher"],
                        "links": line["text"][:m.start()],
                        "treffer": m.group(0),
                        "rechts": line["text"][m.end():],
                        "anker": line["anker"],
                    })

        de_counts: dict[str, int] = {w: 0 for w in field["de"]}
        for sc in al["scenes"]:
            D = speeches(de, sc["act"], sc["scene"])
            for link in sc["links"]:
                de_text = " ".join(plain(D[i]) for i in link["de"])
                for word in field["de"]:
                    de_counts[word] += len(re.findall(rf"\b{word}\w*", de_text))

        result["felder"].append({
            "id": field["id"], "titel": field["titel"],
            "einleitung": field["einleitung"],
            "gesamt": sum(len(v) for v in by_word.values()),
            "woerter": [{"wort": w, "anzahl": len(by_word[w]), "belege": by_word[w]}
                        for w in field["en"]],
            "deutsch": [{"wort": w, "anzahl": n} for w, n in de_counts.items()],
        })
    return result


CSS = """
.felder { display: grid; grid-template-columns: repeat(auto-fill, minmax(15rem, 1fr));
          gap: 1rem; margin: 1.6rem 0; }
.felder a { display: block; padding: .9rem 1rem; border: 1px solid var(--rule);
            border-radius: 4px; text-decoration: none; color: inherit;
            background: var(--note-bg); }
.felder a:hover { border-color: var(--accent); }
.felder .t { font-weight: 600; color: var(--accent); }
.felder .z { font-size: .78rem; color: var(--muted);
             font-family: system-ui, sans-serif; }
.felder .w { font-size: .78rem; color: var(--muted); margin-top: .3rem; }

section.wort { margin: 2.2rem 0; padding-top: 1rem; border-top: 1px solid var(--rule); }
section.wort h2 { font-size: 1rem; margin: 0 0 .8rem; }
section.wort h2 span { color: var(--muted); font-weight: 400; font-size: .82rem;
                       font-family: system-ui, sans-serif; }
.stelle { margin: 0 0 .9rem; padding-left: 5.6rem; position: relative;
          max-width: 52em; }
.stelle .ref { position: absolute; left: 0; top: .1rem; width: 5.2rem;
               font-size: .7rem; font-family: system-ui, sans-serif;
               color: var(--muted); line-height: 1.4; }
.stelle .ref a { text-decoration: none; }
.stelle .ref b { display: block; font-weight: 600; color: var(--fg); }
.stelle .ctx { color: var(--muted); font-size: .86em; }
.stelle .zeile { margin: .05rem 0; }
.stelle em { font-style: normal; font-weight: 600; color: var(--accent); }
.stelle .prosa { font-size: .95em; }
.bezug { display: inline-block; margin-top: .2rem; font-size: .7rem;
         font-family: system-ui, sans-serif; padding: .05rem .5rem;
         border-radius: 999px; border: 1px solid var(--rule); color: var(--muted); }
.bezug.geprueft { border-color: var(--accent); color: var(--accent); }
.bezug.auto { font-style: italic; }
.zahlen { font-size: .8rem; color: var(--muted); font-family: system-ui, sans-serif;
          background: var(--note-bg); padding: .7rem .9rem; border-radius: 4px;
          margin: 1.2rem 0; }
.zahlen b { color: var(--fg); font-weight: 600; }
.zurueck { font-size: .8rem; font-family: system-ui, sans-serif; margin: 1.2rem 0; }
@media (max-width: 700px) {
  .stelle { padding-left: 0; }
  .stelle .ref { position: static; width: auto; margin-bottom: .2rem; }
  .stelle .ref b { display: inline; }
}
"""

HINWEIS = (
    '<div class="hinweis"><b>Wie diese Zahlen entstehen.</b> Gezählt wird am '
    'englischen Text dieser Ausgabe, mit einem Wortgrenzen-Muster je Stichwort '
    '(<code>\\bhonest\\w*\\b</code>): Es werden also auch Ableitungen erfasst — '
    '<i>honesty</i> unter <i>honest</i>, <i>seeing</i> unter <i>see</i>. '
    'Jede Stelle steht in ihrer Zeile, wie die Quelle sie setzt, mit der Zeile '
    'davor und danach; die Zeilennummer zählt innerhalb der Szene. Die deutsche '
    'Spalte zählt Wortformen in der <i>verknüpften</i> Rede — sie zeigt, was in '
    'der Nachbarschaft steht, nicht was das englische Wort übersetzt. '
    'Baudissins »treu« etwa gibt sowohl <i>honest</i> als auch <i>true</i> '
    'wieder. Verlässlich ist die englische Seite samt Stellenangabe; die '
    'deutsche ist ein Fingerzeig.</div>')


def bezug_html(e: dict, anzeige: dict[str, str]) -> str:
    """Auf wen sich die Nennung bezieht — geprüft oder, schwächer, mitgenannt."""
    eintrag = e.get("bezug")
    if eintrag:
        name = anzeige.get(eintrag["wer"], eintrag["wer"])
        selbst = " (über sich)" if eintrag.get("selbst") else ""
        titel = eintrag.get("hinweis", "")
        attr = f' title="{html.escape(titel)}"' if titel else ""
        return (f'<span class="bezug geprueft"{attr}>über: '
                f'{html.escape(name)}{selbst}</span>')
    genannt = [anzeige.get(w, w) for w in e.get("genannt", [])]
    if genannt:
        return ('<span class="bezug auto" title="in der Zeile genannt; '
                'maschinell erkannt, keine Deutung">nennt: '
                + html.escape(", ".join(genannt)) + "</span>")
    return ""


def stelle_html(e: dict, anzeige: dict[str, str] | None = None) -> str:
    cls = " prosa" if e["form_art"] == "prose" else ""
    ctx_before = (f'<div class="zeile ctx">{html.escape(e["vorher"])}</div>'
                  if e["vorher"] else "")
    ctx_after = (f'<div class="zeile ctx">{html.escape(e["nachher"])}</div>'
                 if e["nachher"] else "")
    return (f'<div class="stelle{cls}">'
            f'<span class="ref"><a href="othello-bilingual.html'
            f'#l-en-{e["akt"]}.{e["szene"]}.{e["zeile"]}">'
            f'<b>{e["akt"]},{e["szene"]}</b>Z. {e["zeile"]}<br>'
            f'{html.escape(e["sprecher"])}</a></span>'
            f'{ctx_before}'
            f'<div class="zeile">{html.escape(e["links"])}'
            f'<em>{html.escape(e["treffer"])}</em>{html.escape(e["rechts"])}</div>'
            f'{ctx_after}{bezug_html(e, anzeige or {})}</div>')


def render_field(field: dict, anzeige: dict[str, str]) -> str:
    de_line = " · ".join(f'<b>{html.escape(w["wort"])}</b> {w["anzahl"]}'
                         for w in field["deutsch"] if w["anzahl"])
    head = f"""<header class="title">
  <h1>{html.escape(field["titel"])}</h1>
  <p class="sub">{html.escape(field["einleitung"])}</p>
</header>"""
    sections = []
    for word in field["woerter"]:
        if not word["anzahl"]:
            continue
        sections.append(
            f'<section class="wort" id="w-{word["wort"]}">'
            f'<h2>{html.escape(word["wort"])} <span>· {word["anzahl"]} Belege, '
            f'alle aufgeführt</span></h2>'
            + "".join(stelle_html(e, anzeige) for e in word["belege"]) + "</section>")
    ohne = [w["wort"] for w in field["woerter"] if not w["anzahl"]]
    fehlt = (f'<p class="zurueck">Ohne Beleg in diesem Text: '
             f'{", ".join(html.escape(w) for w in ohne)}.</p>' if ohne else "")
    zaehler: dict[str, int] = {}
    for word in field["woerter"]:
        for e in word["belege"]:
            if e.get("bezug"):
                zaehler[e["bezug"]["wer"]] = zaehler.get(e["bezug"]["wer"], 0) + 1
    bezug_zeile = ""
    if zaehler:
        liste = " · ".join(
            f'<b>{html.escape(anzeige.get(w, w))}</b> {n}'
            for w, n in sorted(zaehler.items(), key=lambda x: -x[1]))
        bezug_zeile = (f'<div class="zahlen">Geprüfter Bezug — auf wen sich die '
                       f'Nennungen richten: {liste}</div>')

    body = (f'<p class="zurueck"><a href="konkordanz.html">← alle Wortfelder</a></p>'
            f'<div class="zahlen">Englisch: {field["gesamt"]} Belege · '
            f'Deutsch in den verknüpften Reden: {de_line or "—"}</div>'
            f"{bezug_zeile}{fehlt}{''.join(sections)}")
    footer = ('Erzeugt mit <code>src/concordance.py</code>. Die Zeilennummer zählt '
              'innerhalb der Szene und entspricht <code>l/@n</code> in der '
              'TEI-Datei. Alle Belege auch in <code>build/konkordanz.json</code>.')
    return page(f"Othello — Konkordanz: {field['titel']}", "konkordanz.html",
                head, body, CSS, "", footer)


def render_index(data: dict) -> str:
    head = """<header class="title">
  <h1>Konkordanz</h1>
  <p class="sub">Zentrale Wortfelder des englischen Textes — jede Stelle in ihrer
     Zeile, mit Verweis in den Paralleltext</p>
</header>"""
    total = sum(f["gesamt"] for f in data["felder"])
    karten = "".join(
        f'<a href="konkordanz-{f["id"]}.html">'
        f'<span class="t">{html.escape(f["titel"])}</span> '
        f'<span class="z">{f["gesamt"]} Belege</span>'
        f'<div class="w">{", ".join(html.escape(w["wort"]) for w in f["woerter"] if w["anzahl"])}</div>'
        f"</a>" for f in data["felder"])
    body = (HINWEIS
            + f'<p>{len(data["felder"])} Wortfelder, {total} Belege. '
              f'Jedes Feld hat seine eigene Seite; dort stehen alle Stellen, '
              f'nichts ist gekürzt.</p>'
            + f'<div class="felder">{karten}</div>')
    footer = ('Erzeugt mit <code>src/concordance.py</code> aus den beiden '
              'Textzeugen dieser Ausgabe; vollständige Daten in '
              '<code>build/konkordanz.json</code>.')
    return page("Othello — Konkordanz", "konkordanz.html", head, body, CSS, "", footer)


def main() -> None:
    data = build()
    BUILD.mkdir(exist_ok=True)
    OUT_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=1),
                        encoding="utf-8")
    OUT_INDEX.write_text(render_index(data), encoding="utf-8")
    for field in data["felder"]:
        (ROOT / f"konkordanz-{field['id']}.html").write_text(
            render_field(field, data["anzeige"]), encoding="utf-8")
    total = sum(f["gesamt"] for f in data["felder"])
    print(f"konkordanz.html + {len(data['felder'])} Unterseiten, {total} Belege")


if __name__ == "__main__":
    main()
