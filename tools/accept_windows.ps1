# Offline Windows CPU smoke test. Does not log in, upload, buy or download models.
param([ValidateRange(1,15)][int]$DurationSeconds = 3)
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path -Parent $PSScriptRoot)
$Python = '.\.venv\Scripts\python.exe'
if (-not (Test-Path $Python)) {
    throw 'Please install the local venv first: py -3.12 -m venv .venv; .\.venv\Scripts\python.exe -m pip install -r requirements.txt'
}
$ReportDir = Join-Path $HOME 'ViralOSPrivateBackups'
New-Item -Type Directory -Force -Path $ReportDir | Out-Null
& $Python tools/owner_acceptance.py preflight --report (Join-Path $ReportDir 'preflight.json')
if ($LASTEXITCODE -ne 0) { throw 'Preflight failed: missing dependencies or FFmpeg' }
& $Python tools/owner_acceptance.py benchmark --duration $DurationSeconds --report (Join-Path $ReportDir 'benchmark.json')
if ($LASTEXITCODE -ne 0) { throw 'CPU synthetic video benchmark failed' }
Write-Host 'Offline acceptance reports saved OUTSIDE Git in your private home directory.' -ForegroundColor Green
Write-Host 'Next: full test suite, Hindi font check and full original video watch-through on your own Windows PC.'