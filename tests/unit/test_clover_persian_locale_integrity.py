"""Persian language parity tests without external translation services."""
import ast
import collections
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
TOKEN = re.compile(
    r"(\{\{[^{}]+\}\}|\{[a-zA-Z_][a-zA-Z0-9_.-]*\}|"
    r"<[^>]*>|%(?:\d+\$)?[-+ #0]*(?:\d+|\*)?(?:\.\d+)?[sdif]|https?://[^\s<>]+)"
)


def _leaves(data):
    if isinstance(data, dict):
        for k, v in data.items():
            yield from ((k + "." + x, y) for x, y in _leaves(v))
    elif isinstance(data, list):
        for n, v in enumerate(data):
            yield from ((str(n) + "." + x, y) for x, y in _leaves(v))
    else:
        yield "", data


def test_persian_main_locale_has_identical_keys_and_safe_placeholders():
    en = json.loads((ROOT / "static/locales/en.json").read_text(encoding="utf-8"))
    fa = json.loads((ROOT / "static/locales/fa.json").read_text(encoding="utf-8"))
    en_values = dict(_leaves(en))
    fa_values = dict(_leaves(fa))
    assert en_values.keys() == fa_values.keys()
    assert len(fa_values) == 6125
    for key, original in en_values.items():
        assert isinstance(fa_values[key], str), key
        assert collections.Counter(TOKEN.findall(original)) == collections.Counter(TOKEN.findall(fa_values[key])), key


def test_backend_recognizes_all_nine_languages_and_farsi_aliases():
    from config.prompts._locale import NEKO_CORE_LOCALES, normalize_prompt_locale
    assert len(NEKO_CORE_LOCALES) == 9
    assert "fa" in NEKO_CORE_LOCALES
    for raw in ("fa", "fa-IR", "FA_ir", "farsi", "persian"):
        assert normalize_prompt_locale(raw) == "fa"


def test_persian_character_persona_preserves_all_required_prompts():
    source = ast.parse((ROOT / "config/prompts/prompts_chara.py").read_text(encoding="utf8"))
    data = next(ast.literal_eval(node.value) for node in source.body
                if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name)
                and t.id == "_L10N" for t in node.targets))
    assert data["fa"].keys() == data["en"].keys()
    for value in data["fa"].values():
        assert isinstance(value, str) and value
    assert "فارسی" in data["fa"]["language_style"]


def test_persian_main_frontend_uses_native_language_selector():
    js = (ROOT / "static/i18n-i18next.js").read_text(encoding="utf-8")
    assert "code: 'fa', label: 'فارسی'" in js
    assert "langCode === 'fa'" in js
    assert "document.documentElement.dir = lng === 'fa'" in js


def test_persian_plugin_manager_is_a_first_class_locale():
    root = ROOT / "frontend/plugin-manager/src"
    index = (root / "i18n/index.ts").read_text(encoding="utf-8")
    switcher = (root / "components/common/LanguageSwitcher.vue").read_text(encoding="utf-8")
    bundle = (root / "i18n/localeBundles.ts").read_text(encoding="utf-8")
    assert "'fa'] as const" in index
    assert 'command="fa"' in switcher
    assert "import('./locales/fa')" in bundle
