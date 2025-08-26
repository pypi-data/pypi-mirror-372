from httpx import Client
from pydantic import Field

from openepi_client import openepi_settings, BaseModel
from ._gfw_types import GFWAdminGeostore

GET_GEOSTORE_ENDPOINT: str = f"{openepi_settings.gfw_api_url}/geostore"


class GetGeostoreRequest(BaseModel):
    geostore_id: str = Field(description="The ID of the geostore to retrieve")
    api_key: str = Field(
        default=openepi_settings.gfw_api_key, description="API key for authentication"
    )
    http_client: Client = Field(..., description="HTTP client for making requests")

    def get_sync(self) -> GFWAdminGeostore:
        with self.http_client as client:
            response = client.get(
                url=f"{GET_GEOSTORE_ENDPOINT}/{self.geostore_id}",
                headers={"x-api-key": self.api_key},
            )

            json = response.json()
            if response.status_code != 200:
                raise ValueError(
                    f"Failed to retrieve geostore: {json.get('message', 'Unknown error')}"
                )

            return GFWAdminGeostore(**json.get("data", {}))
