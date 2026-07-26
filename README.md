# Othello — zweisprachige kommentierte Ausgabe

Shakespeares *Othello* englisch und deutsch nebeneinander, sprechaktweise
verknüpft, deutsch kommentiert, als gültiges TEI P5.

### → **[Ausgabe lesen: ottosmops.github.io/othello](https://ottosmops.github.io/othello/)**

| | |
|---|---|
| Englisch | Project Gutenberg #1531 — Globe-Tradition, Mischtext aus Quarto 1622 und First Folio 1623 |
| Deutsch | Wolf Heinrich Graf Baudissin 1832, über DraCor/TextGrid (CC0) |
| Umfang | 2 354 Sprechakte, 5 889 Verszeilen, 696 Prosaabschnitte, 413 Regieanweisungen |
| Verknüpfungen | 1 183 — davon 1 168 Parallelstellen und 15 verzeichnete Abweichungen |
| Kommentar | 124 Anmerkungen, jede mit Beleg — darunter ein Editionsbericht |
| Konkordanz | 12 Wortfelder, 1 475 Belege; für 4 Felder ist geprüft, auf wen sich jede Nennung bezieht |
| Validierung | wohlgeformt · gültig gegen `tei_all` (RELAX NG) · alle 2 610 Zeiger auflösbar |

Beide Textzeugen sind gemeinfrei. Herkunft, Rechtsstand und die geprüften
Alternativen stehen in **[QUELLEN.md](QUELLEN.md)**.

## Die Seiten

