# Clover Windows launcher: keep the original chat layout

The **Clover - GitHub Updated (Test)** desktop shortcut is for source-based integration testing. It does not rebuild or replace the existing Windows installer or the compiled N.E.K.O executable.

## Single-window rule

The user requested **Persian localization only**, with the original full-size, white/browser-based chat UI unchanged. During initial testing, the launcher started `N.E.K.O.exe` separately, which opened an unintended small dark chat window next to the original browser interface.

This launcher now starts or reuses the existing source backend services (memory 48912, main 48911, agent 48915), confirms the Persian locale is served, then **focuses an existing N.E.K.O Chrome window** instead of starting the legacy Electron executable. If that Chrome window is absent, it opens the original full-page URL in a regular Chrome tab. Repeated invocation with an active N.E.K.O browser window must **not** create duplicate windows. The old `-UseBrowser` argument remains accepted for compatibility.

It never modifies chat styles, replaces the installed executable, or terminates unrelated browser processes. The Electron binary is deliberately not started because its bundled backend and separately styled chat window would conflict with the source-run application.

## Validation and prerequisites

Requires Python 3.11, a prepared `.venv`, locally built Vue/React assets and Google Chrome. Use `-CheckOnly` to inspect service ownership without opening an app. Do not run two copies of each backend against the same user profile. The old installation and files must be preserved until an independently built desktop release has passed compatibility testing.

This is a **temporary source test launcher, not a new installer**. Real audio playback, speech input and provider-based chat answers still need device and API testing.
