PY := python3
TEI := othello-bilingual.tei.xml
PAGES := index.html othello-bilingual.html einleitung.html befunde.html \
         quellen.html konkordanz.html
RNG := build/tei_all.rng
SCHEMA_URL := https://www.tei-c.org/release/xml/tei/custom/schema/relaxng/tei_all.rng

.PHONY: all check clean schema pages

all: pages

pages: $(PAGES)

build/en.json: src/parse_en.py sources/pg1531_othello_en.txt
	$(PY) src/parse_en.py

build/de.json: src/parse_de.py sources/gersh_othello_de.tei.xml
	$(PY) src/parse_de.py

build/align.json: src/align.py build/en.json build/de.json
	$(PY) src/align.py

# Der Kommentar wird gegen beide Zeugen geprüft, bevor er eingebaut wird:
# ein Zitat, das so nicht dasteht, bricht den Bau.
$(TEI): src/build_tei.py src/check_notes.py data/notes.json data/bibliographie.json \
        data/glossar.json build/align.json
	$(PY) src/check_notes.py
	$(PY) src/build_tei.py
	$(PY) src/validate.py

index.html: src/render_index.py src/page.py $(TEI) build/konkordanz.json
	$(PY) src/render_index.py

othello-bilingual.html: src/render_html.py src/page.py $(TEI)
	$(PY) src/render_html.py

einleitung.html: src/render_einleitung.py src/page.py $(TEI)
	$(PY) src/render_einleitung.py

befunde.html: src/render_befunde.py src/page.py $(TEI)
	$(PY) src/render_befunde.py

quellen.html: src/render_quellen.py src/page.py $(TEI)
	$(PY) src/render_quellen.py

# Die Konkordanz erzeugt zusätzlich eine Unterseite je Wortfeld.
build/konkordanz.json konkordanz.html: src/concordance.py src/page.py \
                                        data/bezuege.json build/align.json
	$(PY) src/concordance.py

check: build/align.json
	$(PY) src/check_notes.py
	$(PY) src/validate.py

schema: $(RNG)

$(RNG):
	@mkdir -p build
	curl -sL -o $(RNG) $(SCHEMA_URL)

clean:
	rm -f build/en.json build/de.json build/align.json build/konkordanz.json \
	      $(TEI) $(PAGES) konkordanz-*.html
