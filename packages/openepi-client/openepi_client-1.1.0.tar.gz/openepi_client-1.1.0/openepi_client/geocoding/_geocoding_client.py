from pydantic import BaseModel, Field, computed_field
from httpx import AsyncClient, Client

from openepi_client import openepi_settings, GeoLocation
from openepi_client.geocoding._geocoding_types import FeatureCollection


class GeocodeRequest(BaseModel):
    """
    Request model for geocoding.

    Parameters
    ----------
    q : str
        The query string to geocode.
    geolocation : GeoLocation, optional
        The geolocation to query for.
    lang : str, optional
        Set preferred language (e.g. 'default', 'en', 'de', 'fr').
    limit : int, optional
        The maximum number of results.

    Attributes
    ----------
    _geocode_endpoint : str
        The API endpoint for geocoding requests.

    Methods
    -------
    _params()
        Generates the query parameters for the API request.
    get_sync()
        Synchronously retrieves the geocoding data.
    get_async()
        Asynchronously retrieves the geocoding data.
    """

    q: str = Field(..., description="The query string to geocode")
    geolocation: GeoLocation | None = Field(
        default=None, description="The geolocation to query for"
    )
    lang: str | None = Field(
        default=None,
        description="Set preferred language (e.g. 'default', 'en', 'de', 'fr')",
    )
    limit: int | None = Field(default=None, description="The maximum number of results")
    _geocode_endpoint = f"{openepi_settings.api_root_url}/geocoding/"

    @computed_field
    @property
    def _params(self) -> dict:
        """
        Generates the query parameters for the API request.

        Returns
        -------
        dict
            The query parameters.
        """
        return {
            k: v
            for k, v in {
                "q": self.q,
                "lon": self.geolocation.lon if self.geolocation else None,
                "lat": self.geolocation.lat if self.geolocation else None,
                "lang": self.lang,
                "limit": self.limit,
            }.items()
            if v is not None
        }

    def get_sync(self) -> FeatureCollection:
        """
        Synchronously retrieve geocoding data.

        Returns
        -------
        FeatureCollection
            The geocoding response data as a GeoJSON FeatureCollection object.
            Consists of places matching the query string.
        """
        with Client() as client:
            response = client.get(self._geocode_endpoint, params=self._params)
            return FeatureCollection(**response.json())

    async def get_async(self) -> FeatureCollection:
        """
        Asynchronously retrieve geocoding data.

        Returns
        -------
        FeatureCollection
            The geocoding response data as a GeoJSON FeatureCollection object.
            Consists of places matching the query string.
        """
        async with AsyncClient() as async_client:
            response = await async_client.get(
                self._geocode_endpoint, params=self._params
            )
            return FeatureCollection(**response.json())


class ReverseGeocodeRequest(BaseModel):
    """
    Request model for reverse geocoding.

    Parameters
    ----------
    geolocation : GeoLocation
        The geolocation to query for.
    lang : str, optional
        Set preferred language (e.g. 'default', 'en', 'de', 'fr').
    limit : int, optional
        The maximum number of results.

    Attributes
    ----------
    _reverse_geocode_endpoint : str
        The API endpoint for reverse geocoding requests.

    Methods
    -------
    _params()
        Generates the query parameters for the API request.
    get_sync()
        Synchronously retrieves the reverse geocoding data.
    get_async()
        Asynchronously retrieves the reverse geocoding data.
    """

    geolocation: GeoLocation = Field(..., description="The geolocation to query for")
    lang: str | None = Field(
        default=None,
        description="Set preferred language (e.g. 'default', 'en', 'de', 'fr')",
    )
    limit: int | None = Field(default=None, description="The maximum number of results")
    _reverse_geocode_endpoint = f"{openepi_settings.api_root_url}/geocoding/reverse"

    @computed_field
    @property
    def _params(self) -> dict:
        """
        Generates the query parameters for the API request.

        Returns
        -------
        dict
            The query parameters.
        """
        return {
            k: v
            for k, v in {
                "lon": self.geolocation.lon,
                "lat": self.geolocation.lat,
                "lang": self.lang,
                "limit": self.limit,
            }.items()
            if v is not None
        }

    def get_sync(self) -> FeatureCollection:
        """
        Synchronously retrieve reverse geocoding data.

        Returns
        -------
        FeatureCollection
            The reverse geocoding response data as a GeoJSON FeatureCollection object.
            Consists of places near the provided coordinates.
        """
        with Client() as client:
            response = client.get(self._reverse_geocode_endpoint, params=self._params)
            return FeatureCollection(**response.json())

    async def get_async(self) -> FeatureCollection:
        """
        Asynchronously retrieve reverse geocoding data.

        Returns
        -------
        FeatureCollection
            The reverse geocoding response data as a GeoJSON FeatureCollection object.
            Consists of places near the provided coordinates.
        """
        async with AsyncClient() as async_client:
            response = await async_client.get(
                self._reverse_geocode_endpoint, params=self._params
            )
            return FeatureCollection(**response.json())


