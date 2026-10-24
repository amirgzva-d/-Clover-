"""Add Persian to the ORIGINAL installed N.E.K.O. interface without altering layouts.

Only modifies resources/bin/static/i18n-i18next.js and adds locales/fa.json.
The existing executable, HTML, CSS, JavaScript chat bundle and assets remain intact.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
from datetime import datetime
from pathlib import Path


def flatten(data: object, prefix: str = "") -> dict[str, object]:
    if isinstance(data, dict):
        result: dict[str, object] = {}
        for key, value in data.items():
            result.update(flatten(value, f"{prefix}.{key}" if prefix else key))
        return result
    return {prefix: data}


def merge_old_keys(reference: object, translations: dict[str, object], prefix: str = "") -> object:
    if isinstance(reference, dict):
        return {
            k: merge_old_keys(v, translations, f"{prefix}.{k}" if prefix else k)
            for k, v in reference.items()
        }
    translated = translations.get(prefix, reference)
    if isinstance(reference, str) and isinstance(translated, str):
        placeholders = lambda s: set(re.findall(r"\{\{\s*([\w.]+)\s*\}\}", s))
        if placeholders(reference) != placeholders(translated):
            return reference
    return translated


def updated_menu_js(original: str) -> str:
    script = original

    def replace_one(before: str, after: str) -> None:
        nonlocal script
        if script.count(before) != 1:
            raise ValueError(f"Unsupported original N.E.K.O. version: {before[:65]!r}")
        script = script.replace(before, after, 1)

    replace_one(
        "const SUPPORTED_LANGUAGES = ['zh-CN', 'zh-TW', 'en', 'ja', 'ko', 'ru', 'es', 'pt'];",
        "const SUPPORTED_LANGUAGES = ['zh-CN', 'zh-TW', 'en', 'ja', 'ko', 'ru', 'es', 'pt', 'fa'];",
    )
    replace_one(
        "const LOCALE_VERSION = '2026-08-14-language-preference-freshness';",
        "const LOCALE_VERSION = '2026-10-24-persian-option-original-ui';",
    )
    replace_one(
        "        if (langCode === 'pt') return 'pt';",
        "        if (langCode === 'pt') return 'pt';\n"
        "        if (langCode === 'fa' || lower === 'farsi' || lower === 'persian') return 'fa';",
    )
    replace_one(
        "        Object.freeze({ code: 'pt', label: 'Português' })",
        "        Object.freeze({ code: 'pt', label: 'Português' }),\n"
        "        Object.freeze({ code: 'fa', label: 'فارسی' })",
    )
    replace_one(
        "        // 1. 尝试从 Steam API 获取语言",
        "        // Preserve the user's explicit Persian choice across Steam startup.\n"
        "        try {\n"
        "            if (localStorage.getItem('i18nextLng') === 'fa') return 'fa';\n"
        "        } catch (_) { /* keep original fallback behavior */ }\n\n"
        "        // 1. 尝试从 Steam API 获取语言",
    )
    assert "fa-direction.css" not in script
    assert "document.documentElement.dir" not in script
    return script


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--install-dir", type=Path, required=True,
                        help="N.E.K.O installed folder containing resources/bin/")
    parser.add_argument("--fa-source", type=Path, required=True,
                        help="Source static/locales/fa.json")
    parser.add_argument("--backup-dir", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    bin_root = args.install_dir / "resources" / "bin"
    js_path = bin_root / "static" / "i18n-i18next.js"
    en_path = bin_root / "static" / "locales" / "en.json"
    fa_path = bin_root / "static" / "locales" / "fa.json"
    if not (args.install_dir / "N.E.K.O.exe").is_file():
        raise SystemExit("Not the original installed desktop program.")
    if not js_path.is_file() or not en_path.is_file():
        raise SystemExit("Missing original UI language assets.")
    if fa_path.exists():
        script = js_path.read_text(encoding="utf8")
        if "code: 'fa', label: 'فارسی'" in script:
            print("Persian option is already installed. No changes made.")
            return
        raise SystemExit("Found an existing Persian locale without matching menu; review manually.")

    old_code = js_path.read_text(encoding="utf8")
    patched = updated_menu_js(old_code)
    old_en = json.loads(en_path.read_text(encoding="utf8"))
    new_fa = json.loads(args.fa_source.read_text(encoding="utf8"))
    translated = merge_old_keys(old_en, flatten(new_fa))
    if set(flatten(translated)) != set(flatten(old_en)):
        raise SystemExit("Translation keys do not match the original UI.")
    if args.dry_run:
        print("Dry run validated; original UI layout not modified.")
        return

    backup_root = args.backup_dir / ("before-fa-" + datetime.now().strftime("%Y%m%d-%H%M%S"))
    backup_root.mkdir(parents=True, exist_ok=False)
    shutil.copy2(js_path, backup_root / "i18n-i18next.js")
    shutil.copy2(en_path, backup_root / "en.json")
    js_path.write_text(patched, encoding="utf8")
    fa_path.write_text(json.dumps(translated, ensure_ascii=False, indent=2) + "\n",
                       encoding="utf8")
    print("Persian added to the existing installed menu. Original UI and executable unchanged.")
    print("Backup stored at:", backup_root)


if __name__ == "__main__":
    main()
