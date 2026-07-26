# Kommentierte Quellenliste

Alle Textzeugen dieser Ausgabe sind gemeinfrei. Die Liste verzeichnet, was
verwendet wurde, was geprüft und verworfen wurde, und worauf sich die
textkritischen Angaben des Kommentars stützen. Stand: 25. Juli 2026.

---

## 1. Verwendete Textzeugen

### 1.1 Englisch — Project Gutenberg #1531

> William Shakespeare: *Othello*. Transkribiert vom PG Shakespeare Team.
> Project Gutenberg, EBook #1531, freigegeben am 1. November 1998, zuletzt
> aktualisiert am 19. September 2025.
> <https://www.gutenberg.org/ebooks/1531>
> Lokal: `sources/pg1531_othello_en.txt` (182 kB, 6 666 Zeilen)

**Textgrundlage.** Elektronischer Text in der Nachfolge der Globe-Ausgabe
(Cambridge/Globe 1864) bzw. des daraus hervorgegangenen *Moby Shakespeare*.
Es handelt sich um einen **Mischtext** aus Quarto 1622 und First Folio 1623.
Das lässt sich am Text selbst nachweisen und wurde für diese Ausgabe geprüft:

| Stelle | Lesart im Text | Herkunft |
|---|---|---|
| I,1 »Tush, never tell me« | vorhanden | Q1 (F1 tilgt »Tush«) |
| I,1 »'Sblood, but you will not hear me« | vorhanden | Q1 (F1: »Why«) |
| III,3 »Like to the Pontic Sea« | vorhanden | nur F1 |
| IV,3 Weidenlied, vollständig | vorhanden | nur F1 |
| IV,3 Emilias Rede »Let husbands know« | vorhanden | nur F1 |
| V,2 »base Judean« | vorhanden | F1 (Q1: »base Indian«) |

**Rechtsstand.** Public domain in den USA. Die Transkription wurde von Project
Gutenberg gemeinfrei gestellt; die Lizenzklausel des Projekts betrifft die
Marke »Project Gutenberg«, nicht den Text. Für die Nutzung außerhalb der USA
gilt: Shakespeares Werk ist weltweit gemeinfrei.

**Qualität.** Sauber gesetzt, konsequente Sprecherlabels in Kapitälchen,
Regieanweisungen für Abgänge in Klammern (`[_Exit._]`), für Auftritte
unklammert (`Enter Roderigo and Iago.`). Zwei Sprecherlabels stehen ohne Punkt
(`SECOND SENATOR`, `OTHELLO`), ein Kollektivsprecher lautet
`DUKE and SENATORS.` — der Parser dieser Ausgabe behandelt alle drei Fälle
ausdrücklich. **Vers und Prosa sind nicht ausgezeichnet**; die Unterscheidung
musste erschlossen werden (siehe README, Abschnitt »Vers und Prosa«).

**Warum diese Quelle.** Die einzige leicht maschinenlesbare, zweifelsfrei
gemeinfreie Volltextfassung. Alternativen mit Auszeichnung (Folger) sind
lizenzrechtlich nicht gemeinfrei, siehe 2.1.

---

### 1.2 Deutsch — Baudissins Übersetzung von 1832 über DraCor/TextGrid

> William Shakespeare: *Othello*. Übersetzt von Wolf Heinrich Graf Baudissin.
> German Shakespeare Drama Corpus (`gersh`), hrsg. von Frank Fischer, DraCor.
> <https://dracor.org/gersh/othello> · TEI-XML über
> <https://dracor.org/api/v1/corpora/gersh/plays/othello/tei>
> Lokal: `sources/gersh_othello_de.tei.xml` (356 kB, TEI P5)

**Überlieferungskette** — vollständig, weil sie für die Zitierfähigkeit zählt:

1. **Erstdruck der Übersetzung:** *Shakspeare's dramatische Werke*, übersetzt
   von August Wilhelm Schlegel, ergänzt und erläutert von Ludwig Tieck, Band 8,
   Berlin: Georg Andreas Reimer 1832.
2. **Zugrundeliegende Druckausgabe der Digitalisierung:** *Sämtliche Werke in
   vier Bänden*, hrsg. von Anselm Schlösser, Band 4: Tragödien, 3. Auflage,
   Berlin und Weimar: Aufbau-Verlag 1975, S. 389–496. Diese Ausgabe folgt der
   letzten zu Schlegels Lebzeiten erschienenen Fassung (3. Auflage 1843/44).
3. **Digitalisat:** Zeno.org → TextGrid Repository,
   <http://www.textgridrep.org/textgrid:vn7q.0>
