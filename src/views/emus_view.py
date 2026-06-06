import asyncio

import flet as ft

from src.controllers.emu_controller import EmuController
from src.controllers.gamepad_controller import GamepadController
from src.models.emu import Emu, Successor
from src.services.deprecated_service import DeprecatedEmuChecker
from src.services.github_service import get_latest_release_info
from src.services.install_resolver import ResolveStatus, is_newer_version, resolve_install
from src.services.preferences_service import PreferencesService

_OPTION_FIELDS = [
    ("video_driver",       "Video Driver",       "videoDriver"),
    ("video_scale",        "Video Scale",        "videoScale"),
    ("hide_overlay",       "Hide Overlay",       "hideOverlay"),
    ("region",             "Region",             "region"),
    ("enable_save_states", "Enable Save States", "enableSaveStates"),
]

_PLATFORM_COLORS: dict[str, str] = {
    "Atari 2600":        ft.Colors.BROWN_600,
    "Aventuras gráficas": ft.Colors.TEAL_700,
    "Commodore 64":      ft.Colors.BROWN_400,
    "Dreamcast":         ft.Colors.ORANGE_700,
    "GameCube":          ft.Colors.PURPLE_600,
    "GB / GBC":          ft.Colors.GREEN_600,
    "GBA / GB / GBC":    ft.Colors.GREEN_700,
    "GBA":               ft.Colors.GREEN_700,
    "Mame":              ft.Colors.DEEP_ORANGE_700,
    "Mega Drive":        ft.Colors.BLUE_GREY_700,
    "Neo Geo":           ft.Colors.RED_700,
    "NES":               ft.Colors.RED_900,
    "Nintendo 3DS":      ft.Colors.RED_500,
    "Nintendo 64":       ft.Colors.GREEN_800,
    "Nintendo DS":       ft.Colors.RED_700,
    "PC Engine":         ft.Colors.AMBER_700,
    "PlayStation":       ft.Colors.BLUE_900,
    "PlayStation 2":     ft.Colors.BLUE_700,
    "PlayStation 3":     ft.Colors.BLUE_500,
    "PS Vita":           ft.Colors.INDIGO_400,
    "PSP":               ft.Colors.BLUE_400,
    "Saturn":            ft.Colors.ORANGE_400,
    "SNES":              ft.Colors.PURPLE_700,
    "Wii":               ft.Colors.GREY_600,
    "Wii U":             ft.Colors.BLUE_800,
}

_PLATFORM_SHORT: dict[str, str] = {
    "Atari 2600":        "ATA",
    "Aventuras gráficas": "ADV",
    "Commodore 64":      "C64",
    "Dreamcast":         "DC",
    "GameCube":          "GC",
    "GB / GBC":          "GB",
    "GBA / GB / GBC":    "GBA",
    "GBA":               "GBA",
    "Mame":              "ARC",
    "Mega Drive":        "MD",
    "Neo Geo":           "NEO",
    "NES":               "NES",
    "Nintendo 3DS":      "3DS",
    "Nintendo 64":       "N64",
    "Nintendo DS":       "NDS",
    "PC Engine":         "PCE",
    "PlayStation":       "PS1",
    "PlayStation 2":     "PS2",
    "PlayStation 3":     "PS3",
    "PS Vita":           "PSV",
    "PSP":               "PSP",
    "Saturn":            "SAT",
    "SNES":              "SFC",
    "Wii":               "WII",
    "Wii U":             "WiiU",
}


