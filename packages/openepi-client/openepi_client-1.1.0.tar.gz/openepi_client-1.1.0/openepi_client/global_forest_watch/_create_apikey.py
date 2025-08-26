from httpx import Client
from pydantic import Field

from openepi_client import openepi_settings, BaseModel
from ._gfw_types import GFWApiKey, GFWToken

TOKEN_ENDPOINT: str = f"{openepi_settings.gfw_api_url}/auth/token"
API_KEY_ENDPOINT: str = f"{openepi_settings.gfw_api_url}/auth/apikey"


class CreateApiKeyRequest(BaseModel):
    email: str = Field(
        ..., description="The email address of the account holder", min_length=1
    )
    password: str = Field(
        ..., description="The password of the account holder", min_length=1
    )
    alias: str = Field(..., description="A required alias for the API key")
    organization: str = Field(..., description="The organization name for the API key")
    domains: list[str] = Field(
        description="List of domains for the API key", default_factory=list
    )
    http_client: Client = Field(..., description="HTTP client for making requests")

    def post_sync(self) -> GFWApiKey:
        with self.http_client:
            response = self.http_client.post(
                url=TOKEN_ENDPOINT,
                data={"username": self.email, "password": self.password},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

            json = response.json()
            if response.status_code != 200:
                raise ValueError(
                    f"Failed to get access token: {json.get('message', 'Unknown error')}"
                )

            token = GFWToken(**json.get("data", {}))
            token.status = json.get("status", "unknown")

            response = self.http_client.post(
                url=API_KEY_ENDPOINT,
                json={
                    "alias": self.alias,
                    "email": self.email,
                    "organization": self.organization,
                    "domains": self.domains,
                },
                headers={"Authorization": f"Bearer {token.access_token}"},
            )
            json = response.json()
            if response.status_code != 201:
                raise ValueError(
                    f"Failed to create API key: {json.get('message', 'Unknown error')}"
                )
            api_key = GFWApiKey(**json.get("data", {}))
            api_key.status = json.get("status", "unknown")
            return api_key
