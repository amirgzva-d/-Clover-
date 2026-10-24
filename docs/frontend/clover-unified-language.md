# Clover single-language selector - backend-first source integration

User requirement: one entry in the original N.E.K.O. settings panel selects
language for UI, per-character chat and compatible realtime voice. Original
character, windows, styling, chat rendering and assets must not be replaced.
Chinese restores the original Chinese UI.

## Source implementation

- static/avatar/avatar-ui-popup.js: one row inside existing settings popup;
  nine languages shown with the original native settings panel components.
- static/i18n-i18next.js: changeCloverLanguageEverywhere(lang) loads locale
  resources and sends an authenticated PUT to the existing character language
  endpoint first. Only after success it updates visible UI, character language
  cache and plugin manager preference. It retries once on explicit CSRF failure
  and does not show a fake successful language switch on backend rejection.
  Existing window.changeLanguage remains unchanged for other callers.
- frontend/plugin-manager/src/i18n/index.ts: same-origin Vue panel follows
  the persisted locale setting without CSS or markup modifications.
- main_logic/omni_realtime_client/_client.py, main_logic/core/lifecycle.py,
  main_logic/omni_realtime_client/_transport.py, utils/language_utils.py:
  pass the explicit character locale into the existing overseas free realtime
  session language_code; preserve default global-language behavior when unset.

## Verified and unverified

This is a source integration, NOT an updated native executable or completed
audio integration. Compiled N.E.K.O. v0.9.0.1 rejects character preference fa
with HTTP 400. Its free preview requested with fa spoke Chinese per independent
speech recognition. Neither frontend selection nor an audio buffer guarantees
native Persian pronunciation.

Headless Playwright, using source frontend files against the existing original
local page with MOCKED character preference responses, verified that rejected
fa leaves UI/chat in the old language; accepted fa applies the new UI language,
character preference and plugin manager storage; accepted zh-CN restores Chinese;
the original popup contains nine language entries; and no browser JS errors
occurred. These tests did not change the installed backend or user settings.

Before real deployment, rebuild a version-compatible native backend without
changing original HTML/CSS/React bundles. Test Persian microphone recognition,
real Persian answers from selected model, natural Persian TTS and the Chinese
round-trip using the actual provider and voice. Some ASR/TTS providers do not
support every language and cannot be marked functional without audio tests.
