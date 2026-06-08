from typing import Callable

import flet as ft

from src.models.profile import Profile
from src.services.i18n_service import I18n
from src.services.profile_service import ProfileService


class ProfilesView:
    _ROUTE = "/profiles"

    def __init__(self, page: ft.Page, profile_service: ProfileService, on_activated: Callable):
        self._page = page
        self._svc = profile_service
        self._on_activated = on_activated
        self._list = ft.Column(spacing=0)

    def show(self):
        self._rebuild()
        view = ft.View(
            route=self._ROUTE,
            appbar=ft.AppBar(
                leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=self._go_back),
                title=ft.Text(I18n.t("profiles.title")),
                actions=[
                    ft.IconButton(ft.Icons.ADD, tooltip=I18n.t("profiles.new"), on_click=self._open_create_dialog),
                ],
            ),
            controls=[
                ft.Column(
                    expand=True,
                    scroll=ft.ScrollMode.AUTO,
                    spacing=0,
                    controls=[self._list],
                )
            ],
        )
        self._page.views.append(view)
        self._page.update()

    # ---------------------------------------------------------------- list

    def _rebuild(self):
        active_id = self._svc.get_active_id()
        profiles = self._svc.get_all()
        self._list.controls = [self._build_card(p, active_id) for p in profiles]

    def _build_card(self, profile: Profile, active_id: str) -> ft.Control:
        is_active = profile.id == active_id
        is_default = profile.id == "default"

        leading = ft.Container(
            width=40, height=40,
            border_radius=20,
            bgcolor=ft.Colors.INDIGO_600 if is_active else ft.Colors.GREY_500,
            content=ft.Icon(
                ft.Icons.PERSON,
                color=ft.Colors.WHITE,
                size=20,
            ),
            alignment=ft.Alignment(0, 0),
        )

        actions = ft.Row(
            controls=[
                ft.IconButton(
                    ft.Icons.DRIVE_FILE_RENAME_OUTLINE,
                    icon_color=ft.Colors.BLUE_400,
                    tooltip=I18n.t("profiles.rename"),
                    on_click=lambda _, p=profile: self._open_rename_dialog(p),
                ),
                ft.IconButton(
                    ft.Icons.DELETE_OUTLINE,
                    icon_color=ft.Colors.RED_400 if not is_default else ft.Colors.GREY_400,
                    tooltip=I18n.t("profiles.delete") if not is_default else I18n.t("profiles.delete_default"),
                    disabled=is_default,
                    on_click=lambda _, p=profile: self._confirm_delete(p),
                ),
            ],
            tight=True,
        )

        subtitle_text = I18n.t("profiles.active") if is_active else I18n.t("profiles.tap_to_activate")
        tile = ft.ListTile(
            leading=leading,
            title=ft.Text(
                profile.name,
                weight=ft.FontWeight.BOLD if is_active else ft.FontWeight.NORMAL,
            ),
            subtitle=ft.Text(subtitle_text, size=11,
                             color=ft.Colors.INDIGO_400 if is_active else ft.Colors.GREY_500),
            trailing=actions,
            on_click=(None if is_active else lambda _, p=profile: self._activate(p)),
        )
        return ft.Card(
            content=tile,
            elevation=3 if is_active else 1,
            margin=ft.Margin(left=8, right=8, top=2, bottom=2),
        )

    # ---------------------------------------------------------------- actions

    def _activate(self, profile: Profile):
        self._svc.activate(profile.id)
        self._on_activated(profile)
        self._rebuild()
        self._list.update()

    def _confirm_delete(self, profile: Profile):
        def do_delete(_):
            self._page.pop_dialog()
            self._svc.delete(profile.id)
            self._rebuild()
            self._list.update()

        self._page.show_dialog(ft.AlertDialog(
            title=ft.Text(I18n.t("profiles.confirm_delete_title")),
            content=ft.Text(I18n.t("profiles.confirm_delete_text", name=profile.name)),
            actions=[
                ft.TextButton(I18n.t("cancel"), on_click=lambda _: self._page.pop_dialog()),
                ft.TextButton(I18n.t("delete"), on_click=do_delete),
            ],
        ))

    # ---------------------------------------------------------------- dialogs

    def _open_create_dialog(self, _):
        name_field = ft.TextField(label=I18n.t("profiles.name_label"), autofocus=True)
        copy_check = ft.Checkbox(label=I18n.t("profiles.copy_active"), value=True)

        def on_create(_):
            name = name_field.value.strip()
            if not name:
                return
            self._page.pop_dialog()
            src = self._svc.get_active_id() if copy_check.value else None
            self._svc.create(name, copy_from=src)
            self._rebuild()
            self._list.update()

        self._page.show_dialog(ft.AlertDialog(
            title=ft.Text(I18n.t("profiles.new")),
            content=ft.Column(
                controls=[name_field, copy_check],
                tight=True,
                spacing=8,
            ),
            actions=[
                ft.TextButton(I18n.t("cancel"), on_click=lambda _: self._page.pop_dialog()),
                ft.TextButton(I18n.t("create"), on_click=on_create),
            ],
        ))

    def _open_rename_dialog(self, profile: Profile):
        name_field = ft.TextField(label=I18n.t("profiles.name"), value=profile.name, autofocus=True)

        def on_rename(_):
            name = name_field.value.strip()
            if not name:
                return
            self._page.pop_dialog()
            self._svc.rename(profile.id, name)
            self._rebuild()
            self._list.update()

        self._page.show_dialog(ft.AlertDialog(
            title=ft.Text(I18n.t("profiles.rename_title")),
            content=name_field,
            actions=[
                ft.TextButton(I18n.t("cancel"), on_click=lambda _: self._page.pop_dialog()),
                ft.TextButton(I18n.t("save"), on_click=on_rename),
            ],
        ))

    # ---------------------------------------------------------------- nav

    def _go_back(self, _):
        if len(self._page.views) > 1:
            self._page.views.pop()
        self._page.update()
