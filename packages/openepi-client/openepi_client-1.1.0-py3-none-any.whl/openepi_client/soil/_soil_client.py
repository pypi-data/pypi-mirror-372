from httpx import AsyncClient, Client
import httpx
from pydantic import BaseModel, Field, computed_field
from openepi_client import openepi_settings, BoundingBox, GeoLocation

from openepi_client.soil._soil_types import (
    SoilTypeSummaryJSON,
    SoilTypeJSON,
    SoilPropertyJSON,
)


class SoilTypeRequest(BaseModel):
    """
    Request model for soil type data.

    Parameters
    ----------
    geolocation : GeoLocation
        The geolocation to query for.
    top_k : int, optional
        The number of most probable soil types to return, sorted by probability in descending order.

    Attributes
    ----------
    _soil_type_endpoint : str
        The API endpoint for soil type requests.

    Methods
    -------
    _params()
        Generates the query parameters for the API request.
    get_sync()
        Synchronously retrieves the soil type data.
    get_async()
        Asynchronously retrieves the soil type data.
    """

    geolocation: GeoLocation = Field(description="The geolocation to query for")
    top_k: int = Field(
        0,
        description=(
            "The number of most probable soil types that will "
            "be returned, sorted by probability in descending order"
        ),
    )

    _soil_type_endpoint: str = f"{openepi_settings.api_root_url}/soil/type"

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
            "lat": self.geolocation.lat,
            "lon": self.geolocation.lon,
            "top_k": self.top_k,
        }

    def get_sync(self) -> SoilTypeJSON:
        """
        Synchronously retrieve soil type data.

        Returns
        -------
        SoilTypeJSON
            The soil type response data as a GeoJSON Feature object.
            Consists of the most probable soil type at the
            queried location, along with the top_k most
            probable soil types. The probability of each
            soil type is represented as an integer between
            0 and 100.
        """
        with Client() as client:
            response = client.get(
                self._soil_type_endpoint,
                params=self._params,
                timeout=httpx.Timeout(None),
            )
            return SoilTypeJSON(**response.json())

    async def get_async(self) -> SoilTypeJSON:
        """
        Asynchronously retrieve soil type data.

        Returns
        -------
        SoilTypeJSON
            The soil type response data as a GeoJSON Feature object.
            Consists of the most probable soil type at the
            queried location, along with the top_k most
            probable soil types. The probability of each
            soil type is represented as an integer between
            0 and 100.
        """
        async with AsyncClient() as async_client:
            response = await async_client.get(
                self._soil_type_endpoint,
                params=self._params,
                timeout=httpx.Timeout(None),
            )
            return SoilTypeJSON(**response.json())


class SoilTypeSummaryRequest(BaseModel):
    """
    Request model for soil type summary data.

    Parameters
    ----------
    bounding_box : BoundingBox
        The bounding box to query for.

    Attributes
    ----------
    _soil_type_summary_endpoint : str
        The API endpoint for soil type summary requests.

    Methods
    -------
    _params()
        Generates the query parameters for the API request.
    get_sync()
        Synchronously retrieves the soil type summary data.
    get_async()
        Asynchronously retrieves the soil type summary data.
    """

    bounding_box: BoundingBox = Field(description="The bounding box to query for")

    _soil_type_summary_endpoint: str = (
        f"{openepi_settings.api_root_url}/soil/type/summary"
    )

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
            "min_lat": self.bounding_box.min_lat,
            "max_lat": self.bounding_box.max_lat,
            "min_lon": self.bounding_box.min_lon,
            "max_lon": self.bounding_box.max_lon,
        }

    def get_sync(self) -> SoilTypeSummaryJSON:
        """
        Synchronously retrieve soil type summary data.

        Returns
        -------
        SoilTypeSummaryJSON
            The soil type summary response data as a GeoJSON Feature object.
            Consists of a mapping of each soil type present to its
            number of occurrences in the bounding box.
        """
        with Client() as client:
            response = client.get(
                self._soil_type_summary_endpoint,
                params=self._params,
                timeout=httpx.Timeout(None),
            )
            return SoilTypeSummaryJSON(**response.json())

    async def get_async(self) -> SoilTypeSummaryJSON:
        """
        Asynchronously retrieve soil type summary data.

        Returns
        -------
        SoilTypeSummaryJSON
            The soil type summary response data as a GeoJSON Feature object.
            Consists of a mapping of each soil type present to its
            number of occurrences in the bounding box.
        """
        async with AsyncClient() as async_client:
            response = await async_client.get(
                self._soil_type_summary_endpoint,
                params=self._params,
                timeout=httpx.Timeout(None),
            )
            return SoilTypeSummaryJSON(**response.json())


