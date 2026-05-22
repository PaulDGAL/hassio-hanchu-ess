"""Live integration test — authenticate then fetch battery state-of-charge."""

from __future__ import annotations

import json
import os
import sys
import unittest
from pathlib import Path

import aiohttp

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

_HEADERS = {
    "Content-Type": "text/plain",
    "Share-Link-Key": "",
    "locale": "en",
    "version": "1.0",
    "appPlat": "iess",
}

_CONF_ACCOUNT = os.environ.get("HANCHU_TEST_ACCOUNT", "")
_CONF_PWD = os.environ.get("HANCHU_TEST_PWD", "")
_CONF_SN = os.environ.get("HANCHU_TEST_SN", "")

_SKIP_REASON = "Set HANCHU_TEST_ACCOUNT, HANCHU_TEST_PWD, HANCHU_TEST_SN to run live tests"


@unittest.skipUnless(_CONF_ACCOUNT and _CONF_PWD and _CONF_SN, _SKIP_REASON)
class TestPowerLive(unittest.IsolatedAsyncioTestCase):
    """Authenticate against the real API, then pull live battery SOC."""

    async def test_fetch_battery_soc(self) -> None:
        from custom_components.hanchu.const import (
            AES_IV,
            AES_SECRET_KEY,
            AUTH_URL,
            POWER_URL,
        )
        from custom_components.hanchu.coordinator import _encrypt_payload, _rsa_encode_pwd

        connector = aiohttp.TCPConnector(resolver=aiohttp.resolver.ThreadedResolver())
        timeout = aiohttp.ClientTimeout(total=30)

        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:

            # ── Step 1: authenticate ──────────────────────────────────────
            pwd_rsa = _rsa_encode_pwd(_CONF_PWD)
            self.assertTrue(pwd_rsa, "RSA encryption returned empty string")

            auth_body = _encrypt_payload(
                {"account": _CONF_ACCOUNT, "pwd": pwd_rsa},
                AES_SECRET_KEY,
                AES_IV,
            )

            async with session.post(
                AUTH_URL,
                data=auth_body,
                headers={**_HEADERS, "Access-Token": ""},
            ) as resp:
                raw = await resp.text()
                self.assertLess(resp.status, 500, f"Auth server error: {raw[:200]}")
                auth_payload: dict = json.loads(raw)

            self.assertIn(
                auth_payload.get("code"),
                (200, 20001),
                f"Login failed: {auth_payload}",
            )
            token: str = auth_payload["data"]
            self.assertTrue(token, "Auth returned empty token")

            # ── Step 2: fetch powerChart ──────────────────────────────────
            power_body = _encrypt_payload({"sn": _CONF_SN}, AES_SECRET_KEY, AES_IV)

            async with session.post(
                POWER_URL,
                data=power_body,
                headers={**_HEADERS, "Access-Token": token},
            ) as resp:
                raw = await resp.text()
                self.assertLess(resp.status, 500, f"Power server error: {raw[:200]}")
                power_payload: dict = json.loads(raw)

        self.assertIn(
            power_payload.get("code"),
            (200, 20001),
            f"Power request failed: {power_payload}",
        )

        device: dict = power_payload.get("data") or {}
        self.assertIn("batSoc", device, f"batSoc missing from response: {device}")

        raw_soc = device["batSoc"]
        battery_pct = round(float(raw_soc) * 100, 1)
        self.assertGreaterEqual(battery_pct, 0.0)
        self.assertLessEqual(battery_pct, 100.0)

        print(f"\n  Battery SOC (batSoc): {raw_soc} => {battery_pct}%")
        print(f"\n  Full device record: {json.dumps(device, indent=4)}")


if __name__ == "__main__":
    unittest.main()