class GeocodeClient:
    """
    Client for synchronous geocoding and reverse geocoding operations.

    Methods
    -------
    geocode(q, geolocation, lang, limit)
        Perform geocoding operation.
    reverse_geocode(geolocation, lang, limit)
        Perform reverse geocoding operation.
    """

    @staticmethod
    def geocode(
        q: str,
        geolocation: GeoLocation | None = None,
        lang: str | None = None,
        limit: int | None = None,
    ) -> FeatureCollection:
        """
        Perform geocoding operation.

        Parameters
        ----------
        q : str
            The query string to geocode.
        geolocation : GeoLocation, optional
            The geolocation to query for.
        lang : str, optional
            Set preferred language (e.g. 'default', 'en', 'de', 'fr').
        limit : int, optional
            The maximum number of results.

        Returns
        -------
        FeatureCollection
            The geocoding response data as a GeoJSON FeatureCollection object.
            Consists of places matching the query string.
        """
        return GeocodeRequest(
            q=q, geolocation=geolocation, lang=lang, limit=limit
        ).get_sync()

    @staticmethod
    def reverse_geocode(
        geolocation: GeoLocation,
        lang: str | None = None,
        limit: int | None = None,
    ) -> FeatureCollection:
        """
        Perform reverse geocoding operation.

        Parameters
        ----------
        geolocation : GeoLocation
            The geolocation to query for.
        lang : str, optional
            Set preferred language (e.g. 'default', 'en', 'de', 'fr').
        limit : int, optional
            The maximum number of results.

        Returns
        -------
        FeatureCollection
            The reverse geocoding response data as a GeoJSON FeatureCollection object.
            Consists of places near the provided coordinates.
        """
        return ReverseGeocodeRequest(
            geolocation=geolocation, lang=lang, limit=limit
        ).get_sync()


class AsyncGeocodeClient:
    """
    Client for asynchronous geocoding and reverse geocoding operations.

    Methods
    -------
    geocode(q, geolocation, lang, limit)
        Perform geocoding operation asynchronously.
    reverse_geocode(geolocation, lang, limit)
        Perform reverse geocoding operation asynchronously.
    """

    @staticmethod
    async def geocode(
        q: str,
        geolocation: GeoLocation | None = None,
        lang: str | None = None,
        limit: int | None = None,
    ) -> FeatureCollection:
        """
        Perform geocoding operation asynchronously.

        Parameters
        ----------
        q : str
            The query string to geocode.
        geolocation : GeoLocation, optional
            The geolocation to query for.
        lang : str, optional
            Set preferred language (e.g. 'default', 'en', 'de', 'fr').
        limit : int, optional
            The maximum number of results.

        Returns
        -------
        FeatureCollection
            The geocoding response data as a GeoJSON FeatureCollection object.
            Consists of places matching the query string.
        """
        return await GeocodeRequest(
            q=q, geolocation=geolocation, lang=lang, limit=limit
        ).get_async()

    @staticmethod
    async def reverse_geocode(
        geolocation: GeoLocation,
        lang: str | None = None,
        limit: int | None = None,
    ) -> FeatureCollection:
        """
        Perform reverse geocoding operation asynchronously.

        Parameters
        ----------
        geolocation : GeoLocation
            The geolocation to query for.
        lang : str, optional
            Set preferred language (e.g. 'default', 'en', 'de', 'fr').
        limit : int, optional
            The maximum number of results.

        Returns
        -------
        FeatureCollection
            The reverse geocoding response data as a GeoJSON FeatureCollection object.
            Consists of places near the provided coordinates.
        """
        return await ReverseGeocodeRequest(
            geolocation=geolocation, lang=lang, limit=limit
        ).get_async()
