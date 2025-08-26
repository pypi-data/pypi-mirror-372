import uuid
from typing import ClassVar, Any
from enum import StrEnum

from geojson_pydantic.geometries import Geometry
from geojson_pydantic import FeatureCollection
from pydantic import Field, validator, field_validator
from datetime import datetime
from pydantic import BaseModel

from ._query import Query


class GFWResponse(BaseModel):
    status: str = Field(default="unknown")
    message: str = Field(default="")


class GFWPageLinks(BaseModel):
    self: str | None = None
    first: str | None = None
    last: str | None = None
    prev: str | None = None
    next: str | None = None


class GFWPagedResponse(GFWResponse):
    total_items: int | None = Field(default=None)
    total_pages: int | None = Field(default=None)
    page_size: int | None = Field(default=None)
    links: GFWPageLinks | None = Field(default=None)


class GFWAccountInfo(GFWResponse):
    id: str
    name: str
    email: str
    status: str = Field(default="unknown")
    created_at: datetime = Field(alias="createdAt")


class GFWToken(GFWResponse):
    access_token: str = Field(...)
    token_type: str = Field(default="Bearer")


class GFWApiKey(GFWResponse):
    created_on: datetime = Field(...)
    updated_on: datetime = Field(...)
    alias: str = Field(...)
    user_id: str = Field(...)
    api_key: str = Field(...)
    organization: str = Field(...)
    email: str = Field(...)
    domains: list[str] = Field(default_factory=list)
    expires_on: datetime = Field(...)


class GFWMetadata(BaseModel):
    created_on: datetime | None = None
    updated_on: datetime | None = None
    spatial_resolution: int | None = None
    resolution_description: str | None = None
    geographic_coverage: str | None = None
    update_frequency: str | None = None
    scale: str | None = None
    citation: str | None = None
    title: str | None = None
    subtitle: str | None = None
    source: str | None = None
    license: str | None = None
    data_language: str | None = None
    overview: str | None = None
    function: str | None = None
    cautions: str | None = None
    key_restrictions: str | None = None
    tags: list[str] = Field(default_factory=list)
    why_added: str | None = None
    learn_more: str | None = None
    id: str | None = None

    @field_validator("tags", mode="before")
    def _null_versions_to_empty_list(cls, v):
        return [] if v is None else v


class GFWAssetType(StrEnum):
    DYNAMIC_VECTOR_TILE_CACHE = "Dynamic vector tile cache"
    STATIC_VECTOR_TILE_CACHE = "Static vector tile cache"
    RASTER_TILE_CACHE = "Raster tile cache"
    RASTER_TILE_SET = "Raster tile set"
    DATABASE_TABLE = "Database table"
    GEO_DATABASE_TABLE = "Geo database table"
    SHAPEFILE = ("ESRI Shapefile", "shp")
    GEOPACKAGE = ("Geopackage", "gpkg")
    NDJSON = "ndjson"
    CSV = "csv"
    TSV = "tsv"
    GRID_1X1 = "1x1 grid"
    COG = "COG"

    def __new__(cls, value: str, download_suffix: str | None = None):
        if download_suffix is None:
            download_suffix = value.lower()

        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.download_suffix = download_suffix
        return obj


class GFWAsset(GFWResponse):
    created_on: datetime | None = None
    updated_on: datetime | None = None
    asset_id: str | None = None
    dataset: str | None = None
    version: str | None = None
    asset_type: GFWAssetType | None = None
    asset_uri: str | None = None
    status: str | None = None  # TODO: Replace with enum
    is_managed: bool = False
    is_downloadable: bool = False

    def download(self, to: str | None = None):
        from ._download_asset import DownloadAssetRequest

        return DownloadAssetRequest(
            dataset=self.dataset,
            version=self.version,
            asset_type=self.asset_type,
            to=to,
        ).get_sync()


class GFWPagedAssetResponse(GFWPagedResponse):
    assets: list[GFWAsset] = Field(default_factory=list)


