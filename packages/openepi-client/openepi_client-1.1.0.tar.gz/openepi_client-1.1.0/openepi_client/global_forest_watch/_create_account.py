from httpx import Client
from pydantic import Field

from openepi_client import openepi_settings, BaseModel
from ._gfw_types import GFWAccountInfo


class CreateAccountRequest(BaseModel):
    name: str = Field(..., description="The name of the account holder")
    email: str = Field(..., description="The email address of the account holder")
    http_client: Client = Field(..., description="HTTP client for making requests")

    _create_account_endpoint = f"{openepi_settings.gfw_api_url}/auth/sign-up"

    def post_sync(self) -> GFWAccountInfo:
        with self.http_client:
            response = self.http_client.post(
                url=self._create_account_endpoint,
                json={"name": self.name, "email": self.email},
            )

            json = response.json()
            if response.status_code != 200:
                raise ValueError(
                    f"Failed to create account: {json.get('message', 'Unknown error')}"
                )

            account_info = GFWAccountInfo(**json.get("data", {}))
            account_info.status = json.get("status", "unknown")
            return account_info
