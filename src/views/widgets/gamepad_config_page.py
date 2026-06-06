import asyncio
import os

import flet as ft

from src.config.button_profile import DEFAULT_PROFILE, FLET_KEY_TO_ANDROID, SEMANTIC_BUTTONS
from src.controllers.emu_controller import EmuController
from src.controllers.gamepad_controller import GamepadController
from src.models.gamepad import Gamepad

_TIMEOUT = 10.0
_ROUTE = "/gamepad_config"


def _is_android() -> bool:
    return os.path.exists("/system/build.prop")


class GamepadConfigPage:
    def __init__(self, page: ft.Page, gamepad: Gamepad, controller: GamepadController, emu_controller: EmuController):
        self._page = page
        self._gamepad = gamepad
        self._ctrl = controller
        self._emu_ctrl = emu_controller
        self._detected: dict[str, int] = {}
        self._rows: list[ft.Control] = []
        self._status: ft.Text = ft.Text("", italic=True, color=ft.Colors.BLUE_400)
        self._cancel_event = asyncio.Event()
        self._prev_keyboard_handler = None

    # ------------------------------------------------------------------ public

    def show(self):
        self._show_impl()

    def _show_impl(self):
        existing = self._ctrl.get_profile(self._gamepad.id) or {}
        self._detected = dict(existing)
        self._rows = [self._make_row(sem, label) for sem, label in SEMANTIC_BUTTONS]

        self._prev_keyboard_handler = self._page.on_keyboard_event
        self._page.on_keyboard_event = self._absorb_nav_keys

        view = ft.View(
            route=_ROUTE,
            appbar=ft.AppBar(
                leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=self._go_back),
                title=ft.Text(self._gamepad.name),
            ),
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Container(
                    padding=ft.Padding(left=16, right=16, top=8, bottom=16),
                    content=ft.Column(
                        spacing=10,
                        controls=[
                            ft.ElevatedButton(
                                "Detectar todos",
                                on_click=self._on_detect_all,
                                icon=ft.Icons.GAMEPAD,
                            ),
                            ft.Text(
                                "O pulsa un botón de la lista para asignarlo individualmente.",
                                size=12,
                                color=ft.Colors.GREY_600,
                            ),
                            self._status,
                            ft.Divider(),
                            *self._rows,
                        ],
                    ),
                )
            ],
        )
        self._page.views.append(view)
        self._page.update()

    # --------------------------------------------------------------- rows

    def _make_row(self, sem: str, label: str) -> ft.Control:
        code = self._detected.get(sem)
        code_text = ft.Text(
            str(code) if code is not None else "—",
            color=ft.Colors.GREEN if code is not None else ft.Colors.GREY_400,
        )

        async def on_tap(e, s=sem):
            await self._detect_one(s)

        tile = ft.ListTile(
            title=ft.Text(label),
            trailing=code_text,
            on_click=on_tap,
        )
        tile.data = (sem, code_text)
        return tile

    def _update_row(self, sem: str, code: int | None):
        for tile in self._rows:
            s, code_text = tile.data
            if s != sem:
                continue
            code_text.value = str(code) if code is not None else "—"
            code_text.color = ft.Colors.GREEN if code is not None else ft.Colors.GREY_400
            tile.update()
            break

    # --------------------------------------------------------------- detection

    async def _detect_one(self, sem: str) -> int | None:
        label = next(lbl for s, lbl in SEMANTIC_BUTTONS if s == sem)
        self._status.value = f"Pulsa  {label}…"
        self._status.update()

        if _is_android():
            code = await self._detect_via_keyboard(sem)
        else:
            if not self._gamepad.device_path:
                self._status.value = "Sin ruta de dispositivo — reconecta y refresca."
                self._status.update()
                return None
            code = await self._ctrl.detect_button_press(self._gamepad.device_path, _TIMEOUT)

        if code is not None:
            self._detected[sem] = code
            self._update_row(sem, code)
            self._status.value = f"✓  {label}  →  {code}"
            self._autosave()
        else:
            self._status.value = f"No detectado — {label}."
        self._status.update()
        return code

    async def _detect_via_keyboard(self, sem: str) -> int | None:
        """
        On Android we can't read /dev/input without root.
        Flutter does fire KeyboardEvent for gamepad buttons, but the keyLabel
        is empty ("") for face/shoulder buttons. For those we fall back to the
        DEFAULT_PROFILE code so the user at least gets guided confirmation.
        D-pad buttons (Arrow Up/Down/Left/Right) ARE identified correctly.
        """
        queue: asyncio.Queue[str] = asyncio.Queue()

        def on_key(e: ft.KeyboardEvent):
            queue.put_nowait(e.key)

        self._page.on_keyboard_event = on_key
        try:
            key = await asyncio.wait_for(queue.get(), timeout=_TIMEOUT)
        except asyncio.TimeoutError:
            return None
        finally:
            self._page.on_keyboard_event = self._absorb_nav_keys

        # If Flutter gave us a recognisable label, use its mapped keycode.
        if key in FLET_KEY_TO_ANDROID:
            return FLET_KEY_TO_ANDROID[key]

        # Empty label = gamepad face/shoulder button (Flutter limitation).
        # Fall back to the standard code for this semantic button.
        fallback = DEFAULT_PROFILE.get(sem)
        if fallback is not None:
            self._status.value = f"Botón pulsado → código estándar {fallback}"
            self._status.update()
            await asyncio.sleep(0.6)
            return fallback

        return None

    async def _detect_all(self):
        for sem, _ in SEMANTIC_BUTTONS:
            if self._cancel_event.is_set():
                break
            await self._detect_one(sem)
            await asyncio.sleep(0.3)
        self._status.value = "Detección completa."
        self._status.update()

    def _autosave(self):
        profile = {**DEFAULT_PROFILE, **self._detected}
        self._ctrl.save_profile(self._gamepad.id, profile)
        asyncio.ensure_future(self._apply_to_all_emus())

    async def _apply_to_all_emus(self):
        loop = asyncio.get_running_loop()
        gamepads = self._ctrl.gamepads
        await loop.run_in_executor(None, self._emu_ctrl.apply_profile_to_all, gamepads)

    # --------------------------------------------------------------- handlers

    def _absorb_nav_keys(self, e: ft.KeyboardEvent):
        pass  # prevent D-pad/arrow from scrolling the list

    def _on_detect_all(self, _):
        self._cancel_event.clear()
        asyncio.ensure_future(self._detect_all())

    def _go_back(self, _):
        self._cancel_event.set()
        self._page.on_keyboard_event = self._prev_keyboard_handler
        if len(self._page.views) > 1:
            self._page.views.pop()
        self._page.update()
