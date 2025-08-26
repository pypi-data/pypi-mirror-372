from httpx import Client
from pydantic import BaseModel

from openepi_client import openepi_settings
from ._gfw_types import GFWField, GFWRasterField


class GetFieldsRequest(BaseModel):
    dataset: str
    version: str

    _get_fields_endpoint = "{base_url}/dataset/{dataset_id}/{version_id}/fields"

    def get_sync(self) -> list[GFWField] | list[GFWRasterField] | None:
        with Client() as client:
            response = client.get(
                url=self._get_fields_endpoint.format(
                    base_url=openepi_settings.gfw_api_url,
                    dataset_id=self.dataset,
                    version_id=self.version,
                )
            )

            json = response.json()
            if response.status_code == 404:
                return None

            if response.status_code != 200:
                raise ValueError(
                    f"Failed to get dataset version: {json.get('message', 'Unknown error')}"
                )

            json_data = json.get("data", [])
            first_element = json_data[0] if json_data else {}
            if GFWRasterField.REQUIRED_FIELD in first_element:
                # If the first element has 'pixel_meaning', it's a raster field
                fields = [GFWRasterField(**x) for x in json_data]
            else:
                # Otherwise, it's a regular field
                fields = [GFWField(**x) for x in json_data]

            return fields
