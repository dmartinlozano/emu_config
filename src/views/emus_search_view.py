import flet as ft

from src.controllers.emu_controller import EmuController
from src.controllers.gamepad_controller import GamepadController
from src.models.emu import Emu
from src.services.deprecated_service import DeprecatedEmuChecker
from src.services.i18n_service import I18n
from src.views.platform_theme import PLATFORM_COLORS, build_platform_avatar, build_platform_badge


class EmuSearchView:
    def __init__(self, page: ft.Page, emu_ctrl: EmuController, gamepad_ctrl: GamepadController):
        self._page = page
        self._emu_ctrl = emu_ctrl
        self._gamepad_ctrl = gamepad_ctrl
        self._all_emus: list[Emu] = []
        self._query: str = ""
        self._selected_platforms: set[str] = set()
        self._results_column = ft.Column(spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)

    # ------------------------------------------------------------------ public

    def show(self):
        self._all_emus = DeprecatedEmuChecker.visible_emus(
            self._emu_ctrl.emus, self._emu_ctrl.installed_packages
        )
        platforms = sorted({e.platform for e in self._all_emus if e.platform})
        self._query = ""
        self._selected_platforms = set()

        self._refresh_results()

        chips_row = ft.Row(
            controls=[
                ft.Chip(
                    label=ft.Text(platform, size=11),
                    selected=False,
                    selected_color=PLATFORM_COLORS.get(platform, ft.Colors.GREY_600),
                    on_select=lambda e, p=platform: self._on_chip_toggle(p, e.data),
                )
                for platform in platforms
            ],
            scroll=ft.ScrollMode.AUTO,
            wrap=False,
        )

        body = ft.Column(
            expand=True,
            spacing=0,
            controls=[
                ft.Container(
                    content=chips_row,
                    padding=ft.Padding(left=8, right=8, top=4, bottom=4),
                ),
                ft.Divider(height=1),
                self._results_column,
            ],
        )

        view = ft.View(
            route="/emu_search",
            padding=0,
            appbar=ft.AppBar(
                leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=self._go_back),
                title=ft.TextField(
                    hint_text=I18n.t("search.hint"),
                    prefix_icon=ft.Icons.SEARCH,
                    expand=True,
                    on_change=self._on_query_change,
                    autofocus=True,
                ),
            ),
            controls=[body],
        )

        self._page.views.append(view)
        self._page.update()

    # ------------------------------------------------------------------ events

    def _on_chip_toggle(self, platform: str, data: str):
        if data == "true":
            self._selected_platforms.add(platform)
        else:
            self._selected_platforms.discard(platform)
        self._refresh_results()
        self._results_column.update()

    def _on_query_change(self, e: ft.ControlEvent):
        self._query = e.control.value or ""
        self._refresh_results()
        self._results_column.update()

    def _go_back(self, _):
        if len(self._page.views) > 1:
            self._page.views.pop()
        self._page.update()

    # ------------------------------------------------------------------ helpers

    def _refresh_results(self):
        query = self._query.lower()
        results = [
            emu for emu in self._all_emus
            if (not query or query in emu.name.lower() or (emu.platform and query in emu.platform.lower()))
            and (not self._selected_platforms or emu.platform in self._selected_platforms)
        ]
        self._results_column.controls = [self._build_tile(emu) for emu in results]

    def _build_tile(self, emu: Emu) -> ft.Control:
        installed = self._emu_ctrl.is_installed(emu.package)

        if installed:
            trailing = ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, color=ft.Colors.GREEN)
        elif emu.play_store:
            trailing = ft.ElevatedButton(
                I18n.t("install"),
                icon=ft.Icons.DOWNLOAD,
                url=emu.play_store,
            )
        elif emu.github:
            trailing = ft.ElevatedButton(
                I18n.t("install"),
                icon=ft.Icons.DOWNLOAD,
                url=f"https://github.com/{emu.github}/releases",
            )
        else:
            trailing = ft.Icon(ft.Icons.CLOSE, color=ft.Colors.RED_400)

        tile = ft.ListTile(
            leading=build_platform_avatar(emu),
            title=ft.Text(emu.name),
            subtitle=build_platform_badge(emu.platform),
            trailing=trailing,
        )
        return ft.Card(
            content=tile,
            elevation=2,
            margin=ft.Margin(left=8, right=8, top=1, bottom=1),
        )
