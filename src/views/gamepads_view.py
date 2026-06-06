import flet as ft
from src.controllers.emu_controller import EmuController
from src.controllers.gamepad_controller import GamepadController
from src.models.gamepad import Gamepad
from src.views.widgets.gamepad_config_page import GamepadConfigPage


class GamepadsView:
    def __init__(self, controller: GamepadController, page: ft.Page, emu_controller: EmuController):
        self._controller = controller
        self._page = page
        self._emu_ctrl = emu_controller
        self._list = ft.Column(spacing=0)

    def build(self) -> ft.Control:
        self._rebuild()
        return ft.Column(
            controls=[self._list],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    def refresh(self):
        self._controller.load()
        self._rebuild()
        self._list.update()

    def _rebuild(self):
        self._list.controls = [self._build_row(i, gp) for i, gp in enumerate(self._controller.gamepads)]

    def _build_row(self, index: int, gp: Gamepad) -> ft.Control:
        return ft.Column(
            controls=[
                ft.ListTile(
                    leading=ft.Container(
                        content=ft.Text(f"P{gp.num_player}", weight=ft.FontWeight.BOLD),
                        width=32,
                    ),
                    title=ft.Text(gp.name),
                    subtitle=ft.Text(gp.descriptor or "", size=11, color=ft.Colors.GREY_600),
                    trailing=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.DRAG_HANDLE, color=ft.Colors.GREY_400),
                            ft.IconButton(
                                ft.Icons.DELETE_OUTLINE,
                                icon_color=ft.Colors.RED_400,
                                tooltip="Remove",
                                on_click=lambda _, gid=gp.id: self._delete(gid),
                            ),
                        ],
                        tight=True,
                    ),
                    on_click=lambda _, gp=gp: self._open_config(gp),
                    tooltip="Tap to configure buttons",
                ),
                ft.Divider(height=1),
            ],
            spacing=0,
        )

    def _open_config(self, gp: Gamepad):
        GamepadConfigPage(self._page, gp, self._controller, self._emu_ctrl).show()

    def _promote(self, index: int):
        if index == 0:
            return
        self._controller.swap_with_player1(index)
        self._rebuild()
        self._list.update()

    def _delete(self, gamepad_id: str):
        self._controller.delete(gamepad_id)
        self._rebuild()
        self._list.update()