4. **TEI-Aufbereitung:** DraCor, Korpus `gersh`.

Die Seitenzählung der Aufbau-Ausgabe ist im DraCor-Text als `<pb/>` erhalten
und wurde in diese Ausgabe übernommen (`ed="aufbau1975"`), so dass nach der
gedruckten Ausgabe zitiert werden kann.

**Rechtsstand.** Baudissin starb 1878; die Übersetzung ist gemeinfrei. Die
TEI-Fassung von DraCor steht unter **CC0 1.0**. Die Herausgeberleistung der
Aufbau-Ausgabe von 1975 (Anselm Schlösser) betrifft Auswahl und Apparat, nicht
den Übersetzungstext selbst.

**Qualität.** Bereits TEI P5: 1 172 `<sp>`, Akt- und Szenengliederung,
Vers (`<lg>/<l>`) und Prosa (`<p>`) unterschieden, `@who` mit normalisierten
Figuren-IDs, `<pb/>`-Marken. Ein Sammelsprecher ist in Einzelpersonen aufgelöst
(`who="#montano #gratiano #jago"` für gedrucktes »ALLE«); diese Ausgabe stellt
das gedruckte Kollektivlabel wieder her.

**Warum diese Quelle.** Baudissins Übersetzung ist die kanonische deutsche
Fassung, folgt Shakespeares Sprechaktgliederung nahezu eins zu eins und
unterscheidet Vers und Prosa — beides Voraussetzung für ein belastbares
Alignment. Der maschinelle Abgleich ergab 1 168 direkte Parallelstellen bei nur
15 Abweichungen.

---

## 2. Geprüft und nicht verwendet

### 2.1 Folger Shakespeare / DraCor-Korpus `shake`

<https://shakespeare.folger.edu> · <https://dracor.org/shake/othello>

Technisch die beste englische Quelle: TEI mit ausgezeichneter Vers/Prosa-
Unterscheidung, Zeilenzählung nach Folger, Herausgeber Barbara A. Mowat und
Paul Werstine. **Nicht verwendet**, weil die Folger Digital Texts unter einer
CC-BY-NC-Lizenz stehen und damit nicht gemeinfrei sind. Da die Anfrage
ausdrücklich Public-Domain-Quellen verlangte, schied sie aus. Wer die
NC-Bedingung akzeptieren kann, gewinnt damit eine autoritative Vers/Prosa-
Auszeichnung und die Folger-Zeilenzählung (TLN).

### 2.2 Wieland, *Othello* 1766 (Wikisource)

> William Shakespeare: *Othello, der Mohr von Venedig*. Übersetzt von Christoph
> Martin Wieland. In: *Shakespear. Theatralische Werke*, Band 7, S. 177–403,
> Zürich: Orell, Geßner & Comp. 1766.
> <https://de.wikisource.org/wiki/Othello,_der_Mohr_von_Venedig>

Der **erste deutsche Othello**, gemeinfrei, auf Wikisource vollständig
transkribiert mit Bearbeitungsstand »fertig«, mit Seitenzahlen und Scan-Bezug
(HAAB Weimar, Commons). Nicht als Haupttext verwendet, weil Wieland in Prosa
übersetzt, kürzt und einer anderen englischen Vorlage (Warburton 1747) folgt —
das Alignment wäre deutlich lückenhafter geworden. **Als dritte Kolumne einer
erweiterten Ausgabe ist die Quelle erste Wahl**, gerade weil sie zeigt, wie
sich der deutsche Shakespeare zwischen 1766 und 1832 verändert; die
Wieland'schen Fußnoten sind selbst ein Kommentar.

### 2.3 Internet Shakespeare Editions — Q1 1622 und F1 1623

<https://internetshakespeare.uvic.ca/Library/Texts/Oth/>

Diplomatische Transkriptionen beider Frühdrucke, die einzige Möglichkeit, die
Q/F-Differenzen unmittelbar am Text zu prüfen statt aus der Sekundärliteratur.
Nicht eingebunden, weil die Nutzungsbedingungen der ISE gesondert zu klären
wären und die Ausgabe ohne sie auskommt. **Für eine erweiterte Fassung mit
echtem textkritischem Apparat (`<app>/<rdg>`) wäre das der nächste Schritt.**

### 2.4 Zeno.org

<https://www.zeno.org/Literatur/M/Shakespeare,+William>

Bietet denselben Baudissin-Text, war aber beim Aufbau dieser Ausgabe nicht
erreichbar. Da TextGrid dieselbe Textgrundlage in besserer Auszeichnung
bereitstellt, entstand kein Nachteil.

