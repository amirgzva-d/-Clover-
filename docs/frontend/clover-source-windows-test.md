# Running the latest Clover source on Windows (test mode)

This is an interim source-based test method. It does not replace or modify the official installed backend binary or installer.

Prerequisites: Python 3.11, project .venv prepared by uv sync, compiled Vue plugin manager and React chat assets.

Run scripts/Launch-Clover-Latest-Windows.ps1 from the repository with PowerShell. It starts the existing memory_server (48912), main_server (48911), and agent_server (48915), then opens the installed N.E.K.O Electron shell. Use the UseBrowser switch to open the same source interface in Chrome app mode instead.

The script will refuse to run if a different application occupies a required service port; it never kills or overwrites a running program. CheckOnly examines prerequisites and current service ownership without launching anything. Services use existing profile data, so back up the profile before testing newer source, and do not run two copies of the same backend against one profile.

The existing backend executable is a large compiled Nuitka binary. A real installable upgrade requires separately building the Python backend and a compatible Electron distribution. Do not describe this test launcher as a native installer update.

Regression evidence at source commit df966597b305d18feed15012cf5ca4706488be8a: 250 selected Python tests passed; plugin manager type check and 9-locale i18n check passed; React build passed; HTTP 200 was observed for the Persian locale and chat; the Agent health endpoints were also healthy. Real microphone-to-voice and live AI provider responses remain unverified.