# Othello — zweisprachige kommentierte TEI-Ausgabe

Shakespeares *Othello* englisch und deutsch nebeneinander, sprechaktweise
verknüpft, mit deutschem Stellenkommentar, als gültiges TEI P5.

Beide Textzeugen sind gemeinfrei; Herkunft, Rechtsstand und die geprüften
Alternativen stehen in **[QUELLEN.md](QUELLEN.md)**.

| | |
|---|---|
| Englisch | Project Gutenberg #1531 (Globe-/Moby-Tradition, Mischtext Q1 1622 / F1 1623) |
| Deutsch | Wolf Heinrich Graf Baudissin 1832, über DraCor/TextGrid (CC0) |
| Umfang | 2 354 Sprechakte, 5 889 Verszeilen, 701 Prosaabschnitte, 413 Regieanweisungen |
| Verknüpfungen | 1 183 — davon 1 168 Parallelstellen und 15 verzeichnete Abweichungen |
| Kommentar | 121 Anmerkungen (106 Stellen, 9 Einleitung, 6 Befunde), deutsch, auf beide Zeugen bezogen |
| Belege | jede Anmerkung mit Belegart: 70 am Wortlaut, 26 ausgezählt, 25 aus Literatur |
| Konkordanz | 12 Wortfelder, 1 475 Belege des englischen Textes mit Stellenangabe |
| Validierung | wohlgeformt · gültig gegen `tei_all` (RELAX NG) · alle Zeiger auflösbar |

## Ergebnisdateien

| Datei | Inhalt |
|---|---|
| `othello-bilingual.tei.xml` | die Ausgabe (1,1 MB, TEI P5) |
| `othello-bilingual.html` | Leseansicht, zweispaltig, aus der TEI-Datei erzeugt |
| `einleitung.html` | die neun Texte zum Stück: Überlieferung, Übersetzung, Stoff, Rezeption |
| `befunde.html` | die Auszählungen: Redeanteile, Vers/Prosa, Verknüpfung, Szenenumfang |
| `konkordanz.html` + 12 Unterseiten | Wortfelder des englischen Textes, 1 475 Belege in ihrer Zeile |
| `quellen.html` | Quellenverzeichnis, auch das Verworfene mit Begründung |
| `QUELLEN.md` | dieselbe Liste ausführlich, mit allen Erwägungen |
| `data/notes.json` | der Kommentar als eigene Datenschicht |
| `data/bibliographie.json` | die Belegstellen des Kommentars |
| `data/glossar.json` | die im Kommentar erklärten Fachbegriffe |
| `data/bezuege.json` | wem im Ehre-Feld das Wort jeweils gilt, Stelle für Stelle gelesen |

Die vier Seiten sind in sich geschlossene HTML-Dateien ohne externe
Abhängigkeiten — einfach im Browser öffnen; sie verlinken einander.

**Der Kommentar stört das Lesen nicht.** Eine Anmerkung erscheint nur als
laufende Nummer — `[1]`, `[2]`, … — am Zeilenrand und öffnet sich als Karte
über dem Text, ohne den Satz zu verschieben. Die Nummern folgen der Reihenfolge
des Textes und stehen auch in der TEI-Datei (`annotation/@n`), sind also
zitierfähig. Zwei Schalter oben: *Anmerkungen* schaltet die Marken ganz ab,
*im Text statt als Marke* stellt sie für alle, die durchlesen wollen, doch in
den Fließtext. Die Einstellung bleibt über `localStorage` erhalten.

**Die Belegstellen sind nummeriert.** Die Bibliographie trägt `[1]`–`[14]`;
die Belegkarte einer Anmerkung zitiert mit diesen Nummern, die Seite *Quellen*
führt sie auf.

**Fachbegriffe erklären sich selbst.** Wörter wie Q1, Folio, Blankvers oder
Stichomythie sind im Kommentar unterstrichen; sobald die Maus darauf ruht — oder
der Tastaturfokus —, erscheint die Erklärung. Grundlage ist `data/glossar.json`;
im TEI stehen die Begriffe als `<term ref="#g-…">` und die Erklärungen als
`<list type="gloss">`.

**Jede Anmerkung nennt ihren Beleg.** Am Fuß der Karte steht, worauf sie beruht,
und bei Literaturangaben der Nachweis samt Link zum Volltext.

