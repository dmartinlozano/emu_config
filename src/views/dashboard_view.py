import flet as ft
from src.config.app_config import APP_TITLE
from src.controllers.emu_controller import EmuController
from src.controllers.gamepad_controller import GamepadController
from src.controllers.launcher_controller import LauncherController
from src.models.profile import Profile
from src.services.i18n_service import I18n
from src.services.preferences_service import PreferencesService
from src.services.profile_service import ProfileService
from src.views.backup_view import BackupView
from src.views.emus_search_view import EmuSearchView
from src.views.emus_view import EmusView
from src.views.gamepads_view import GamepadsView
from src.views.launchers_view import LaunchersView
from src.views.profiles_view import ProfilesView


class DashboardView:
    def __init__(self, page: ft.Page):
        self._page = page
        self._emu_ctrl = EmuController()
        self._gamepad_ctrl = GamepadController()
        self._prefs = PreferencesService()
        self._profile_svc = ProfileService()

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

        self._profile_svc.init_active()
        self._emu_ctrl.load()
        self._gamepad_ctrl.load()

        gamepads_view = GamepadsView(self._gamepad_ctrl, self._page, self._emu_ctrl)
        emus_view = EmusView(self._page, self._emu_ctrl, self._gamepad_ctrl)
        launcher_ctrl = LauncherController(self._emu_ctrl.installed_packages)
        launchers_view = LaunchersView(self._page, launcher_ctrl)

        gp_content = gamepads_view.build()
        emu_content = emus_view.build()
        launcher_content = launchers_view.build()

        content_area = ft.Container(content=gp_content, expand=True)

        def on_nav_change(e):
            idx = e.control.selected_index
            if idx == 0:
                content_area.content = gp_content
            elif idx == 1:
                content_area.content = emu_content
            else:
                content_area.content = launcher_content
            content_area.update()

        rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=72,
            on_change=on_nav_change,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.Icons.SPORTS_ESPORTS_OUTLINED,
                    selected_icon=ft.Icons.SPORTS_ESPORTS,
                    label=I18n.t("app.tab_gamepads"),
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.VIDEOGAME_ASSET_OUTLINED,
                    selected_icon=ft.Icons.VIDEOGAME_ASSET,
                    label=I18n.t("app.tab_emus"),
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.APPS_OUTLINED,
                    selected_icon=ft.Icons.APPS,
                    label=I18n.t("app.tab_launchers"),
                ),
            ],
        )

        layout = ft.Row(
            expand=True,
            spacing=0,
            controls=[
                rail,
                ft.VerticalDivider(width=1),
                content_area,
            ],
        )

        title_text = ft.Text(self._title_label())

        def on_profile_activated(profile: Profile):
            self._emu_ctrl.load()
            emus_view.refresh()
            title_text.value = self._title_label()
            title_text.update()

        def on_refresh(_):
            if rail.selected_index == 0:
                gamepads_view.refresh()
            elif rail.selected_index == 1:
                emus_view.refresh()

        def on_toggle_dark(_):
            self._page.theme_mode = (
                ft.ThemeMode.LIGHT
                if self._page.theme_mode == ft.ThemeMode.DARK
                else ft.ThemeMode.DARK
            )
            self._prefs.set_app("theme", "dark" if self._page.theme_mode == ft.ThemeMode.DARK else "light")
            self._page.update()

        def open_profiles(_):
            ProfilesView(self._page, self._profile_svc, on_profile_activated).show()

        def open_language(_):
            langs = I18n.available_langs()
            dd = ft.Dropdown(
                value=I18n.current_lang(),
                options=[ft.dropdown.Option(key=code, text=name) for code, name in langs.items()],
                width=220,
            )

            def on_apply(_):
                new_lang = dd.value
                self._page.pop_dialog()
                self._prefs.set_app("lang", new_lang)
                self._page.clean()
                self._page.appbar = None
                self._page.overlay.clear()
                self.build()

            self._page.show_dialog(ft.AlertDialog(
                title=ft.Text(I18n.t("app.language_modal_title")),
                content=dd,
                actions=[
                    ft.TextButton(I18n.t("cancel"), on_click=lambda _: self._page.pop_dialog()),
                    ft.TextButton(I18n.t("accept"), on_click=on_apply),
                ],
            ))

        self._page.appbar = ft.AppBar(
            title=title_text,
            actions=[
                ft.IconButton(ft.Icons.SEARCH, tooltip=I18n.t("app.search_emus"),
                              on_click=lambda _: EmuSearchView(self._page, self._emu_ctrl, self._gamepad_ctrl).show()),
                ft.IconButton(ft.Icons.MANAGE_ACCOUNTS, tooltip=I18n.t("app.profiles"), on_click=open_profiles),
                ft.IconButton(ft.Icons.BACKUP, tooltip=I18n.t("app.backup_restore"),
                              on_click=lambda _: BackupView(self._page, self._emu_ctrl).show()),
                ft.IconButton(ft.Icons.LANGUAGE, tooltip=I18n.t("app.language"), on_click=open_language),
                ft.IconButton(ft.Icons.DARK_MODE, tooltip=I18n.t("app.dark_mode"), on_click=on_toggle_dark),
                ft.IconButton(ft.Icons.REFRESH, tooltip=I18n.t("app.refresh"), on_click=on_refresh),
            ],
        )

        self._page.add(layout)

    def _title_label(self) -> str:
        active = self._profile_svc.get_active()
        if active.id == "default":
            return APP_TITLE
        return f"{APP_TITLE} · {active.name}"
