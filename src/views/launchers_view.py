import asyncio

import flet as ft

from src.controllers.launcher_controller import LauncherController
from src.models.launcher import Launcher
from src.services.i18n_service import I18n
from src.services.install_resolver import resolve_install


class LaunchersView:
    def __init__(self, page: ft.Page, launcher_ctrl: LauncherController):
        self._page = page
        self._ctrl = launcher_ctrl

    def build(self) -> ft.Control:
        return ft.Column(
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=0,
            controls=[self._build_tile(launcher) for launcher in self._ctrl.launchers],
        )

    def _build_tile(self, launcher: Launcher) -> ft.Control:
        installed = launcher.package in self._ctrl.installed_packages

        if installed:
            trailing = ft.Container(
                content=ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, color=ft.Colors.GREEN)
            )
        else:
            install_url = launcher.play_store or (
                f"https://github.com/{launcher.github}/releases" if launcher.github else None
            )
            trailing = ft.ElevatedButton(
                I18n.t("launchers.install"), icon=ft.Icons.DOWNLOAD, url=install_url
            )

        leading = self._build_leading(launcher)
        platforms_count = self._ctrl.platforms_with_players()

        tile = ft.ExpansionTile(
            leading=leading,
            title=ft.Text(launcher.name),
            subtitle=ft.Text(
                I18n.t("launchers.platforms", count=platforms_count),
                size=12,
            ),
            trailing=trailing,
            controls=[self._build_content(launcher)] if installed else [],
        )

        return ft.Card(
            content=tile,
            elevation=2,
            margin=ft.Margin(left=8, right=8, top=1, bottom=1),
        )

    def _build_leading(self, launcher: Launcher) -> ft.Control:
        if launcher.image:
            return ft.Container(
                width=40, height=40,
                border_radius=8,
                clip_behavior=ft.ClipBehavior.HARD_EDGE,
                content=ft.Image(src=f"images/{launcher.image}", width=40, height=40),
            )
        initials = "".join(w[0] for w in launcher.name.split()[:2]).upper()
        return ft.Container(
            width=40, height=40,
            border_radius=8,
            bgcolor=ft.Colors.INDIGO_100,
            content=ft.Text(
                initials,
                size=11,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.INDIGO_700,
                text_align=ft.TextAlign.CENTER,
            ),
            alignment=ft.Alignment(0, 0),
        )

    def _build_content(self, launcher: Launcher) -> ft.Control:
        instruction = I18n.t(f"launchers.instructions.{launcher.id}")
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Text(
                        instruction,
                        size=12,
                        color=ft.Colors.GREY_600,
                        expand=True,
                    ),
                    ft.ElevatedButton(
                        I18n.t("launchers.export"),
                        icon=ft.Icons.UPLOAD_FILE,
                        on_click=lambda _, lid=launcher.id: self._page.run_task(
                            self._do_export, lid
                        ),
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
            ),
            padding=ft.Padding(left=12, right=12, top=8, bottom=12),
        )

    async def _do_export(self, launcher_id: str):
        loop = asyncio.get_running_loop()
        count = await loop.run_in_executor(None, self._ctrl.export, launcher_id)
        self._page.show_dialog(
            ft.SnackBar(ft.Text(I18n.t("launchers.exported", count=count)))
        )