class SoilPropertyRequest(BaseModel):
    """
    Request model for soil property data.

    Parameters
    ----------
    geolocation : GeoLocation
        The geolocation to query for.
    depths : list of str, optional
        List of depths to query for.
    properties : list of str, optional
        List of properties to query for.
    values : list of str, optional
        List of values to query for.

    Attributes
    ----------
    _soil_propery_endpoint : str
        The API endpoint for soil property requests.

    Methods
    -------
    _params()
        Generates the query parameters for the API request.
    get_sync()
        Synchronously retrieves the soil property data.
    get_async()
        Asynchronously retrieves the soil property data.
    """

    geolocation: GeoLocation = Field(description="The geolocation to query for")
    depths: list[str] = Field(
        ["0-5cm", "0-30cm", "5-15cm", "15-30cm", "30-60cm", "60-100cm", "100-200cm"],
        description="List of depths to query for",
    )
    properties: list[str] = Field(
        [
            "bdod",
            "cec",
            "cfvo",
            "clay",
            "nitrogen",
            "ocd",
            "ocs",
            "phh2o",
            "sand",
            "silt",
            "soc",
        ],
        description="List of properties to query for",
    )
    values: list[str] = Field(
        ["mean", "Q0.05", "Q0.5", "Q0.95", "uncertainty"],
        description="List of values to query for",
    )

    _soil_propery_endpoint: str = f"{openepi_settings.api_root_url}/soil/property"

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
            "lat": self.geolocation.lat,
            "lon": self.geolocation.lon,
            "depths": self.depths,
            "properties": self.properties,
            "values": self.values,
        }

    def get_sync(self) -> SoilPropertyJSON:
        """
        Synchronously retrieve soil property data.

        Returns
        -------
        SoilPropertyJSON
            The soil property response data as a GeoJSON Feature object.
            Consists of the values of the soil properties for the
            given location and depths.
            Note: The ocs (Organic carbon stocks) property is
            only available for the 0-30cm depth and vice versa.
            If the depth and property are incompatible, the
            response will not include the property.
        """
        with Client() as client:
            response = client.get(
                self._soil_propery_endpoint,
                params=self._params,
                timeout=httpx.Timeout(None),
            )
            return SoilPropertyJSON(**response.json())

    async def get_async(self) -> SoilPropertyJSON:
        """
        Asynchronously retrieve soil property data.

        Returns
        -------
        SoilPropertyJSON
            The soil property response data as a GeoJSON Feature object.
            Consists of the values of the soil properties for the
            given location and depths.
            Note: The ocs (Organic carbon stocks) property is
            only available for the 0-30cm depth and vice versa.
            If the depth and property are incompatible, the
            response will not include the property.
        """
        async with AsyncClient() as async_client:
            response = await async_client.get(
                self._soil_propery_endpoint,
                params=self._params,
                timeout=httpx.Timeout(None),
            )
            return SoilPropertyJSON(**response.json())


class SoilClient:
    """
    Client for synchronous soil data retrieval.

    Methods
    -------
    get_soil_type(geolocation, top_k)
        Get soil type data for a location.
    get_soil_property(geolocation, depths, properties, values)
        Get soil property data for a location.
    get_soil_type_summary(bounding_box)
        Get soil type summary data for a bounding box.
    """

    @staticmethod
    def get_soil_type(
        geolocation: GeoLocation,
        top_k: int = 0,
    ) -> SoilTypeJSON:
        """
        Get soil type data for a location.

        Parameters
        ----------
        geolocation : GeoLocation
            The geolocation to query for.
        top_k : int, optional
            The number of most probable soil types to return.

        Returns
        -------
        SoilTypeJSON
            The soil type response data as a GeoJSON Feature object.
            Consists of the most probable soil type at the
            queried location, along with the top_k most
            probable soil types. The probability of each
            soil type is represented as an integer between
            0 and 100.
        """
        return SoilTypeRequest(geolocation=geolocation, top_k=top_k).get_sync()

    @staticmethod
    def get_soil_property(
        geolocation: GeoLocation,
        depths: list[str] = [
            "0-5cm",
            "0-30cm",
            "5-15cm",
            "15-30cm",
            "30-60cm",
            "60-100cm",
            "100-200cm",
        ],
        properties: list[str] = [
            "bdod",
            "cec",
            "cfvo",
            "clay",
            "nitrogen",
            "ocd",
            "ocs",
            "phh2o",
            "sand",
            "silt",
            "soc",
        ],
        values: list[str] = ["mean", "Q0.05", "Q0.5", "Q0.95", "uncertainty"],
    ) -> SoilPropertyJSON:
        """
        Get soil property data for a location.

        Parameters
        ----------
        geolocation : GeoLocation
            The geolocation to query for.
        depths : list of str, optional
            List of depths to query for.
        properties : list of str, optional
            List of properties to query for.
        values : list of str, optional
            List of values to query for.

        Returns
        -------
        SoilPropertyJSON
            The soil property response data as a GeoJSON Feature object.
            Consists of the values of the soil properties for the
            given location and depths.
            Note: The ocs (Organic carbon stocks) property is
            only available for the 0-30cm depth and vice versa.
            If the depth and property are incompatible, the
            response will not include the property.
        """
        return SoilPropertyRequest(
            geolocation=geolocation, depths=depths, properties=properties, values=values
        ).get_sync()

    @staticmethod
    def get_soil_type_summary(
        bounding_box: BoundingBox,
    ) -> SoilTypeSummaryJSON:
        """
        Get soil type summary data for a bounding box.

        Parameters
        ----------
        bounding_box : BoundingBox
            The bounding box to query for.

        Returns
        -------
        SoilTypeSummaryJSON
            The soil type summary response data as a GeoJSON Feature object.
            Consists of a mapping of each soil type present to its
            number of occurrences in the bounding box.
        """
        return SoilTypeSummaryRequest(bounding_box=bounding_box).get_sync()


