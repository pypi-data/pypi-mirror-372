from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class Type(Enum):
    Feature = "Feature"


class SolarTime(BaseModel):
    time: str = Field(..., examples=["2019-12-03T13:52:13Z"])


class SunriseForecast(BaseModel):
    body: str
    sunrise: SolarTime
    sunset: SolarTime


class GeometryType(Enum):
    Point = "Point"


class PointGeometry(BaseModel):
    coordinates: List[float] = Field(
        description="[longitude, latitude, altitude]. All numbers in decimal.",
        examples=[60.5, 11.59, 1001],
        min_length=2,
    )
    type: GeometryType


class METJSONSunrise(BaseModel):
    copyright: str
    licenseURL: str
    type: Type = Field(..., examples=["Feature"])
    geometry: PointGeometry
    properties: SunriseForecast


class ForecastTimeInstant(BaseModel):
    air_pressure_at_sea_level: Optional[float] = Field(
        None, examples=[1017.23], description="Air pressure at sea level"
    )
    air_temperature: Optional[float] = Field(
        None, examples=[17.1], description="Air temperature"
    )
    cloud_area_fraction: Optional[float] = Field(
        None, examples=[95.2], description="Amount of sky covered by clouds."
    )
    cloud_area_fraction_high: Optional[float] = Field(
        None,
        examples=[95.2],
        description="Amount of sky covered by clouds at high elevation.",
    )
    cloud_area_fraction_low: Optional[float] = Field(
        None,
        examples=[95.2],
        description="Amount of sky covered by clouds at low elevation.",
    )
    cloud_area_fraction_medium: Optional[float] = Field(
        None,
        examples=[95.2],
        description="Amount of sky covered by clouds at medium elevation.",
    )
    dew_point_temperature: Optional[float] = Field(
        None, examples=[8.1], description="Dew point temperature at sea level"
    )
    fog_area_fraction: Optional[float] = Field(
        None, examples=[95.2], description="Amount of area covered by fog."
    )
    relative_humidity: Optional[float] = Field(
        None, examples=[81.1], description="Amount of humidity in the air."
    )
    wind_from_direction: Optional[float] = Field(
        None, examples=[121.3], description="The directon which moves towards"
    )
    wind_speed: Optional[float] = Field(
        None, examples=[5.9], description="Speed of wind"
    )
    wind_speed_of_gust: Optional[float] = Field(
        None, examples=[15.9], description="Speed of wind gust"
    )


class ForecastTimePeriod(BaseModel):
    air_temperature_max: Optional[float] = Field(
        None, examples=[17.1], description="Maximum air temperature in period"
    )

    air_temperature_min: Optional[float] = Field(
        None, examples=[11.1], description="Minimum air temperature in period"
    )

    precipitation_amount: Optional[float] = Field(
        None,
        examples=[1.71],
        description="Best estimate for amount of precipitation for this period",
    )

    precipitation_amount_max: Optional[float] = Field(
        None,
        examples=[4.32],
        description="Maximum amount of precipitation for this period" "",
    )

    precipitation_amount_min: Optional[float] = Field(
        None,
        examples=[4.32],
        description="Minimum amount of precipitation for this period",
    )

    probability_of_precipitation: Optional[float] = Field(
        None,
        examples=[37.0],
        description="Probability of any precipitation coming for this period",
    )

    probability_of_thunder: Optional[float] = Field(
        None,
        examples=[54.32],
        description="Probability of any thunder coming for this period",
    )

    ultraviolet_index_clear_sky_max: Optional[float] = Field(
        None, examples=[1.0], description="Maximum ultraviolet index if sky is clear"
    )


class Instant(BaseModel):
    details: Optional[ForecastTimeInstant] = None


