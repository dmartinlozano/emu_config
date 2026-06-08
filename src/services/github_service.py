import json
import urllib.request


def _get(url: str) -> dict | list | None:
    req = urllib.request.Request(
        url,
        headers={"Accept": "application/vnd.github+json", "User-Agent": "emu-config"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except Exception:
        return None


def _apk_from_release(data: dict) -> str | None:
    for asset in data.get("assets", []):
        if asset["name"].lower().endswith(".apk"):
            return asset["browser_download_url"]
    return None


def _fetch_release_with_apk(repo: str) -> dict | None:
    """Returns the most recent release (stable or pre-release) that has an APK asset."""
    data = _get(f"https://api.github.com/repos/{repo}/releases/latest")
    if data and _apk_from_release(data):
        return data

    releases = _get(f"https://api.github.com/repos/{repo}/releases?per_page=10")
    if isinstance(releases, list):
        for release in releases:
            if _apk_from_release(release):
                return release
    return data


def get_latest_apk_url(repo: str) -> str | None:
    data = _fetch_release_with_apk(repo)
    if not data:
        return None
    return _apk_from_release(data)


def get_latest_release_info(repo: str) -> tuple[str, str] | None:
    """Returns (version_tag, apk_url) for the latest release, or None on failure."""
    data = _fetch_release_with_apk(repo)
    if not data:
        return None
    tag = data.get("tag_name", "").lstrip("vV").strip()
    apk_url = _apk_from_release(data) or f"https://github.com/{repo}/releases"
    return (tag, apk_url) if tag else None
