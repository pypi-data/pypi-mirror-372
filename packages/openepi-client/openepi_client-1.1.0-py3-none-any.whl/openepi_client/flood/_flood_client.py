from datetime import date

from httpx import AsyncClient, Client
from pydantic import BaseModel, Field, model_validator, computed_field

from openepi_client import openepi_settings, BoundingBox, GeoLocation
from openepi_client.flood._flood_types import (
    ThresholdResponseModel,
    SummaryResponseModel,
    DetailedResponseModel,
)


class ThresholdRequest(BaseModel):
    """
    Request model for flood threshold data.

    Parameters
    ----------
    geolocation : GeoLocation, optional
        The geolocation to query for.
    bounding_box : BoundingBox, optional
        The bounding box to query for.

    Attributes
    ----------
    _threshold_endpoint : str
        The API endpoint for flood threshold requests.

    Methods
    -------
    check_mutually_exclusive()
        Ensures either geolocation or bounding_box is provided, but not both.
    _params()
        Generates the query parameters for the API request.
    get_sync()
        Synchronously retrieves the flood threshold data.
    get_async()
        Asynchronously retrieves the flood threshold data.
    """

    geolocation: GeoLocation | None = Field(
        default=None, description="The geolocation to query for"
    )

    bounding_box: BoundingBox | None = Field(
        default=None, description="The bounding box to query for"
    )

    _threshold_endpoint: str = f"{openepi_settings.api_root_url}/flood/threshold"

    @model_validator(mode="after")
    def check_mutually_exclusive(self) -> "ThresholdRequest":
        """
        Ensures either geolocation or bounding_box is provided, but not both.

        Raises
        ------
        ValueError
            If both geolocation and bounding_box are provided or if neither are provided.

        Returns
        -------
        ThresholdRequest
            The instance of the flood threshold request.
        """
        if not (self.geolocation is not None) ^ (self.bounding_box is not None):
            raise ValueError("Either specify a geolocation or a boundingbox.")
        return self

    @computed_field
    @property
    def _params(self) -> dict:
        """
        Generates the query parameters for the API request.
        If geolocation is provided, the lat and lon are used.
        Otherwise, the bounding box coordinates are used.

        Returns
        -------
        dict
            The query parameters.
        """
        if self.geolocation:
            return {"lat": self.geolocation.lat, "lon": self.geolocation.lon}
        else:
            return {
                "min_lat": self.bounding_box.min_lat,
                "max_lat": self.bounding_box.max_lat,
                "min_lon": self.bounding_box.min_lon,
                "max_lon": self.bounding_box.max_lon,
            }

    def get_sync(self) -> ThresholdResponseModel:
        """
        Synchronously retrieve flood threshold data.

        Returns
        -------
        ThresholdResponseModel
            The flood threshold response data as a JSON object
            with a `queried_location` key, itself being
            a GeoJSON FeatureCollection object.
            Consists of the 2-, 5-, and 20-year
            return period thresholds in m^3/s.
        """
        with Client() as client:
            response = client.get(self._threshold_endpoint, params=self._params)
            return ThresholdResponseModel(**response.json())

    async def get_async(self) -> ThresholdResponseModel:
        """
        Asynchronously retrieve flood threshold data.

        Returns
        -------
        ThresholdResponseModel
            The flood threshold response data as a JSON object
            with a `queried_location` key, itself being
            a GeoJSON FeatureCollection object.
            Consists of the 2-, 5-, and 20-year
            return period thresholds in m^3/s.
        """
        async with AsyncClient() as async_client:
            response = await async_client.get(
                self._threshold_endpoint, params=self._params
            )
            return ThresholdResponseModel(**response.json())


