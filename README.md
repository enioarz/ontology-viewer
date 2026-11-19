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

Open `_site/index.html` directly or serve the output directory with any static
web server. The generator writes `index.html` and `style.css`, replacing those
two files on subsequent builds. It can read RDF/XML, OWL/XML, and OWL Functional
Syntax. Use `--format rdf`, `--format owx`, or `--format ofn` if the input needs
an explicit format.

The page shows ontology metadata, import declarations, entity indexes grouped
by OWL type, entity annotations, and asserted axioms that mention each entity.
Labels prefer English, then untagged text, then other languages. The generator
documents the input file. It does not resolve imports or infer axioms.

## Theming

Pass `--stylesheet path/to/theme.css` to replace the bundled plain stylesheet.
The HTML provides semantic hooks for the ontology (`.ontology`,
`.ontology-header`, `.ontology-imports`), navigation (`.entity-navigation`,
`.entity-group`, `.entity-index`), and details (`.entity`, `.iri`,
`.annotations`, `.annotation-property`, `.annotation-value`, `.axioms`).
Generated HTML and CSS use relative paths and require no JavaScript.

## Extending the renderer

`ontology_viewer.ontology.load_ontology` reads a local file into an ontology
document. `ontology_viewer.render.render_html` renders that document to a string,
with a configurable stylesheet URL. The CLI writes the static files. A future
HTTP adapter can reuse the renderer for HTML and supply ontology serializations
for other media types.
