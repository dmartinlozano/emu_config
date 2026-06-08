import json
import uuid
from pathlib import Path

from src.models.profile import Profile
from src.services.preferences_service import PreferencesService

_PROFILES_PATH = Path("assets/conf/profiles.json")
_DEFAULT = Profile(id="default", name="Default")


class ProfileService:
    def __init__(self):
        self._prefs = PreferencesService()

    # --------------------------------------------------------- persistence

    def _load(self) -> list[Profile]:
        if not _PROFILES_PATH.exists():
            return [_DEFAULT]
        try:
            data = json.loads(_PROFILES_PATH.read_text(encoding="utf-8"))
            profiles = [Profile(**p) for p in data]
            if not any(p.id == "default" for p in profiles):
                profiles.insert(0, _DEFAULT)
            return profiles
        except Exception:
            return [_DEFAULT]

    def _save(self, profiles: list[Profile]):
        _PROFILES_PATH.parent.mkdir(parents=True, exist_ok=True)
        _PROFILES_PATH.write_text(
            json.dumps([{"id": p.id, "name": p.name} for p in profiles], indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    # --------------------------------------------------------- public API

    def get_all(self) -> list[Profile]:
        return self._load()

    def get_active_id(self) -> str:
        return self._prefs.get_app("active_profile") or "default"

    def get_active(self) -> Profile:
        active_id = self.get_active_id()
        return next((p for p in self._load() if p.id == active_id), _DEFAULT)

    def activate(self, profile_id: str):
        PreferencesService.set_active_profile(profile_id)
        self._prefs.set_app("active_profile", profile_id)

    def create(self, name: str, copy_from: str | None = None) -> Profile:
        profiles = self._load()
        new_id = uuid.uuid4().hex[:8]
        profile = Profile(id=new_id, name=name)
        profiles.append(profile)
        self._save(profiles)
        if copy_from:
            self._prefs.copy_profile(copy_from, new_id)
        return profile

    def rename(self, profile_id: str, new_name: str):
        profiles = self._load()
        for p in profiles:
            if p.id == profile_id:
                p.name = new_name
                break
        self._save(profiles)

    def delete(self, profile_id: str):
        if profile_id == "default":
            return
        profiles = [p for p in self._load() if p.id != profile_id]
        self._save(profiles)
        self._prefs.delete_profile(profile_id)
        if self.get_active_id() == profile_id:
            self.activate("default")

    def init_active(self):
        """Call at startup to restore the saved active profile."""
        PreferencesService.set_active_profile(self.get_active_id())
