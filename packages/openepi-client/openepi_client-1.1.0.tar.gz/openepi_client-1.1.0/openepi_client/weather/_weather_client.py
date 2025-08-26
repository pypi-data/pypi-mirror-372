from pydantic import BaseModel, Field, model_validator, computed_field
from httpx import AsyncClient, Client
from datetime import datetime
from openepi_client.weather._weather_types import METJSONSunrise, METJSONForecast
from openepi_client import openepi_settings, GeoLocation


class SunriseRequest(BaseModel):
    """
    Request model for sunrise data.

    Parameters
    ----------
    geolocation : GeoLocation
        The geolocation to query for.
    date : datetime | None, optional
        The date to query for. Defaults to today's date.

    Attributes
    ----------
    _sunrise_endpoint : str
        The API endpoint for sunrise requests.

    Methods
    -------
    _params()
        Generates the query parameters for the API request.
    get_sync()
        Synchronously retrieves the sunrise data.
    get_async()
        Asynchronously retrieves the sunrise data.
    """

    geolocation: GeoLocation = Field(..., description="The geolocation to query for")
    date: datetime | None = Field(
        default_factory=datetime.today, description="The date to query for"
    )
    _sunrise_endpoint = f"{openepi_settings.met_api_url}/sunrise/3.0/sun"

    @computed_field
    @property
    def _params(self) -> dict:
        """
        Generates the query parameters for the API request.

        Returns
        -------
        dict
            The query parameters for the API request.
        """
        return {
            "lat": self.geolocation.lat,
            "lon": self.geolocation.lon,
            "date": self.date.strftime("%Y-%m-%d"),
        }

    def get_sync(self) -> METJSONSunrise:
        """
        Synchronously retrieves the sunrise data.

        Returns
        -------
        METJSONSunrise
            The sunrise data as a GeoJSON Feature object.
            Consists of sunrise time and sunset
            time for the given location and date.
        """
        with Client() as client:
            response = client.get(
                self._sunrise_endpoint,
                params=self._params,
                headers=openepi_settings.met_headers,
            )
            return METJSONSunrise(**response.json())

    async def get_async(self) -> METJSONSunrise:
        """
        Asynchronously retrieves the sunrise data.

        Returns
        -------
        METJSONSunrise
            The sunrise data as a GeoJSON Feature object.
            Consists of sunrise time and sunset
            time for the given location and date.
        """
        async with AsyncClient() as async_client:
            response = await async_client.get(
                self._sunrise_endpoint,
                params=self._params,
                headers=openepi_settings.met_headers,
            )
            return METJSONSunrise(**response.json())


class LocationForecastRequest(BaseModel):
    """
    Request model for location forecast data.

    Parameters
    ----------
    geolocation : GeoLocation
        The geolocation to query for.

    Attributes
    ----------
    _location_forecast_endpoint : str
        The API endpoint for location forecast requests.

    Methods
    -------
    _params()
        Generates the query parameters for the API request.
    get_sync()
        Synchronously retrieves the location forecast data.
    get_async()
        Asynchronously retrieves the location forecast data.
    """

    geolocation: GeoLocation = Field(..., description="The geolocation to query for")
    _location_forecast_endpoint = (
        f"{openepi_settings.met_api_url}/locationforecast/2.0/complete"
    )

    @computed_field
    @property
    def _params(self) -> dict:
        """
        Generates the query parameters for the API request.

        Returns
        -------
        dict
            The query parameters for the API request.
        """
        params = {
            "lat": self.geolocation.lat,
            "lon": self.geolocation.lon,
        }

        if self.geolocation.alt is not None:
            params["altitude"] = self.geolocation.alt

        return params

    def get_sync(self) -> METJSONForecast:
        """
        Synchronously retrieves the location forecast data.

        Returns
        -------
        METJSONForecast
            The location forecast data as a GeoJSON Feature object.
            Consists of the weather forecast for the
            next 9 days for the given location.
        """
        with Client() as client:
            response = client.get(
                self._location_forecast_endpoint,
                params=self._params,
                headers=openepi_settings.met_headers,
            )
            return METJSONForecast(**response.json())

    async def get_async(self) -> METJSONForecast:
        """
        Asynchronously retrieves the location forecast data.

        Returns
        -------
        METJSONForecast
            The location forecast data as a GeoJSON Feature object.
            Consists of the weather forecast for the
            next 9 days for the given location.
        """
        async with AsyncClient() as async_client:
            response = await async_client.get(
                self._location_forecast_endpoint,
                params=self._params,
                headers=openepi_settings.met_headers,
            )
            return METJSONForecast(**response.json())


class WeatherClient:
    """
    Synchronous client for weather-related API requests.

    Methods
    -------
    get_sunrise(geolocation: GeoLocation, date: datetime | None = datetime.today())
        Retrieves sunrise data for a given geolocation and date.
    get_location_forecast(geolocation: GeoLocation)
        Retrieves location forecast data for a given geolocation.
    """

    @staticmethod
    def get_sunrise(
        geolocation: GeoLocation,
        date: datetime | None = datetime.today(),
    ) -> METJSONSunrise:
        """
        Retrieves sunrise data for a given geolocation and date.

        Parameters
        ----------
        geolocation : GeoLocation
            The geolocation to query for.
        date : datetime | None, optional
            The date to query for. Defaults to today's date.

        Returns
        -------
        METJSONSunrise
            The sunrise data as a GeoJSON Feature object.
            Consists of sunrise time and sunset
            time for the given location and date.
        """
        return SunriseRequest(geolocation=geolocation, date=date).get_sync()

    @staticmethod
    def get_location_forecast(geolocation: GeoLocation) -> METJSONForecast:
        """
        Retrieves location forecast data for a given geolocation.

        Parameters
        ----------
        geolocation : GeoLocation
            The geolocation to query for.

        Returns
        -------
        METJSONForecast
            The location forecast data as a GeoJSON Feature object.
            Consists of the weather forecast for the
            next 9 days for the given location.
        """
        return LocationForecastRequest(geolocation=geolocation).get_sync()


class AsyncWeatherClient:
    """
    Asynchronous client for weather-related API requests.

    Methods
    -------
    get_sunrise(geolocation: GeoLocation, date: datetime | None = datetime.today())
        Asynchronously retrieves sunrise data for a given geolocation and date.
    get_location_forecast(geolocation: GeoLocation)
        Asynchronously retrieves location forecast data for a given geolocation.
    """

    @staticmethod
    async def get_sunrise(
        geolocation: GeoLocation,
        date: datetime | None = datetime.today(),
    ) -> METJSONSunrise:
        """
        Asynchronously retrieves sunrise data for a given geolocation and date.

        Parameters
        ----------
        geolocation : GeoLocation
            The geolocation to query for.
        date : datetime | None, optional
            The date to query for. Defaults to today's date.

        Returns
        -------
        METJSONSunrise
            The sunrise data as a GeoJSON Feature object.
            Consists of sunrise time and sunset
            time for the given location and date.
        """
        return await SunriseRequest(geolocation=geolocation, date=date).get_async()

    @staticmethod
    async def get_location_forecast(
        geolocation: GeoLocation,
    ) -> METJSONForecast:
        """
        Asynchronously retrieves location forecast data for a given geolocation.

        Parameters
        ----------
        geolocation : GeoLocation
            The geolocation to query for.

        Returns
        -------
        METJSONForecast
            The location forecast data as a GeoJSON Feature object.
            Consists of the weather forecast for the
            next 9 days for the given location.
        """
        return await LocationForecastRequest(geolocation=geolocation).get_async()
