from src.models.emu import Emu
from src.models.gamepad import Gamepad
from src.services.emu_service import EmuService


class EmuController:
    def __init__(self):
        self._service = EmuService()
        self._emus: list[Emu] = []
        self._installed: set[str] = set()

    def load(self):
        self._emus = self._service.load_emus()
        self._installed = self._service.get_installed_packages()

    @property
    def emus(self) -> list[Emu]:
        return self._emus

    @property
    def installed_packages(self) -> set[str]:
        return self._installed

    def is_installed(self, package: str) -> bool:
        return package in self._installed

    def get_installed_version(self, package: str) -> str | None:
        return self._service.get_package_version(package)

    def apply_mapping(self, emu: Emu, use_xbox_style: bool, gamepads: list[Gamepad]) -> bool:
        return self._service.update_config(emu, use_xbox_style, gamepads)

    def apply_profile_to_all(self, gamepads: list[Gamepad]):
        self._service.apply_profile_to_all(self._emus, self._installed, gamepads)

    def get_option(self, file: str, key: str) -> str | None:
        return self._service.get_option(file, key)

    def set_option(self, file: str, key: str, value: str):
        self._service.set_option(file, key, value)

    def save_import_profile_local(self, emu: Emu, dest_dir: str, gamepad_name: str = ""):
        self._service.save_import_profile_local(emu, dest_dir, gamepad_name)

    def save_import_profile_adb(self, emu: Emu, gamepads: list[Gamepad]):
        self._service.save_import_profile_adb(emu, gamepads)
