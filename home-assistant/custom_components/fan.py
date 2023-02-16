"""Platform for light integration."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp

# import awesomelights
import voluptuous as vol

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.config_validation import (  # noqa: F401
    PLATFORM_SCHEMA,
)
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.util.percentage import (
    ordered_list_item_to_percentage,
)

from .pynrf905api import nRF905API

from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_USERNAME,
)

_LOGGER = logging.getLogger(__name__)

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Optional(CONF_USERNAME, default="admin"): cv.string,
        vol.Optional(CONF_PASSWORD, default="nrf905"): cv.string,
    }
)


CONFIG_SCHEMA = vol.Schema(
    {
        "nrf905_api": vol.Schema(
            {
                vol.Required(CONF_HOST): cv.string,
                vol.Optional(CONF_NAME, default="nrf905"): cv.string,
                vol.Optional(CONF_USERNAME, default=""): cv.string,
                vol.Optional(CONF_PASSWORD, default=""): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

PRESET_MODE_AUTO = "high"
PRESET_MODES = [PRESET_MODE_AUTO, "medium", "low"]
ORDERED_NAMED_FAN_SPEEDS = ["low", "medium", "high"]  # off is not included


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the Awesome Light platform."""
    # Assign configuration variables.
    # The configuration check takes care they are present.
    host = config[CONF_HOST]
    username = config[CONF_USERNAME]
    password = config.get(CONF_PASSWORD)
    fan = {"username": username, "password": password, "host": host}

    # Add devices
    add_entities([FanNRF905Api(fan)])


class FanNRF905Api(FanEntity):
    """Representation of an Awesome Light."""

    _attr_icon = "mdi:air-conditioner"
    _attr_should_poll = False
    # _attr_supported_features = FanEntityFeature.SET_SPEED | FanEntityFeature.PRESET_MODE
    _attr_supported_features = FanEntityFeature.PRESET_MODE
    _attr_preset_modes = PRESET_MODES
    current_speed: float | None = None

    _host = ""
    _username = ""
    _password = ""
    _ssl = False
    _timer = 0

    def __init__(self, fan) -> None:
        """Initialize an AwesomeLight."""
        self._fan = fan
        # self._name = fan.name
        self._name = "fan.name"
        self._state = None

    @property
    def name(self) -> str:
        """Return the display name of this light."""
        return self._name

    @property
    def is_on(self) -> bool | None:
        """Return true if light is on."""
        return self._state

    # def turn_on(self, **kwargs: Any) -> None:
    #     """Instruct the light to turn on.

    #     You can skip the brightness part if your light does not support
    #     brightness control.
    #     """
    #     _LOGGER.info("Call nrf905 turn on")

    # def turn_off(self, **kwargs: Any) -> None:
    #     """Instruct the light to turn off."""
    #     _LOGGER.info("Call nrf905 turn off")

    def update(self) -> None:
        """Fetch new state data for this light.

        This is the only method that should fetch new data for Home Assistant.
        """
        # self._light.update()
        # self._state = self._light.is_on()
        # self._brightness = self._light.brightness

    async def async_turn_on(
        self,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Turn on the fan."""

        _LOGGER.info("Call nrf905 turn on")
        self.set_percentage(100)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the fan off."""
        _LOGGER.info("Call nrf905 turn off")
        self.set_percentage(0)

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the speed percentage of the fan."""
        _LOGGER.info("Call nrf905 set_percentage %s", str(percentage))

    # @property
    # def percentage(self) -> Optional[int]:
    #     """Return the current speed percentage."""
    #     return ordered_list_item_to_percentage(ORDERED_NAMED_FAN_SPEEDS, current_speed)

    @property
    def speed_count(self) -> int:
        """Return the number of speeds the fan supports."""
        return len(ORDERED_NAMED_FAN_SPEEDS)

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode of the fan."""

        _LOGGER.info("Call nrf905 set_preset %s", preset_mode)
        _LOGGER.info(
            "Call nrf905 that means %s",
            ordered_list_item_to_percentage(ORDERED_NAMED_FAN_SPEEDS, preset_mode),
        )

        async with aiohttp.ClientSession(
            auth=aiohttp.BasicAuth(self._fan["username"], self._fan["password"])
        ) as mainsession:
            await self.nrf905_set_speed(
                s_session=mainsession,
                host=self._fan["host"],
                ssl=self._ssl,
                username=self._fan["username"],
                password=self._fan["password"],
                speed=preset_mode,
                timer=self._timer,
            )

    async def nrf905_set_speed(
        self, s_session, host, ssl, username, password, speed, timer
    ):  # pylint: disable=invalid-name
        """Show status."""

        api = nRF905API(
            session=s_session, host=host, ssl=ssl, username=username, password=password
        )

        await api.fan_setspeed(speed)
