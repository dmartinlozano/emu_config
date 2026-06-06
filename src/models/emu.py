from dataclasses import dataclass
from typing import Optional


@dataclass
class Input:
    file: str
    mapper: dict[str, str]
    controller_style_xbox: Optional[dict[str, str]] = None


@dataclass
class VideoDriver:
    file: str
    key: str
    options: dict[str, str]


@dataclass
class VideoScale:
    file: str
    key: str
    options: dict[str, str]


@dataclass
class RomsPath:
    file: str
    key: str


@dataclass
class Region:
    file: str
    key: str
    options: dict[str, str]


@dataclass
class EnableSaveStates:
    file: str
    key: str
    options: dict[str, str]


@dataclass
class HideOverlay:
    file: str
    key: str
    options: dict[str, str]


@dataclass
class ImportProfile:
    filename: str
    content: str
    description: str
    adb_path: Optional[str] = None


@dataclass
class Successor:
    name: str
    play_store: Optional[str] = None
    github: Optional[str] = None


@dataclass
class Emu:
    id: int
    name: str
    package: str
    num_max_players: int
    platform: Optional[str] = None
    play_store: Optional[str] = None
    github: Optional[str] = None
    deprecated: bool = False
    successor: Optional[Successor] = None
    input: Optional[Input] = None
    video_driver: Optional[VideoDriver] = None
    video_scale: Optional[VideoScale] = None
    roms_path: Optional[RomsPath] = None
    region: Optional[Region] = None
    enable_save_states: Optional[EnableSaveStates] = None
    hide_overlay: Optional[HideOverlay] = None
    import_profile: Optional[ImportProfile] = None

    @staticmethod
    def from_dict(data: dict) -> "Emu":
        def _optional(cls, key):
            return cls(**data[key]) if data.get(key) else None

        succ_data = data.get("successor")
        successor = Successor(
            name=succ_data["name"],
            play_store=succ_data.get("playStore"),
            github=succ_data.get("github"),
        ) if succ_data else None

        return Emu(
            id=data["id"],
            name=data["name"],
            package=data["package"],
            num_max_players=data["numMaxPlayers"],
            platform=data.get("platform"),
            play_store=data.get("playStore"),
            github=data.get("github"),
            deprecated=data.get("deprecated", False),
            successor=successor,
            input=Input(
                file=data["input"]["file"],
                mapper=data["input"]["mapper"],
                controller_style_xbox=data["input"].get("controllerStyleXbox"),
            ) if data.get("input") else None,
            video_driver=_optional(VideoDriver, "videoDriver"),
            video_scale=_optional(VideoScale, "videoScale"),
            roms_path=_optional(RomsPath, "romsPath"),
            region=_optional(Region, "region"),
            enable_save_states=_optional(EnableSaveStates, "enableSaveStates"),
            hide_overlay=_optional(HideOverlay, "hideOverlay"),
            import_profile=ImportProfile(
                filename=data["importProfile"]["filename"],
                content=data["importProfile"]["content"],
                description=data["importProfile"]["description"],
                adb_path=data["importProfile"].get("adbPath"),
            ) if data.get("importProfile") else None,
        )
