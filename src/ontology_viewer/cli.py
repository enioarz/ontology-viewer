import argparse
from importlib.resources import files
from pathlib import Path

from .annotation_roles import read_annotation_properties
from .ontology import load_ontology
from .render import render_entity_html, render_html


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a static HTML site for an OWL ontology.")
    parser.add_argument("ontology", type=Path, help="Local ontology file")
    parser.add_argument("-o", "--output", type=Path, required=True, help="Output directory")
    parser.add_argument("--format", help="Input serialization override, such as rdf, owx or ofn")
    parser.add_argument("--stylesheet", type=Path, help="Use a custom CSS file")
    parser.add_argument("--annotation-config", type=Path, help="JSON mapping annotation roles to property IRIs")
    args = parser.parse_args()

    try:
        if not args.ontology.is_file():
            raise FileNotFoundError(f"Ontology file does not exist: {args.ontology}")
        properties = read_annotation_properties(args.annotation_config)
        document = load_ontology(args.ontology, args.format, annotation_properties=properties)
        html = render_html(document)
        assets = files("ontology_viewer")
        stylesheet = args.stylesheet or assets.joinpath("themes", "plain.css")
        css = stylesheet.read_bytes()
        entity_dir = args.output / "entities"
        entity_dir.mkdir(parents=True, exist_ok=True)
        entities = {entity.iri: entity for group in document.groups for entity in group.entities}
        for entity in entities.values():
            page = render_entity_html(
                entity, ontology_title=document.title, annotation_properties=properties
            )
            (entity_dir / f"{entity.anchor}.html").write_text(page, encoding="utf-8")
        (args.output / "style.css").write_bytes(css)
        for name, output_name in (("htmx.min.js", "htmx.min.js"), ("LICENSE", "htmx.LICENSE")):
            (args.output / output_name).write_bytes(assets.joinpath("vendor", name).read_bytes())
        (args.output / "index.html").write_text(html, encoding="utf-8")
    except (OSError, ValueError, RuntimeError) as error:
        parser.exit(1, f"{parser.prog}: {error}\n")


if __name__ == "__main__":
    main()
