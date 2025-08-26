from pydantic import BaseModel, Field, computed_field, model_validator
from httpx import AsyncClient, Client

from openepi_client import openepi_settings
from openepi_client.crop_health._crop_health_types import (
    SingleHLTPredictionResponse,
    MultiHLTPredictionResponse,
    BinaryPredictionResponse,
)


class PredictionRequest(BaseModel):
    """
    Base class for prediction requests.

    Parameters
    ----------
    image_data : bytes
        The image data as bytes.

    Attributes
    ----------
    _prediction_endpoint : str
        The endpoint URL for predictions.

    Methods
    -------
    check_image_data()
        Validates that image data is provided and non-empty.
    _content()
        Returns the image data as bytes.
    """

    image_data: bytes = Field(..., description="The image data as bytes")

    _prediction_endpoint: str = (
        f"{openepi_settings.api_root_url}/crop-health/predictions"
    )

    @model_validator(mode="after")
    def check_image_data(self) -> "PredictionRequest":
        """
        Validates that image data is provided and non-empty.

        Raises
        ------
        ValueError
            If image data is not provided or is empty.

        Returns
        -------
        PredictionRequest
            The instance of the prediction request.
        """
        if not self.image_data:
            raise ValueError("Image data must be provided and non-empty")
        return self

    @computed_field
    @property
    def _content(self) -> bytes:
        """
        Returns the image data as bytes.

        Returns
        -------
        bytes
            The image data as bytes.
        """
        return self.image_data


class BinaryPredictionRequest(PredictionRequest):
    """
    Request class for binary predictions.

    Methods
    -------
    get_sync()
        Synchronously gets a binary prediction.
    get_async()
        Asynchronously gets a binary prediction.
    """

    def get_sync(self) -> BinaryPredictionResponse:
        """
        Synchronously gets a binary prediction.

        Returns
        -------
        BinaryPredictionResponse
            The response containing the binary prediction as a JSON object.
            Consists of a mapping of the binary model classes
            to their respective confidence scores.
        """
        with Client() as client:
            response = client.post(
                f"{self._prediction_endpoint}/binary", content=self._content
            )
            return BinaryPredictionResponse(**response.json())

    async def get_async(self) -> BinaryPredictionResponse:
        """
        Asynchronously gets a binary prediction.

        Returns
        -------
        BinaryPredictionResponse
            The response containing the binary prediction as a JSON object.
            Consists of a mapping of the binary model classes
            to their respective confidence scores.
        """
        async with AsyncClient() as async_client:
            response = await async_client.post(
                f"{self._prediction_endpoint}/binary", content=self._content
            )
            return BinaryPredictionResponse(**response.json())


class SingleHLTPredictionRequest(PredictionRequest):
    """
    Request class for single HLT predictions.

    Methods
    -------
    get_sync()
        Synchronously gets a single HLT prediction.
    get_async()
        Asynchronously gets a single HLT prediction.
    """

    def get_sync(self) -> SingleHLTPredictionResponse:
        """
        Synchronously gets a single HLT prediction.

        Returns
        -------
        SingleHLTPredictionResponse
            The response containing the single HLT prediction as a JSON object.
            Consists of a mapping of the single HLT model classes
            to their respective confidence scores.
        """
        with Client() as client:
            response = client.post(
                f"{self._prediction_endpoint}/single-HLT", content=self._content
            )
            return SingleHLTPredictionResponse(**response.json())

    async def get_async(self) -> SingleHLTPredictionResponse:
        """
        Asynchronously gets a single HLT prediction.

        Returns
        -------
        SingleHLTPredictionResponse
            The response containing the single HLT prediction as a JSON object.
            Consists of a mapping of the single HLT model classes
            to their respective confidence scores.
        """
        async with AsyncClient() as async_client:
            response = await async_client.post(
                f"{self._prediction_endpoint}/single-HLT", content=self._content
            )
            return SingleHLTPredictionResponse(**response.json())


class MultiHLTPredictionRequest(PredictionRequest):
    """
    Request class for multi HLT predictions.

    Methods
    -------
    get_sync()
        Synchronously gets a multi HLT prediction.
    get_async()
        Asynchronously gets a multi HLT prediction.
    """

    def get_sync(self) -> MultiHLTPredictionResponse:
        """
        Synchronously gets a multi HLT prediction.

        Returns
        -------
        MultiHLTPredictionResponse
            The response containing the multi HLT prediction as a JSON object.
            Consists of a mapping of the multi HLT model classes
            to their respective confidence scores.
        """
        with Client() as client:
            response = client.post(
                f"{self._prediction_endpoint}/multi-HLT", content=self._content
            )
            return MultiHLTPredictionResponse(**response.json())

    async def get_async(self) -> MultiHLTPredictionResponse:
        """
        Asynchronously gets a multi HLT prediction.

        Returns
        -------
        MultiHLTPredictionResponse
            The response containing the multi HLT prediction as a JSON object.
            Consists of a mapping of the multi HLT model classes
            to their respective confidence scores.
        """
        async with AsyncClient() as async_client:
            response = await async_client.post(
                f"{self._prediction_endpoint}/multi-HLT", content=self._content
            )
            return MultiHLTPredictionResponse(**response.json())