class ForecastUnits(BaseModel):
    air_pressure_at_sea_level: Optional[str] = Field(None, examples=["hPa"])
    air_temperature: Optional[str] = Field(None, examples=["C"])
    air_temperature_max: Optional[str] = Field(None, examples=["C"])
    air_temperature_min: Optional[str] = Field(None, examples=["C"])
    cloud_area_fraction: Optional[str] = Field(None, examples=["%"])
    cloud_area_fraction_high: Optional[str] = Field(None, examples=["%"])
    cloud_area_fraction_low: Optional[str] = Field(None, examples=["%"])
    cloud_area_fraction_medium: Optional[str] = Field(None, examples=["%"])
    dew_point_temperature: Optional[str] = Field(None, examples=["C"])
    fog_area_fraction: Optional[str] = Field(None, examples=["%"])
    precipitation_amount: Optional[str] = Field(None, examples=["mm"])
    precipitation_amount_max: Optional[str] = Field(None, examples=["mm"])
    precipitation_amount_min: Optional[str] = Field(None, examples=["mm"])
    probability_of_precipitation: Optional[str] = Field(None, examples=["%"])
    probability_of_thunder: Optional[str] = Field(None, examples=["%"])
    relative_humidity: Optional[str] = Field(None, examples=["%"])
    ultraviolet_index_clear_sky_max: Optional[str] = Field(None, examples=["1"])
    wind_from_direction: Optional[str] = Field(None, examples=["degrees"])
    wind_speed: Optional[str] = Field(None, examples=["m/s"])
    wind_speed_of_gust: Optional[str] = Field(None, examples=["m/s"])


class FeatureType(Enum):
    Feature = "Feature"


class WeatherSymbol(Enum):
    ClearSkyDay = "clearsky_day"
    ClearSkyNight = "clearsky_night"
    ClearSkyPolarTwilight = "clearsky_polartwilight"
    FairDay = "fair_day"
    FairNight = "fair_night"
    FairPolarTwilight = "fair_polartwilight"
    LightsSnowShowersAndThunderDay = "lightssnowshowersandthunder_day"
    LightsSnowShowersAndThunderNight = "lightssnowshowersandthunder_night"
    LightsSnowShowersAndThunderPolarTwilight = (
        "lightssnowshowersandthunder_polartwilight"
    )
    LightSnowShowersDay = "lightsnowshowers_day"
    LightSnowShowersNight = "lightsnowshowers_night"
    LightSnowShowersPolarTwilight = "lightsnowshowers_polartwilight"
    HeavyRainAndThunder = "heavyrainandthunder"
    HeavySnowAndThunder = "heavysnowandthunder"
    RainAndThunder = "rainandthunder"
    HeavySleetShowersAndThunderDay = "heavysleetshowersandthunder_day"
    HeavySleetShowersAndThunderNight = "heavysleetshowersandthunder_night"
    HeavySleetShowersAndThunderPolarTwilight = (
        "heavysleetshowersandthunder_polartwilight"
    )
    HeavySnow = "heavysnow"
    HeavyRainShowersDay = "heavyrainshowers_day"
    HeavyRainShowersNight = "heavyrainshowers_night"
    HeavyRainShowersPolarTwilight = "heavyrainshowers_polartwilight"
    LightSleet = "lightsleet"
    HeavyRain = "heavyrain"
    LightRainShowersDay = "lightrainshowers_day"
    LightRainShowersNight = "lightrainshowers_night"
    LightRainShowersPolarTwilight = "lightrainshowers_polartwilight"
    HeavySleetShowersDay = "heavysleetshowers_day"
    HeavySleetShowersNight = "heavysleetshowers_night"
    HeavySleetShowersPolarTwilight = "heavysleetshowers_polartwilight"
    LightSleetShowersDay = "lightsleetshowers_day"
    LightSleetShowersNight = "lightsleetshowers_night"
    LightSleetShowersPolarTwilight = "lightsleetshowers_polartwilight"
    Snow = "snow"
    HeavyRainShowersAndThunderDay = "heavyrainshowersandthunder_day"
    HeavyRainShowersAndThunderNight = "heavyrainshowersandthunder_night"
    HeavyRainShowersAndThunderPolarTwilight = "heavyrainshowersandthunder_polartwilight"
    SnowShowersDay = "snowshowers_day"
    SnowShowersNight = "snowshowers_night"
    SnowShowersPolarTwilight = "snowshowers_polartwilight"
    Fog = "fog"
    SnowShowersAndThunderDay = "snowshowersandthunder_day"
    SnowShowersAndThunderNight = "snowshowersandthunder_night"
    SnowShowersAndThunderPolarTwilight = "snowshowersandthunder_polartwilight"
    LightSnowAndThunder = "lightsnowandthunder"
    HeavySleetAndThunder = "heavysleetandthunder"
    LightRain = "lightrain"
    RainShowersAndThunderDay = "rainshowersandthunder_day"
    RainShowersAndThunderNight = "rainshowersandthunder_night"
    RainShowersAndThunderPolarTwilight = "rainshowersandthunder_polartwilight"
    Rain = "rain"
    LightSnow = "lightsnow"
    LightRainShowersAndThunderDay = "lightrainshowersandthunder_day"
    LightRainShowersAndThunderNight = "lightrainshowersandthunder_night"
    LightRainShowersAndThunderPolarTwilight = "lightrainshowersandthunder_polartwilight"
    HeavySleet = "heavysleet"
    SleetAndThunder = "sleetandthunder"
    LightRainAndThunder = "lightrainandthunder"
    Sleet = "sleet"
    LightsSleetShowersAndThunderDay = "lightssleetshowersandthunder_day"
    LightsSleetShowersAndThunderNight = "lightssleetshowersandthunder_night"
    LightsSleetShowersAndThunderPolarTwilight = (
        "lightssleetshowersandthunder_polartwilight"
    )
    LightSleetAndThunder = "lightsleetandthunder"
    PartlyCloudyDay = "partlycloudy_day"
    PartlyCloudyNight = "partlycloudy_night"
    PartlyCloudyPolarTwilight = "partlycloudy_polartwilight"
    SleetShowersAndThunderDay = "sleetshowersandthunder_day"
    SleetShowersAndThunderNight = "sleetshowersandthunder_night"
    SleetShowersAndThunderPolarTwilight = "sleetshowersandthunder_polartwilight"
    RainShowersDay = "rainshowers_day"
    RainShowersNight = "rainshowers_night"
    RainShowersPolarTwilight = "rainshowers_polartwilight"
    SnowAndThunder = "snowandthunder"
    SleetShowersDay = "sleetshowers_day"
    SleetShowersNight = "sleetshowers_night"
    SleetShowersPolarTwilight = "sleetshowers_polartwilight"
    Cloudy = "cloudy"
    HeavySnowShowersAndThunderDay = "heavysnowshowersandthunder_day"
    HeavySnowShowersAndThunderNight = "heavysnowshowersandthunder_night"
    HeavySnowShowersAndThunderPolarTwilight = "heavysnowshowersandthunder_polartwilight"
    HeavySnowShowersDay = "heavysnowshowers_day"
    HeavySnowShowersNight = "heavysnowshowers_night"
    HeavySnowShowersPolarTwilight = "heavysnowshowers_polartwilight"


