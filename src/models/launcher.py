from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Launcher:
    id: str
    name: str
    package: str
    image: Optional[str] = None
    play_store: Optional[str] = None
    github: Optional[str] = None

    @staticmethod
    def from_dict(data: dict) -> "Launcher":
        return Launcher(
            id=data["id"],
            name=data["name"],
            package=data["package"],
            image=data.get("image"),
            play_store=data.get("playStore"),
            github=data.get("github"),
        )


@dataclass
class LauncherPlayer:
    name: str
    package: str
    am_start_arguments: str
    kill_package_processes: bool = False


@dataclass
class LauncherPlatform:
    platform_name: str
    unique_id: str
    accepted_filename_regex: str
    extensions: str
    players: list[LauncherPlayer] = field(default_factory=list)

    @staticmethod
    def from_dict(data: dict) -> "LauncherPlatform":
        players = [
            LauncherPlayer(
                name=p["name"],
                package=p["package"],
                am_start_arguments=p["amStartArguments"],
                kill_package_processes=p.get("killPackageProcesses", False),
            )
            for p in data.get("players", [])
        ]
        return LauncherPlatform(
            platform_name=data["platformName"],
            unique_id=data["uniqueId"],
            accepted_filename_regex=data["acceptedFilenameRegex"],
            extensions=data["extensions"],
            players=players,
        )