class CropHealthClient:
    """
    Client class for synchronous crop health predictions.

    Methods
    -------
    get_binary_prediction(image_data)
        Gets a binary prediction for the given image data.
    get_singleHLT_prediction(image_data)
        Gets a single HLT prediction for the given image data.
    get_multiHLT_prediction(image_data)
        Gets a multi HLT prediction for the given image data.
    """

    @staticmethod
    def get_binary_prediction(
        image_data: bytes,
    ) -> BinaryPredictionResponse:
        """
        Gets a binary prediction for the given image data.

        Parameters
        ----------
        image_data : bytes
            The image data as bytes.

        Returns
        -------
        BinaryPredictionResponse
            The response containing the binary prediction results as a JSON object.
            Consists of a mapping of the binary model classes
            to their respective confidence scores.
        """
        return BinaryPredictionRequest(image_data=image_data).get_sync()

    @staticmethod
    def get_singleHLT_prediction(
        image_data: bytes,
    ) -> SingleHLTPredictionResponse:
        """
        Gets a single HLT prediction for the given image data.

        Parameters
        ----------
        image_data : bytes
            The image data as bytes.

        Returns
        -------
        SingleHLTPredictionResponse
            The response containing the single HLT prediction results as a JSON object.
            Consists of a mapping of the single HLT model classes
            to their respective confidence scores.
        """
        return SingleHLTPredictionRequest(image_data=image_data).get_sync()

    @staticmethod
    def get_multiHLT_prediction(
        image_data: bytes,
    ) -> MultiHLTPredictionResponse:
        """
        Gets a multi HLT prediction for the given image data.

        Parameters
        ----------
        image_data : bytes
            The image data as bytes.

        Returns
        -------
        MultiHLTPredictionResponse
            The response containing the multi HLT prediction results as a JSON object.
            Consists of a mapping of the multi HLT model classes
            to their respective confidence scores.
        """
        return MultiHLTPredictionRequest(image_data=image_data).get_sync()


class AsyncCropHealthClient:
    """
    Client class for asynchronous crop health predictions.

    Methods
    -------
    get_binary_prediction(image_data)
        Gets a binary prediction for the given image data asynchronously.
    get_singleHLT_prediction(image_data)
        Gets a single HLT prediction for the given image data asynchronously.
    get_multiHLT_prediction(image_data)
        Gets a multi HLT prediction for the given image data asynchronously.
    """

    @staticmethod
    async def get_binary_prediction(
        image_data: bytes,
    ) -> BinaryPredictionResponse:
        """
        Gets a binary prediction for the given image data asynchronously.

        Parameters
        ----------
        image_data : bytes
            The image data as bytes.

        Returns
        -------
        BinaryPredictionResponse
            The response containing the binary prediction results as a JSON object.
            Consists of a mapping of the binary model classes
            to their respective confidence scores.
        """
        return await BinaryPredictionRequest(image_data=image_data).get_async()

    @staticmethod
    async def get_singleHLT_prediction(
        image_data: bytes,
    ) -> SingleHLTPredictionResponse:
        """
        Gets a single HLT prediction for the given image data asynchronously.

        Parameters
        ----------
        image_data : bytes
            The image data as bytes.

        Returns
        -------
        SingleHLTPredictionResponse
            The response containing the single HLT prediction results as a JSON object.
            Consists of a mapping of the single HLT model classes
            to their respective confidence scores.
        """
        return await SingleHLTPredictionRequest(image_data=image_data).get_async()

    @staticmethod
    async def get_multiHLT_prediction(
        image_data: bytes,
    ) -> MultiHLTPredictionResponse:
        """
        Gets a multi HLT prediction for the given image data asynchronously.

        Parameters
        ----------
        image_data : bytes
            The image data as bytes.

        Returns
        -------
        MultiHLTPredictionResponse
            The response containing the multi HLT prediction results as a JSON object.
            Consists of a mapping of the multi HLT model classes
            to their respective confidence scores.
        """
        return await MultiHLTPredictionRequest(image_data=image_data).get_async()
