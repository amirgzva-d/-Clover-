# Original N.E.K.O. installed UI — Persian language only

**User decision (2026-10-24):** preserve the exact original installed desktop application and all existing visual design. Do not replace the chat with the compact dark Electron test window, do not launch a second Chrome interface, and do not change layout, animation, character, fonts, colors or CSS to implement translation.

The Windows installation `N.E.K.O_v0.9.0.1` was still present and its original compiled executable matched the saved pre-test backup. The full-page template, chat template and React chat bundle also matched their backups.

The original legacy i18next client has an eight-language registry. Only **two assets** inside the existing installation were updated:
- `resources/bin/static/i18n-i18next.js`: add `fa` to the existing language menu, normalization, and preserve an explicitly selected Persian choice through Steam startup. It does not change the original language default or direction/CSS.
- `resources/bin/static/locales/fa.json`: Persian translations matched to the exact original English locale keys, with original English fallback when a translation or placeholder is incompatible.

This change is intentionally different from rebuilding the *latest* upstream interface. Do not package the newer source's redesigned UI as a replacement for this original executable. Future installation upgrades must be based on the corresponding original release and must pass a byte-level visual-asset comparison before delivery.

For a future clean installation of the original version, run `scripts/patch-original-neko-persian-only.py` with the original install directory, the repository's `static/locales/fa.json`, and an explicit backup directory. It validates the existing assets, supports `--dry-run`, and modifies only the same two language files.

The earlier GitHub source-based launcher was removed: it incorrectly ran the existing Electron backend and a separate browser page at the same time. No side-by-side test app or additional Chrome window is required for the original desktop version.

**Verification:** original executable and original HTML/chat bundle hashes matched backups; Persian file served HTTP 200 from the compiled installed server; language registry contains fa; the old installed exe launched with the old native backend on ports 48911, 48912 and 48915; source-test backend processes were stopped and desktop test shortcut removed. The native window's language dropdown must still be clicked and visually inspected for the new item on-device; API-powered conversation and speech are outside this UI-only change.
