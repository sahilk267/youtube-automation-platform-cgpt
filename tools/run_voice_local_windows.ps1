# M2.5 owner-triggered offline Piper sample runner; no models downloaded or video uploaded.
param(
    [Parameter(Mandatory=$true)][string]$PiperExe,
    [Parameter(Mandatory=$true)][string]$Model,
    [Parameter(Mandatory=$true)][string]$TextFile,
    [Parameter(Mandatory=$true)][ValidateSet('hi-IN','en-US')][string]$Locale,
    [Parameter(Mandatory=$true)][string]$SampleId,
    [Parameter(Mandatory=$true)][string]$LicenseName,
    [switch]$LicenseReviewed
)
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path -Parent $PSScriptRoot)
if (-not $LicenseReviewed) { throw 'Review your Piper model licence first, then explicitly pass -LicenseReviewed' }
$Python = '.\.venv\Scripts\python.exe'
if (-not (Test-Path $Python)) { throw 'Initialize the project .venv first (Python 3.12).' }
$PrivateOut = Join-Path $HOME 'ViralOSPrivateVoiceSamples'
& $Python -m tools.run_local_piper --piper-exe $PiperExe --model $Model --locale $Locale --text-file $TextFile --sample-id $SampleId --out-dir $PrivateOut --license-name $LicenseName --license-reviewed
if ($LASTEXITCODE -ne 0) { throw ('Piper sample was not accepted for review (exit code ' + $LASTEXITCODE + '). Check private audio and local logs.') }
Write-Host 'Raw voice, 16k WAV, unapproved manifest and redacted report stored OUTSIDE Git.' -ForegroundColor Green
Write-Host 'NEXT: human full listen + actual local forced alignment + M2.5 evaluator; no automatic upload.'