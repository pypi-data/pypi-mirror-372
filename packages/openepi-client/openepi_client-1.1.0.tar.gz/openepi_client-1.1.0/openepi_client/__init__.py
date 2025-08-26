from pydantic import BaseModel as PydanticBaseModel, Field, ConfigDict
from pydantic_settings import BaseSettings


class OpenEpiSettings(BaseSettings):
    api_root_url: str = "https://api.openepi.io"

    gfw_api_url: str = "https://data-api.globalforestwatch.org"
    gfw_email: str | None = None
    gfw_password: str | None = None
    gfw_api_key: str | None = None

    met_api_url: str = "https://api.met.no/weatherapi"
    met_headers: dict[str, str] = {
        "User-Agent": "openepi.io github.com/openearthplatforminitiative/openepi-client-py"
    }


openepi_settings = OpenEpiSettings()


class GeoLocation(PydanticBaseModel):
    lat: float = Field(..., description="Latitude of the location")
    lon: float = Field(..., description="Longitude of the location")
    alt: int | None = Field(default=None, description="Altitude of the location")


class BoundingBox(PydanticBaseModel):
    min_lat: float = Field(..., description="Minimum latitude of the bounding box")
    max_lat: float = Field(..., description="Maximum latitude of the bounding box")
    min_lon: float = Field(..., description="Minimum longitude of the bounding box")
    max_lon: float = Field(..., description="Maximum longitude of the bounding box")


class BaseModel(PydanticBaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
