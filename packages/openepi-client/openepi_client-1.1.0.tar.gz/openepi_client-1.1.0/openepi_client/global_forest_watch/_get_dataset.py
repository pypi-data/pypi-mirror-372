from httpx import Client
from pydantic import Field

from openepi_client import openepi_settings, BaseModel
from ._gfw_types import GFWDataset

GET_DATASET_ENDPOINT = f"{openepi_settings.gfw_api_url}/dataset"


class GetDatasetRequest(BaseModel):
    dataset_id: str = Field(..., description="ID of the dataset to retrieve")
    http_client: Client = Field(..., description="HTTP client for making requests")

    def get_sync(self) -> GFWDataset | None:
        with self.http_client as client:
            response = client.get(url=f"{GET_DATASET_ENDPOINT}/{self.dataset_id}")

            json = response.json()
            if response.status_code == 404:
                return None

            if response.status_code != 200:
                raise ValueError(
                    f"Failed to get dataset: {json.get('message', 'Unknown error')}"
                )

            dataset = GFWDataset(**json.get("data", {}))
            dataset.status = json.get("status", "unknown")

            return dataset
