from collections import defaultdict
from collections.abc import Mapping
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from pyhornedowl import model, open_ontology_from_file

from .annotation_roles import DEFAULT_PROPERTIES, LABEL
TITLE_PROPERTIES = (
    "http://purl.org/dc/terms/title",
    "http://purl.org/dc/elements/1.1/title",
    LABEL,
)


@dataclass(frozen=True, order=True)
class Annotation:
    property_iri: str
    value: str
    language: str = ""
    datatype: str = ""

    @classmethod
    def from_owl(cls, annotation):
        property_iri = str(annotation.ap.first)
        value = annotation.av
        match value:
            case model.LanguageLiteral():
                return cls(property_iri, value.literal, language=value.lang)
            case model.DatatypeLiteral():
                return cls(property_iri, value.literal, datatype=str(value.datatype_iri))
            case model.SimpleLiteral():
                return cls(property_iri, value.literal)
            case _:
                return cls(property_iri, str(value))


@dataclass(frozen=True)
class Entity:
    iri: str
    label: str
    annotations: tuple[Annotation, ...]
    axioms: tuple[tuple[str, tuple[str, ...]], ...]

    @property
    def anchor(self) -> str:
        return "entity-" + sha256(self.iri.encode()).hexdigest()


@dataclass(frozen=True)
class EntityGroup:
    id: str
    title: str
    entities: tuple[Entity, ...]


@dataclass(frozen=True)
class OntologyDocument:
    title: str
    iri: str | None
    version_iri: str | None
    imports: tuple[str, ...]
    annotations: tuple[Annotation, ...]
    groups: tuple[EntityGroup, ...]


def display_name(iri: str) -> str:
    return iri.rstrip("/#").rsplit("#", 1)[-1].rsplit("/", 1)[-1] or iri


def preferred_label(annotations, properties, fallback):
    for property_iri in properties:
        candidates = [
            annotation for annotation in annotations
            if annotation.property_iri == property_iri and annotation.value.strip()
        ]
        if candidates:
            return min(
                candidates,
                key=lambda item: (
                    item.language.lower().split("-")[0] != "en",
                    bool(item.language),
                    item.value.casefold(),
                    item,
                ),
            ).value
    return fallback


def load_ontology(
    path: Path,
    serialization: str | None = None,
    *,
    annotation_properties: Mapping[str, tuple[str, ...]] = DEFAULT_PROPERTIES,
) -> OntologyDocument:
    ontology = open_ontology_from_file(str(path), serialization)
    ontology_annotations = []
    entity_annotations = defaultdict(list)
    imports = set()
    for annotated in ontology.get_components():
        match annotated.component:
            case model.OntologyAnnotation(annotation):
                ontology_annotations.append(Annotation.from_owl(annotation))
            case model.AnnotationAssertion(subject, annotation) if isinstance(subject, model.IRI):
                entity_annotations[str(subject)].append(Annotation.from_owl(annotation))
            case model.Import(iri):
                imports.add(str(iri))

    categories = (
        ("classes", "Classes", ontology.get_classes()),
        ("object-properties", "Object properties", ontology.get_object_properties()),
        ("data-properties", "Data properties", ontology.get_data_properties()),
        ("annotation-properties", "Annotation properties", ontology.get_annotation_properties()),
        ("individuals", "Named individuals", ontology.get_named_individuals()),
        ("datatypes", "Datatypes", ontology.get_datatypes()),
    )
    entities = {}
    for iri in set().union(*(iris for _, _, iris in categories)):
        annotations = tuple(sorted(entity_annotations[iri]))
        axioms = defaultdict(list)
        for axiom in ontology.get_axioms_for_iri((iri, True)):
            axioms[type(axiom.component).__name__].append(str(axiom))
        entities[iri] = Entity(
            iri,
            preferred_label(
                annotations,
                annotation_properties["prefLabel"] + annotation_properties["label"],
                display_name(iri),
            ),
            annotations,
            tuple((kind, tuple(sorted(items))) for kind, items in sorted(axioms.items())),
        )

    groups = tuple(
        EntityGroup(
            group_id,
            title,
            tuple(sorted((entities[iri] for iri in iris), key=lambda e: (e.label.casefold(), e.iri))),
        )
        for group_id, title, iris in categories if iris
    )
    ontology_iri = ontology.get_iri()
    version_iri = ontology.get_version_iri()
    iri = str(ontology_iri) if ontology_iri is not None else None
    return OntologyDocument(
        preferred_label(ontology_annotations, TITLE_PROPERTIES, display_name(iri) if iri else path.stem),
        iri,
        str(version_iri) if version_iri is not None else None,
        tuple(sorted(imports)),
        tuple(sorted(ontology_annotations)),
        groups,
    )