class EmusView:
    def __init__(self, page: ft.Page, emu_controller: EmuController, gamepad_controller: GamepadController):
        self._page = page
        self._emu_ctrl = emu_controller
        self._gamepad_ctrl = gamepad_controller
        self._prefs = PreferencesService()
        self._column = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)

    def build(self) -> ft.Control:
        self._rebuild()
        return self._column

    def refresh(self):
        self._emu_ctrl.load()
        self._rebuild()
        self._column.update()

    # ------------------------------------------------------------------ tiles

    def _rebuild(self):
        emus = DeprecatedEmuChecker.visible_emus(
            self._emu_ctrl.emus, self._emu_ctrl.installed_packages
        )
        self._column.controls = [self._build_tile(emu) for emu in emus]

    def _build_tile(self, emu: Emu) -> ft.Control:
        if emu.deprecated:
            return self._build_deprecated_tile(emu)

        installed = self._emu_ctrl.is_installed(emu.package)

        if installed:
            trailing = ft.Container(content=ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, color=ft.Colors.GREEN))
            if emu.github:
                self._page.run_task(self._resolve_update, emu, trailing)
        else:
            trailing = ft.Container(content=ft.ProgressRing(width=20, height=20, stroke_width=2))
            self._page.run_task(self._resolve_trailing, emu.play_store, emu.github, trailing)

        tile = ft.ExpansionTile(
            leading=self._build_platform_avatar(emu.platform),
            title=ft.Text(emu.name),
            subtitle=self._build_platform_badge(emu.platform),
            trailing=trailing,
            controls=[self._build_content(emu)] if installed else [],
        )
        return ft.Card(
            content=tile,
            elevation=2,
            margin=ft.margin.symmetric(horizontal=8, vertical=4),
        )

    def _build_deprecated_tile(self, emu: Emu) -> ft.Control:
        succ = emu.successor
        subtitle_text = f"Obsoleto — migra a {succ.name}" if succ else "Obsoleto"

        if succ:
            trailing = ft.Container(content=ft.ProgressRing(width=20, height=20, stroke_width=2))
            self._page.run_task(self._resolve_successor_trailing, succ, trailing)
        else:
            trailing = None

        tile = ft.ListTile(
            leading=ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color=ft.Colors.AMBER),
            title=ft.Text(emu.name, color=ft.Colors.GREY_500),
            subtitle=ft.Text(subtitle_text, size=12),
            trailing=trailing,
        )
        return ft.Card(
            content=tile,
            elevation=1,
            margin=ft.margin.symmetric(horizontal=8, vertical=4),
        )

    # --------------------------------------------------------------- platform helpers

    def _build_platform_avatar(self, platform: str | None) -> ft.Control:
        color = _PLATFORM_COLORS.get(platform, ft.Colors.GREY_600)
        short = _PLATFORM_SHORT.get(platform, platform[:3].upper() if platform else "?")
        return ft.Container(
            width=40,
            height=40,
            border_radius=20,
            bgcolor=color,
            content=ft.Text(short, size=10, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
            alignment=ft.alignment.center,
        )

    def _build_platform_badge(self, platform: str | None) -> ft.Control | None:
        if not platform:
            return None
        color = _PLATFORM_COLORS.get(platform, ft.Colors.GREY_600)
        return ft.Row(
            controls=[
                ft.Container(
                    content=ft.Text(platform, size=10, color=ft.Colors.WHITE),
                    bgcolor=color,
                    border_radius=4,
                    padding=ft.padding.symmetric(horizontal=6, vertical=2),
                )
            ],
            tight=True,
        )

    # --------------------------------------------------------------- install resolution

    async def _resolve_trailing(self, play_store: str | None, github: str | None, container: ft.Container):
        result = await resolve_install(play_store, github)
        if result.status == ResolveStatus.UNAVAILABLE:
            container.content = ft.Icon(ft.Icons.CLOSE, color=ft.Colors.RED_400)
        else:
            container.content = ft.ElevatedButton(
                "Install",
                icon=ft.Icons.DOWNLOAD,
                url=result.url,
            )
        try:
            container.update()
        except Exception:
            pass

    async def _resolve_successor_trailing(self, succ: Successor, container: ft.Container):
        result = await resolve_install(succ.play_store, succ.github)
        if result.status == ResolveStatus.UNAVAILABLE:
            container.content = None
        else:
            container.content = ft.ElevatedButton(
                f"Install {succ.name}",
                icon=ft.Icons.DOWNLOAD,
                url=result.url,
            )
        try:
            container.update()
        except Exception:
            pass

    async def _resolve_update(self, emu: Emu, container: ft.Container):
        loop = asyncio.get_running_loop()
        installed_ver = await loop.run_in_executor(None, self._emu_ctrl.get_installed_version, emu.package)
        if not installed_ver:
            return
        latest = await loop.run_in_executor(None, get_latest_release_info, emu.github)
        if not latest:
            return
        latest_ver, apk_url = latest
        if not is_newer_version(latest_ver, installed_ver):
            return
        container.content = ft.ElevatedButton(
            "Update",
            icon=ft.Icons.SYSTEM_UPDATE,
            url=apk_url,
            style=ft.ButtonStyle(color=ft.Colors.ORANGE_700),
        )
        try:
            container.update()
        except Exception:
            pass

    # --------------------------------------------------------------- widgets

    def _build_content(self, emu: Emu) -> ft.Control:
        gamepads = self._gamepad_ctrl.gamepads
        rows: list[ft.Control] = []

        if emu.roms_path:
            rows.append(self._build_roms_path(emu))

        if emu.input and gamepads:
            rows.append(self._build_mapping_buttons(emu))

        for attr, label, pref_key in _OPTION_FIELDS:
            option_obj = getattr(emu, attr)
            if option_obj:
                rows.append(self._build_option(emu, label, option_obj, pref_key))

        if emu.import_profile:
            rows.append(ft.ElevatedButton(
                "Import/export mapping manually",
                on_click=lambda _, e=emu: self._show_import_dialog(e),
            ))

        return ft.Container(
            content=ft.Column(controls=rows, spacing=8),
            padding=ft.Padding(left=10, top=10, right=10, bottom=10),
        )

    def _build_mapping_buttons(self, emu: Emu) -> ft.Control:
        is_xbox = self._prefs.get(emu.id, "controllerStyleXbox") == "true"

        def on_switch(e):
            use_xbox = e.control.value
            ok = self._emu_ctrl.apply_mapping(emu, use_xbox, self._gamepad_ctrl.gamepads)
            if ok:
                self._prefs.set(emu.id, "controllerStyleXbox", "true" if use_xbox else "false")
            else:
                e.control.value = not use_xbox
                e.control.update()
            self._page.show_dialog(ft.SnackBar(ft.Text("Mapping applied" if ok else "Error applying mapping")))

        return ft.Row(
            controls=[
                ft.Switch(value=is_xbox, on_change=on_switch),
                ft.Text("Intercambiar botones A/B"),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def _build_roms_path(self, emu: Emu) -> ft.Control:
        saved = self._prefs.get(emu.id, "romsPath")
        if not saved:
            saved = self._emu_ctrl.get_option(emu.roms_path.file, emu.roms_path.key) or ""
            if saved:
                self._prefs.set(emu.id, "romsPath", saved)
        field = ft.TextField(value=saved or "", label="Roms Path", read_only=True, expand=True)
        picker = ft.FilePicker()

        async def on_pick(_):
            path = await picker.get_directory_path()
            if path:
                self._prefs.set(emu.id, "romsPath", path)
                self._emu_ctrl.set_option(emu.roms_path.file, emu.roms_path.key, path)
                field.value = path
                field.update()

        return ft.Row(controls=[field, ft.IconButton(ft.Icons.FOLDER_OPEN, on_click=on_pick)])

    def _build_option(self, emu: Emu, label: str, option_obj, pref_key: str) -> ft.Control:
        options = option_obj.options
        saved = self._prefs.get(emu.id, pref_key)
        current = saved if saved in options.values() else next(iter(options.values()))
        dropdown = ft.Dropdown(
            value=current,
            options=[ft.dropdown.Option(key=v, text=k) for k, v in options.items()],
            on_select=lambda e, obj=option_obj, pk=pref_key: self._on_option_changed(e, emu, obj, pk),
        )
        return ft.Row(controls=[ft.Text(label, width=140), dropdown])

    # ---------------------------------------------------------------- events

    def _on_option_changed(self, e: ft.ControlEvent, emu: Emu, option_obj, pref_key: str):
        self._prefs.set(emu.id, pref_key, e.control.value)
        self._emu_ctrl.set_option(option_obj.file, option_obj.key, e.control.value)

    def _show_import_dialog(self, emu: Emu):
        profile = emu.import_profile

        if profile.adb_path:
            def on_accept(_):
                self._page.pop_dialog()
                self._emu_ctrl.save_import_profile_adb(emu, self._gamepad_ctrl.gamepads)
                self._page.show_dialog(ft.SnackBar(ft.Text("Mapping written to device")))
        else:
            picker = ft.FilePicker()

            async def on_accept(_):
                self._page.pop_dialog()
                path = await picker.get_directory_path(dialog_title="Save profile")
                if path:
                    gamepad_name = self._gamepad_ctrl.gamepads[0].name if self._gamepad_ctrl.gamepads else ""
                    self._emu_ctrl.save_import_profile_local(emu, path, gamepad_name)
                    self._page.show_dialog(ft.SnackBar(ft.Text(f"Profile saved to {path}")))

        dlg = ft.AlertDialog(
            title=ft.Text("Import/export mapping manually"),
            content=ft.Text(profile.description),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self._page.pop_dialog()),
                ft.TextButton("Accept", on_click=on_accept),
            ],
        )
        self._page.show_dialog(dlg)
