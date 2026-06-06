import flet as ft
from src.config.app_config import APP_TITLE
from src.controllers.emu_controller import EmuController
from src.controllers.gamepad_controller import GamepadController
from src.services.i18n_service import I18n
from src.services.preferences_service import PreferencesService
from src.views.emus_view import EmusView
from src.views.gamepads_view import GamepadsView


class DashboardView:
    def __init__(self, page: ft.Page):
        self._page = page
        self._emu_ctrl = EmuController()
        self._gamepad_ctrl = GamepadController()
        self._prefs = PreferencesService()

    def build(self):
        saved_lang = self._prefs.get_app("lang")
        I18n.load(saved_lang)
        if not saved_lang:
            self._prefs.set_app("lang", I18n.current_lang())

        saved_theme = self._prefs.get_app("theme")
        self._page.theme_mode = (
            ft.ThemeMode.DARK if saved_theme == "dark" else ft.ThemeMode.LIGHT
        )
        self._page.title = APP_TITLE
        self._emu_ctrl.load()
        self._gamepad_ctrl.load()

        gamepads_view = GamepadsView(self._gamepad_ctrl, self._page, self._emu_ctrl)
        emus_view = EmusView(self._page, self._emu_ctrl, self._gamepad_ctrl)

        tabs = ft.Tabs(
            length=2,
            expand=True,
            content=ft.Column(
                expand=True,
                controls=[
                    ft.TabBar(
                        tabs=[
                            ft.Tab(label="Gamepads"),
                            ft.Tab(label="Emus"),
                        ]
                    ),
                    ft.TabBarView(
                        expand=True,
                        controls=[
                            gamepads_view.build(),
                            emus_view.build(),
                        ],
                    ),
                ],
            ),
        )

        def on_refresh(_):
            if tabs.selected_index == 0:
                gamepads_view.refresh()
            else:
                emus_view.refresh()

        def on_toggle_dark(_):
            self._page.theme_mode = (
                ft.ThemeMode.LIGHT
                if self._page.theme_mode == ft.ThemeMode.DARK
                else ft.ThemeMode.DARK
            )
            self._prefs.set_app("theme", "dark" if self._page.theme_mode == ft.ThemeMode.DARK else "light")
            self._page.update()

        self._page.appbar = ft.AppBar(
            title=ft.Text(APP_TITLE),
            actions=[
                ft.IconButton(ft.Icons.DARK_MODE, tooltip="Toggle dark mode", on_click=on_toggle_dark),
                ft.IconButton(ft.Icons.REFRESH, tooltip="Refresh", on_click=on_refresh),
            ],
        )

        self._page.add(tabs)
