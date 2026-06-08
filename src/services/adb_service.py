import asyncio
import os
import subprocess
import tempfile
from pathlib import Path

from src.config.button_profile import LINUX_TO_ANDROID


def _is_android() -> bool:
    return os.path.exists("/system/build.prop")


class AdbService:
    def __init__(self):
        self._local = _is_android()

    # ------------------------------------------------------------------ shell

    def shell(self, cmd: str) -> str:
        if self._local:
            r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        else:
            r = subprocess.run(["adb", "shell", cmd], capture_output=True, text=True)
        return r.stdout.strip()

    # ------------------------------------------------------------ packages

    def get_installed_packages(self) -> set[str]:
        if not self._local:
            r = subprocess.run(["adb", "shell", "pm", "list", "packages"], capture_output=True, text=True)
        else:
            r = subprocess.run(["/system/bin/pm", "list", "packages"], capture_output=True, text=True, timeout=15)
        return {
            line.replace("package:", "").strip()
            for line in r.stdout.splitlines()
            if line.startswith("package:")
        }

    def is_package_installed(self, package: str) -> bool:
        """Check a single package via pm path — works even without QUERY_ALL_PACKAGES."""
        if not self._local:
            r = subprocess.run(["adb", "shell", "pm", "path", package], capture_output=True, text=True, timeout=5)
        else:
            r = subprocess.run(["/system/bin/pm", "path", package], capture_output=True, text=True, timeout=5)
        return "package:" in r.stdout

    # ------------------------------------------------------------ gamepads

    def get_gamepads(self) -> list[dict]:
        if self._local:
            return self._get_gamepads_from_proc()
        return self._get_gamepads_via_adb()

    def _get_gamepads_from_proc(self) -> list[dict]:
        """Parse /proc/bus/input/devices — readable without root on Android."""
        try:
            content = Path("/proc/bus/input/devices").read_text(encoding="utf-8", errors="replace")
        except OSError:
            return []

        # Names that indicate non-gamepad devices with EV_KEY+EV_ABS
        _non_gamepad = ("touch", "ts", "fts", "pen", "stylus", "digitizer", "key_input", "qbt")

        gamepads: list[dict] = []
        current: dict = {}
        has_js = False   # joystick handler — most reliable indicator
        ev_flags = 0     # EV bitmask: bit1=EV_KEY, bit3=EV_ABS

        def _finalize():
            nonlocal has_js, ev_flags
            name = current.get("name", "")
            name_ok = not any(kw in name.lower() for kw in _non_gamepad)
            has_ev = (ev_flags & 0b1010) == 0b1010  # EV_KEY + EV_ABS
            if name and (has_js or (has_ev and name_ok)):
                gamepads.append(dict(current))
            has_js = False
            ev_flags = 0

        for line in content.splitlines():
            line = line.strip()
            if not line:
                _finalize()
                current = {}
                continue

            if line.startswith("N: Name="):
                current["name"] = line.split("=", 1)[1].strip().strip('"')
            elif line.startswith("U: Uniq="):
                val = line.split("=", 1)[1].strip()
                if val:
                    current["descriptor"] = val
            elif line.startswith("I:"):
                parts = dict(p.split("=") for p in line[3:].split() if "=" in p)
                try:
                    current["vendor_id"] = int(parts.get("Vendor", "0"), 16)
                    current["product_id"] = int(parts.get("Product", "0"), 16)
                except ValueError:
                    pass
            elif line.startswith("H: Handlers="):
                for h in line.split("=", 1)[1].split():
                    if h.startswith("event"):
                        current["device_path"] = f"/dev/input/{h}"
                    elif h.startswith("js"):
                        has_js = True
            elif line.startswith("B: EV="):
                try:
                    ev_flags = int(line.split("=")[1].strip(), 16)
                except ValueError:
                    pass

        _finalize()
        return gamepads

    def _get_gamepads_via_adb(self) -> list[dict]:
        """Desktop dev: use ADB + getevent to list gamepads."""
        gamepad_btn_codes = {f"{c:04x}" for c in range(0x130, 0x13f)}
        output = self.shell("getevent -i 2>/dev/null")
        gamepads: list[dict] = []
        current: dict = {}
        events_lines: list[str] = []
        in_events = False

        def _is_gamepad(events_text: str) -> bool:
            lower = events_text.lower()
            return "abs" in lower and any(btn in lower for btn in gamepad_btn_codes)

        def _finalize():
            if current.get("name") and _is_gamepad(" ".join(events_lines)):
                gamepads.append(dict(current))

        for line in output.splitlines():
            if line.startswith("add device"):
                _finalize()
                current = {}
                events_lines = []
                in_events = False
                parts = line.split(":", 1)
                if len(parts) == 2:
                    current["device_path"] = parts[1].strip()
                continue

            s = line.strip()
            if s.startswith("name:"):
                current["name"] = s.split('"')[1] if '"' in s else s[5:].strip()
            elif s.startswith("id:"):
                val = s.split('"')[1] if '"' in s else s[3:].strip()
                if val:
                    current["descriptor"] = val
            elif s.startswith("vendor"):
                try:
                    current["vendor_id"] = int(s.split()[-1], 16)
                except (ValueError, IndexError):
                    pass
            elif s.startswith("product"):
                try:
                    current["product_id"] = int(s.split()[-1], 16)
                except (ValueError, IndexError):
                    pass
            elif s.startswith("events:"):
                in_events = True
            elif s.startswith("input props:"):
                in_events = False
            elif in_events:
                events_lines.append(s)

        _finalize()
        return gamepads

    async def detect_button_press(self, device_path: str, timeout: float = 10.0) -> int | None:
        if self._local:
            cmd = f"su -c 'getevent {device_path}'"
        else:
            cmd = f"getevent {device_path}"

        if self._local:
            proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.DEVNULL,
            )
        else:
            proc = await asyncio.create_subprocess_exec(
                "adb", "shell", cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.DEVNULL,
            )

        android_code: int | None = None

        async def _read():
            nonlocal android_code
            async for raw in proc.stdout:
                parts = raw.decode(errors="replace").strip().split()
                if len(parts) < 3:
                    continue
                try:
                    ev_type = int(parts[-3], 16)
                    ev_code = int(parts[-2], 16)
                    ev_value = int(parts[-1], 16)
                except ValueError:
                    continue
                if ev_type == 0x01 and ev_value == 1:  # EV_KEY DOWN
                    android_code = LINUX_TO_ANDROID.get(ev_code, ev_code)
                    return

        try:
            await asyncio.wait_for(_read(), timeout=timeout)
        except asyncio.TimeoutError:
            pass
        finally:
            try:
                proc.kill()
                await proc.wait()
            except Exception:
                pass

        return android_code

    # ---------------------------------------------------------- packages

    def get_package_version(self, package: str) -> str | None:
        if self._local:
            r = subprocess.run(
                ["/system/bin/dumpsys", "package", package],
                capture_output=True, text=True, timeout=10
            )
            output = r.stdout
        else:
            output = self.shell(f"dumpsys package {package}")

        for line in output.splitlines():
            if "versionName" in line:
                try:
                    return line.strip().split("=", 1)[1].strip()
                except IndexError:
                    pass
        return None

    # ---------------------------------------------------------- file I/O

    def read_lines(self, remote_path: str) -> list[str]:
        if self._local:
            try:
                return Path(remote_path).read_text(encoding="utf-8", errors="replace").splitlines()
            except OSError:
                return []
        with tempfile.NamedTemporaryFile(delete=False, suffix=".cfg") as f:
            tmp = f.name
        subprocess.run(["adb", "pull", remote_path, tmp], capture_output=True)
        return Path(tmp).read_text(encoding="utf-8", errors="replace").splitlines()

    def write_lines(self, lines: list[str], remote_path: str):
        if self._local:
            Path(remote_path).write_text("\n".join(lines), encoding="utf-8")
            return
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".cfg", encoding="utf-8") as f:
            f.write("\n".join(lines))
            tmp = f.name
        subprocess.run(["adb", "push", tmp, remote_path], capture_output=True)

    def push_content(self, content: str, remote_path: str):
        if self._local:
            Path(remote_path).parent.mkdir(parents=True, exist_ok=True)
            Path(remote_path).write_text(content, encoding="utf-8")
            return
        remote_dir = "/".join(remote_path.split("/")[:-1])
        self.shell(f"mkdir -p '{remote_dir}'")
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".cfg", encoding="utf-8") as f:
            f.write(content)
            tmp = f.name
        subprocess.run(["adb", "push", tmp, remote_path], capture_output=True)
