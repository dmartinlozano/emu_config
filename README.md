# Emu Config

**Emu Config** es una aplicación Android que configura automáticamente tus emuladores: mapea los mandos, ajusta opciones de vídeo y configura las rutas de ROMs escribiendo directamente en los ficheros de configuración de cada emulador.

---

## Características

### Mandos / Gamepads
- Detecta automáticamente los mandos conectados.
- Mapea botones por emulador en un solo tap o mediante detección automática secuencial.
- Guarda perfiles por mando y los aplica a todos los emuladores instalados a la vez.
- Intercambia la posición de los botones A/B (estilo Xbox ↔ Nintendo).

### Emuladores soportados
La app detecta cuáles tienes instalados y muestra solo esos:

| Plataforma | Emuladores |
|---|---|
| Multi-sistema | RetroArch |
| PlayStation | DuckStation |
| PlayStation 2 | AetherSX2 / NetherSX2, PCSX2 |
| PlayStation 3 | RPCS3 |
| PS Vita | Vita3K |
| PSP | PPSSPP, PPSSPP Gold |
| GameCube / Wii | Dolphin |
| Wii U | Cemu |
| Nintendo 64 | M64Plus FZ, M64Plus FZ Pro |
| Nintendo DS | melonDS |
| Nintendo 3DS | Azahar |
| GBA | GBA.emu, mGBA |
| GB / GBC | GBC.emu, mGBA |
| NES / Famicom | NES.emu |
| SNES | Snes9x EX+ |
| Mega Drive | MD.emu |
| Sega Saturn | Yaba Sanshiro 2 |
| Dreamcast | Flycast, Redream |
| Neo Geo | NEO.emu |
| PC Engine | PCE.emu |
| Arcade | MAME4droid |
| Atari 2600 | 2600.emu |
| Commodore 64 | C64.emu |
| Aventura | ScummVM |

### Launchers
Exporta la configuración de plataformas (con sus players y extensiones) a los launchers instalados:
- **Daijisho** — importa vía Ajustes → Biblioteca → Importar plataforma.
- **ES-DE** — escribe directamente en la carpeta de ES-DE.
- **Pegasus Frontend** — escribe en `/sdcard/pegasus-frontend/`.

### Perfiles
- Crea múltiples perfiles de configuración (p. ej. uno por cada dispositivo o set de mandos).
- Activa el perfil deseado con un tap; todos los ajustes de emuladores se aplican al perfil activo.
- Copia, renombra o elimina perfiles.

### Backup & Restore
- Exporta todos los ficheros de configuración de los emuladores instalados a un ZIP en la carpeta de Descargas.
- Restaura desde cualquier ZIP generado por la app.

### Idioma
- Interfaz en **español** e **inglés**.
- Selección automática según el idioma del sistema; cambio manual desde el botón de idioma en la barra superior.

### Otros
- Modo oscuro / claro con persistencia.
- Búsqueda de emuladores por nombre o plataforma con filtros por chip.
- Aviso de actualizaciones disponibles en GitHub para los emuladores que lo soporten.

---

## Instalación del APK

El APK se genera automáticamente en GitHub Actions con cada tag `v*`. Descárgalo desde la sección [Releases](../../releases) o desde la pestaña **Actions → Build Android APK → Artifacts**.

Para lanzar el build manualmente desde GitHub: **Actions → Build Android APK → Run workflow**.

### Compilar en local

Requisitos: Python 3.12+, Java JDK 17, Android SDK con NDK 27.

```bash
# Instala dependencias
pip install "flet>=0.85.2"

# Compila el APK (descarga Flutter automáticamente la primera vez)
flet build android

# El APK queda en:
# build/android/outputs/apk/release/app-release.apk

# Instala en el dispositivo conectado por ADB
adb install build/android/outputs/apk/release/app-release.apk
```

---

## Ejecutar en Android (modo debug)

```bash
adb devices
uv run flet debug android --yes --device-id <device-id>
```
