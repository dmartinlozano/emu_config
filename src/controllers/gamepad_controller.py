from src.models.gamepad import Gamepad
from src.services.adb_service import AdbService
from src.services.gamepad_service import GamepadService
from src.services.preferences_service import PreferencesService


class GamepadController:
    def __init__(self):
        self._service = GamepadService()
        self._adb = AdbService()
        self._prefs = PreferencesService()
        self._gamepads: list[Gamepad] = []

    def load(self):
        self._gamepads = self._service.get_gamepads()

    @property
    def gamepads(self) -> list[Gamepad]:
        return self._gamepads

    def swap_with_player1(self, index: int):
        if 0 < index < len(self._gamepads):
            self._gamepads[0], self._gamepads[index] = self._gamepads[index], self._gamepads[0]
            self._gamepads[0].num_player = 1
            self._gamepads[index].num_player = index + 1

    def delete(self, gamepad_id: str):
        self._gamepads = [g for g in self._gamepads if g.id != gamepad_id]
        for i, gp in enumerate(self._gamepads):
            gp.num_player = i + 1

    async def detect_button_press(self, device_path: str, timeout: float = 10.0) -> int | None:
        return await self._adb.detect_button_press(device_path, timeout)

    def get_profile(self, gamepad_id: str) -> dict | None:
        return self._prefs.get_gamepad_profile(gamepad_id)

    def save_profile(self, gamepad_id: str, profile: dict[str, int]):
        self._prefs.set_gamepad_profile(gamepad_id, profile)
