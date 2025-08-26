from httpx import Client
from pydantic import BaseModel

from openepi_client import openepi_settings
from ._gfw_types import GFWVersion, GFWAssetType


class DownloadAssetRequest(BaseModel):
    dataset: str
    version: str
    asset_type: GFWAssetType
    to: str | None = None

    _download_asset_endpoint = (
        "{base_url}/dataset/{dataset_id}/{version_id}/download/{asset_type}"
    )

    def get_sync(self):
        if self.asset_type in [GFWAssetType.SHAPEFILE, GFWAssetType.GEOPACKAGE]:
            self._download_file()
        else:
            raise NotImplementedError(
                f"Asset type {self.asset_type} is not supported for download."
            )

    def _download_file(self):
        url = self._download_asset_endpoint.format(
            base_url=openepi_settings.gfw_api_url,
            dataset_id=self.dataset,
            version_id=self.version,
            asset_type=self.asset_type.download_suffix,
        )
        with Client(follow_redirects=True) as client:
            with client.stream(
                "GET", url, headers={"x-api-key": openepi_settings.gfw_api_key}
            ) as response:
                response.raise_for_status()
                with open(self.to, "wb") as f:
                    for chunk in response.iter_bytes():
                        f.write(chunk)