| | |
|---|---|
| [Start](https://ottosmops.github.io/othello/) | Übersicht und Kennzahlen |
| [Einleitung](https://ottosmops.github.io/othello/einleitung.html) | Überlieferung, Übersetzung, Stoff, Wirkungsgeschichte — und der Editionsbericht |
| [Ausgabe](https://ottosmops.github.io/othello/othello-bilingual.html) | der Paralleltext mit Kommentar |
| [Befunde](https://ottosmops.github.io/othello/befunde.html) | die Auszählungen, jeweils mit der Abfrage, die sie erzeugt |
| [Konkordanz](https://ottosmops.github.io/othello/konkordanz.html) | Wortfelder, jede Stelle in ihrer Zeile |
| [Quellen](https://ottosmops.github.io/othello/quellen.html) | Textzeugen, Literatur — und was verworfen wurde, mit Begründung |

**Lesen ohne Störung.** Eine Anmerkung erscheint nur als laufende Nummer
(`[1]`, `[2]`, …) am Zeilenrand und öffnet sich als Karte über dem Text.
Umschaltbar: Anmerkungen ganz aus, Anmerkungen im Fließtext, Zeilennummern ein.
Fachbegriffe wie Q1 oder Blankvers erklären sich, sobald die Maus darauf ruht.

## Was daran belegt ist

Der Kommentar ist **kein Nachdruck einer vorhandenen Ausgabe, sondern für diese
Zusammenstellung verfasst — maschinell, von einem Sprachmodell**. Deshalb trägt
jede Anmerkung eine Belegart:

| Belegart | Anzahl | Was das heißt |
|---|---|---|
| `textzeuge` | 70 | am Wortlaut beider Fassungen ablesbar; jedes Zitat maschinell geprüft |
| `auszählung` | 28 | am Text dieser Ausgabe erhoben, mit reproduzierbarer Abfrage |
| `literatur` | 25 | aus der Literatur, im Volltext nachgeschlagen — oder ausdrücklich als *nicht nachgeprüft* gekennzeichnet |
| `werkstatt` | 1 | aus der Arbeit an dieser Ausgabe selbst — der Editionsbericht |

`src/check_notes.py` besteht auf dem Feld und prüft, dass jedes Zitat in der
Fassung vorkommt, der es zugeschrieben wird. Ein falsch erinnertes Zitat bricht
den Bau. Die philologischen Urteile sind damit **nicht** abgesichert — sie
gehören geprüft, bevor jemand sie zitiert.

Zitiert werden drei gemeinfreie Klassiker, deren Volltexte geladen und deren
Stellen im Wortlaut nachgeschlagen wurden: **Coleridge**, *Literary Remains* II
(1836), **Hazlitt**, *Characters of Shakespear's Plays* (1817), **Bradley**,
*Shakespearean Tragedy* (1904).

## Die 15 Abweichungen

Kein Fehler des Alignments, sondern der interessanteste Ertrag:

| `@type` | Anzahl | |
|---|---|---|
| `parallel` | 1 168 | Sprechakt zu Sprechakt |
| `en-only` | 11 | nur englisch — u. a. die sechs Zoten des Narren in III,1, die Baudissin ausspart |
| `attribution` | 3 | abweichende Sprecherzuweisung, etwa die Q/F-Differenz in I,3 |
| `de-only` | 1 | nur deutsch |

Jede ist kommentiert.

## Aufbau der TEI-Datei

```
TEI
├── teiHeader        zwei Zeugen mit Lizenz und Provenienz, Editionsgrundsätze,
│                    Alignment-Verfahren, Figurenverzeichnis beider Fassungen
└── text
    ├── front        die Texte zum Stück als ganzes
    └── group
        ├── text @xml:id="text-en"   englischer Zeuge
        └── text @xml:id="text-de"   deutscher Zeuge (mit pb der Aufbau-Ausgabe)
standOff
├── linkGrp          Sprechakt-Alignment, typisiert
├── listAnnotation   Stellenkommentar, je Anmerkung mit note[@type="beleg"]
├── listBibl         Belegstellen, durchnummeriert
└── list @type=gloss die erklärten Fachbegriffe
```

Jeder Sprechakt trägt eine `xml:id` (`en-3.3.70`), jede Zeile einen Anker
(`#l-en-3.3.304`). Darauf zeigen Verknüpfungen, Kommentar und Konkordanz — die
beiden Texte selbst bleiben unangetastet und für sich lesbar.

## Neu bauen

```sh
make            # alles: einlesen, alignieren, prüfen, TEI bauen, validieren, Seiten
make check      # nur die Prüfungen
make schema     # TEI-Schema für die Validierung laden
```

Voraussetzungen: Python 3.10+ (nur Standardbibliothek). Für die
Schemavalidierung zusätzlich `jing` (`brew install jing`); fehlt es, überspringt
`validate.py` diesen Schritt und prüft den Rest.

## Werkstatt

| Datei | Inhalt |
|---|---|
| `othello-bilingual.tei.xml` | die Ausgabe |
| `data/notes.json` | der Kommentar als eigene Datenschicht |
| `data/bibliographie.json` | die Belegstellen, nummeriert |
| `data/glossar.json` | die erklärten Fachbegriffe |
| `data/bezuege.json` | wem eine Nennung gilt — 280 Einträge für 297 Belege, einzeln gelesen |
| `src/observe.py` | Befunde am Text: `ratio`, `word`, `rhyme`, `form`, `share`, `stage`, `songs` |
| `src/concordance.py` | Wortfelder → Konkordanzseiten |

**Anmerkung hinzufügen** — Eintrag in `data/notes.json`, dann `make`:

```json
{"id": "3.3-beispiel", "act": 3, "scene": 3, "type": "translation",
 "find": "Zeichenkette aus dem englischen Text",
 "lemma_en": "Stichwort englisch", "lemma_de": "Stichwort deutsch",
 "note": "Kommentartext.",
 "belegart": "textzeuge",
 "beleg": "Beide Fassungen an der bezeichneten Stelle; Zitate maschinell geprüft."}
```

`find` muss in der Szene eindeutig sein, die Lemmata müssen im verknüpften
Sprechakt vorkommen. Kategorien: `textual`, `translation`, `realia`, `rhetoric`,
`dramaturgy`, `reception`, `source`, `edition`.

## Editorische Entscheidungen

**Kein Eingriff in den Wortlaut.** Beide Zeugen stehen unverändert. Für das
Alignment werden Apostroph, Anführung, Gedankenstrich und ß normalisiert — nur
intern, nicht im Text.

**Auszeichnung statt Klartext.** Die Konventionen des Gutenberg-Textes sind
aufgelöst: Regieanweisungen in eckigen Klammern werden zu `<stage>`, auch mitten
in der Verszeile, die Unterstriche der Lieder zu `@rend="italic"`. Es handelt
sich dabei nicht um Markdown, sondern um die Kursivkonvention von Project
Gutenberg.

**Alignment.** Szenenweise Needleman-Wunsch über die Sprecherfolge, mit der
relativen Redelänge als Tiebreak. Beide Zeugen teilen die Akt- und
Szenengliederung, was das Problem auf je eine Szene begrenzt.

**Vers und Prosa.** Der deutsche Zeuge unterscheidet beides, der englische
nicht; dort ist es aus dem Zeilenmaß erschlossen (Prosa auf ~70 Zeichen
umbrochen, Vers unter 58). 129 Redegruppen (10,5 %) beruhen auf einer
Kontextregel und sind mit `cert="low"` markiert. Der unabhängige Abgleich mit
dem deutschen Zeugen bestätigt die Zuordnung in 96 % der Fälle.

**Bezug der Nennungen.** Für vier Wortfelder wurde jede Stelle einzeln gelesen
und festgehalten, wem das Wort gilt (`data/bezuege.json`) — eine
Lektüreentscheidung, in der Anzeige als solche gekennzeichnet (»über: Jago«).
Daneben erkennt das Skript Figurennamen, die in der Zeile selbst stehen; das
erscheint schwächer als »nennt: …« und ist reine Zeichenkettensuche.

## Wie diese Ausgabe entstand

Der Editionsbericht steht in der
[Einleitung](https://ottosmops.github.io/othello/einleitung.html#note-play-entstehung):
was die Vorgabe »nur gemeinfreie Quellen« für die Textwahl bedeutete, wie das
Alignment arbeitet, woran die Prüfschicht beim ersten Durchlauf anschlug — sie
beanstandete dreißig von sechzig Anmerkungen, durchweg deutsche Wortlaute aus
der Erinnerung statt aus dem Text — und was auch nach allen Prüfungen
ungesichert bleibt.

## Grenzen

- Die philologischen Urteile des Kommentars sind maschinell und ungeprüft.
- Die Vers/Prosa-Zuordnung des englischen Zeugen ist erschlossen, nicht
  überliefert.
- Die Verknüpfung reicht bis zum Sprechakt, nicht bis zur Verszeile; Baudissin
  verschiebt Zeilengrenzen regelmäßig.
- Die Bezugsschicht deckt vier der zwölf Wortfelder ab.
- Zwei Zurufe aus dem Off (II,1) sind englisch Rede, deutsch Regieanweisung.

## Naheliegende Erweiterungen

**Dritte Kolumne:** Wielands Prosaübersetzung von 1766 liegt auf Wikisource
vollständig transkribiert vor. **Textkritischer Apparat:** Mit den
ISE-Transkriptionen von Q1 und F1 ließen sich die Varianten als `<app>/<rdg>` in
den englischen Text ziehen. **Deutsche Rezeption:** Schlegels *Vorlesungen über
dramatische Kunst und Litteratur* (1809–11) — bisher nur als Fraktur-Scan mit
unzuverlässiger Texterkennung.

## Lizenz

Beide Textzeugen sind gemeinfrei. Kodierung, Alignment, Kommentar und Skripte
stehen unter [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/).
