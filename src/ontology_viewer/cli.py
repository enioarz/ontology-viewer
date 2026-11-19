import argparse
from importlib.resources import files
from pathlib import Path

from .ontology import load_ontology
from .render import render_html


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a static HTML site for an OWL ontology.")
    parser.add_argument("ontology", type=Path, help="Local ontology file")
    parser.add_argument("-o", "--output", type=Path, required=True, help="Output directory")
    parser.add_argument("--format", help="Input serialization override, such as rdf, owx or ofn")
    parser.add_argument("--stylesheet", type=Path, help="Use a custom CSS file")
    args = parser.parse_args()

    try:
        if not args.ontology.is_file():
            raise FileNotFoundError(f"Ontology file does not exist: {args.ontology}")
        document = load_ontology(args.ontology, args.format)
        html = render_html(document)
        stylesheet = args.stylesheet or files("ontology_viewer").joinpath("themes", "plain.css")
        css = stylesheet.read_bytes()
        args.output.mkdir(parents=True, exist_ok=True)
        (args.output / "style.css").write_bytes(css)
        (args.output / "index.html").write_text(html, encoding="utf-8")
    except (OSError, ValueError, RuntimeError) as error:
        parser.exit(1, f"{parser.prog}: {error}\n")


if __name__ == "__main__":
    main()
