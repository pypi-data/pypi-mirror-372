from __future__ import annotations

import logging
from typing import Any, final

from meteole.clients import BaseClient, MeteoFranceClient
from meteole.forecast import WeatherForecast

logger = logging.getLogger(__name__)

AVAILABLE_PIAF_TERRITORY: list[str] = [
    "FRANCE",
]

PIAF_INSTANT_INDICATORS: list[str] = []


PIAF_OTHER_INDICATORS: list[str] = [
    "TOTAL_PRECIPITATION_RATE__GROUND_OR_WATER_SURFACE",
]


@final
class PiafForecast(WeatherForecast):
    """Access the PIAF numerical weather forecast data from Meteo-France API.

    Doc:
        - https://portail-api.meteofrance.fr/web/fr/api/arome

    Attributes:
        territory: Covered area (e.g., FRANCE, ANTIL, ...).
        precision: Precision value of the forecast.
        capabilities: DataFrame containing details on all available coverage ids.
    """

    # Model constants
    MODEL_NAME: str = "piaf"
    INDICATORS: list[str] = PIAF_INSTANT_INDICATORS + PIAF_OTHER_INDICATORS
    INSTANT_INDICATORS: list[str] = PIAF_INSTANT_INDICATORS
    BASE_ENTRY_POINT: str = "wcs/MF-NWP-HIGHRES-PIAF"
    DEFAULT_TERRITORY: str = "FRANCE"
    DEFAULT_PRECISION: float = 0.01
    CLIENT_CLASS: type[BaseClient] = MeteoFranceClient

    def __init__(
        self,
        **kwargs: Any,
    ):
        """Initialize attributes.

        Args:
            api_key: The API key for authentication. Defaults to None.
            token: The API token for authentication. Defaults to None.
            application_id: The Application ID for authentication. Defaults to None.
        """
        super().__init__(api_base_url="https://api.meteofrance.fr/pro/", **kwargs)

    def _validate_parameters(self) -> None:
        """Check the territory and the precision parameters.

        Raise:
            ValueError: At least, one parameter is not good.
        """
        if self.precision != 0.01:
            raise ValueError("Parameter `precision` must be in 0.01.")

        if self.territory not in AVAILABLE_PIAF_TERRITORY:
            raise ValueError(f"Parameter `territory` must be in {AVAILABLE_PIAF_TERRITORY}")
