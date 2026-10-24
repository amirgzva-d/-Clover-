[CmdletBinding()]
param(
    [switch]$CheckOnly,
    [switch]$UseBrowser
)

$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$python = Join-Path $root '.venv\Scripts\python.exe'
$chrome = Join-Path $env:ProgramFiles 'Google\Chrome\Application\chrome.exe'
$logRoot = Join-Path $env:LOCALAPPDATA 'CloverNEKO\source-run-logs'

function Test-ServicePort([int]$port, [string]$module) {
    $connections = @(Get-NetTCPConnection -State Listen -LocalPort $port -ErrorAction SilentlyContinue)
    if ($connections.Count -eq 0) { return $false }
    foreach ($connection in $connections) {
        $running = Get-CimInstance Win32_Process -Filter "ProcessId=$($connection.OwningProcess)" -ErrorAction SilentlyContinue
        if ($running -and $running.CommandLine -like "*-m app.$module*") {
            return $true
        }
    }
    throw "Port $port is occupied by another process. Clover will not override it."
}

function Ensure-Service([string]$module, [int]$port) {
    if (Test-ServicePort $port $module) { return }
    New-Item -ItemType Directory -Force -Path $logRoot | Out-Null
    $prefix = Join-Path $logRoot $module
    Start-Process -FilePath $python -ArgumentList @('-m',"app.$module") -WorkingDirectory $root -WindowStyle Hidden -RedirectStandardOutput "$prefix.stdout.log" -RedirectStandardError "$prefix.stderr.log" | Out-Null
    for ($i = 0; $i -lt 120; $i++) {
        Start-Sleep -Milliseconds 500
        if (Test-ServicePort $port $module) { return }
    }
    throw "Clover $module did not start; check log files under $logRoot."
}

# The old Electron binary opens its own separate dark chat window and bundled
# backend. Clover source testing must NEVER launch that binary alongside the
# original full-size browser interface. Only open/focus the original web UI.
function Open-OriginalCloverWindow {
    $existing = Get-Process -Name chrome -ErrorAction SilentlyContinue |
        Where-Object { $_.MainWindowHandle -ne 0 -and $_.MainWindowTitle -match 'N\.E\.K\.O' } |
        Select-Object -First 1

    if ($existing) {
        # Keep the user's existing chat, scroll position, layout, and window.
        # Do not create another window or navigate away from active chat.
        Write-Output "Reusing original Clover window, Chrome PID $($existing.Id)"
        try {
            if (-not ('CloverWindowFocus' -as [type])) {
                Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class CloverWindowFocus {
    [DllImport("user32.dll")] public static extern bool ShowWindowAsync(IntPtr hWnd, int nCmdShow);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
}
'@ -ErrorAction Stop
            }
            [CloverWindowFocus]::ShowWindowAsync($existing.MainWindowHandle, 9) | Out-Null
            [CloverWindowFocus]::SetForegroundWindow($existing.MainWindowHandle) | Out-Null
        } catch {
            Write-Warning "Could not focus existing Chrome window: $($_.Exception.Message)"
        }
        return
    }

    if (-not (Test-Path -LiteralPath $chrome -PathType Leaf)) {
        throw "Google Chrome not found: $chrome"
    }
    # A regular browser tab preserves the original full-size chat layout,
    # instead of opening a separate Electron chat panel or an --app window.
    Start-Process -FilePath $chrome -ArgumentList 'http://127.0.0.1:48911/'
    Write-Output 'Opened original Clover full-page interface in Chrome.'
}

if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
    throw "Python 3.11 virtual environment not found. Run uv sync in $root."
}
if ($CheckOnly) {
    Write-Output "Clover source directory: $root"
    Write-Output "Python virtual environment: $python"
    foreach ($service in @(@('memory_server',48912),@('main_server',48911),@('agent_server',48915))) {
        $status = Test-ServicePort ([int]$service[1]) ([string]$service[0])
        Write-Output "$($service[0]) listening: $status"
    }
    exit 0
}

Ensure-Service 'memory_server' 48912
Ensure-Service 'main_server' 48911
Ensure-Service 'agent_server' 48915

$response = Invoke-WebRequest -Uri 'http://127.0.0.1:48911/static/locales/fa.json' -UseBasicParsing -TimeoutSec 12
if ($response.StatusCode -ne 200 -or $response.Content -notmatch '"character"') {
    throw 'Clover source server did not serve the Persian UI resources.'
}

# -UseBrowser remains accepted for old shortcuts, but browser UI is now always
# the default to prevent reopening the unintended dark Electron chat window.
Open-OriginalCloverWindow
