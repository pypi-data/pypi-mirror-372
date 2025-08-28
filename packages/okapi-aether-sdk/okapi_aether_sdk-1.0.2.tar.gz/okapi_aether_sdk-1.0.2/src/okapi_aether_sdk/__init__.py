import logging

from okapi_aether_sdk.aether_api import AetherApi
from okapi_aether_sdk.aether_satellites_api import AetherSatellitesApi
from okapi_aether_sdk.aether_sensors_api import AetherSensorsApi
from okapi_aether_sdk.aether_services_api import AetherServicesApi

__all__ = ["AetherApi", "AetherSatellitesApi", "AetherSensorsApi", "AetherServicesApi"]
# Add a default null handler
logging.getLogger(__name__).addHandler(logging.NullHandler())