class SummaryRequest(BaseModel):
    """
    Request model for summary flood data.

    Parameters
    ----------
    geolocation : GeoLocation, optional
        The geolocation to query for.
    bounding_box : BoundingBox, optional
        The bounding box to query for.
    include_neighbors : bool, optional
        Whether to include neighboring locations.

    Attributes
    ----------
    _summary_endpoint : str
        The API endpoint for summary flood requests.

    Methods
    -------
    check_mutually_exclusive()
        Ensures either geolocation or bounding_box is provided, but not both.
    _params()
        Generates the query parameters for the API request.
    get_sync()
        Synchronously retrieves the summary flood data.
    get_async()
        Asynchronously retrieves the summary flood data.
    """

    geolocation: GeoLocation | None = Field(
        default=None, description="The geolocation to query for"
    )

    bounding_box: BoundingBox | None = Field(
        default=None, description="The bounding box to query for"
    )

    include_neighbors: bool | None = Field(
        default=False, description="Whether to include neighboring locations"
    )

    _summary_endpoint: str = f"{openepi_settings.api_root_url}/flood/summary"

    @model_validator(mode="after")
    def check_mutually_exclusive(self) -> "SummaryRequest":
        """
        Ensures either geolocation or bounding_box is provided, but not both.

        Raises
        ------
        ValueError
            If both geolocation and bounding_box are provided or if neither are provided.

        Returns
        -------
        SummaryRequest
            The instance of the summary flood request.
        """
        if not (self.geolocation is not None) ^ (self.bounding_box is not None):
            raise ValueError("Either specify a geolocation or a boundingbox.")
        return self

    @computed_field
    @property
    def _params(self) -> dict:
        """
        Generates the query parameters for the API request.
        If geolocation is provided, the lat and lon are used.
        Otherwise, the bounding box coordinates are used.

        Returns
        -------
        dict
            The query parameters.
        """
        params = {"include_neighbors": self.include_neighbors}
        if self.geolocation:
            params.update({"lat": self.geolocation.lat, "lon": self.geolocation.lon})
        else:
            params.update(
                {
                    "min_lat": self.bounding_box.min_lat,
                    "max_lat": self.bounding_box.max_lat,
                    "min_lon": self.bounding_box.min_lon,
                    "max_lon": self.bounding_box.max_lon,
                }
            )
        return {k: v for k, v in params.items() if v is not None}

    def get_sync(self) -> SummaryResponseModel:
        """
        Synchronously retrieve summary flood data.

        Returns
        -------
        SummaryResponseModel
            The summary flood response data as a JSON object with
            `queried_location` and `neighboring_location` keys,
            both being GeoJSON FeatureCollection objects.
            Consists of a 30-day summary of forecasted
            flooding in the queried location.
        """
        with Client() as client:
            response = client.get(self._summary_endpoint, params=self._params)
            return SummaryResponseModel(**response.json())

    async def get_async(self) -> SummaryResponseModel:
        """
        Asynchronously retrieve summary data.

        Returns
        -------
        SummaryResponseModel
            The summary flood response data as a JSON object with
            `queried_location` and `neighboring_location` keys,
            both being GeoJSON FeatureCollection objects.
            Consists of a 30-day summary of forecasted
            flooding in the queried location.
        """
        async with AsyncClient() as async_client:
            response = await async_client.get(
                self._summary_endpoint, params=self._params
            )
            return SummaryResponseModel(**response.json())


