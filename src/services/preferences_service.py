import json
from pathlib import Path
from typing import Optional


class PreferencesService:
    _PATH = Path(".emu_prefs.json")
    _active_profile: str = "default"

    @classmethod
    def set_active_profile(cls, profile_id: str):
        cls._active_profile = profile_id

    @classmethod
    def get_active_profile(cls) -> str:
        return cls._active_profile

    def __init__(self):
        self._data: dict = {}
        if self._PATH.exists():
            self._data = json.loads(self._PATH.read_text(encoding="utf-8"))
        self._migrate()

    def _migrate(self):
        """Move legacy flat keys ({emu_id}_{key}) into the default profile namespace."""
        new_data = {}
        changed = False
        for k, v in self._data.items():
            if k.startswith(("p:", "app_", "gp_")):
                new_data[k] = v
            else:
                new_data[f"p:default:{k}"] = v
                changed = True
        if changed:
            self._data = new_data
            self._save()

    def _save(self):
        self._PATH.write_text(json.dumps(self._data, indent=2), encoding="utf-8")

    # --------------------------------------------------------- emu prefs (per profile)

    def get(self, emu_id: int, key: str) -> str | None:
        return self._data.get(f"p:{self._active_profile}:{emu_id}_{key}")

    def set(self, emu_id: int, key: str, value: str):
        self._data[f"p:{self._active_profile}:{emu_id}_{key}"] = value
        self._save()

    # --------------------------------------------------------- app prefs (global)

    def get_app(self, key: str) -> str | None:
        return self._data.get(f"app_{key}")

    def set_app(self, key: str, value: str):
        self._data[f"app_{key}"] = value
        self._save()

    # --------------------------------------------------------- gamepad profiles (global)

    def get_gamepad_profile(self, gamepad_id: str) -> Optional[dict[str, int]]:
        raw = self._data.get(f"gp_profile_{gamepad_id}")
        return raw if isinstance(raw, dict) else None

    def set_gamepad_profile(self, gamepad_id: str, profile: dict[str, int]):
        self._data[f"gp_profile_{gamepad_id}"] = profile
        self._save()

    # --------------------------------------------------------- profile data ops

    def copy_profile(self, src_id: str, dst_id: str):
        """Duplicate all emu preferences from src profile to dst profile."""
        prefix_src = f"p:{src_id}:"
        prefix_dst = f"p:{dst_id}:"
        additions = {
            f"{prefix_dst}{k[len(prefix_src):]}": v
            for k, v in self._data.items()
            if k.startswith(prefix_src)
        }
        self._data.update(additions)
        self._save()

    def delete_profile(self, profile_id: str):
        """Remove all emu preferences for a profile."""
        prefix = f"p:{profile_id}:"
        self._data = {k: v for k, v in self._data.items() if not k.startswith(prefix)}
        self._save()
