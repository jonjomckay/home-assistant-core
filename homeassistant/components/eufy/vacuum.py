"""Support for Eufy vacuums."""
from __future__ import annotations
from homeassistant.components.eufy.api import LakesideSwitch

from homeassistant.components.vacuum import VacuumEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up Eufy vacuums."""
    if discovery_info is None:
        return
    add_entities([EufyVacuum(discovery_info)], True)


class EufyVacuum(VacuumEntity):
    """Representation of a Eufy vacuum."""

    def __init__(self, device):
        """Initialize the vacuum."""

        self._state = None
        self._name = device["name"]
        self._address = device["address"]
        self._code = device["code"]
        self._type = device["type"]
        self._switch = LakesideSwitch(self._address, self._code, self._type)
        self._switch.connect()

    def update(self):
        """Synchronise state from the switch."""
        self._switch.update()
        self._state = self._switch.power

    @property
    def unique_id(self):
        """Return the ID of this vacuum."""
        return self._address

    @property
    def name(self):
        """Return the name of the device if any."""
        return self._name

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._state

    def turn_on(self, **kwargs):
        """Turn the specified switch on."""
        try:
            self._switch.set_state(True)
        except BrokenPipeError:
            self._switch.connect()
            self._switch.set_state(power=True)

    def turn_off(self, **kwargs):
        """Turn the specified switch off."""
        try:
            self._switch.set_state(False)
        except BrokenPipeError:
            self._switch.connect()
            self._switch.set_state(False)
