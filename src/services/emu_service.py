import json
import re
import tempfile
from pathlib import Path

from src.config.button_profile import DEFAULT_PROFILE
from src.models.emu import Emu
from src.models.gamepad import Gamepad
from src.services.adb_service import AdbService
from src.services.preferences_service import PreferencesService


def _apply_profile(mapper: dict, profile: dict[str, int]) -> dict:
    """Replaces default button codes in mapper values with profile codes."""
    translation = {
        str(DEFAULT_PROFILE[sem]): str(code)
        for sem, code in profile.items()
        if sem in DEFAULT_PROFILE and DEFAULT_PROFILE[sem] != code
    }
    if not translation:
        return mapper
    result = {}
    for k, v in mapper.items():
        v_str = str(v)
        for old, new in translation.items():
            v_str = re.sub(r'(?<![0-9])' + re.escape(old) + r'(?![0-9])', new, v_str)
        result[k] = v_str
    return result


class EmuService:
    _EMUS_JSON = Path("assets/conf/emus.json")

    def __init__(self):
        self._adb = AdbService()
        self._prefs = PreferencesService()

    def load_emus(self) -> list[Emu]:
        data = json.loads(self._EMUS_JSON.read_text(encoding="utf-8"))
        return [Emu.from_dict(item) for item in data]

    def get_installed_packages(self) -> set[str]:
        return self._adb.get_installed_packages()

    def get_package_version(self, package: str) -> str | None:
        return self._adb.get_package_version(package)

    def update_config(self, emu: Emu, use_xbox_style: bool, gamepads: list[Gamepad]) -> bool:
        if emu.input is None:
            return False

        mapper = dict(emu.input.mapper)
        if use_xbox_style and emu.input.controller_style_xbox:
            mapper.update(emu.input.controller_style_xbox)

        if emu.num_max_players > 1 and gamepads:
            expanded: dict = {}
            for gp in gamepads:
                for k, v in mapper.items():
                    expanded[k.replace("%NUM_PLAYER%", str(gp.num_player))] = v
            mapper = expanded

        # Apply custom button profile for the active gamepad if it exists
        if gamepads:
            profile = self._prefs.get_gamepad_profile(gamepads[0].id)
            if profile:
                mapper = _apply_profile(mapper, profile)

        lines = self._adb.read_lines(emu.input.file)
        updated = []
        for line in lines:
            eq = line.find("=")
            if eq > 0:
                key = line[:eq].strip()
                value = str(mapper[key]) if key in mapper else line[eq + 1:].strip()
                updated.append(f"{key} = {value}")
            else:
                updated.append(line)

        self._adb.write_lines(updated, emu.input.file)
        return True

    def apply_profile_to_all(self, emus: list[Emu], installed: set[str], gamepads: list[Gamepad]):
        for emu in emus:
            if emu.package not in installed or emu.input is None:
                continue
            use_xbox = self._prefs.get(emu.id, "controllerStyleXbox") == "true"
            try:
                self.update_config(emu, use_xbox, gamepads)
            except Exception:
                pass

    def get_option(self, file: str, key: str) -> str | None:
        for line in self._adb.read_lines(file):
            eq = line.find("=")
            if eq > 0 and line[:eq].strip() == key:
                return line[eq + 1:].strip()
        return None

    def set_option(self, file: str, key: str, value: str):
        lines = self._adb.read_lines(file)
        updated = []
        for line in lines:
            eq = line.find("=")
            if eq > 0 and line[:eq].strip() == key:
                updated.append(f"{key} = {value}")
            else:
                updated.append(line)
        self._adb.write_lines(updated, file)

    def save_import_profile_local(self, emu: Emu, dest_dir: str, gamepad_name: str = ""):
        profile = emu.import_profile
        content = profile.content.replace("\\n", "\n").replace("%GAMEPAD_NAME%", gamepad_name)
        filename = profile.filename.replace("%GAMEPAD_NAME%", gamepad_name)
        Path(dest_dir, filename).write_text(content, encoding="utf-8")

    def save_import_profile_adb(self, emu: Emu, gamepads: list[Gamepad]):
        profile = emu.import_profile
        gamepad_name = gamepads[0].name if gamepads else "Default"
        content = profile.content.replace("\\n", "\n").replace("%GAMEPAD_NAME%", gamepad_name)
        remote_path = profile.adb_path.replace("%GAMEPAD_NAME%", gamepad_name)
        self._adb.push_content(content, remote_path)
