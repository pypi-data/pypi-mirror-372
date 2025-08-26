from httpx import Client
from pydantic import BaseModel, Field

from openepi_client import openepi_settings
from ._gfw_types import GFWPagedAssetResponse, GFWPageLinks, GFWAsset


class ListAssetsRequest(BaseModel):
    dataset: str
    version: str
    page: int | None = Field(description="The requested page", default=None)
    page_size: int | None = Field(description="The requested page size", default=None)
    _list_assets_endpoint = f"{openepi_settings.gfw_api_url}/assets"

    def get_sync(self) -> GFWPagedAssetResponse:
        paging: bool = self.page is not None and self.page_size is not None

        params = {"dataset": self.dataset, "version": self.version}
        if paging:
            params.update({"page[number]": self.page, "page[size]": self.page_size})

        with Client() as client:
            response = client.get(
                url=self._list_assets_endpoint,
                params=params,
            )

            json = response.json()
            if response.status_code != 200:
                raise ValueError(
                    f"Failed to list assets: {json.get('message', 'Unknown error')}"
                )

            gfw_paged_response = GFWPagedAssetResponse()
            gfw_paged_response.status = json.get("status", "unknown")

            gfw_paged_response.assets = [
                GFWAsset(**asset) for asset in json.get("data", [])
            ]

            if paging:
                gfw_paged_response.links = GFWPageLinks(**json.get("links", {}))
                json_metadata = json.get("meta", {})
                gfw_paged_response.page_size = json_metadata.get("size", None)
                gfw_paged_response.total_pages = json_metadata.get("total_pages", None)
                gfw_paged_response.total_items = json_metadata.get("total_items", None)

            return gfw_paged_response