## Aufbau der TEI-Datei

```
TEI
├── teiHeader        zwei Zeugen mit Lizenz und Provenienz, Editionsgrundsätze,
│                    Alignment-Verfahren, Figurenverzeichnis beider Fassungen
└── text
    ├── front        Einleitung: die Kommentare zum Stück als ganzes
    └── group
        ├── text @xml:id="text-en"   englischer Zeuge
        └── text @xml:id="text-de"   deutscher Zeuge (mit pb der Aufbau-Ausgabe)
standOff
├── linkGrp          Sprechakt-Alignment, typisiert
├── listAnnotation   Stellenkommentar, je Anmerkung mit note[@type="beleg"]
├── listBibl         Belegstellen des Kommentars
└── list @type=gloss die erklärten Fachbegriffe
```

Jeder Sprechakt trägt eine `xml:id` der Form `en-3.3.70` beziehungsweise
`de-3.3.70` (Zeuge, Akt, Szene, laufende Nummer). Darauf zeigen sowohl die
Verknüpfungen als auch der Kommentar — die beiden Texte selbst bleiben
unangetastet und für sich lesbar.

Die Verknüpfungen sind typisiert:

| `@type` | Anzahl | Bedeutung |
|---|---|---|
| `parallel` | 1 168 | Sprechakt zu Sprechakt |
| `attribution` | 3 | abweichende Sprecherzuweisung |
| `en-only` | 11 | nur im englischen Zeugen |
| `de-only` | 1 | nur im deutschen Zeugen |

Diese 15 Abweichungen sind keine Fehler des Alignments, sondern das
interessanteste Ergebnis: die im Deutschen ausgelassenen Zoten des Narren
(III,1), die Q/F-Differenz beim Auftritt Desdemonas vor dem Senat (I,3), die
fehlende dritte Runde der »The handkerchief!«-Stichomythie (III,4). Jede ist
kommentiert.

## Neu bauen

```sh
make          # alles: einlesen, alignieren, prüfen, TEI bauen, validieren, HTML
make check    # nur die Prüfungen
```

Ohne `make`:

```sh
python3 src/observe.py       # Befunde am Text (Grundlage der Anmerkungen)
python3 src/parse_en.py      # PG-Plaintext  → build/en.json
python3 src/parse_de.py      # DraCor-TEI    → build/de.json
python3 src/align.py         # Alignment     → build/align.json
python3 src/check_notes.py   # jedes Zitat des Kommentars gegen beide Zeugen
python3 src/build_tei.py     # → othello-bilingual.tei.xml
python3 src/validate.py      # Wohlgeformtheit, TEI P5, Referenzintegrität
python3 src/render_html.py     # → othello-bilingual.html
python3 src/render_befunde.py  # → befunde.html
python3 src/render_quellen.py  # → quellen.html
python3 src/concordance.py     # → konkordanz.html, build/konkordanz.json
```

Voraussetzungen: Python 3.10+ (nur Standardbibliothek). Für die
Schemavalidierung zusätzlich `jing` (`brew install jing`) und das Schema:

```sh
curl -o build/tei_all.rng \
  https://www.tei-c.org/release/xml/tei/custom/schema/relaxng/tei_all.rng
```

Fehlt eines von beiden, überspringt `validate.py` diesen Schritt und prüft den
Rest.

## Editorische Entscheidungen

**Kein Eingriff in den Wortlaut.** Beide Zeugen stehen unverändert, mit ihrer
Orthographie und Interpunktion. Für das Alignment werden Apostroph,
Anführungszeichen, Gedankenstrich und ß normalisiert — nur intern, nicht im Text.

**Auszeichnung statt Klartext.** Die Konventionen des englischen
Gutenberg-Textes sind aufgelöst: Regieanweisungen in eckigen Klammern werden zu
`<stage>`, auch wenn sie mitten in der Verszeile stehen (»Good night to
everyone. `[_To Brabantio._]` And, noble signior«), und die Unterstriche, mit
denen die Transkription die Lieder kursiv setzt, werden zu `@rend="italic"`.
Im Text bleibt kein Auszeichnungszeichen der Quelle stehen — es handelt sich
dabei nicht um Markdown, sondern um die Kursivkonvention von Project
Gutenberg.

