import xml.etree.ElementTree as ET
from xml.dom import minidom

from src.models.launcher import LauncherPlatform, LauncherPlayer
from src.services.adb_service import AdbService

_REMOTE_PATH = "/sdcard/ES-DE/custom_systems/es_systems.xml"


def _to_esde_command(am_start_arguments: str) -> str:
    single_line = am_start_arguments.replace("\n", " ").replace("{file.uri}", "%ROM%")
    return f"%STARTACTIVITY%{single_line}"


class EsdeService:
    def __init__(self):
        self._adb = AdbService()

    def installed_players(self, platform: LauncherPlatform, installed: set[str]) -> list[LauncherPlayer]:
        return [p for p in platform.players if p.package in installed]

    def export_all(self, platforms: list[LauncherPlatform], installed: set[str]) -> int:
        root = ET.Element("systemList")
        count = 0

        for platform in platforms:
            active = self.installed_players(platform, installed)
            if not active:
                continue

            system = ET.SubElement(root, "system")
            ET.SubElement(system, "name").text = platform.unique_id
            ET.SubElement(system, "fullname").text = platform.platform_name
            ET.SubElement(system, "path").text = f"~/ROMs/{platform.unique_id.upper()}"
            ET.SubElement(system, "extension").text = " ".join(
                f".{ext.strip()}" for ext in platform.extensions.split(",")
            )
            for player in active:
                cmd = ET.SubElement(system, "command")
                cmd.set("label", player.name)
                cmd.text = _to_esde_command(player.am_start_arguments)
            ET.SubElement(system, "platform").text = platform.unique_id
            ET.SubElement(system, "theme").text = platform.unique_id
            count += 1

        xml_str = minidom.parseString(
            ET.tostring(root, encoding="unicode")
        ).toprettyxml(indent="  ")
        self._adb.push_content(xml_str, _REMOTE_PATH)
        return count
