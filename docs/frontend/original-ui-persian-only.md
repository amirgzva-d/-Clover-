# Original N.E.K.O. UI — Persian in existing settings

Requirement (2026-10-24): Preserve the original N.E.K.O. v0.9.0.1 Windows executable, chat, avatar, CSS, layout and animation. Add a visible ninth UI language, Persian, only inside the existing settings popup. No second Chrome or Electron app.

## Preserving the original

The installed original compiled binary and original HTML, CSS and React chat assets are unchanged. The original bundled projectneko_server.exe still serves the app on port 48911. The previous source-based test launcher was removed.

The only UI-language changes to the installed original are:
- resources/bin/static/locales/fa.json: Persian translations matched to original English locale keys with safe fallback where necessary.
- resources/bin/static/i18n-i18next.js: existing ninth-language registration, plus preservation of a deliberately selected UI language over automatic Steam language detection. Non-explicit defaults remain unchanged.
- resources/bin/static/avatar/avatar-ui-popup.js: one Language row inside the original settings popup. It reuses original _createSettingsMenuButton, _createSidePanelContainer and _attachSidePanelHover functions; its choices come from the existing NEKO_NATIVE_LANGUAGE_OPTIONS registry. No global CSS or layout changes.

## Install or revert

For a fresh copy of the SAME original release:
1. Run scripts/patch-original-neko-persian-only.py using the installed executable folder, source translation static/locales/fa.json and a backup directory. Supports --dry-run.
2. Run scripts/add-original-neko-language-menu.py --install-dir PATH_TO_ORIGINAL_INSTALL --backup-dir PATH_TO_BACKUPS. Supports --dry-run. Refuses unexpected versions and saves copies of both JavaScript files.
3. Restart the SAME N.E.K.O.exe. No new application or installer is required for this UI-only change.

Current live backup path: C:\Users\cibesabz\AppData\Local\CloverNEKO\backups\2026-10-24\language-menu . To revert the selector, restore its archived i18n-i18next.js and avatar-ui-popup.js to the installed original locations.

## Test record

Headless browser tests against the original native backend verified the actual settings popup creates the Language row and native side panel with nine options. Persian selection changed i18next language to fa, translated common.close to بستن, and persisted the chosen locale. English switched back; Persian persisted after reload while Steam language was mocked to Chinese. No JavaScript page errors occurred in these tests. Real AI provider responses and speech were not tested for this UI-only change.

The source repository may continue separately, but do not replace the installed original with a differently styled source build unless the user explicitly requests a redesign.
