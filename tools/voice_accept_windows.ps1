# No model download, network access, OAuth login or automatic publishing.
param(
    [Parameter(Mandatory=$true)][string]$Wav,
    [Parameter(Mandatory=$true)][ValidateSet('hi-IN','en-US')][string]$Locale,
    [Parameter(Mandatory=$true)][string]$SampleId,
    [switch]$Evaluate,
    [string]$Manifest = ''
)
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path -Parent $PSScriptRoot)
$Python = '.\.venv\Scripts\python.exe'
if (-not (Test-Path $Python)) { throw 'Install repo dependencies/venv first using docs/START_HERE.md' }
$PrivateDir = Join-Path $HOME 'ViralOSPrivateReports'
New-Item -ItemType Directory -Force -Path $PrivateDir | Out-Null
if (-not $Evaluate) {
    $NewManifest = Join-Path $PrivateDir ("m25-$SampleId-" + [Guid]::NewGuid().ToString('N') + '.json')
    & $Python tools/create_voice_manifest.py $Wav --locale $Locale --sample-id $SampleId --out $NewManifest
    if ($LASTEXITCODE -ne 0) { throw 'Manifest initialization failed; see errors above' }
    Write-Host 'Manifest created privately. Fill REAL model hashes, human reference words, local candidate timestamps, rights and listening review. Nothing uploaded.'
    Write-Host $NewManifest
} else {
    if (-not $Manifest) { throw 'Supply -Manifest <private-json-path> when using -Evaluate' }
    & $Python tools/audio_acceptance.py $Manifest
    if ($LASTEXITCODE -ne 0) { throw 'Acceptance evidence missing, invalid or BLOCKED; read private report for reasons' }
    Write-Host 'Metrics evaluated. This does NOT authorize publishing or establish independent model quality.'
}