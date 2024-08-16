from typing import Any, Optional

import geojson
from geoalchemy2 import Geometry, WKBElement
from pydantic import field_serializer
from shapely import wkt
from shapely.geometry import mapping
from shapely.wkb import loads as wkb_loads
from sqlalchemy import Column
from sqlmodel import Field


class GeolocationMixin:
    """Mixin class for geolocation fields."""

    geom: Optional[Any] = Field(
        default=None,
        sa_column=Column(Geometry(geometry_type="POINT", srid=4326)),
        description="The geometry point representing the geolocation, created with a latitude and longitude pair stored as a PostGIS POINT.",
    )

    @field_serializer("geom")
    def serialize_geom(self, geom: Any, _info) -> Optional[str]:
        """Serialize the geometry point to a GeoJSON object."""
        if geom is None:
            return None
        if isinstance(geom, str):
            return geojson.dumps(mapping(wkt.loads(geom)))
        elif isinstance(geom, WKBElement):
            return geojson.dumps(wkb_loads(bytes(geom.data)))
