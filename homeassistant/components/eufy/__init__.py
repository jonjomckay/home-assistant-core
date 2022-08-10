"""Support for Eufy devices."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType
import lakeside
import voluptuous as vol

from homeassistant.const import (
    CONF_ACCESS_TOKEN,
    CONF_ADDRESS,
    CONF_DEVICES,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_TYPE,
    CONF_USERNAME,
    Platform,
)
from homeassistant.core import Config, HomeAssistant
from homeassistant.helpers import discovery
import homeassistant.helpers.config_validation as cv

DOMAIN = "eufy"

DEVICE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ADDRESS): cv.string,
        vol.Required(CONF_ACCESS_TOKEN): cv.string,
        vol.Required(CONF_TYPE): cv.string,
        vol.Optional(CONF_NAME): cv.string,
    }
)

CONFIG_DOMAIN_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_DEVICES, default=[]): vol.All(
            cv.ensure_list, [DEVICE_SCHEMA]
        ),
        vol.Inclusive(CONF_USERNAME, "authentication"): cv.string,
        vol.Inclusive(CONF_PASSWORD, "authentication"): cv.string,
    }
)

CONFIG_SCHEMA = vol.Schema(
    {DOMAIN: CONFIG_DOMAIN_SCHEMA},
    extra=vol.ALLOW_EXTRA,
)

PLATFORMS = {
    "T1011": Platform.LIGHT,
    "T1012": Platform.LIGHT,
    "T1013": Platform.LIGHT,
    "T1201": Platform.SWITCH,
    "T1202": Platform.SWITCH,
    "T1203": Platform.SWITCH,
    "T1211": Platform.SWITCH,
    "T2103": Platform.VACUUM,
}


async def async_setup_entry(hass: HomeAssistant, config: ConfigEntry):
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})

    await do_setup_automatic(
        hass,
        config.data,
        config.data.get(CONF_USERNAME),
        config.data.get(CONF_PASSWORD),
    )
    do_setup_manual(hass, config.data)

    return True


async def async_setup(hass: HomeAssistant, config: Config) -> bool:
    """Set up Eufy devices."""

    if DOMAIN not in config:
        return True

    if CONF_USERNAME in config[DOMAIN] and CONF_PASSWORD in config[DOMAIN]:
        await do_setup_automatic(
            hass,
            config.data,
            config[DOMAIN][CONF_USERNAME],
            config[DOMAIN][CONF_PASSWORD],
        )

    do_setup_manual(hass, config[DOMAIN])

    return True


async def do_setup_automatic(
    hass: HomeAssistant, config: ConfigType, username, password
):
    data = await hass.async_add_executor_job(lakeside.get_devices, username, password)
    for device in data:
        kind = device["type"]
        if kind not in PLATFORMS:
            continue
        await discovery.async_load_platform(
            hass, PLATFORMS[kind], DOMAIN, device, config
        )


def do_setup_manual(hass: HomeAssistant, config: ConfigType):
    if CONF_DEVICES not in config:
        return

    for device_info in config[CONF_DEVICES]:
        kind = device_info["type"]
        if kind not in PLATFORMS:
            continue
        device = {}
        device["address"] = device_info["address"]
        device["code"] = device_info["access_token"]
        device["type"] = device_info["type"]
        device["name"] = device_info["name"]
        discovery.load_platform(hass, PLATFORMS[kind], DOMAIN, device, config)