**Alignment.** Szenenweise Needleman-Wunsch über die Sprecherfolge, mit der
relativen Redelänge als Tiebreak; benachbarte Lücken desselben Sprechers werden
zu n:m-Verknüpfungen zusammengefasst. Beide Zeugen teilen die Akt- und
Szenengliederung (5 Akte, 15 Szenen), was das Problem auf je eine Szene
begrenzt.

**Vers und Prosa.** Der deutsche Zeuge unterscheidet beides in der Auszeichnung,
der englische nicht. Dort wurde die Unterscheidung aus dem Zeilenmaß der
Transkription erschlossen: Prosa ist auf rund 70 Zeichen umbrochen, Vers folgt
der metrischen Zeile und bleibt unter 58. Kurze Reden, bei denen die Typographie
nichts hergibt, erben die Form ihrer Umgebung; 129 Redegruppen (10,5 %) beruhen
auf dieser Kontextregel und sind mit `cert="low"` markiert. Der unabhängige
Abgleich mit dem deutschen Zeugen bestätigt die Zuordnung in 96 % der
verknüpften Sprechakte — die Heuristik ist also brauchbar, aber nicht mehr als
das, und sie ist im Header als solche deklariert.

**Kommentar.** Deutsch, bezogen auf beide Fassungen; als eigene Datenschicht in
`data/notes.json` gehalten und erst beim Bauen in die TEI-Datei eingesetzt. Jede
Anmerkung nennt ihr Stichwort in beiden Sprachen, und `check_notes.py` weist
nach, dass jedes Zitat in der Fassung, der es zugeschrieben wird, tatsächlich
vorkommt. Ein falsch erinnertes Zitat bricht den Bau.

**Belegpflicht.** Jede Anmerkung führt mit, worauf sie beruht — am Wortlaut
beider Zeugen ablesbar (`textzeuge`), an dieser Ausgabe ausgezählt
(`auszählung`, mit der reproduzierbaren Abfrage) oder aus der Literatur
(`literatur`, mit Verweis auf `data/bibliographie.json`). Wo eine Angabe aus
dem Fachwissen stammt und für diese Ausgabe **nicht** an einer Quelle geprüft
wurde, sagt das Belegfeld das ausdrücklich. `check_notes.py` besteht auf dem
Feld und prüft, dass jeder Literaturverweis existiert.

## Erweitern

**Anmerkung hinzufügen** — Eintrag in `data/notes.json`:

```json
{"id": "3.3-beispiel", "act": 3, "scene": 3, "type": "translation",
 "find": "Zeichenkette aus dem englischen Text",
 "lemma_en": "Stichwort englisch", "lemma_de": "Stichwort deutsch",
 "note": "Kommentartext.",
 "belegart": "textzeuge",
 "beleg": "Beide Fassungen an der bezeichneten Stelle; Zitate maschinell geprüft.",
 "refs": []}
```

`find` muss innerhalb der Szene eindeutig sein; `lemma_en`/`lemma_de` müssen im
verknüpften Sprechakt vorkommen. Danach `make`. Kategorien: `textual`,
`translation`, `realia`, `rhetoric`, `dramaturgy`, `reception`, `source`.
Belegarten: `textzeuge`, `auszählung`, `literatur`.

**Konkordanz.** `src/concordance.py` legt zwölf Wortfelder an und schreibt für
jedes eine eigene Seite. Jede Stelle steht dort in ihrer Zeile, wie die Quelle
sie setzt, mit der Zeile davor und danach, der Zeilennummer innerhalb der Szene
(dieselbe wie `l/@n` im TEI) und einem Sprung auf genau diese Zeile im
Paralleltext. Gekürzt wird nichts: Wer ein Feld öffnet, sieht alle Belege. Neue
Felder werden in der Liste `FIELDS` ergänzt.

