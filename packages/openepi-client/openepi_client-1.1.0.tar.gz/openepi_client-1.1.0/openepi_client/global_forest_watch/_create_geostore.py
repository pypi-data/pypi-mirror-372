from httpx import Client
from pydantic import Field
from geojson_pydantic.geometries import Geometry
from geojson_pydantic.features import Feature, FeatureCollection

from openepi_client import openepi_settings, BaseModel
from ._gfw_types import GFWAdminGeostore


CREATE_GEOSTORE_ENDPOINT: str = f"{openepi_settings.gfw_api_url}/geostore"
GEOJSON_EXCLUDE = {
    "id": True,
    "bbox": True,
    "geometry": {
        "bbox": True,
        "geometries": {"__all__": {"bbox": True}},
    },
    "features": {
        "__all__": {
            "id": True,
            "bbox": True,
            "geometry": {
                "bbox": True,
                "geometries": {"__all__": {"bbox": True}},
            },
        }
    },
}


class CreateGeostoreRequest(BaseModel):
    geojson: Geometry | Feature | FeatureCollection = Field(
        ..., description="The geometry to create a geostore for"
    )
    http_client: Client = Field(..., description="HTTP client for making requests")
    api_key: str = Field(
        default=openepi_settings.gfw_api_key, description="API key for authentication"
    )

    def post_sync(self) -> GFWAdminGeostore:
        with self.http_client as client:
            response = client.post(
                url=CREATE_GEOSTORE_ENDPOINT,
                json={
                    "geojson": self.geojson.model_dump(
                        exclude=GEOJSON_EXCLUDE,
                        exclude_none=True,
                        # exclude={"bbox": True, "id": True, "geometry": {"bbox": True}}
                    )
                },
                headers={"x-api-key": self.api_key},
            )

            json = response.json()
            if response.status_code != 201:
                raise ValueError(
                    f"Failed to create geoStore: {json.get('message', 'Unknown error')}"
                )

            response = GFWAdminGeostore(**json.get("data", {}))
            response.status = json.get("status", "unknown")
            return response
