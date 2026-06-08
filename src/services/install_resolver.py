import asyncio
import re
import urllib.request
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from src.services.github_service import get_latest_apk_url


class ResolveStatus(Enum):
    PLAY_STORE = "play_store"
    GITHUB_APK = "github_apk"
    UNAVAILABLE = "unavailable"


@dataclass
class ResolvedInstall:
    status: ResolveStatus
    url: Optional[str] = None


def _check_url(url: str) -> bool:
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status < 400
    except Exception:
        return False


def _parse_version(v: str) -> tuple[int, ...]:
    parts = re.split(r"[.\-_]", v.strip().lstrip("vV"))
    result = []
    for p in parts:
        try:
            result.append(int(p))
        except ValueError:
            break
    return tuple(result)


def is_newer_version(latest: str, installed: str) -> bool:
    return _parse_version(latest) > _parse_version(installed)


async def resolve_install(play_store: Optional[str], github: Optional[str]) -> ResolvedInstall:
    loop = asyncio.get_running_loop()

    if play_store:
        ok = await loop.run_in_executor(None, _check_url, play_store)
        if ok:
            return ResolvedInstall(status=ResolveStatus.PLAY_STORE, url=play_store)

    if github:
        apk_url = await loop.run_in_executor(None, get_latest_apk_url, github)
        if apk_url:
            return ResolvedInstall(status=ResolveStatus.GITHUB_APK, url=apk_url)
        return ResolvedInstall(
            status=ResolveStatus.GITHUB_APK,
            url=f"https://github.com/{github}/releases",
        )

    return ResolvedInstall(status=ResolveStatus.UNAVAILABLE)
