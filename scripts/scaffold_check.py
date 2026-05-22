"""Quick local checks for the Hanchu scaffold."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    ROOT / "hacs.json",
    ROOT / "README.md",
    ROOT / "pyproject.toml",
    ROOT / "custom_components" / "hanchu" / "manifest.json",
    ROOT / "custom_components" / "hanchu" / "__init__.py",
    ROOT / "custom_components" / "hanchu" / "config_flow.py",
    ROOT / "custom_components" / "hanchu" / "coordinator.py",
    ROOT / "custom_components" / "hanchu" / "sensor.py",
]


def _check_exists() -> None:
    missing = [str(path.relative_to(ROOT)) for path in REQUIRED_FILES if not path.exists()]
    if missing:
        raise SystemExit(f"Missing required files: {', '.join(missing)}")


def _check_manifest() -> None:
    manifest_path = ROOT / "custom_components" / "hanchu" / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    required_keys = {
        "domain": "hanchu",
        "config_flow": True,
        "integration_type": "hub",
        "iot_class": "cloud_polling",
    }

    for key, expected in required_keys.items():
        if manifest.get(key) != expected:
            raise SystemExit(f"manifest.json key '{key}' must be '{expected}'")


def _check_hacs() -> None:
    hacs_path = ROOT / "hacs.json"
    hacs = json.loads(hacs_path.read_text(encoding="utf-8"))

    if "hanchu" not in hacs.get("domains", []):
        raise SystemExit("hacs.json must include 'hanchu' in domains")


if __name__ == "__main__":
    _check_exists()
    _check_manifest()
    _check_hacs()
    print("Scaffold checks passed.")