### 2.5 Digitalisate auf archive.org

Scans der historischen Drucke, u. a. `OthelloDerMohrVonVenedig` (Wieland 1766),
`bub_gb_G3-8MyH4rykC` (1800), `11920042bsb` (Shakspeare's Othello, 1806).
Gemeinfrei, aber nur als OCR-Volltext verfügbar; für eine Ausgabe, die auf
Zeichengenauigkeit angewiesen ist, ohne Nachkorrektur nicht brauchbar. Als
**Faksimile-Beleg** für Einzelstellen dagegen wertvoll.

### 2.6 Die Stoffquelle: Cinthios Novelle online

Die Vorlage — Giraldi Cinthios Novelle vom Mohren von Venedig, dritte Dekade,
siebte Novelle der *Hecatommithi* — ist gemeinfrei und in mehreren Fassungen
digitalisiert. Für diese Ausgabe geprüft:

| Fassung | Nachweis | Zustand |
|---|---|---|
| *De gli Hecatommithi*, Erstausgabe 1565 (italienisch) | [archive.org](https://archive.org/details/de-gli-hecatommithi-parte-prima) | Scan mit Volltexterkennung; Frakturähnliche Type, OCR nur eingeschränkt brauchbar |
| *Hecatommithi*, Venedig 1574 (italienisch) | archive.org, `bub_gb_Wc8KcIHIFHgC` | Scan |
| *Gli Ecatommiti*, Ausgaben 1833–1854 (italienisch) | archive.org, u. a. `bub_gb_py6CLg9ISTAC` | jüngere Drucke, besser lesbar |
| Wolstenholme Parr: *The Story of the Moor of Venice*, London 1795 | [archive.org](https://archive.org/details/bim_eighteenth-century_the-story-of-the-moor-of_parr-wolstenholme_1795) | älteste englische Übersetzung, gemeinfrei; die OCR des Scans ist für Zitate unbrauchbar |
| *Shakespeare's Library*, hrsg. Hazlitt, 1875 | archive.org, `in.ernet.dli.2015.175671` u. a. | Sammlung der Shakespeare-Quellen; der Othello-Band ist zu prüfen |
| Internet Shakespeare Editions: *Cinthio's Tale* | [ISE](https://internetshakespeare.uvic.ca/doc/Cinthio_M/index.html) | moderne englische Übersetzung, gut lesbar; Lizenz gesondert zu klären |

Für eine Ausgabe, die den Stoff dokumentieren will, ist der praktikable Weg:
die italienische Erstausgabe als Faksimile nachweisen, für den Wortlaut aber
einen der jüngeren italienischen Drucke oder die ISE-Übersetzung heranziehen.
**Der Kommentar dieser Ausgabe zitiert die Novelle nicht** — die Angaben zum
Inhalt in der Anmerkung »Die Quelle: Cinthios Novelle« sind entsprechend als
ungeprüft gekennzeichnet.

### 2.7 projekt-gutenberg.org / Gutenberg-DE

Enthält Baudissins Übersetzung, die Website-Nutzungsbedingungen sind jedoch
restriktiver als der gemeinfreie Text darunter. Da mit DraCor/TextGrid eine
ausdrücklich CC0-lizenzierte Fassung vorliegt, wurde diese Quelle gemieden.

---

## 3. Nachweise für die textkritischen Angaben des Kommentars

Die Aussagen über Quarto und Folio (Umfang der Differenz, die nur im Folio
überlieferten Passagen, die Crux »Judean«/»Indian«) stützen sich auf:

- **Internet Shakespeare Editions, *Othello*: Textual Introduction** —
  <https://internetshakespeare.uvic.ca/m/doc/Oth_TextIntro/section/The%20text/>
  Grundlage für: F1 rund 160 Zeilen länger als Q1; Emilias Rede IV,3 und das
  Pontus-Gleichnis III,3 fehlen in Q1; Q1-Auslassungen gelten als
  Bühnenkürzungen, nicht als Folio-Zusätze.
- **Folger Shakespeare Library, *An Introduction to This Text: Othello*** —
  <https://www.folger.edu/explore/shakespeares-works/othello/an-introduction-to-this-text/>
  Grundlage für: Verhältnis Q1/F1/Q2, über tausend Varianten.
- **Shakespeare Documented (Folger), *Othello, first edition*** —
  <https://shakespearedocumented.folger.edu/resource/document/othello-first-edition>
  Grundlage für: Weidenlied in Q1 nur teilweise, in F1 vollständig.

Alle übrigen Angaben des Kommentars — Wortzählungen, Übersetzungsvergleiche,
Auslassungen Baudissins, Zuweisungsdifferenzen — sind **am Textbestand dieser
Ausgabe selbst nachgerechnet** und mit `src/check_notes.py` gegen beide Zeugen
geprüft: jedes Zitat im Kommentar muss in der Fassung, der es zugeschrieben
wird, tatsächlich vorkommen.

**Jede Anmerkung sagt selbst, worauf sie beruht.** Das Feld `belegart` in
`data/notes.json` unterscheidet drei Fälle, die in der TEI-Datei als
`note[@type="beleg"]` und in der Leseansicht als Popup erscheinen:

| Belegart | Anzahl | Bedeutung |
|---|---|---|
| `textzeuge` | 72 | Die Behauptung ist am Wortlaut beider Fassungen ablesbar; die Zitate sind maschinell geprüft. |
| `auszählung` | 25 | Zahlenangabe, an dieser Ausgabe erhoben; die Abfrage steht im Belegfeld und ist mit `src/observe.py` reproduzierbar. |
| `literatur` | 18 | Angabe aus der Literatur. Wo eine Quelle eingesehen wurde, steht sie unter `refs`; wo nicht, sagt das Belegfeld ausdrücklich, dass die Angabe nicht nachgeprüft ist. |

Die Bibliographie steht maschinenlesbar in `data/bibliographie.json`, in der
TEI-Datei als `listBibl[@xml:id="commentary-bibliography"]` und am Fuß der
Leseansicht.

---

## 3a. Verwendete Sekundärliteratur

Alle drei Werke sind gemeinfrei; die zitierten Stellen wurden im Volltext
nachgeschlagen, nicht aus dem Gedächtnis wiedergegeben.

| Werk | Nachweis | Wofür |
|---|---|---|
| Samuel Taylor Coleridge: *The Literary Remains*, Bd. 2, London 1836 | [PG 8533](https://www.gutenberg.org/ebooks/8533) | »the motive-hunting of a motiveless malignity« (zu Jagos Monolog I,3); der Einspruch gegen einen »veritable negro« und die Bemerkung zu »thick-lips« |
| William Hazlitt: *Characters of Shakespear's Plays*, London 1817 | [PG 5085](https://www.gutenberg.org/ebooks/5085) | die Figurenkontraste als »opposition of costume in a picture«; »the pity of it« als »momentary fit of weakness« |
| A. C. Bradley: *Shakespearean Tragedy*, London 1904 | [PG 16966](https://www.gutenberg.org/ebooks/16966) | Othello als »most romantic figure«; Jago »almost destitute of humanity«; die Lehre von der doppelten Zeitrechnung und ihre Herkunft bei »Christopher North« |

**Nicht eingearbeitet, aber naheliegend:** August Wilhelm Schlegels *Vorlesungen
über dramatische Kunst und Litteratur* (1809–11) für die deutsche Seite der
Rezeption. Sie liegen auf archive.org nur als Fraktur-Scan mit unzuverlässiger
Texterkennung vor (u. a. `10574606bsb`, `ueberdramatisch06schlgoog`) und
bräuchten eine Nachkorrektur, bevor daraus zitiert werden kann.

## 4. Zitiervorschlag

> Shakespeare, William: *Othello, der Mohr von Venedig / Othello, the Moor of
> Venice*. Zweisprachige Ausgabe englisch–deutsch mit Stellenkommentar.
> Englischer Text nach Project Gutenberg #1531 (Globe/Moby-Tradition), deutscher
> Text nach der Übersetzung Wolf Heinrich Graf Baudissins (1832) in der Fassung
> des German Shakespeare Drama Corpus (DraCor/TextGrid). TEI-P5-Ausgabe,
> Version 1.0, 25. Juli 2026.

Einzelstellen lassen sich über die `xml:id` der Sprechakte zitieren, etwa
`#en-3.3.70` / `#de-3.3.70` für Jagos »green-ey'd monster«, oder für den
deutschen Text nach der Seitenzählung der Aufbau-Ausgabe von 1975, die als
`<pb/>` erhalten ist.

---

## 5. Vorbehalt

Der Stellenkommentar dieser Ausgabe ist maschinell verfasst. Die Zitate sind
automatisch gegen beide Textzeugen geprüft und die statistischen Angaben am
Material nachgerechnet; die philologischen Urteile und die Angaben zur
Wirkungsgeschichte sind es nicht. Vor einer Veröffentlichung sollte der
Kommentar fachlich durchgesehen werden — insbesondere die Abschnitte zur
Stoffgeschichte (Cinthio), zur Wirkungsgeschichte und die Datierungen.
