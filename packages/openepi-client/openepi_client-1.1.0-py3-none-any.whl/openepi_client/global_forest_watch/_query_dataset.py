from typing import Any

from httpx import Client
from ._gfw_types import GFWQueryResponse
from pydantic import BaseModel

from geojson_pydantic.geometries import Geometry
from openepi_client import openepi_settings


class QueryDatasetRequest(BaseModel):
    dataset: str
    version: str
    query: str
    geometry: Geometry | None = None
    geostore_id: str | None = None
    _query_dataset_endpoint = "{base_url}/dataset/{dataset_id}/{version_id}/query/json"

    def get_sync(self) -> GFWQueryResponse:
        response = self._do_get() if self.geostore_id else self._do_post()

        json = response.json()
        if response.status_code == 404:
            return None

        if response.status_code != 200:
            raise ValueError(
                f"Failed to get dataset version: {json.get('message', 'Unknown error')}"
            )

        response = GFWQueryResponse(**json)
        return response

    def _do_post(self):
        with Client() as client:
            body: dict[str, Any] = {"sql": self.query}
            if self.geometry:
                body["geometry"] = self.geometry.dict(exclude={"bbox"})

            return client.post(
                url=self._query_dataset_endpoint.format(
                    base_url=openepi_settings.gfw_api_url,
                    dataset_id=self.dataset,
                    version_id=self.version,
                ),
                json=body,
                headers={"x-api-key": openepi_settings.gfw_api_key},
            )

    def _do_get(self):
        with Client() as client:
            return client.get(
                url=self._query_dataset_endpoint.format(
                    base_url=openepi_settings.gfw_api_url,
                    dataset_id=self.dataset,
                    version_id=self.version,
                ),
                params={"sql": self.query, "geostore_id": self.geostore_id},
                headers={"x-api-key": openepi_settings.gfw_api_key},
            )
