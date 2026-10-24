"""Regression: Persian text must not be treated as unknown or English in translation."""
from pathlib import Path
from utils.language_utils import detect_language, normalize_language_code

def test_persian_orthography_detected():
    cases=[
        "سلام دوست من",
        "سلام، حالت چطوره؟",
        "لطفاً این متن را ترجمه کن.",
        "پایتخت ایران کجاست؟",
        "می‌توانم به زبان فارسی صحبت کنم.",
        "جواب را به فارسی بگو",
    ]
    for text in cases:
        assert detect_language(text)=="fa",text

def test_unchanged_other_language_family():
    assert detect_language("Hello good morning")=="en"
    assert detect_language("你好，世界")=="zh"
    assert detect_language("こんにちは")=="ja"
    assert detect_language("Привет")=="ru"
    assert detect_language("안녕하세요")=="ko"
    assert detect_language("12345 😀")=="unknown"

def test_unmarked_arabic_not_force_labeled_farsi():
    assert detect_language("مرحبا بك في هذا اليوم")=="unknown"

def test_persian_input_codes_are_supported():
    for code in ["fa","fa-IR","farsi","persian","FA_ir"]:
        assert normalize_language_code(code,format="short")=="fa"


def test_subtitle_ui_and_translation_normalizers_include_farsi():
    root = Path(__file__).resolve().parents[2]
    shared = (root / "static/subtitle/subtitle-shared.js").read_text(encoding="utf8")
    fallback = (root / "static/subtitle/subtitle.js").read_text(encoding="utf8")
    menu = (root / "static/i18n-i18next.js").read_text(encoding="utf8")
    assert "value.indexOf('fa') === 0" in shared
    assert "lower.indexOf('fa') === 0" in shared
    assert "value.indexOf('fa') === 0" in fallback
    assert "window.subtitleBridge.setUserLanguage(normalized)" in menu


def test_llm_fallback_names_persian_in_each_language():
    from config.prompts.prompts_sys import TRANSLATION_LANG_NAMES
    assert len(TRANSLATION_LANG_NAMES) == 9
    assert all('fa' in names for names in TRANSLATION_LANG_NAMES.values())
    assert TRANSLATION_LANG_NAMES['en']['fa'] == 'Persian'
    assert TRANSLATION_LANG_NAMES['fa']['en'] == '\u0627\u0646\u06af\u0644\u06cc\u0633\u06cc'