class Meta(BaseModel):
    units: ForecastUnits
    updated_at: str = Field(
        description="Update time for this forecast", examples=["2019-12-03T13:52:13Z"]
    )


class ForecastSummary(BaseModel):
    symbol_code: WeatherSymbol


class Next12Hours(BaseModel):
    details: ForecastTimePeriod
    summary: ForecastSummary


class Next1Hours(BaseModel):
    details: ForecastTimePeriod
    summary: ForecastSummary


class Next6Hours(BaseModel):
    details: ForecastTimePeriod
    summary: ForecastSummary


class Data(BaseModel):
    instant: Instant = Field(
        description="Parameters which applies to this exact point in time"
    )
    next_12_hours: Optional[Next12Hours] = Field(
        default=None,
        description="Parameters with validity times over twelve hours. Will not exist for all time steps.",
    )
    next_1_hours: Optional[Next1Hours] = Field(
        default=None,
        description="Parameters with validity times over one hour. Will not exist for all time steps.",
    )
    next_6_hours: Optional[Next6Hours] = Field(
        default=None,
        description="Parameters with validity times over six hours. Will not exist for all time steps.",
    )


class ForecastTimeStep(BaseModel):
    data: Data = Field(description="Forecast for a specific time")
    time: str = Field(
        description="The time these forecast values are valid for. Timestamp in format YYYY-MM-DDThh:mm:ssZ (ISO 8601)",
        examples=["2019-12-03T14:00:00Z"],
    )


class Forecast(BaseModel):
    meta: Meta
    timeseries: List[ForecastTimeStep]


class METJSONForecast(BaseModel):
    geometry: PointGeometry
    properties: Forecast
    type: FeatureType = Field(
        description="The feature type of this geojson-object",
        default=FeatureType.Feature,
        examples=["Feature"],
    )
