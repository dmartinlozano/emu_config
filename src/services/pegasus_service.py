from src.models.launcher import LauncherPlatform, LauncherPlayer
from src.services.adb_service import AdbService

_REMOTE_PATH = "/sdcard/pegasus-frontend/collections.pegasus.txt"


def _to_pegasus_launch(am_start_arguments: str) -> str:
    single_line = am_start_arguments.replace("\n", " ")
    return f"am start {single_line}"


class PegasusService:
    def __init__(self):
        self._adb = AdbService()

    def installed_players(self, platform: LauncherPlatform, installed: set[str]) -> list[LauncherPlayer]:
        return [p for p in platform.players if p.package in installed]

    def export_all(self, platforms: list[LauncherPlatform], installed: set[str]) -> int:
        blocks = []
        count = 0

        for platform in platforms:
            active = self.installed_players(platform, installed)
            if not active:
                continue

            player = active[0]
            lines = [
                f"collection: {platform.platform_name}",
                f"shortname: {platform.unique_id}",
                f"launch: {_to_pegasus_launch(player.am_start_arguments)}",
                f"extension: {platform.extensions}",
            ]
            blocks.append("\n".join(lines))
            count += 1

        self._adb.push_content("\n\n".join(blocks) + "\n", _REMOTE_PATH)
        return count
