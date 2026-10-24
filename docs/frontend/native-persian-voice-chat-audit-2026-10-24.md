# Native N.E.K.O. v0.9.0.1 — Persian speech/chat compatibility audit (2026-10-24)

**Scope and non-negotiable UI requirement:** Do not change or replace the original installed N.E.K.O. UI, chat window, character, colors, animations, templates, frontend bundles or Electron application. Persian UI translation and a ninth language menu option have been selectively patched into this installed copy. Upgrading the existing compiled backend requires a separately tested, compatible replacement; do not deploy a generic, differently styled newer build or spawn a second Chrome window.

## Actual on-device results

Windows: DESKTOP-LR1PDM2; original installed app folder:
C:\Users\cibesabz\AppData\Local\Programs\N.E.K.O_v0.9.0.1
Original backend: resources\bin\projectneko_server.exe (compiled Nuitka).

- GET /health: HTTP 200 (the original server runs).
- GET /api/config/core_api: coreApi=free, effectiveCoreApi=free, assistApi=free, disableTts=false, supportsIndependentAsr=false. Do not copy API keys/tokens into logs.
- GET /api/characters/character/YUI/language-preference: success=true, explicit language=null, effective_language=en.
- Attempt to update the preference to fa using a valid local CSRF token: HTTP 400, "unsupported language". The installed compiled backend does not support fa as a conversation locale. No preference was changed.
- Both built-in /api/config/test_connectivity checks for the free core/assist providers returned success=true. **However, a real, isolated OpenAI-compatible chat completion to the free assist model returned HTTP 400.** That distinction is material: the connectivity probe alone does not prove generated answers work (the repository's free-provider test can accept HTTP 400).
- GET /api/characters/voices: four listed native free voices, eleven free-voice references. An English preview and a fa-requested preview each once returned an audio payload. A subsequent English preview returned HTTP 500; do not assume voice stability.
- On a generated audio preview specifically requested with language=fa, an independent local faster-whisper tiny transcriber detected **Chinese (zh), p=0.994**, with Chinese transcription rather than Persian. This proves the selected free preview request does not honor a Persian output language in the currently installed compiled backend. A saved audio sample was deleted after testing.

## Risk and compatibility implications

Changing static/locales/fa.json or the existing language menu **cannot** add Persian to the original compiled conversation prompt registry or fix speech generation. Do not set fa for a provider that refuses it, and do not treat a synthesized audio buffer as proof of spoken Persian. The user prefers retaining the same original voice and voice pipeline; another TTS provider must not be silently substituted.

The GitHub source separately contains Persian prompts, a fa voice-preview template and fa-aware TTS language handling. Those changes are not present in the old native compiled backend. They do **not** imply the installed app works in Persian, and they do **not** authorize replacing the original UI.

## Requirements before a native release upgrade

1. Rebuild or carefully patch **only a version-compatible backend** based on the installed v0.9.0.1 code, extending character language validation, prompt locale, text response instructions and matching ASR/TTS routing to support fa-IR. Preserve the existing chat/UI bytes.
2. Confirm the free realtime model can **actually** return a Persian response; the separate free assist chat-completion endpoint gave HTTP 400. Do not conflate the two.
3. Determine whether the existing selected female voice can truly synthesize Persian. If not, provide an explicit voice-provider choice and discuss voice-quality/voice-identity limitations before switching providers.
4. Perform isolated text-chat and mic -> ASR -> Persian response -> real Persian audio end-to-end tests with the installed app. Verify no new Chrome window, no duplicate Electron process, and no loss of original UI or user data.
5. Keep a full rollback backup of the native backend, user config and character memory. Do not overwrite the working original app until the rebuild passes all compatibility and UI regression checks.

## Preservation and impact of this audit

This is a diagnostic report, not a native installer or a functional speech upgrade. During the audit no UI files, installed executable, language preferences or provider config were altered. Original configuration and memory backups were saved under AppData\Local\CloverNEKO\backups\2026-10-24\before-persian-conversation. The installed app was restarted to test the normal native runtime.

On the initial observed failure, replacing the original UI with the newest source frontend would violate the user's explicit requirement. Restrict future changes to safe backend integration and existing-settings controls.