**Auf wen sich eine Nennung bezieht.** Für das Feld »Ehre, Redlichkeit, Name«
wurde jede der 67 Stellen einzeln gelesen und festgehalten, wem das Wort gilt
(`data/bezuege.json`) — mit Begründung, wo sie nötig ist. Das Ergebnis steht auf
der Feldseite und ist der schlagendste Befund dieser Ausgabe: **Jago 25,
Othello 10, Desdemona 10, Cassio 9**, achtmal ohne Personenbezug. Diese
Zuordnung ist eine Lektüreentscheidung und als solche gekennzeichnet
(»über: Jago«). Daneben erkennt das Skript automatisch Figurennamen, die in der
Zeile selbst stehen; das erscheint schwächer als »nennt: …« und ist reine
Zeichenkettensuche, keine Deutung.

**Zeilennummern.** In der Leseansicht schaltbar (*Zeilennummern*); sie stehen
dann in der Marge, ohne den Zeilenfall zu ändern. Jede Zeile hat einen Anker der
Form `#l-en-1.3.304`, so dass Konkordanz und Zitate auf die Zeile verweisen
können — wer so einsteigt, bekommt die Nummern automatisch eingeblendet und die
Zeile hervorgehoben.

**Befunde suchen, bevor man schreibt.** `src/observe.py` liefert das Material,
aus dem sich belegbare Anmerkungen machen lassen: `ratio` zeigt, wo Baudissin am
stärksten kürzt, `word` die Vorkommen eines Leitworts samt deutscher
Entsprechungen, dazu `rhyme`, `form`, `share`, `stage`, `songs`.

**Dritte Kolumne.** Wielands Prosaübersetzung von 1766 liegt auf Wikisource
vollständig transkribiert vor (siehe QUELLEN.md, 2.2). Nötig wären ein
`parse_wieland.py` und eine Erweiterung des Alignments auf drei Zeugen —
`align.py` ist paarweise gebaut, ließe sich aber gegen den englischen Text als
Anker zweimal laufen lassen.

**Textkritischer Apparat.** Die Q1/F1-Varianten stehen derzeit nur im Kommentar.
Mit den ISE-Transkriptionen ließen sie sich als `<app>/<rdg>` in den englischen
Text einziehen.

## Sekundärliteratur

Der Kommentar zitiert drei gemeinfreie Klassiker der Shakespeare-Kritik, und
zwar nicht aus dem Gedächtnis: Die Volltexte wurden geladen und die Stellen im
Wortlaut nachgeschlagen.

- **Coleridge**, *Literary Remains* II (1836) — die Formel vom »motive-hunting
  of a motiveless malignity«, und der aufschlussreiche Einspruch gegen einen
  schwarzen Othello, verfasst im selben Jahrzehnt wie Baudissins Übersetzung.
- **Hazlitt**, *Characters of Shakespear's Plays* (1817) — die Figurenkontraste
  als »opposition of costume in a picture«, und die Lesart von »the pity of it«.
- **Bradley**, *Shakespearean Tragedy* (1904) — Othello als »most romantic
  figure«, Jago als der Empfindungslose, und die Herkunft der Lehre von der
  doppelten Zeitrechnung bei »Christopher North«.

Damit sind drei zuvor ungeprüfte Anmerkungen belegt. Als nächstes läge nahe:
Schlegels *Vorlesungen über dramatische Kunst und Litteratur* (1809–11) für die
deutsche Seite — sie liegen nur als Fraktur-Scan vor und bräuchten
Nachkorrektur.

## Grenzen

- Der Stellenkommentar ist maschinell verfasst. Zitate und Zahlen sind geprüft,
  die philologischen Urteile nicht — vor einer Veröffentlichung fachlich
  durchsehen (siehe QUELLEN.md, 5).
- Die Vers/Prosa-Zuordnung des englischen Zeugen ist erschlossen, nicht
  überliefert.
- Die Verknüpfung reicht bis zum Sprechakt, nicht bis zur Zeile. Für ein
  Alignment auf Verszeilenebene wäre eine andere Methode nötig; Baudissin
  verschiebt Zeilengrenzen regelmäßig.
- Zwei Zurufe aus dem Off (»A sail, a sail!«, II,1) sind im englischen Zeugen
  Rede, im deutschen Regieanweisung. Sie stehen deshalb als sprecherlose `<sp>`
  ohne deutsches Gegenstück.

## Lizenz

Beide Textzeugen sind gemeinfrei. Kodierung, Alignment, Kommentar und die
Skripte dieser Ausgabe stehen unter
[CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/).
