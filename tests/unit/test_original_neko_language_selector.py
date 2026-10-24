"""Static regression tests for the original N.E.K.O. UI-only language selector."""
from importlib import util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PATCH = ROOT / "scripts" / "add-original-neko-language-menu.py"


@pytest.fixture(scope="module")
def module():
    spec = util.spec_from_file_location("original_neko_lang_menu", PATCH)
    obj = util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def test_settings_menu_uses_original_native_components(module):
    popup = (
        "function createSettingsPopupContent(manager, prefix, popup) {\n"
        + module.BUTTON_ANCHOR
        + "\n}\n"
    )
    new = module.patch_settings(popup)
    assert new.count("function createSettingsPopupContent(") == 1
    assert "_createSettingsMenuButton" in new
    assert "_createSidePanelContainer" in new
    assert "_attachSidePanelHover" in new
    assert "settings.menu.language" in new
    assert "window.NEKO_NATIVE_LANGUAGE_OPTIONS" in new
    assert "window.changeLanguage(code)" in new
    assert "localStorage.setItem('nekoManualUiLanguage', code)" in new
    assert "panel.style.maxHeight" in new
    assert "<style" not in new
    assert "document.documentElement.dir" not in new


def test_manual_preference_overrides_steam_without_changing_default(module):
    old = (
        "async function getInitialLanguage() {\n"
        "        // Honor a manually selected Persian UI over automatic Steam language.\n"
        "        // 1. Steam\n"
        "        return getBrowserLanguage();\n"
        "}\n"
    )
    new = module.patch_i18n(old)
    assert new.index("getItem('nekoManualUiLanguage')") < new.index("// 1. Steam")
    assert "SUPPORTED_LANGUAGES.includes(manual)" in new
    assert "return getBrowserLanguage();" in new


def test_unexpected_original_versions_fail_closed(module):
    with pytest.raises(ValueError):
        module.patch_settings("function createSettingsPopupContent() {}")
    with pytest.raises(ValueError):
        module.patch_i18n("function getInitialLanguage() {}")


def test_selector_does_not_change_existing_styles_and_windows(module):
    raw = PATCH.read_text(encoding="utf8")
    assert "N.E.K.O.exe" in raw
    assert "Start-Process" not in raw
    assert "chrome.exe" not in raw
    assert "templates/index.html" not in raw
    assert "templates/chat.html" not in raw
    assert "style.css" not in raw
