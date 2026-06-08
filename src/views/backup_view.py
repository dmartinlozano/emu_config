import asyncio

import flet as ft

from src.controllers.emu_controller import EmuController
from src.services.backup_service import BackupService
from src.services.i18n_service import I18n


class BackupView:
    _ROUTE = "/backup"

    def __init__(self, page: ft.Page, emu_ctrl: EmuController):
        self._page = page
        self._emu_ctrl = emu_ctrl
        self._service = BackupService()

    def show(self):
        backup_status = ft.Text("", size=12)
        restore_status = ft.Text("", size=12)
        backup_btn = ft.ElevatedButton(
            I18n.t("backup.create"),
            icon=ft.Icons.BACKUP,
        )
        restore_btn = ft.ElevatedButton(
            I18n.t("backup.select"),
            icon=ft.Icons.FOLDER_OPEN,
        )

        async def do_backup(_):
            backup_btn.disabled = True
            backup_btn.update()
            backup_status.value = I18n.t("backup.creating")
            backup_status.color = ft.Colors.BLUE_400
            backup_status.update()
            try:
                loop = asyncio.get_running_loop()
                path = await loop.run_in_executor(
                    None,
                    self._service.create_backup,
                    self._emu_ctrl.emus,
                    self._emu_ctrl.installed_packages,
                )
                backup_status.value = I18n.t("backup.saved", path=path)
                backup_status.color = ft.Colors.GREEN
            except Exception as e:
                backup_status.value = f"Error: {e}"
                backup_status.color = ft.Colors.RED_400
            finally:
                backup_btn.disabled = False
                backup_btn.update()
                backup_status.update()

        async def do_restore(_):
            files = await ft.FilePicker().pick_files(
                dialog_title=I18n.t("backup.select_title"),
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["zip"],
                allow_multiple=False,
            )
            if not files or not files[0].path:
                if files:
                    restore_status.value = I18n.t("backup.error_no_path")
                    restore_status.color = ft.Colors.RED_400
                    restore_status.update()
                return

            restore_btn.disabled = True
            restore_btn.update()
            restore_status.value = I18n.t("backup.restoring")
            restore_status.color = ft.Colors.BLUE_400
            restore_status.update()
            try:
                loop = asyncio.get_running_loop()
                n = await loop.run_in_executor(None, self._service.restore_backup, files[0].path)
                restore_status.value = I18n.t("backup.restored", count=n)
                restore_status.color = ft.Colors.GREEN
            except Exception as e:
                restore_status.value = f"Error: {e}"
                restore_status.color = ft.Colors.RED_400
            finally:
                restore_btn.disabled = False
                restore_btn.update()
                restore_status.update()

        backup_btn.on_click = do_backup
        restore_btn.on_click = do_restore

        def go_back(_):
            if len(self._page.views) > 1:
                self._page.views.pop()
            self._page.update()

        body = ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=0,
            controls=[
                ft.Container(
                    padding=ft.Padding(left=16, right=16, top=20, bottom=16),
                    content=ft.Column(
                        spacing=10,
                        controls=[
                            ft.Text(I18n.t("backup.section_backup"), size=15, weight=ft.FontWeight.BOLD),
                            ft.Text(
                                I18n.t("backup.section_backup_desc"),
                                size=12,
                                color=ft.Colors.GREY_600,
                            ),
                            backup_btn,
                            backup_status,
                        ],
                    ),
                ),
                ft.Divider(),
                ft.Container(
                    padding=ft.Padding(left=16, right=16, top=16, bottom=20),
                    content=ft.Column(
                        spacing=10,
                        controls=[
                            ft.Text(I18n.t("backup.section_restore"), size=15, weight=ft.FontWeight.BOLD),
                            ft.Text(
                                I18n.t("backup.section_restore_desc"),
                                size=12,
                                color=ft.Colors.GREY_600,
                            ),
                            restore_btn,
                            restore_status,
                        ],
                    ),
                ),
            ],
        )

        view = ft.View(
            route=self._ROUTE,
            appbar=ft.AppBar(
                leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=go_back),
                title=ft.Text(I18n.t("backup.title")),
            ),
            controls=[body],
        )
        self._page.views.append(view)
        self._page.update()
