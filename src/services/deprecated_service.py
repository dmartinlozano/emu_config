from src.models.emu import Emu


class DeprecatedEmuChecker:
    """Filters deprecated emulators: only surfaces them when already installed."""

    @staticmethod
    def visible_emus(emus: list[Emu], installed: set[str]) -> list[Emu]:
        return [e for e in emus if not e.deprecated or e.package in installed]