class DetailedRequest(BaseModel):
    """
    Request model for detailed flood data.

    Parameters
    ----------
    geolocation : GeoLocation, optional
        The geolocation to query for.
    bounding_box : BoundingBox, optional
        The bounding box to query for.
    include_neighbors : bool, optional
        Whether to include neighboring locations.
    start_date : date, optional
        The start date of the query.
    end_date : date, optional
        The end date of the query.

    Attributes
    ----------
    _detailed_endpoint : str
        The API endpoint for detailed flood requests.

    Methods
    -------
    check_mutually_exclusive()
        Ensures either geolocation or bounding_box is provided, but not both.
    _params()
        Generates the query parameters for the API request.
    get_sync()
        Synchronously retrieves the detailed flood data.
    get_async()
        Asynchronously retrieves the detailed flood data.
    """

    geolocation: GeoLocation | None = Field(
        default=None, description="The geolocation to query for"
    )

    bounding_box: BoundingBox | None = Field(
        default=None, description="The bounding box to query for"
    )

    include_neighbors: bool | None = Field(
        default=False, description="Whether to include neighboring locations"
    )

    start_date: date | None = Field(
        default=None, description="The start date of the query"
    )

    end_date: date | None = Field(default=None, description="The end date of the query")

    _detailed_endpoint: str = f"{openepi_settings.api_root_url}/flood/detailed"

    @model_validator(mode="after")
    def check_mutually_exclusive(self) -> "DetailedRequest":
        """
        Ensures either geolocation or bounding_box is provided, but not both.

        Raises
        ------
        ValueError
            If both geolocation and bounding_box are provided or if neither are provided.

        Returns
        -------
        DetailedRequest
            The instance of the detailed flood request.
        """
        if not (self.geolocation is not None) ^ (self.bounding_box is not None):
            raise ValueError("Either specify a geolocation or a boundingbox.")
        return self

    @computed_field
    @property
    def _params(self) -> dict:
        """
        Generates the query parameters for the API request.
        If geolocation is provided, the lat and lon are used.
        Otherwise, the bounding box coordinates are used.

        Returns
        -------
        dict
            The query parameters.
        """
        params = {
            "include_neighbors": self.include_neighbors,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
        }
        if self.geolocation:
            params.update({"lat": self.geolocation.lat, "lon": self.geolocation.lon})
        else:
            params.update(
                {
                    "min_lat": self.bounding_box.min_lat,
                    "max_lat": self.bounding_box.max_lat,
                    "min_lon": self.bounding_box.min_lon,
                    "max_lon": self.bounding_box.max_lon,
                }
            )
        return {k: v for k, v in params.items() if v is not None}

    def get_sync(self) -> DetailedResponseModel:
        """
        Synchronously retrieve detailed flood data.

        Returns
        -------
        DetailedResponseModel
            The detailed flood response data as a JSON object with
            `queried_location` and `neighboring_location` keys,
            both being GeoJSON FeatureCollection objects.
            Consists of a detailed forecast of flooding
            in the queried location over the specified time period,
            at most 30 days into the future.
        """
        with Client() as client:
            response = client.get(
                self._detailed_endpoint,
                params=self._params,
            )
            return DetailedResponseModel(**response.json())

    async def get_async(self) -> DetailedResponseModel:
        """
        Asynchronously retrieve detailed flood data.

        Returns
        -------
        DetailedResponseModel
            The detailed flood response data as a JSON object with
            `queried_location` and `neighboring_location` keys,
            both being GeoJSON FeatureCollection objects.
            Consists of a detailed forecast of flooding
            in the queried location over the specified time period,
            at most 30 days into the future.
        """
        async with AsyncClient() as async_client:
            response = await async_client.get(
                self._detailed_endpoint,
                params=self._params,
            )
            return DetailedResponseModel(**response.json())


