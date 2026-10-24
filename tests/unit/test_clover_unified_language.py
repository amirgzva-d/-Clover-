"""Regression tests for original-style unified language switching."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
def source(path): return (ROOT / path).read_text(encoding="utf8")

def test_unified_selector_updates_character_before_ui():
    js=source("static/i18n-i18next.js")
    assert "window.changeCloverLanguageEverywhere = async function" in js
    assert "await persistUnifiedConversationLanguage(name, normalized)" in js
    assert "await i18next.changeLanguage(normalized)" in js
    assert js.index("await persistUnifiedConversationLanguage(name, normalized)") < js.index("await i18next.changeLanguage(normalized)")
    assert "payload.success !== true" in js
    assert "csrf_validation_failed" in js
    assert "unifiedLanguageBusy" in js

def test_original_menu_components_not_replaced():
    js=source("static/avatar/avatar-ui-popup.js")
    assert "_createSettingsMenuButton({" in js
    assert "_attachSidePanelHover(languageSettingsBtn, languageSidePanel)" in js
    assert "window.NEKO_NATIVE_LANGUAGE_OPTIONS || []" in js
    assert "createUnifiedLanguageSidePanel(manager, prefix)" in js
    assert "window.changeCloverLanguageEverywhere(code)" in js
    assert "document.body.appendChild(panel)" in js
    assert "window.location =" not in js.split("// Language selector uses the original settings-menu button")[1].split("// 2.5",1)[0]

def test_all_nine_languages_represented_and_plugin_manager_follows():
    js=source("static/i18n-i18next.js")
    vue=source("frontend/plugin-manager/src/i18n/index.ts")
    assert "['zh-CN', 'zh-TW', 'en', 'ja', 'ko', 'ru', 'es', 'pt', 'fa']" in js
    assert "'nekoManualUiLanguage'" in js
    assert "localStorage.setItem('locale', normalized === 'en' ? 'en-US' : normalized)" in js
    assert "event.key !== 'locale'" in vue
    assert "void applySetting(setting as LocaleSetting, false)" in vue

def test_realtime_tts_uses_session_preference_not_global_mutation():
    lang=source("utils/language_utils.py")
    client=source("main_logic/omni_realtime_client/_client.py")
    transport=source("main_logic/omni_realtime_client/_transport.py")
    lifecycle=source("main_logic/core/lifecycle.py")
    assert "def get_tts_language_code(language: Optional[str] = None)" in lang
    assert "'fa':    'fa-IR'" in lang
    assert "self.conversation_language = conversation_language" in client
    assert 'getattr(self, "conversation_language", None)' in transport
    assert lifecycle.count("conversation_language=self.user_language") == 2
    assert "set_global_language(" not in transport
