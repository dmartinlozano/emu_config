import json
from pathlib import Path

from src.models.launcher import Launcher, LauncherPlatform, LauncherPlayer
from src.services.daijisho_service import DaijishouService
from src.services.esde_service import EsdeService
from src.services.pegasus_service import PegasusService

_LAUNCHERS_JSON = Path("assets/conf/launchers.json")


class LauncherController:
    def __init__(self, installed_packages: set[str]):
        self._installed = installed_packages
        data = json.loads(_LAUNCHERS_JSON.read_text(encoding="utf-8"))
        self._launchers: list[Launcher] = [Launcher.from_dict(l) for l in data["launchers"]]
        self._platforms: list[LauncherPlatform] = [LauncherPlatform.from_dict(p) for p in data["platforms"]]
        self._services = {
            "daijisho": DaijishouService(),
            "esde": EsdeService(),
            "pegasus": PegasusService(),
        }

    @property
    def installed_packages(self) -> set[str]:
        return self._installed

    @property
    def launchers(self) -> list[Launcher]:
        return self._launchers

    def installed_players(self, platform: LauncherPlatform) -> list[LauncherPlayer]:
        return [p for p in platform.players if p.package in self._installed]

    def platforms_with_players(self) -> int:
        return sum(1 for p in self._platforms if self.installed_players(p))

    def export(self, launcher_id: str) -> int:
        svc = self._services.get(launcher_id)
        if not svc:
            return 0
        return svc.export_all(self._platforms, self._installed)