class FloodClient:
    """
    Client for synchronous flood data retrieval.

    Methods
    -------
    get_threshold(geolocation, bounding_box)
        Get flood threshold data for a location or bounding box.
    get_summary(geolocation, bounding_box, include_neighbors)
        Get summary flood data for a location or bounding box.
    get_detailed(geolocation, bounding_box, include_neighbors, start_date, end_date)
        Get detailed flood data for a location or bounding box.
    """

    @staticmethod
    def get_threshold(
        geolocation: GeoLocation | None = None, bounding_box: BoundingBox | None = None
    ) -> ThresholdResponseModel:
        """
        Get flood threshold data for a location or bounding box.

        Parameters
        ----------
        geolocation : GeoLocation, optional
            The geolocation to query for.
        bounding_box : BoundingBox, optional
            The bounding box to query for.

        Returns
        -------
        ThresholdResponseModel
            The flood threshold response data as a JSON object
            with a `queried_location` key, itself being
            a GeoJSON FeatureCollection object.
            Consists of the 2-, 5-, and 20-year
            return period thresholds in m^3/s.
        """
        return ThresholdRequest(
            geolocation=geolocation, bounding_box=bounding_box
        ).get_sync()

    @staticmethod
    def get_summary(
        geolocation: GeoLocation | None = None,
        bounding_box: BoundingBox | None = None,
        include_neighbors: bool | None = False,
    ) -> SummaryResponseModel:
        """
        Get summary flood data for a location or bounding box.

        Parameters
        ----------
        geolocation : GeoLocation, optional
            The geolocation to query for.
        bounding_box : BoundingBox, optional
            The bounding box to query for.
        include_neighbors : bool, optional
            Whether to include neighboring locations.

        Returns
        -------
        SummaryResponseModel
            The summary flood response data as a JSON object with
            `queried_location` and `neighboring_location` keys,
            both being GeoJSON FeatureCollection objects.
            Consists of a 30-day summary of forecasted
            flooding in the queried location.
        """
        return SummaryRequest(
            geolocation=geolocation,
            bounding_box=bounding_box,
            include_neighbors=include_neighbors,
        ).get_sync()

    @staticmethod
    def get_detailed(
        geolocation: GeoLocation | None = None,
        bounding_box: BoundingBox | None = None,
        include_neighbors: bool | None = False,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> DetailedResponseModel:
        """
        Get detailed flood data for a location or bounding box.

        Parameters
        ----------
        geolocation : GeoLocation, optional
            The geolocation to query for.
        bounding_box : BoundingBox, optional
            The bounding box to query for.
        include_neighbors : bool, optional
            Whether to include neighboring locations.
        start_date : date, optional
            The start date of the query.
        end_date : date, optional
            The end date of the query.

        Returns
        -------
        DetailedResponseModel
            The detailed flood response data as a JSON object with
            `queried_location` and `neighboring_location` keys,
            both being GeoJSON FeatureCollection objects.
            Consists of a detailed forecast of flooding
            in the queried location over the specified time period,
            at most 30 days into the future.
        """
        return DetailedRequest(
            geolocation=geolocation,
            bounding_box=bounding_box,
            include_neighbors=include_neighbors,
            start_date=start_date,
            end_date=end_date,
        ).get_sync()


class AsyncFloodClient:
    """
    Client for asynchronous flood data retrieval.

    Methods
    -------
    get_threshold(geolocation, bounding_box)
        Get flood threshold data for a location or bounding box asynchronously.
    get_summary(geolocation, bounding_box)
        Get summary flood data for a location or bounding box asynchronously.
    get_detailed(geolocation, bounding_box, include_neighbors, start_date, end_date)
        Get detailed flood data for a location or bounding box asynchronously.
    """

    @staticmethod
    async def get_threshold(
        geolocation: GeoLocation | None = None, bounding_box: BoundingBox | None = None
    ) -> ThresholdResponseModel:
        """
        Get flood threshold data for a location or bounding box asynchronously.

        Parameters
        ----------
        geolocation : GeoLocation, optional
            The geolocation to query for.
        bounding_box : BoundingBox, optional
            The bounding box to query for.

        Returns
        -------
        ThresholdResponseModel
            The flood threshold response data as a JSON object
            with a `queried_location` key, itself being
            a GeoJSON FeatureCollection object.
            Consists of the 2-, 5-, and 20-year
            return period thresholds in m^3/s.
        """
        return await ThresholdRequest(
            geolocation=geolocation, bounding_box=bounding_box
        ).get_async()

    @staticmethod
    async def get_summary(
        geolocation: GeoLocation | None = None, bounding_box: BoundingBox | None = None
    ) -> SummaryResponseModel:
        """
        Get summary flood data for a location or bounding box asynchronously.

        Parameters
        ----------
        geolocation : GeoLocation, optional
            The geolocation to query for.
        bounding_box : BoundingBox, optional
            The bounding box to query for.

        Returns
        -------
        SummaryResponseModel
            The summary flood response data as a JSON object with
            `queried_location` and `neighboring_location` keys,
            both being GeoJSON FeatureCollection objects.
            Consists of a 30-day summary of forecasted
            flooding in the queried location.
        """
        return await SummaryRequest(
            geolocation=geolocation, bounding_box=bounding_box
        ).get_async()

    @staticmethod
    async def get_detailed(
        geolocation: GeoLocation | None = None,
        bounding_box: BoundingBox | None = None,
        include_neighbors: bool | None = False,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> DetailedResponseModel:
        """
        Get detailed flood data for a location or bounding box asynchronously.

        Parameters
        ----------
        geolocation : GeoLocation, optional
            The geolocation to query for.
        bounding_box : BoundingBox, optional
            The bounding box to query for.
        include_neighbors : bool, optional
            Whether to include neighboring locations.
        start_date : date, optional
            The start date of the query.
        end_date : date, optional
            The end date of the query.

        Returns
        -------
        DetailedResponseModel
            The detailed flood response data as a JSON object with
            `queried_location` and `neighboring_location` keys,
            both being GeoJSON FeatureCollection objects.
            Consists of a detailed forecast of flooding
            in the queried location over the specified time period,
            at most 30 days into the future.
        """
        return await DetailedRequest(
            geolocation=geolocation,
            bounding_box=bounding_box,
            include_neighbors=include_neighbors,
            start_date=start_date,
            end_date=end_date,
        ).get_async()