class GFWPgType(StrEnum):
    DATE = "date"
    TIMESTAMP = "timestamp"
    TIMESTAMP_WO_TZ = "timestamp without time zone"
    CHARACTER_VARYING = "character varying"
    TEXT = "text"
    BIGINT = "bigint"
    DOUBLE_PRECISION = "double precision"
    INTEGER = "integer"
    NUMERIC = "numeric"
    SMALLINT = "smallint"
    GEOMETRY = "geometry"
    ARRAY = "ARRAY"
    BOOLEAN = "boolean"
    JSONB = "jsonb"
    TIME = "time"
    UUID = "uuid"
    XML = "xml"


class GFWField(BaseModel):
    name: str | None = None
    alias: str | None = None
    description: str | None = None
    data_type: GFWPgType | None = None
    unit: str | None = None
    is_feature_info: bool = False
    is_filter: bool = False


class GFWValue(BaseModel):
    value: int | None = None
    meaning: str | int | None = None


class GFWValuesTable(BaseModel):
    rows: list[GFWValue] = Field(default_factory=list)


class GFWRasterField(BaseModel):
    REQUIRED_FIELD: ClassVar[str] = "pixel_meaning"

    pixel_meaning: str | None = None
    unit: str | None = None
    description: str | None = None
    # statistics: Statistics # GFW does not provide the object definition in the openapi docs yet, so skipping for now
    values_table: GFWValuesTable | None = None
    data_type: str | None = None
    compression: str | None = None
    no_data_value: str | None = None


class GFWDateRange(BaseModel):
    start_date: datetime | None = None
    end_date: datetime | None = None


class GFWVersionMetadata(BaseModel):
    created_on: datetime | None = None
    updated_on: datetime | None = None
    spatial_resolution: int | None = None
    resolution_description: str | None = None
    geographic_coverage: str | None = None
    update_frequency: str | None = None
    scale: str | None = None
    citation: str | None = None
    content_date: datetime | None = None
    content_date_range: GFWDateRange | None = None
    content_date_description: str | None = None
    last_update: datetime | None = None
    id: str | None = None


class GFWQueryResponse(GFWResponse):
    data: list[dict[str, Any]] = Field(default_factory=list)


class GFWVersion(GFWResponse):
    created_on: datetime | None = None
    updated_on: datetime | None = None
    dataset: str | None = None
    version: str | None = None
    is_latest: bool = False
    is_mutable: bool = False
    metadata: GFWVersionMetadata | None = None
    status: str | None = None

    def assets(
        self, page: int | None = None, page_size: int | None = None
    ) -> GFWPagedAssetResponse:
        from ._list_assets import ListAssetsRequest

        return ListAssetsRequest(
            dataset=self.dataset, version=self.version, page=page, page_size=page_size
        ).get_sync()

    def fields(self) -> list[GFWField] | list[GFWRasterField] | None:
        from ._get_fields import GetFieldsRequest

        return GetFieldsRequest(dataset=self.dataset, version=self.version).get_sync()

    def query(self, query: str) -> Query:
        return Query(dataset=self.dataset, version=self.version, query=query)


class GFWDataset(GFWResponse):
    created_on: datetime = Field(...)
    updated_on: datetime = Field(...)
    dataset: str
    is_downloadable: bool = Field(...)
    metadata: GFWMetadata = Field(...)
    versions: list[str] = Field(default_factory=list)

    @field_validator("versions", mode="before")
    def _null_versions_to_empty_list(cls, v):
        return [] if v is None else v

    @property
    def latest_version_id(self) -> str | None:
        return next((v for v in reversed(self.versions)), None)

    def get_version(self, version: str | None) -> GFWVersion | None:
        if version is None:
            return None
        else:
            from ._get_version import GetVersionRequest

            return GetVersionRequest(dataset=self.dataset, version=version).get_sync()


class GFWPagedDatasetResponse(GFWPagedResponse):
    datasets: list[GFWDataset] = Field(default_factory=list)


class GFWAdminGeostoreAttributes(BaseModel):
    geojson: FeatureCollection = Field(...)
    hash: str | None = None
    provider: dict[str, Any] | None = None
    areaHa: float | None = Field(default=None)
    bbox: list[float] | None = Field(default=None)
    lock: bool | None = Field(default=None)
    info: dict[str, Any] | None = Field(default=None)


class GFWAdminGeostore(GFWResponse):
    type: str = Field(...)
    id: str = Field(...)
    attributes: GFWAdminGeostoreAttributes
