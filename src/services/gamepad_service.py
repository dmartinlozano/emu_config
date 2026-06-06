from src.models.gamepad import Gamepad
from src.services.adb_service import AdbService


class GamepadService:
    def __init__(self):
        self._adb = AdbService()

    def get_gamepads(self) -> list[Gamepad]:
        raw = self._adb.get_gamepads()
        gamepads = []
        for i, entry in enumerate(raw):
            gamepads.append(Gamepad(
                id=entry.get("descriptor") or entry["name"],
                name=entry["name"],
                num_player=i + 1,
                descriptor=entry.get("descriptor"),
                vendor_id=entry.get("vendor_id"),
                product_id=entry.get("product_id"),
                device_path=entry.get("device_path"),
            ))
        return gamepads
