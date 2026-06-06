import traceback

import flet as ft
from src.views.dashboard_view import DashboardView


def main(page: ft.Page):
    try:
        DashboardView(page).build()
    except Exception as e:
        page.add(
            ft.Text(
                f"ERROR:\n{e}\n\n{traceback.format_exc()}",
                size=11,
                selectable=True,
                font_family="monospace",
            )
        )
        page.update()


ft.run(main)
