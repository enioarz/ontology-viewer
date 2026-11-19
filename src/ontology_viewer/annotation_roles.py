import json
from pathlib import Path
from urllib.parse import urlsplit

SKOS = "http://www.w3.org/2004/02/skos/core#"
LABEL = "http://www.w3.org/2000/01/rdf-schema#label"

ROLE_HEADINGS = {
    "definition": "Definitions",
    "label": "Labels",
    "prefLabel": "Preferred labels",
    "altLabel": "Alternative labels",
    "example": "Examples",
}
DEFAULT_PROPERTIES = {
    "definition": (SKOS + "definition",),
    "label": (LABEL,),
    "prefLabel": (SKOS + "prefLabel",),
    "altLabel": (SKOS + "altLabel",),
    "example": (SKOS + "example",),
}


def read_annotation_properties(path: Path | None) -> dict[str, tuple[str, ...]]:
    properties = DEFAULT_PROPERTIES.copy()
    if path is None:
        return properties
    custom = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(custom, dict):
        raise ValueError("Annotation config must be a JSON object mapping roles to lists of IRIs.")
    for role, iris in custom.items():
        if role not in properties:
            raise ValueError(f"Unknown annotation role: {role}")
        if not isinstance(iris, list) or not all(
            isinstance(iri, str)
            and not any(character.isspace() for character in iri)
            and urlsplit(iri).scheme
            for iri in iris
        ):
            raise ValueError(f"Annotation role {role} must contain a list of absolute IRIs.")
        properties[role] = tuple(dict.fromkeys(iris))
    return properties
