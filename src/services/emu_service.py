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
    _DEFAULT_JSON = Path("assets/conf/emus.json")

    def __init__(self):
        self._adb = AdbService()
        self._prefs = PreferencesService()

    def _emus_json(self) -> Path:
        profile_id = PreferencesService.get_active_profile()
        profile_path = Path(f"assets/conf/profiles/{profile_id}/emus.json")
        return profile_path if profile_path.exists() else self._DEFAULT_JSON

    def load_emus(self) -> list[Emu]:
        data = json.loads(self._emus_json().read_text(encoding="utf-8"))
        return [Emu.from_dict(item) for item in data]

    def get_installed_packages(self) -> set[str]:
        # pm list packages works on desktop (ADB) and on Android < 11 or with QUERY_ALL_PACKAGES
        packages = self._adb.get_installed_packages()
        if packages:
            return packages
        # Android 11+ visibility restriction: fall back to per-emulator detection
        return self._detect_installed_by_path()

    def _detect_installed_by_path(self) -> set[str]:
        """
        Detect installed packages without pm list packages.
        Primary: check if the app's external data directory exists (created on first run).
        Fallback: pm path per package (works for packages never run yet).
        Covers both emulators and launchers.
        """
        all_packages = self._all_known_packages()
        installed: set[str] = set()
        for pkg in all_packages:
            if self._data_dir_exists(pkg):
                installed.add(pkg)
            elif self._adb.is_package_installed(pkg):
                installed.add(pkg)
        return installed

    def _all_known_packages(self) -> set[str]:
        packages: set[str] = set()
        for emu in self.load_emus():
            if not emu.deprecated:
                packages.add(emu.package)
        launchers_path = Path("assets/conf/launchers.json")
        if launchers_path.exists():
            data = json.loads(launchers_path.read_text(encoding="utf-8"))
            for launcher in data.get("launchers", []):
                if pkg := launcher.get("package"):
                    packages.add(pkg)
            for platform in data.get("platforms", []):
                for player in platform.get("players", []):
                    if pkg := player.get("package"):
                        packages.add(pkg)
        return packages

    @staticmethod
    def _data_dir_exists(package: str) -> bool:
        for base in ("/storage/emulated/0/Android/data", "/sdcard/Android/data"):
            if Path(f"{base}/{package}").exists():
                return True
        return False

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
