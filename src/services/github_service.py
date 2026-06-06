import json
import urllib.request


def _fetch_latest_release(repo: str) -> dict | None:
    api_url = f"https://api.github.com/repos/{repo}/releases/latest"
    req = urllib.request.Request(
        api_url,
        headers={"Accept": "application/vnd.github+json", "User-Agent": "emu-config"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except Exception:
        return None


def get_latest_apk_url(repo: str) -> str | None:
    data = _fetch_latest_release(repo)
    if not data:
        return None
    for asset in data.get("assets", []):
        if asset["name"].lower().endswith(".apk"):
            return asset["browser_download_url"]
    return None


def get_latest_release_info(repo: str) -> tuple[str, str] | None:
    """Returns (version_tag, apk_url) for the latest release, or None on failure."""
    data = _fetch_latest_release(repo)
    if not data:
        return None
    tag = data.get("tag_name", "").lstrip("vV").strip()
    apk_url = next(
        (a["browser_download_url"] for a in data.get("assets", []) if a["name"].lower().endswith(".apk")),
        f"https://github.com/{repo}/releases",
    )
    return (tag, apk_url) if tag else None
