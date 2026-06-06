import json
from pathlib import Path
from typing import Optional


class PreferencesService:
    _PATH = Path(".emu_prefs.json")

    def __init__(self):
        self._data: dict = {}
        if self._PATH.exists():
            self._data = json.loads(self._PATH.read_text(encoding="utf-8"))

    def get(self, emu_id: int, key: str) -> str | None:
        return self._data.get(f"{emu_id}_{key}")

    def set(self, emu_id: int, key: str, value: str):
        self._data[f"{emu_id}_{key}"] = value
        self._PATH.write_text(json.dumps(self._data, indent=2), encoding="utf-8")

    def get_app(self, key: str) -> str | None:
        return self._data.get(f"app_{key}")

    def set_app(self, key: str, value: str):
        self._data[f"app_{key}"] = value
        self._PATH.write_text(json.dumps(self._data, indent=2), encoding="utf-8")

    def get_gamepad_profile(self, gamepad_id: str) -> Optional[dict[str, int]]:
        raw = self._data.get(f"gp_profile_{gamepad_id}")
        return raw if isinstance(raw, dict) else None

    def set_gamepad_profile(self, gamepad_id: str, profile: dict[str, int]):
        self._data[f"gp_profile_{gamepad_id}"] = profile
        self._PATH.write_text(json.dumps(self._data, indent=2), encoding="utf-8")
