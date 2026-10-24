# Original N.E.K.O. translation/chat audit, October 24 2026

UI restriction: Preserve original installed N.E.K.O. v0.9.0.1
Electron application, avatar, HTML, CSS, fonts, icons, original chat window,
and original Chinese audio. Only change isolated language handling.

## Reproduced live backend failures

Actual requests to original installed localhost:48911 /api/translate:
- Persian "سلام دوست من" to English: HTTP 200, source_lang unknown, same Persian text returned.
- English "Hello, good morning." to Persian: HTTP 200, target_lang en, same English text returned.
- English "Good morning" to Chinese: HTTP 200, correct Chinese translation "早上好".
The compiled backend has neither reliable Persian script recognition nor
Persian normalization: target fa becomes en; source Persian becomes unknown.

Original React chat can answer questions in BOTH languages: it has replied
"Four." to an English arithmetic question and
"پایتخت ایران تهران است." to a Persian geography question. A different
chat test sent after selecting fa failed when startup still used explicit
character language zh-CN, so Persian answers are not guaranteed simply by
switching UI language. The compiled character preference endpoint also
rejected setting fa earlier with HTTP 400. Do not call this fully working.

## Identified and resolved installed-front-end bug

The subtitle module was converting fa to zh in its translation language
normalizer and in its fallback normalizer. The original language selector
only updated UI locale, not subtitle language.
Patched only three *existing* installed Javascript files:
- static/subtitle/subtitle-shared.js
- static/subtitle/subtitle.js
- static/avatar/avatar-ui-popup.js
Made matching source changes in first two, and linked subtitle target to the
source's existing unified-language function only after backend acceptance.

Verified with headless Chromium against the installed original server:
fa -> UI language fa, subtitle language fa, manual choice fa;
zh-CN -> UI language zh-CN, subtitle language zh, manual choice zh-CN;
nine native languages remain, no Javascript page errors.

Backup of the three previous installed files:
AppData/Local/CloverNEKO/backups/2026-10-24/subtitle-fa-normalization.
No executable, theme, HTML/CSS or React bundle was changed.

## Source backend fix, not yet compiled into installed binary

utils/language_utils.py now detects Persian orthography conservatively and
maps fa explicitly to Google translation. Ordinary Arabic without Persian
markers is not mislabeled. config/prompts/prompts_sys.py supplies the missing
Persian language names for all LLM fallback translation prompt locales.
Tests cover Persian detection, preserved other languages, translation
provider calls in both directions and correct subtitle locale propagation.

The installed Nuitka backend still needs version-compatible rebuilding and
testing. Source changes alone do NOT make its translation endpoint work in
Persian. Its provider fallbacks can also fail when upstream translation
services are unavailable. Do not report complete Persian translation until
real installed fa->en and en->fa requests return translated content.

## Speech limitation

A local Piper Persian model and a separate authenticated PCM speech bridge
are available in development, but not wired into the compiled original
realtime audio path: replacing the default route would damage the user's
existing Chinese-voice behavior. Live audio/microphone end-to-end testing is
still required after a strictly compatible native backend integration.

No credentials, chat transcripts or private configuration were committed.
