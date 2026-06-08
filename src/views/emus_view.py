import asyncio

import flet as ft

from src.controllers.emu_controller import EmuController
from src.controllers.gamepad_controller import GamepadController
from src.models.emu import Emu, Successor
from src.services.deprecated_service import DeprecatedEmuChecker
from src.services.github_service import get_latest_release_info
from src.services.i18n_service import I18n
from src.services.install_resolver import ResolveStatus, is_newer_version, resolve_install
from src.services.preferences_service import PreferencesService
from src.views.platform_theme import (
    PLATFORM_COLORS,
    PLATFORM_SHORT,
    build_platform_avatar,
    build_platform_badge,
)

_OPTION_FIELDS = [
    ("video_driver",       "Video Driver",       "videoDriver"),
    ("video_scale",        "Video Scale",        "videoScale"),
    ("hide_overlay",       "Hide Overlay",       "hideOverlay"),
    ("region",             "Region",             "region"),
    ("enable_save_states", "Enable Save States", "enableSaveStates"),
]


class EmusView:
    def __init__(self, page: ft.Page, emu_controller: EmuController, gamepad_controller: GamepadController):
        self._page = page
        self._emu_ctrl = emu_controller
        self._gamepad_ctrl = gamepad_controller
        self._prefs = PreferencesService()
        self._column = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=0)
        self._update_targets: list[tuple[Emu, ft.Container]] = []

    def build(self) -> ft.Control:
        self._rebuild()
        self._page.run_task(self._check_all_updates)
        return self._column

    def refresh(self):
        self._emu_ctrl.load()
        self._rebuild()
        self._column.update()
        self._page.run_task(self._check_all_updates)

    # ------------------------------------------------------------------ tiles

    def _rebuild(self):
        self._update_targets = []
        emus = DeprecatedEmuChecker.visible_emus(
            self._emu_ctrl.emus, self._emu_ctrl.installed_packages
        )
        self._column.controls = [self._build_tile(emu) for emu in emus]

    @staticmethod
    def _has_content(emu: Emu) -> bool:
        return bool(
            emu.input
            or emu.roms_path
            or emu.video_driver
            or emu.video_scale
            or emu.hide_overlay
            or emu.region
            or emu.enable_save_states
            or emu.import_profile
        )

    def _build_tile(self, emu: Emu) -> ft.Control:
        if emu.deprecated:
            return self._build_deprecated_tile(emu)

        installed = self._emu_ctrl.is_installed(emu.package)

        if installed:
            trailing = ft.Container(content=ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, color=ft.Colors.GREEN))
            if emu.github:
                self._update_targets.append((emu, trailing))
        else:
            trailing = ft.Container(content=ft.ProgressRing(width=20, height=20, stroke_width=2))

        has_content = self._has_content(emu)

        if has_content:
            tile = ft.ExpansionTile(
                leading=build_platform_avatar(emu),
                title=ft.Text(emu.name),
                subtitle=build_platform_badge(emu.platform),
                trailing=trailing,
                controls=[self._build_content(emu)] if installed else [],
            )
        else:
            tile = ft.ListTile(
                leading=build_platform_avatar(emu),
                title=ft.Text(emu.name),
                subtitle=build_platform_badge(emu.platform),
                trailing=trailing,
            )

        card = ft.Card(
            content=tile,
            elevation=2,
            margin=ft.Margin(left=8, right=8, top=1, bottom=1),
        )

        if not installed:
            self._page.run_task(self._resolve_trailing, emu.play_store, emu.github, trailing, card)

        return card

    def _build_deprecated_tile(self, emu: Emu) -> ft.Control:
        succ = emu.successor
        subtitle_text = (
            I18n.t("emus.obsolete_migrate", name=succ.name) if succ
            else I18n.t("emus.obsolete")
        )

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
            margin=ft.Margin(left=8, right=8, top=1, bottom=1),
        )

    # --------------------------------------------------------------- install resolution

    async def _resolve_trailing(self, play_store: str | None, github: str | None, container: ft.Container, card: ft.Card):
        result = await resolve_install(play_store, github)
        if result.status == ResolveStatus.UNAVAILABLE:
            try:
                self._column.controls.remove(card)
                self._column.update()
            except Exception:
                pass
            return
        container.content = ft.ElevatedButton(
            I18n.t("install"),
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
                f"{I18n.t('install')} {succ.name}",
                icon=ft.Icons.DOWNLOAD,
                url=result.url,
            )
        try:
            container.update()
        except Exception:
            pass

    async def _check_all_updates(self):
        targets = list(self._update_targets)
        if not targets:
            return
        loop = asyncio.get_running_loop()

        async def _check_one(emu: Emu, container: ft.Container):
            installed_ver = await loop.run_in_executor(
                None, self._emu_ctrl.get_installed_version, emu.package
            )
            if not installed_ver:
                return
            latest = await loop.run_in_executor(None, get_latest_release_info, emu.github)
            if not latest:
                return
            latest_ver, apk_url = latest
            if not is_newer_version(latest_ver, installed_ver):
                return
            container.content = ft.ElevatedButton(
                I18n.t("update"),
                icon=ft.Icons.SYSTEM_UPDATE,
                url=apk_url,
                style=ft.ButtonStyle(color=ft.Colors.ORANGE_700),
            )
            try:
                container.update()
            except Exception:
                pass

        await asyncio.gather(*[_check_one(emu, c) for emu, c in targets])

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
                I18n.t("emus.import_export"),
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
            self._page.show_dialog(ft.SnackBar(ft.Text(
                I18n.t("emus.mapping_applied") if ok else I18n.t("emus.mapping_error")
            )))

        return ft.Row(
            controls=[
                ft.Switch(value=is_xbox, on_change=on_switch),
                ft.Text(I18n.t("emus.swap_ab")),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def _build_roms_path(self, emu: Emu) -> ft.Control:
        saved = self._prefs.get(emu.id, "romsPath")
        if not saved:
            saved = self._emu_ctrl.get_option(emu.roms_path.file, emu.roms_path.key) or ""
            if saved:
                self._prefs.set(emu.id, "romsPath", saved)
        field = ft.TextField(value=saved or "", label=I18n.t("emus.roms_path"), read_only=True, expand=True)

        async def on_pick(_):
            path = await ft.FilePicker().get_directory_path()
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
            async def on_accept(_):
                self._page.pop_dialog()
                path = await ft.FilePicker().get_directory_path(dialog_title="Save profile")
                if path:
                    gamepad_name = self._gamepad_ctrl.gamepads[0].name if self._gamepad_ctrl.gamepads else ""
                    self._emu_ctrl.save_import_profile_local(emu, path, gamepad_name)
                    self._page.show_dialog(ft.SnackBar(ft.Text(f"Profile saved to {path}")))

        dlg = ft.AlertDialog(
            title=ft.Text(I18n.t("emus.import_export")),
            content=ft.Text(profile.description),
            actions=[
                ft.TextButton(I18n.t("cancel"), on_click=lambda _: self._page.pop_dialog()),
                ft.TextButton(I18n.t("accept"), on_click=on_accept),
            ],
        )
        self._page.show_dialog(dlg)
