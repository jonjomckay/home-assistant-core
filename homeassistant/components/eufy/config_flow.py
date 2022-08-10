"""Config flow to configure Eufy component."""
from typing import cast
from requests.exceptions import ConnectTimeout, HTTPError

import requests
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.components.eufy import DEVICE_SCHEMA, DOMAIN
from homeassistant.const import CONF_DEVICES, CONF_USERNAME, CONF_PASSWORD
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv


class EufyFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Eufy."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize."""
        self.data_schema = {
            vol.Inclusive(CONF_USERNAME, "authentication"): cv.string,
            vol.Inclusive(CONF_PASSWORD, "authentication"): cv.string,
        }

        self._password: str | None = None
        self._username: str | None = None

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle a flow initialized by the user."""

        if user_input is not None:
            # TODO: Errors don't work
            valid, error = await self.hass.async_add_executor_job(
                self._test_credentials,
                user_input[CONF_USERNAME],
                user_input[CONF_PASSWORD],
            )
            if valid:
                return self.async_create_entry(
                    title=user_input[CONF_USERNAME], data=user_input
                )

            return await self._show_config_form(user_input, errors={"base": error})

        return await self._show_config_form(user_input)

    async def _show_config_form(
        self, user_input, errors=None
    ) -> FlowResult:  # pylint: disable=unused-argument
        """Show the configuration form to edit configuration."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(self.data_schema),
            errors=errors,
        )

    def _test_credentials(self, username, password):
        """Return true if credentials are valid."""
        try:
            response = requests.post(
                "https://home-api.eufylife.com/v1/user/email/login",
                json={
                    "client_id": "eufyhome-app",
                    "client_secret": "GQCpr9dSp3uQpsOMgJ4xQ",
                    "email": username,
                    "password": password,
                },
            )

            if response.ok:
                return True, None

            return False, "invalid_auth"
        except (ConnectTimeout):
            return False, "cannot_connect"
