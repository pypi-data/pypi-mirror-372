from httpx import Client
from openepi_client import openepi_settings
from geojson_pydantic.geometries import Geometry
from geojson_pydantic.features import Feature, FeatureCollection
from ._create_account import CreateAccountRequest
from ._create_apikey import CreateApiKeyRequest
from ._get_dataset import GetDatasetRequest
from ._create_geostore import CreateGeostoreRequest
from ._get_geostore import GetGeostoreRequest
from ._gfw_types import (
    GFWAccountInfo,
    GFWApiKey,
    GFWPagedDatasetResponse,
    GFWDataset,
    GFWAdminGeostore,
)
from ._list_datasets import ListDatasetsRequest


class GlobalForestWatchClient:
    def __init__(
        self,
        email: str | None = openepi_settings.gfw_email,
        password: str | None = openepi_settings.gfw_password,
        api_key: str | None = openepi_settings.gfw_api_key,
        http_client: Client = Client(follow_redirects=True),
    ):
        self.email = email
        self.password = password
        self.api_key = api_key
        self.http_client = http_client

    def create_account(self, name: str, email: str) -> GFWAccountInfo:
        return CreateAccountRequest(
            name=name, email=email, http_client=self.http_client
        ).post_sync()

    def create_api_key(
        self, alias: str, organization: str, domains: list[str] = None
    ) -> GFWApiKey:
        return CreateApiKeyRequest(
            email=self.email,
            password=self.password,
            alias=alias,
            organization=organization,
            domains=domains or [],
            http_client=self.http_client,
        ).post_sync()

    def list_datasets(
        self,
        page: int | None = None,
        page_size: int | None = None,
        downloadable: bool | None = None,
    ) -> GFWPagedDatasetResponse:
        return ListDatasetsRequest(
            page=page,
            page_size=page_size,
            downloadable=downloadable,
            http_client=self.http_client,
        ).get_sync()

    def get_dataset(self, dataset_id: str) -> GFWDataset | None:
        return GetDatasetRequest(
            dataset_id=dataset_id, http_client=self.http_client
        ).get_sync()

    def create_geostore(
        self, geojson: Geometry | Feature | FeatureCollection
    ) -> GFWAdminGeostore:
        return CreateGeostoreRequest(
            geojson=geojson, http_client=self.http_client, api_key=self.api_key
        ).post_sync()

    def get_geostore(self, geostore_id: str) -> GFWAdminGeostore:
        return GetGeostoreRequest(
            geostore_id=geostore_id, http_client=self.http_client, api_key=self.api_key
        ).get_sync()
