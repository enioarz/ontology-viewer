# Ontology Viewer

Generate a static, browsable HTML reference for an OWL ontology using
[py-horned-owl](https://github.com/ontology-tools/py-horned-owl).

## Quick start

With Python 3.10 or later, run from the checkout root:

```sh
python -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/ontology-viewer examples/animals.ofn --output _site
```

Open `_site/index.html` directly, or serve the generated site to enable htmx
navigation:

```sh
python -m http.server --directory _site 8000
```

The index links to a standalone page in `entities/` for each distinct declared
entity IRI. When served over HTTP, htmx follows those same links, swaps the page's
main content, and updates the browser URL. Direct links and normal browser
navigation work without JavaScript. As each entity comes into view on the index,
htmx loads the entity page and extracts its IRI, definitions, and asserted
`SubClassOf` relations beneath the linked label. The label and IRI are available
before the summary loads. The pinned htmx 2.0.10 script and its license
ship with the site, so it can run without a CDN.

The generator supports RDF/XML, OWL/XML, and OWL Functional Syntax. Use
`--format rdf`, `--format owx`, or `--format ofn` to override detection. The
index shows ontology metadata, import declarations, and entities grouped by
OWL type. Entity pages show annotations and group asserted axioms by OWL
axiom type, with counts and expandable details. The generator does not resolve
imports or infer axioms. Use a fresh output directory if you want to exclude
pages left over from a previous build.

## Annotation properties

Definitions, labels, preferred labels, alternative labels, and examples appear
in dedicated sections on entity pages. Defaults use `rdfs:label` and
`skos:definition`, `skos:prefLabel`, `skos:altLabel`, and `skos:example`.
Entity titles use the first available preferred-label property, then a label
property, then the IRI's local name. Within a property they prefer English,
then untagged text, then other languages.

Pass `--annotation-config examples/iao-annotations.json` to recognize common
IAO properties alongside SKOS. A config is a JSON object whose keys are
`definition`, `label`, `prefLabel`, `altLabel`, and `example`. Each supplied
list replaces that role's defaults and accepts absolute property IRIs in
priority order. Omitted roles retain their defaults. An empty list disables
the dedicated section for that role.

## Theming

Pass `--stylesheet path/to/theme.css` to replace the bundled plain stylesheet.
The HTML provides semantic hooks for the ontology (`.ontology`,
`.ontology-header`, `.ontology-imports`), navigation (`.entity-navigation`,
`.entity-group`, `.entity-index`), and details (`.entity`, `.iri`,
`.annotations`, `.annotation-property`, `.annotation-value`, `.axioms`,
`.axiom-group`). Use `[data-annotation-role="definition"]` and analogous role
selectors to style individual annotation sections.

## Extending the renderer

`ontology_viewer.ontology.load_ontology` reads a local file into an ontology
document. `ontology_viewer.render.render_html` renders the index, and
`ontology_viewer.render.render_entity_html` renders an entity page. Both return
HTML strings with configurable URLs. The CLI writes the static files. A future
HTTP adapter can reuse the renderer for HTML and supply ontology serializations
for other media types.
