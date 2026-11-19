from collections.abc import Mapping

from jinja2 import Environment, PackageLoader, select_autoescape

from .annotation_roles import DEFAULT_PROPERTIES, ROLE_HEADINGS
from .ontology import Entity, OntologyDocument, display_name

_templates = Environment(
    loader=PackageLoader("ontology_viewer"),
    autoescape=select_autoescape(),
)
_templates.filters["display_name"] = display_name


def render_html(
    document: OntologyDocument,
    stylesheet_url: str = "style.css",
    *,
    script_url: str = "htmx.min.js",
    entity_base_url: str = "entities/",
) -> str:
    """Render the ontology index independently of the transport."""
    return _templates.get_template("ontology.html").render(
        document=document, stylesheet_url=stylesheet_url,
        script_url=script_url, entity_base_url=entity_base_url,
    )


def render_entity_html(
    entity: Entity,
    *,
    ontology_title: str,
    index_url: str = "../index.html",
    stylesheet_url: str = "../style.css",
    script_url: str = "../htmx.min.js",
    annotation_properties: Mapping[str, tuple[str, ...]] = DEFAULT_PROPERTIES,
) -> str:
    """Render a standalone entity resource, also usable in an htmx swap."""
    sections = [
        (role, heading, tuple(
            annotation for annotation in entity.annotations
            if annotation.property_iri in annotation_properties[role]
        ))
        for role, heading in ROLE_HEADINGS.items()
    ]
    special_properties = {
        iri for properties in annotation_properties.values() for iri in properties
    }
    return _templates.get_template("entity.html").render(
        entity=entity, ontology_title=ontology_title, index_url=index_url,
        stylesheet_url=stylesheet_url, script_url=script_url, sections=sections,
        other_annotations=tuple(
            item for item in entity.annotations if item.property_iri not in special_properties
        ),
    )
