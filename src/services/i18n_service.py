import json
import locale
import os
from pathlib import Path


class I18n:
    _I18N_DIR = Path("assets/i18n")
    _supported = {"en", "es"}
    _lang_names = {"en": "English", "es": "Español"}
    _strings: dict[str, str] = {}
    _lang: str = "en"

    @classmethod
    def load(cls, lang: str | None = None):
        if not lang:
            system_lang = locale.getdefaultlocale()[0] or os.environ.get("LANG", "en")
            lang = system_lang[:2]
        if lang not in cls._supported:
            lang = "en"
        cls._lang = lang
        path = cls._I18N_DIR / f"{lang}.json"
        cls._strings = json.loads(path.read_text(encoding="utf-8"))

    @classmethod
    def current_lang(cls) -> str:
        return cls._lang

    @classmethod
    def available_langs(cls) -> dict[str, str]:
        return {code: cls._lang_names.get(code, code) for code in sorted(cls._supported)}

    @classmethod
    def t(cls, key: str, fallback: str = "", **kwargs) -> str:
        text = cls._strings.get(key, fallback or key)
        if kwargs:
            text = text.format(**kwargs)
        return text
