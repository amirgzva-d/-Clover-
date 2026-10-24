"""Regression contract: source testing must preserve the original Clover chat window."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "Launch-Clover-Latest-Windows.ps1"


def test_clover_windows_launcher_does_not_spawn_legacy_electron():
    text = SCRIPT.read_text(encoding="utf8")
    assert "Open-OriginalCloverWindow" in text
    assert "Get-Process -Name chrome" in text
    assert "MainWindowTitle -match 'N\\.E\\.K\\.O'" in text
    assert "Reusing original Clover window" in text
    assert "Start-Process -FilePath $chrome" in text
    assert "Start-Process -FilePath $electron" not in text
    assert "Start-Process -FilePath $exe" not in text
    assert "--app=http://127.0.0.1:48911/" not in text
    assert "--new-window" not in text


def test_clover_windows_launcher_still_checks_all_source_services():
    text = SCRIPT.read_text(encoding="utf8")
    assert "Ensure-Service 'memory_server' 48912" in text
    assert "Ensure-Service 'main_server' 48911" in text
    assert "Ensure-Service 'agent_server' 48915" in text
    assert "if ($CheckOnly)" in text
    assert "fa.json" in text


def test_clover_windows_launcher_does_not_mutate_chat_styles():
    text = SCRIPT.read_text(encoding="utf8")
    assert "stylesheets" not in text.lower()
    assert "Set-Content" not in text
    assert "Remove-Item" not in text
    assert "Stop-Process" not in text
