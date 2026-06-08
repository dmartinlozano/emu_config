import json

from src.models.launcher import LauncherPlatform, LauncherPlayer
from src.services.adb_service import AdbService

_REMOTE_DIR = "/sdcard/Download/emu_config/daijisho"


class DaijishouService:
    def __init__(self):
        self._adb = AdbService()

    def installed_players(self, platform: LauncherPlatform, installed: set[str]) -> list[LauncherPlayer]:
        return [p for p in platform.players if p.package in installed]

    def _export_platform(self, platform: LauncherPlatform, installed: set[str]) -> bool:
        active = self.installed_players(platform, installed)
        if not active:
            return False

        player_list = [
            {
                "name": f"{platform.unique_id} - {p.name}",
                "uniqueId": f"{platform.unique_id}.{p.package}",
                "description": f"Supported extensions: {platform.extensions}.",
                "acceptedFilenameRegex": platform.accepted_filename_regex,
                "amStartArguments": p.am_start_arguments,
                "killPackageProcesses": p.kill_package_processes,
                "killPackageProcessesWarning": True,
                "extra": "",
            }
            for p in active
        ]

        payload = {
            "databaseVersion": 14,
            "revisionNumber": 1,
            "platform": {
                "name": platform.platform_name,
                "uniqueId": platform.unique_id,
                "shortname": platform.unique_id,
                "description": None,
                "acceptedFilenameRegex": platform.accepted_filename_regex,
                "scraperSourceList": ["LIBRETRO"],
                "boxArtAspectRatioId": 0,
                "useCustomBoxArtAspectRatio": False,
                "customBoxArtAspectRatio": None,
                "screenAspectRatioId": 0,
                "useCustomScreenAspectRatio": False,
                "customScreenAspectRatio": None,
                "retroAchievementsConsoleIdList": [],
                "extra": "",
            },
            "playerList": player_list,
        }

        filename = platform.platform_name.replace(" ", "").replace("/", "") + ".json"
        self._adb.push_content(
            json.dumps(payload, indent=2, ensure_ascii=False),
            f"{_REMOTE_DIR}/{filename}",
        )
        return True

    def export_all(self, platforms: list[LauncherPlatform], installed: set[str]) -> int:
        return sum(1 for p in platforms if self._export_platform(p, installed))
