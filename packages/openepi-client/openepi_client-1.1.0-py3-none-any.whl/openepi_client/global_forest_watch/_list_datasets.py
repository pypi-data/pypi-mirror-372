from httpx import Client
from pydantic import Field

from openepi_client import openepi_settings, BaseModel
from ._gfw_types import GFWPagedDatasetResponse, GFWPageLinks, GFWDataset

LIST_DATASETS_ENDPOINT = f"{openepi_settings.gfw_api_url}/datasets"


class ListDatasetsRequest(BaseModel):
    page: int | None = Field(description="The requested page", default=None)
    page_size: int | None = Field(description="The requested page size", default=None)
    downloadable: bool | None = Field(
        description="Filter for downloadable datasets", default=None
    )
    http_client: Client = Field(..., description="HTTP client for making requests")

    def get_sync(self) -> GFWPagedDatasetResponse:
        paging: bool = self.page is not None and self.page_size is not None

        with self.http_client as client:
            response = client.get(
                url=LIST_DATASETS_ENDPOINT,
                params=(
                    {"page[number]": self.page, "page[size]": self.page_size}
                    if paging
                    else None
                ),
            )

            json = response.json()
            if response.status_code != 200:
                raise ValueError(
                    f"Failed to create account: {json.get('message', 'Unknown error')}"
                )

            gfw_paged_response = GFWPagedDatasetResponse()
            gfw_paged_response.status = json.get("status", "unknown")

            gfw_paged_response.datasets = [
                GFWDataset(**dataset) for dataset in json.get("data", [])
            ]

            if self.downloadable is not None:
                gfw_paged_response.datasets = [
                    dataset
                    for dataset in gfw_paged_response.datasets
                    if dataset.is_downloadable == self.downloadable
                ]

            if paging:
                gfw_paged_response.links = GFWPageLinks(**json.get("links", {}))
                json_metadata = json.get("meta", {})
                gfw_paged_response.page_size = json_metadata.get("size", None)
                gfw_paged_response.total_pages = json_metadata.get("total_pages", None)
                gfw_paged_response.total_items = json_metadata.get("total_items", None)

            return gfw_paged_response
