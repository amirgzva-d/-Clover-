"""Add a language row to the ORIGINAL N.E.K.O. settings popup, without redesign."""
from __future__ import annotations
import argparse
from datetime import datetime
from pathlib import Path
import shutil

POPUP_FUNCTION = "function createSettingsPopupContent(manager, prefix, popup) {"
BUTTON_ANCHOR = """    manager._attachSidePanelHover(animSettingsBtn, animSidePanel);

    // 3."""
BUTTON_REPLACEMENT = """    manager._attachSidePanelHover(animSettingsBtn, animSidePanel);

    // UI language: reuse the native settings row and native floating side panel.
    const uiLanguageBtn = manager._createSettingsMenuButton({
        id: 'ui-language',
        label: window.t ? window.t('settings.menu.language') : 'Language',
        labelKey: 'settings.menu.language'
    });
    popup.appendChild(uiLanguageBtn);
    const uiLanguagePanel = createUiLanguageSettingsPanel(manager, prefix);
    uiLanguagePanel._anchorElement = uiLanguageBtn;
    uiLanguagePanel._popupElement = popup;
    manager._attachSidePanelHover(uiLanguageBtn, uiLanguagePanel);

    // 3."""
NEW_FUNCTION = r"""// A local addition to the original settings popup. No global styles/layout changed.
function createUiLanguageSettingsPanel(manager, prefix) {
    const panel = manager._createSidePanelContainer({
        alignItems: 'stretch', flexDirection: 'column', width: '190px'
    });
    panel.setAttribute('data-neko-sidepanel-type', 'ui-language');
    panel.style.padding = '4px';
    panel.style.gap = '1px';
    panel.style.maxHeight = 'min(350px, calc(100vh - 24px))';
    panel.style.overflowY = 'auto';

    const languageOptions = window.NEKO_NATIVE_LANGUAGE_OPTIONS || [];
    const rows = [];
    const currentLanguage = () => {
        const current = window.i18next && window.i18next.language;
        if (current) return current;
        try { return localStorage.getItem('i18nextLng') || ''; }
        catch (_) { return ''; }
    };

    function refreshChoice() {
        const current = currentLanguage();
        rows.forEach(({ code, entry, mark }) => {
            const selected = code === current;
            entry.setAttribute('aria-pressed', String(selected));
            mark.textContent = selected ? '\u2713' : '';
        });
    }

    languageOptions.forEach(({ code, label }) => {
        const entry = document.createElement('div');
        entry.className = prefix + '-settings-menu-item';
        entry.setAttribute('role', 'button');
        entry.setAttribute('tabindex', '0');
        entry.setAttribute('data-neko-ui-language', code);
        Object.assign(entry.style, {
            display: 'flex', alignItems: 'center', justifyContent: 'space-between',
            gap: '8px', padding: '7px 10px', borderRadius: '6px',
            fontSize: '12px', cursor: 'pointer', userSelect: 'none',
            width: '100%', boxSizing: 'border-box'
        });

        const caption = document.createElement('span');
        caption.textContent = label;
        caption.lang = code;
        const checkmark = document.createElement('span');
        checkmark.setAttribute('aria-hidden', 'true');
        entry.appendChild(caption);
        entry.appendChild(checkmark);

        entry.addEventListener('mouseenter', () => {
            entry.style.background = 'var(--neko-popup-hover, rgba(68,183,254,0.1))';
        });
        entry.addEventListener('mouseleave', () => {
            entry.style.background = 'transparent';
        });

        async function chooseLanguage(event) {
            event.stopPropagation();
            if (typeof window.changeLanguage !== 'function') return;
            try {
                await window.changeLanguage(code);
                // This is a deliberate UI choice, unlike the automatic Steam language.
                localStorage.setItem('nekoManualUiLanguage', code);
                refreshChoice();
            } catch (error) {
                console.error('[i18n] Could not change UI language:', error);
            }
        }
        entry.addEventListener('click', chooseLanguage);
        entry.addEventListener('keydown', event => {
            if (event.key !== 'Enter' && event.key !== ' ') return;
            event.preventDefault();
            void chooseLanguage(event);
        });

        panel.appendChild(entry);
        rows.push({ code, entry, mark: checkmark });
    });

    const nativeExpand = panel._expand;
    panel._expand = function () {
        refreshChoice();
        return nativeExpand.call(this);
    };
    refreshChoice();
    document.body.appendChild(panel);
    return panel;
}

"""


def patch_i18n(source: str) -> str:
    if "nekoManualUiLanguage" in source:
        raise ValueError("Already patched, or a different manual language implementation.")
    anchor = """        // Honor a manually selected Persian UI over automatic Steam language."""
    if source.count(anchor) != 1:
        raise ValueError("Original i18next startup doesn't match approved build")
    addition = """        // An explicit selection in the original UI menu overrides Steam auto-detection.
        try {
            const manual = localStorage.getItem('nekoManualUiLanguage') || '';
            if (SUPPORTED_LANGUAGES.includes(manual)) return manual;
        } catch (_) { /* Keep the original fallback. */ }

"""
    return source.replace(anchor, addition + anchor, 1)


def patch_settings(source: str) -> str:
    if source.count(POPUP_FUNCTION) != 1 or source.count(BUTTON_ANCHOR) != 1:
        raise ValueError("Original settings menu does not match the approved build.")
    source = source.replace(POPUP_FUNCTION, NEW_FUNCTION + POPUP_FUNCTION, 1)
    return source.replace(BUTTON_ANCHOR, BUTTON_REPLACEMENT, 1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--install-dir", required=True, type=Path)
    parser.add_argument("--backup-dir", required=True, type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    folder = args.install_dir / "resources" / "bin" / "static"
    settings = folder / "avatar" / "avatar-ui-popup.js"
    i18n = folder / "i18n-i18next.js"
    fa = folder / "locales" / "fa.json"
    if not fa.exists() or not (args.install_dir / "N.E.K.O.exe").exists():
        raise SystemExit("Needs the original N.E.K.O installation with Persian locale.")
    first = patch_settings(settings.read_text(encoding="utf8"))
    second = patch_i18n(i18n.read_text(encoding="utf8"))
    if args.dry_run:
        print("DRY_RUN_PASS: existing popup template and i18next compatible")
        return
    backup = args.backup_dir / ("before-language-selector-" + datetime.now().strftime("%Y%m%d-%H%M%S"))
    backup.mkdir(parents=True, exist_ok=False)
    shutil.copy2(settings, backup / settings.name)
    shutil.copy2(i18n, backup / i18n.name)
    settings.write_text(first, encoding="utf8")
    i18n.write_text(second, encoding="utf8")
    print("UI_LANGUAGE_SELECTOR_INSTALLED:", settings, i18n)
    print("BACKUP:", backup)
    print("NO_HTML_CSS_CHAT_ASSETS_MODIFIED")


if __name__ == "__main__":
    main()
