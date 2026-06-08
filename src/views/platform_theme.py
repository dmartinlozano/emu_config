import flet as ft

from src.models.emu import Emu

PLATFORM_COLORS: dict[str, str] = {
    "Atari 2600":        ft.Colors.BROWN_600,
    "Aventuras gráficas": ft.Colors.TEAL_700,
    "Commodore 64":      ft.Colors.BROWN_400,
    "Dreamcast":         ft.Colors.ORANGE_700,
    "GameCube":          ft.Colors.PURPLE_600,
    "GB / GBC":          ft.Colors.GREEN_600,
    "GBA / GB / GBC":    ft.Colors.GREEN_700,
    "GBA":               ft.Colors.GREEN_700,
    "Mame":              ft.Colors.DEEP_ORANGE_700,
    "Mega Drive":        ft.Colors.BLUE_GREY_700,
    "Neo Geo":           ft.Colors.RED_700,
    "NES":               ft.Colors.RED_900,
    "Nintendo 3DS":      ft.Colors.RED_500,
    "Nintendo 64":       ft.Colors.GREEN_800,
    "Nintendo DS":       ft.Colors.RED_700,
    "PC Engine":         ft.Colors.AMBER_700,
    "PlayStation":       ft.Colors.BLUE_900,
    "PlayStation 2":     ft.Colors.BLUE_700,
    "PlayStation 3":     ft.Colors.BLUE_500,
    "PS Vita":           ft.Colors.INDIGO_400,
    "PSP":               ft.Colors.BLUE_400,
    "Saturn":            ft.Colors.ORANGE_400,
    "SNES":              ft.Colors.PURPLE_700,
    "Wii":               ft.Colors.GREY_600,
    "Wii U":             ft.Colors.BLUE_800,
}

PLATFORM_SHORT: dict[str, str] = {
    "Atari 2600":        "ATA",
    "Aventuras gráficas": "ADV",
    "Commodore 64":      "C64",
    "Dreamcast":         "DC",
    "GameCube":          "GC",
    "GB / GBC":          "GB",
    "GBA / GB / GBC":    "GBA",
    "GBA":               "GBA",
    "Mame":              "ARC",
    "Mega Drive":        "MD",
    "Neo Geo":           "NEO",
    "NES":               "NES",
    "Nintendo 3DS":      "3DS",
    "Nintendo 64":       "N64",
    "Nintendo DS":       "NDS",
    "PC Engine":         "PCE",
    "PlayStation":       "PS1",
    "PlayStation 2":     "PS2",
    "PlayStation 3":     "PS3",
    "PS Vita":           "PSV",
    "PSP":               "PSP",
    "Saturn":            "SAT",
    "SNES":              "SFC",
    "Wii":               "WII",
    "Wii U":             "WiiU",
}


def build_platform_avatar(emu: Emu) -> ft.Control:
    if emu.image:
        return ft.Container(
            width=40,
            height=40,
            border_radius=8,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            content=ft.Image(
                src=f"/images/{emu.image}",
                width=40,
                height=40,
            ),
        )
    color = PLATFORM_COLORS.get(emu.platform, ft.Colors.GREY_600)
    short = PLATFORM_SHORT.get(emu.platform, emu.platform[:3].upper() if emu.platform else "?")
    return ft.Container(
        width=40,
        height=40,
        border_radius=20,
        bgcolor=color,
        content=ft.Text(short, size=10, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
        alignment=ft.Alignment(0, 0),
    )


def build_platform_badge(platform: str | None) -> ft.Control | None:
    if not platform:
        return None
    color = PLATFORM_COLORS.get(platform, ft.Colors.GREY_600)
    return ft.Row(
        controls=[
            ft.Container(
                content=ft.Text(platform, size=10, color=ft.Colors.WHITE),
                bgcolor=color,
                border_radius=4,
                padding=ft.Padding(left=6, right=6, top=2, bottom=2),
            )
        ],
        tight=True,
    )
