# Persian voice in Clover

The existing speech pipeline remains unchanged: ASR -> conversation model -> TTS.
Persian (`fa`) is a normal session language and is not a separate speech engine.

- **Microphone / ASR:** The existing local faster-whisper supports Persian (`fa`, `fa-IR`). The current Qwen and Step ASR language allowlists do not include Persian, so auto-detection on those providers is not a guarantee of correct Farsi transcription. Select a compatible ASR engine where possible.
- **Conversation:** the existing Persian persona fragments request concise, natural Persian speech when the session language is fa.
- **Spoken output:** OpenAI TTS and Gemini TTS already accept text in Persian through their native synthesis. Gemini now receives an explicit Persian speaking cue for distinguishable Persian text, while keeping its original audio worker/voice model/credentials. The existing lanlan.app Gemini proxy receives `fa-IR` where Persian is detected or the global language is fa.
- **Other providers:** Qwen/CosyVoice/StepFun voice API capabilities differ. Do not send unsupported Persian-specific flags to these providers; retain their existing autodetection and error behavior.
- **Voice previews:** Persian gets a native voice preview sample and is selectable through the normal frontend locale. The reference-audio language dropdown for voice *cloning* is a separate provider-restricted feature and is intentionally unchanged until each provider can validate Farsi support.

This is a code-level integration. On-device testing with microphone, selected API credentials, interruptions and real audio output remains necessary before claiming full speech support. The existing Windows binary and installer are not rebuilt by these GitHub commits.
