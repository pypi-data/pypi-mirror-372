from __future__ import annotations
from typing import Any
from geojson_pydantic.geometries import Geometry


class Query:
    def __init__(self, dataset: str, version: str, query: str):
        self.dataset = dataset
        self.version = version
        self.query = query
        self.geometry: Geometry | None = None

    def for_geometry(self, geometry: Geometry):
        self.geometry = geometry
        return self

    def for_geostore(self, geostore_id: str):
        self.geostore_id = geostore_id
        return self

    def execute(self):
        from ._query_dataset import QueryDatasetRequest

        return QueryDatasetRequest(
            dataset=self.dataset,
            version=self.version,
            query=self.query,
            geometry=self.geometry,
            geostore_id=self.geostore_id,
        ).get_sync()
