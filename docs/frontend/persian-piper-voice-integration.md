# Persian Piper speech module: installation and live chat audit

Date: 2026-10-24. Do not alter the original N.E.K.O. UI, React chat
or character design. Persian and Chinese must preserve separate voices.

## Verified on the Windows PC

- Original Windows program is still the same N.E.K.O. v0.9.0.1.
- English chat via the original React composer: asked two plus two and
  received "Four." from the actual N.E.K.O. server.
- Persian chat via the original React composer: asked the capital of Iran in
  Persian and received "پایتخت ایران تهران است." in Persian in around 16 seconds.
  So text chat IS capable of Persian responses. This does not imply its
  current language switch is fully synchronized.
- Female Microsoft Edge voice fa-IR-DilaraNeural: available publicly, but the
  PC could not resolve speech.platform.bing.com during an actual request.
  Do not report it working locally.
- Piper fa_IR-amir-medium: downloaded original upstream model (~63MB) and
  installed piper-tts into the existing source development virtual environment.
  Offline synthesis succeeded. Independent Whisper tiny detected Persian on
  a full sentence with confidence about 0.98. A shorter sample had ambiguous
  automatic classification. This voice is MALE and less natural than desired.

## Optional on-device voice adapter

scripts/clover_persian_piper_bridge.py is a loopback-only
OpenAI-compatible TTS endpoint, with bearer-token authentication.
Its endpoint is POST /v1/audio/speech on port 48919, accepts
model piper-fa, voice fa_IR-amir-medium, input UTF-8 Persian text and
response_format pcm. It returns little-endian 24kHz mono PCM16, matching the
existing custom TTS worker's expected format. The local model and secret
remain outside GitHub.

IMPORTANT: The bridge is not currently connected to the compiled old
N.E.K.O. realtime audio path. The built-in free realtime model generates
its own voice. Forcing the custom TTS provider globally would risk changing
the original Chinese voice and does not necessarily affect realtime playback.
Do not claim voice switching works until the native compatible backend can
select the Persian adapter only for fa, cancel the native voice for that turn,
and preserve its existing voice for Chinese and all other languages.

A source-only unified language menu and per-character language propagation
have been committed separately. The old compiled backend still rejects
saving fa character locale with HTTP 400. Rebuild and test a compatible
native backend before installing that source change. Do not replace or
redesign the old Electron UI to solve this.
