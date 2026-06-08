import io
import subprocess
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path

from src.models.emu import Emu
from src.services.adb_service import AdbService

_BACKUP_DIR = "/storage/emulated/0/Download"


class BackupService:
    def __init__(self):
        self._adb = AdbService()

    def _config_files(self, emus: list[Emu], installed: set[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for emu in emus:
            if emu.package not in installed or emu.deprecated:
                continue
            candidates: list[str] = []
            if emu.input:
                candidates.append(emu.input.file)
            for attr in ("video_driver", "video_scale", "roms_path", "region", "enable_save_states", "hide_overlay"):
                obj = getattr(emu, attr)
                if obj and hasattr(obj, "file"):
                    candidates.append(obj.file)
            for f in candidates:
                if f and f not in seen:
                    seen.add(f)
                    result.append(f)
        return result

    def create_backup(self, emus: list[Emu], installed: set[str]) -> str:
        files = self._config_files(emus, installed)
        if not files:
            raise RuntimeError("No hay ficheros de configuración en emuladores instalados")

        buf = io.BytesIO()
        written = 0
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for remote_path in files:
                lines = self._adb.read_lines(remote_path)
                if lines:
                    zf.writestr(remote_path.lstrip("/"), "\n".join(lines))
                    written += 1

        if not written:
            raise RuntimeError("No se pudo leer ningún fichero de configuración")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = f"{_BACKUP_DIR}/emu_config_{timestamp}.zip"
        zip_bytes = buf.getvalue()

        if self._adb._local:
            Path(dest).parent.mkdir(parents=True, exist_ok=True)
            Path(dest).write_bytes(zip_bytes)
        else:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as f:
                f.write(zip_bytes)
                tmp = f.name
            subprocess.run(["adb", "push", tmp, dest], capture_output=True, check=True)

        return dest

    def restore_backup(self, zip_path: str) -> int:
        if self._adb._local:
            data = Path(zip_path).read_bytes()
        else:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as f:
                tmp = f.name
            subprocess.run(["adb", "pull", zip_path, tmp], capture_output=True, check=True)
            data = Path(tmp).read_bytes()

        restored = 0
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            for name in zf.namelist():
                remote_path = "/" + name
                content = zf.read(name).decode("utf-8", errors="replace")
                self._adb.write_lines(content.splitlines(), remote_path)
                restored += 1

        return restored