class AsyncSoilClient:
    """
    Client for asynchronous soil data retrieval.

    Methods
    -------
    get_soil_type(geolocation, top_k)
        Get soil type data for a location asynchronously.
    get_soil_property(geolocation, depths, properties, values)
        Get soil property data for a location asynchronously.
    get_soil_type_summary(bounding_box)
        Get soil type summary data for a bounding box asynchronously.
    """

    @staticmethod
    async def get_soil_type(
        geolocation: GeoLocation,
        top_k: int = 0,
    ) -> SoilTypeJSON:
        """
        Get soil type data for a location asynchronously.

        Parameters
        ----------
        geolocation : GeoLocation
            The geolocation to query for.
        top_k : int, optional
            The number of most probable soil types to return.

        Returns
        -------
        SoilTypeJSON
            The soil type response data as a GeoJSON Feature object.
            Consists of the most probable soil type at the
            queried location, along with the top_k most
            probable soil types. The probability of each
            soil type is represented as an integer between
            0 and 100.
        """
        return await SoilTypeRequest(geolocation=geolocation, top_k=top_k).get_async()

    @staticmethod
    async def get_soil_property(
        geolocation: GeoLocation,
        depths: list[str] = [
            "0-5cm",
            "0-30cm",
            "5-15cm",
            "15-30cm",
            "30-60cm",
            "60-100cm",
            "100-200cm",
        ],
        properties: list[str] = [
            "bdod",
            "cec",
            "cfvo",
            "clay",
            "nitrogen",
            "ocd",
            "ocs",
            "phh2o",
            "sand",
            "silt",
            "soc",
        ],
        values: list[str] = ["mean", "Q0.05", "Q0.5", "Q0.95", "uncertainty"],
    ) -> SoilPropertyJSON:
        """
        Get soil property data for a location asynchronously.

        Parameters
        ----------
        geolocation : GeoLocation
            The geolocation to query for.
        depths : list of str, optional
            List of depths to query for.
        properties : list of str, optional
            List of properties to query for.
        values : list of str, optional
            List of values to query for.

        Returns
        -------
        SoilPropertyJSON
            The soil property response data as a GeoJSON Feature object.
            Consists of the values of the soil properties for the
            given location and depths.
            Note: The ocs (Organic carbon stocks) property is
            only available for the 0-30cm depth and vice versa.
            If the depth and property are incompatible, the
            response will not include the property.
        """
        return await SoilPropertyRequest(
            geolocation=geolocation, depths=depths, properties=properties, values=values
        ).get_async()

    @staticmethod
    async def get_soil_type_summary(
        bounding_box: BoundingBox,
    ) -> SoilTypeSummaryJSON:
        """
        Get soil type summary data for a bounding box asynchronously.

        Parameters
        ----------
        bounding_box : BoundingBox
            The bounding box to query for.

        Returns
        -------
        SoilTypeSummaryJSON
            The soil type summary response data as a GeoJSON Feature object.
            Consists of a mapping of each soil type present to its
            number of occurrences in the bounding box.
        """
        return await SoilTypeSummaryRequest(bounding_box=bounding_box).get_async()
