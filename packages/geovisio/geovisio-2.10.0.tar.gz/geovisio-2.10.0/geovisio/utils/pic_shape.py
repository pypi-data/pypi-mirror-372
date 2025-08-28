from typing import Annotated, Any, Iterator, List, Literal, NamedTuple, Tuple
from pydantic import BaseModel, Discriminator, Field, Tag, field_validator

BBox = Annotated[List[int], Field(min_length=4, max_length=4)]

Position = NamedTuple("Position", [("x", int), ("y", int)])

LinearRing = Annotated[List[Position], Field(min_length=4)]
PolygonCoords = List[LinearRing]


class Polygon(BaseModel):
    type: Literal["Polygon"]
    coordinates: PolygonCoords

    @field_validator("coordinates")
    def check_closure(cls, coordinates: List) -> List:
        """Validate that Polygon is closed (first and last coordinates are the same)."""
        if any(ring[-1] != ring[0] for ring in coordinates):
            raise ValueError("All linear rings have the same start and end coordinates")

        return coordinates

    def coords_iter(self) -> Iterator[Tuple[int, int]]:
        for ring in self.coordinates:
            yield from ring

    @classmethod
    def from_bounds(cls, xmin: float, ymin: float, xmax: float, ymax: float) -> "Polygon":
        """Create a Polygon geometry from a boundingbox."""
        return cls(
            type="Polygon",
            coordinates=[[(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax), (xmin, ymin)]],
        )


Geometry = Polygon  # for the moment we support only polygons, but later we might add support for more, so the type is aliased


def shape_discriminator(v: Any) -> str:
    if isinstance(v, list):
        return "bbox"
    return "geometry"


# Shapes can be provided as a bounding box or as a geometry
InputAnnotationShape = Annotated[(Annotated[Polygon, Tag("geometry")] | Annotated[BBox, Tag("bbox")]), Discriminator(shape_discriminator)]


def get_coords_from_shape(shape: InputAnnotationShape) -> Iterator[Tuple[int, int]]:
    """Get an iterator to all coordinates of a shape"""
    if shape_discriminator(shape) == "bbox":
        yield shape[0], shape[1]
        yield shape[2], shape[3]
    else:
        yield from shape.coords_iter()


def shape_as_geometry(shape: InputAnnotationShape) -> Geometry:
    """If the shape has been provided as a bounding box, transform it to a polygon"""
    if shape_discriminator(shape) == "bbox":
        return Polygon.from_bounds(*shape)
    return shape
