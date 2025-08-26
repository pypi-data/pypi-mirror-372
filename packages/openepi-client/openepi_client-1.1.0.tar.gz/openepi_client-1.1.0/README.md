# openepi-client
A python client for accessing data from OpenEPI.
Can be installed from PyPI on [https://pypi.org/project/openepi-client/](https://pypi.org/project/openepi-client/)

## Table of Contents
- [Weather Data](#weather)
  - [Sync usage](#sync-usage)
  - [Async usage](#async-usage)
- [Geocoding](#geocoding)
  - [Sync usage](#sync-usage-1)
  - [Async usage](#async-usage-1)
- [Flood predictions](#flood)
  - [Sync usage](#sync-usage-2)
  - [Async usage](#async-usage-2)
- [Deforestation](#deforestation)
  - [Sync usage](#sync-usage-3)
  - [Async usage](#async-usage-3)
- [Soil Information](#soil)
  - [Sync usage](#sync-usage-4) 
  - [Async usage](#async-usage-4)
- [Crop Health Information](#crop-health)
  - [Sync usage](#sync-usage-5)
  - [Sync usage](#async-usage-5)

## Weather
### Sync usage
```python
from openepi_client import GeoLocation
from openepi_client.weather import WeatherClient

# Getting the sunrise and sunset times for a location
sunrise_sunset = WeatherClient.get_sunrise(geolocation=GeoLocation(lat=51.5074, lon=0.1278))

# Getting the weather forecast for a location
forecast = WeatherClient.get_location_forecast(geolocation=GeoLocation(lat=51.5074, lon=0.1278, alt=0))
```

### Async usage
```python
from openepi_client import GeoLocation
from openepi_client.weather import AsyncWeatherClient

# Getting the sunrise and sunset times for a location
sunrise_sunset = await AsyncWeatherClient.get_sunrise(geolocation=GeoLocation(lat=51.5074, lon=0.1278))

# Getting the weather forecast for a location
forecast = await AsyncWeatherClient.get_location_forecast(geolocation=GeoLocation(lat=51.5074, lon=0.1278, alt=0))
```

## Geocoding
### Sync usage
```python
from openepi_client import GeoLocation
from openepi_client.geocoding import GeocodeClient

# Searching for the coordinates to a named place
feature_collection = GeocodeClient.geocode(q="Kigali, Rwanda")

# Geocode with priority to a lat and lon
feature_collection = GeocodeClient.geocode(q="Kigali, Rwanda", geolocation=GeoLocation(lat=51.5074, lon=0.1278))

# Reverse geocode
feature_collection = GeocodeClient.reverse_geocode(geolocation=GeoLocation(lat=51.5074, lon=0.1278))
```

### Async usage
```python
from openepi_client import GeoLocation
from openepi_client.geocoding import AsyncGeocodeClient

# Searching for coordinates for a location
feature_collection = await AsyncGeocodeClient.geocode(q="Kigali, Rwanda")

# Geocode with priority to a lat and lon
feature_collection = await AsyncGeocodeClient.geocode(q="Kigali, Rwanda", geolocation=GeoLocation(lat=51.5074, lon=0.1278))

# Reverse geocode
feature_collection = await AsyncGeocodeClient.reverse_geocode(geolocation=GeoLocation(lat=51.5074, lon=0.1278))
```

## Flood
### Sync usage
```python
from openepi_client import GeoLocation, BoundingBox
from openepi_client.flood import FloodClient
from datetime import date, timedelta

# Get the return period thresholds for a given geolocation
thresholds = FloodClient.get_threshold(geolocation=GeoLocation(lat=-3.422, lon=30.075))

# Get the return period thresholds for a given bounding box
thresholds = FloodClient.get_threshold(bounding_box=BoundingBox(min_lat=4.764412, min_lon=22.0, max_lat=5.015732, max_lon=23.05))

# Get a summary flood forecast for a given coordinate
summary = FloodClient.get_summary(geolocation=GeoLocation(lat=-3.422, lon=30.075))

# Get a summary flood forecast for a given coordinate and include neighboring cells
summary = FloodClient.get_summary(geolocation=GeoLocation(lat=-3.422, lon=30.075), include_neighbors=True)

# Get a summary flood forecast for a given bounding box
summary = FloodClient.get_summary(bounding_box=BoundingBox(min_lat=4.764412, min_lon=22.0, max_lat=5.015732, max_lon=23.05))

# Get a detailed flood forecast for a given coordinate
detailed = FloodClient.get_detailed(geolocation=GeoLocation(lat=-3.422, lon=30.075))

# Get a detailed flood forecast for a given coordinate and timeframe (inclusive bounds)
start_date = date.today()
end_date = start_date + timedelta(days=4)
detailed = FloodClient.get_detailed(geolocation=GeoLocation(lat=-3.422, lon=30.075), start_date=start_date, end_date=end_date)

# Get a detailed flood forecast for a given bounding box
detailed = FloodClient.get_detailed(bounding_box=BoundingBox(min_lat=4.764412, min_lon=22.0, max_lat=5.015732, max_lon=23.05))
```


### Async usage
```python
from openepi_client import GeoLocation, BoundingBox
from openepi_client.flood import AsyncFloodClient
from datetime import date, timedelta

# Get the return period thresholds for a given geolocation
thresholds = await AsyncFloodClient.get_threshold(geolocation=GeoLocation(lat=-3.422, lon=30.075))

# Get the return period thresholds for a given bounding box
thresholds = await AsyncFloodClient.get_threshold(bounding_box=BoundingBox(min_lat=4.764412, min_lon=22.0, max_lat=5.015732, max_lon=23.05))

# Get a summary flood forecast for a given coordinate
summary = await AsyncFloodClient.get_summary(geolocation=GeoLocation(lat=-3.422, lon=30.075))

# Get a summary flood forecast for a given coordinate and include neighboring cells
summary = await AsyncFloodClient.get_summary(geolocation=GeoLocation(lat=-3.422, lon=30.075), include_neighbors=True)

# Get a summary flood forecast for a given bounding box
summary = await AsyncFloodClient.get_summary(bounding_box=BoundingBox(min_lat=4.764412, min_lon=22.0, max_lat=5.015732, max_lon=23.05))

# Get a detailed flood forecast for a given coordinate
detailed = await AsyncFloodClient.get_detailed(geolocation=GeoLocation(lat=-3.422, lon=30.075))

# Get a detailed flood forecast for a given coordinate and timeframe (inclusive bounds)
start_date = date.today()
end_date = start_date + timedelta(days=4)
detailed = await AsyncFloodClient.get_detailed(geolocation=GeoLocation(lat=-3.422, lon=30.075), start_date=start_date, end_date=end_date)

# Get a detailed flood forecast for a given bounding box
detailed = await AsyncFloodClient.get_detailed(bounding_box=BoundingBox(min_lat=4.764412, min_lon=22.0, max_lat=5.015732, max_lon=23.05))
```

## Deforestation
### Sync usage
```python
from openepi_client import GeoLocation, BoundingBox
from openepi_client.deforestation import DeforestationClient

# Get the yearly forest cover loss within a river basin for a given geolocation
forest_loss = DeforestationClient.get_basin(geolocation=GeoLocation(lat=5.175, lon=37.124))

# Get yearly forest cover loss for all river basins within the given bounding box
forest_loss = DeforestationClient.get_basin(bounding_box=BoundingBox(min_lat=30.909622, min_lon=28.850951, max_lat=-1.041395, max_lon=-2.840114))
```


### Async usage
```python
from openepi_client import GeoLocation, BoundingBox
from openepi_client.deforestation import AsyncDeforestationClient

# Get the yearly forest cover loss within a river basin for a given geolocation
forest_loss = await AsyncDeforestationClient.get_basin(geolocation=GeoLocation(lat=5.175, lon=37.124))

# Get yearly forest cover loss for all river basins within the given bounding box
forest_loss = await AsyncDeforestationClient.get_basin(bounding_box=BoundingBox(min_lat=30.909622, min_lon=28.850951, max_lat=-1.041395, max_lon=-2.840114))
```

## Soil
### Sync usage
```python
from openepi_client import GeoLocation, BoundingBox
from openepi_client.soil import SoilClient

# Get the most probable soil type at the queried location
# and the probability of the top 4 most probable soil types
soil_type = SoilClient.get_soil_type(
  geolocation=GeoLocation(lat=60.1, lon=9.58),
  top_k=4
)

# Get the mean and the 0.05 quantile of the soil 
# properties at the queried location and depths       
properties = ["clay", "silt"]
depths = ["0-5cm", "5-15cm"]
values = ["mean", "Q0.05"]
soil_property = SoilClient.get_soil_property(
  geolocation=GeoLocation(lat=60.1, lon=9.58), 
  depths=depths, 
  properties=properties, 
  values=values
)

# Get a summary of the soil types in the queried bounding box, 
# represented by a mapping of each soil type to the number 
# of occurrences in the bounding box
soil_type_summary = SoilClient.get_soil_type_summary(
  bounding_box=BoundingBox(
    min_lat=60.1,
    max_lat=60.12,
    min_lon=9.58,
    max_lon=9.6,
  )
)
```

### Async usage
```python
from openepi_client import GeoLocation, BoundingBox
from openepi_client.soil import AsyncSoilClient

# Get the most probable soil type at the queried location
# and the probability of the top 4 most probable soil types
soil_type = await AsyncSoilClient.get_soil_type(
  geolocation=GeoLocation(lat=60.1, lon=9.58),
  top_k=4
)

# Get the mean and the 0.05 quantile of the soil 
# properties at the queried location and depths       
properties = ["clay", "silt"]
depths = ["0-5cm", "5-15cm"]
values = ["mean", "Q0.05"]
soil_property = await AsyncSoilClient.get_soil_property(
  geolocation=GeoLocation(lat=60.1, lon=9.58), 
  depths=depths, 
  properties=properties, 
  values=values
)

# Get a summary of the soil types in the queried bounding box, 
# represented by a mapping of each soil type to the number 
# of occurrences in the bounding box
soil_type_summary = await AsyncSoilClient.get_soil_type_summary(
  bounding_box=BoundingBox(
    min_lat=60.1,
    max_lat=60.12,
    min_lon=9.58,
    max_lon=9.6,
  )
)
```

## Crop Health
### Sync usage
```python
import os
from openepi_client.crop_health import CropHealthClient

image_path = os.path.abspath("cocoa.jpg")

# Get the predicted health of the crop pictured in cocoa.jpg with the binary model.
with open(image_path, "rb") as f:
  image_data = f.read()
  health = CropHealthClient.get_binary_prediction(image_data)

# Get the predicted health of the crop pictured in cocoa.jpg with the single-HLT model.
with open(image_path, "rb") as f:
  image_data = f.read()
  health = CropHealthClient.get_singleHLT_prediction(image_data)

# Get the predicted health of the crop pictured in cocoa.jpg with the multi-HLT model.
with open(image_path, "rb") as f:
  image_data = f.read()
  health = CropHealthClient.get_multiHLT_prediction(image_data)
```


### Async usage
```python
import os
from openepi_client.crop_health import AsyncCropHealthClient

image_path = os.path.abspath("cocoa.jpg")

# Get the predicted health of the crop pictured in cocoa.jpg with the binary model.
with open(image_path, "rb") as f:
  image_data = f.read()
  health = await AsyncCropHealthClient.get_binary_prediction(image_data)

# Get the predicted health of the crop pictured in cocoa.jpg with the single-HLT model.
with open(image_path, "rb") as f:
  image_data = f.read()
  health = await AsyncCropHealthClient.get_singleHLT_prediction(image_data)

# Get the predicted health of the crop pictured in cocoa.jpg with the multi-HLT model.
with open(image_path, "rb") as f:
  image_data = f.read()
  health = await AsyncCropHealthClient.get_multiHLT_prediction(image_data)
```

## Global Forest Watch
### Sync usage
```python
from openepi_client.global_forest_watch import GlobalForestWatchClient

# Create an account
# Note that after doing this, you must verify your email and set a password before you can use your account
GlobalForestWatchClient().create_account(name="Your Name", email="your@mail.com")

# Create an API key
gfw = GlobalForestWatchClient(email="your@mail.com", password="your secret password")
response = gfw.create_api_key(alias="my-alias", organization="Example org", domains=["example.com"])
print(f"Your API key is: {response.api_key}")

gfw = GlobalForestWatchClient(api_key="your-api-key")

# List datasets
datasets = gfw.list_datasets()

# Get a specific dataset
dataset = gfw.get_dataset(dataset_id="<identifier>")

# Get the latest version of a dataset
latest_version = dataset.get_version(version = dataset.latest_version_id)

# List fields in a dataset version
fields = latest_version.fields()
for field in fields:
    print(fields.description)

# List assets in a dataset version
assets_response = latest_version.assets()

# download all downloadable assets
for asset in assets_response.assets:
    if asset.is_downloadable:
        asset.download(to="<my_download_path>")
```

## Updating the client
The following commands are used to update the client types. The commands are run from the root of the project.
```bash
poetry run datamodel-codegen --url https://api.openepi.io/geocoding/openapi.json --output openepi_client/geocoding/_geocoding_types.py --enum-field-as-literal all --output-model-type pydantic_v2.BaseModel --input-file-type "openapi"
poetry run datamodel-codegen --url https://api.openepi.io/flood/openapi.json --output openepi_client/flood/_flood_types.py --enum-field-as-literal all --output-model-type pydantic_v2.BaseModel --input-file-type "openapi"
poetry run datamodel-codegen --url https://api.openepi.io/deforestation/openapi.json --output openepi_client/deforestation/_deforestation_types.py --enum-field-as-literal all --output-model-type pydantic_v2.BaseModel --input-file-type "openapi"
poetry run datamodel-codegen --url https://api.openepi.io/soil/openapi.json --output openepi_client/soil/_soil_types.py --enum-field-as-literal all --output-model-type pydantic_v2.BaseModel --input-file-type "openapi"
poetry run datamodel-codegen --url https://api.openepi.io/crop-health/openapi.json --output openepi_client/crop_health/_crop_health_types.py --enum-field-as-literal all --output-model-type pydantic_v2.BaseModel --input-file-type "openapi"
```

