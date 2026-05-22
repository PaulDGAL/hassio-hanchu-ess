"""Config flow for Hanchu."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.data_entry_flow import FlowResult

from .const import CONF_ACCOUNT, CONF_PWD, CONF_SN, DEFAULT_NAME, DOMAIN


class HanchuConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Hanchu."""

    VERSION = 1
    MINOR_VERSION = 1

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        """Handle the initial step."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        errors: dict[str, str] = {}

        if user_input is not None:
            if not user_input.get(CONF_ACCOUNT, "").strip():
                errors[CONF_ACCOUNT] = "account_required"
            if not user_input.get(CONF_PWD, ""):
                errors[CONF_PWD] = "pwd_required"
            if not user_input.get(CONF_SN, "").strip():
                errors[CONF_SN] = "sn_required"

            if not errors:
                name = user_input.get(CONF_NAME) or DEFAULT_NAME
                return self.async_create_entry(
                    title=name,
                    data={
                        CONF_NAME: name,
                        CONF_ACCOUNT: user_input[CONF_ACCOUNT].strip(),
                        CONF_PWD: user_input[CONF_PWD],
                        CONF_SN: user_input[CONF_SN].strip(),
                    },
                )

        data_schema = vol.Schema(
            {
                vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
                vol.Required(CONF_ACCOUNT): str,
                vol.Required(CONF_PWD): str,
                vol.Required(CONF_SN): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_step_reauth(self, entry_data: Mapping[str, Any]) -> FlowResult:
        """Handle re-authentication when credentials are rejected by the API."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input: dict | None = None) -> FlowResult:
        """Handle re-authentication confirmation."""
        reauth_entry = self._get_reauth_entry()
        errors: dict[str, str] = {}

        if user_input is not None:
            if not user_input.get(CONF_ACCOUNT, "").strip():
                errors[CONF_ACCOUNT] = "account_required"
            if not user_input.get(CONF_PWD, ""):
                errors[CONF_PWD] = "pwd_required"
            if not user_input.get(CONF_SN, "").strip():
                errors[CONF_SN] = "sn_required"

            if not errors:
                return self.async_update_reload_and_abort(
                    reauth_entry,
                    data_updates={
                        CONF_ACCOUNT: user_input[CONF_ACCOUNT].strip(),
                        CONF_PWD: user_input[CONF_PWD],
                        CONF_SN: user_input[CONF_SN].strip(),
                    },
                )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_ACCOUNT, default=reauth_entry.data.get(CONF_ACCOUNT, "")): str,
                vol.Required(CONF_PWD): str,
                vol.Required(CONF_SN, default=reauth_entry.data.get(CONF_SN, "")): str,
            }
        )

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=data_schema,
            errors=errors,
        )

