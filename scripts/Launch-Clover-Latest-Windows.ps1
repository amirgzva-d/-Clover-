[CmdletBinding()]
param([switch]$CheckOnly, [switch]$UseBrowser)

$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$python = Join-Path $root '.venv\Scripts\python.exe'
$electron = Join-Path $env:LOCALAPPDATA 'Programs\N.E.K.O_v0.9.0.1\N.E.K.O.exe'
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
    throw "Clover $module did not start; check the log files under $logRoot."
}

if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
    throw "Python 3.11 project environment is missing. Run uv sync in $root."
}
if (-not $UseBrowser -and -not (Test-Path -LiteralPath $electron -PathType Leaf)) {
    throw "The original N.E.K.O Electron executable is missing: $electron"
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
    throw 'The source server did not serve the Persian interface resources.'
}
if ($UseBrowser) {
    $chrome = Join-Path $env:ProgramFiles 'Google\Chrome\Application\chrome.exe'
    if (-not (Test-Path -LiteralPath $chrome -PathType Leaf)) {
        throw 'Google Chrome was not found.'
    }
    Start-Process -FilePath $chrome -ArgumentList @('--app=http://127.0.0.1:48911/','--new-window')
} else {
    Start-Process -FilePath $electron -WorkingDirectory (Split-Path $electron)
}
