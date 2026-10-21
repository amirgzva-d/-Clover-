# Clover Persian as the UI default

New Clover UI sessions use fa as their default for the main interface and plugin manager.

Order in the main interface: explicit saved server override, URL override, saved i18nextLng, then fa. Steam/system/browser values do not override the new default. Previously chosen languages are retained.

In plugin manager: missing locale preference resolves to fa. An explicitly saved auto preference continues to follow the browser (preserving original auto mode). A saved concrete locale is never overwritten. Both UI bundles load Persian eagerly to avoid first-render Chinese translations and use an Element Plus Persian locale.

This affects only UI labels and layout. It does not change the chosen AI model, conversation language, voice synthesis provider, or microphone settings. The separately installed executable/installer must be rebuilt to include source changes.
