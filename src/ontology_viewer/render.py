from jinja2 import Environment, PackageLoader, select_autoescape

from .ontology import OntologyDocument, display_name

_templates = Environment(
    loader=PackageLoader("ontology_viewer"),
    autoescape=select_autoescape(),
)
_templates.filters["display_name"] = display_name


def render_html(document: OntologyDocument, stylesheet_url: str = "style.css") -> str:
    """Render an ontology independently of the filesystem or HTTP transport."""
    entity_groups = {}
    for group in document.groups:
        for entity in group.entities:
            entity_groups.setdefault(entity.iri, group.id)
    return _templates.get_template("ontology.html").render(
        document=document, stylesheet_url=stylesheet_url, entity_groups=entity_groups
    )
