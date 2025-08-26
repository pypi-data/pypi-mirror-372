from httpx import Client
from pydantic import BaseModel

from openepi_client import openepi_settings
from ._gfw_types import GFWVersion


class GetVersionRequest(BaseModel):
    dataset: str
    version: str

    _get_version_endpoint = "{base_url}/dataset/{dataset_id}/{version_id}"

    def get_sync(self) -> GFWVersion | None:
        with Client() as client:
            response = client.get(
                url=self._get_version_endpoint.format(
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

            gfw_version = GFWVersion(**json.get("data", {}))
            gfw_version.status = json.get("status", "unknown")

            return gfw_version
