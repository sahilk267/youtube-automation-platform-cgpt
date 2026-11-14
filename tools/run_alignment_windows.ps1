# Explicitly opt-in, offline-configured model-backed word proposals. NO publication.
param(
    [Parameter(Mandatory=$true)][string]$SampleDir,
    [Parameter(Mandatory=$true)][string]$ScriptFile,
    [Parameter(Mandatory=$true)][string]$ModelDir,
    [Parameter(Mandatory=$true)][ValidateSet('hi-IN','en-US')][string]$Locale,
    [Parameter(Mandatory=$true)][string]$LicenseName,
    [switch]$LicenseReviewed,
    [ValidateRange(30,1800)][int]$TimeoutSeconds = 600
)
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path -Parent $PSScriptRoot)
$Python = '.\.venv\Scripts\python.exe'
if (-not (Test-Path $Python)) { throw 'Project .venv with Python 3.12 is required.' }
if (-not $LicenseReviewed) { throw 'Review local aligner model rights, then explicitly provide -LicenseReviewed.' }
if (-not (Test-Path $SampleDir -PathType Container)) { throw 'Piper private sample folder not found.' }
if (-not (Test-Path $ModelDir -PathType Container)) { throw 'Preinstalled local aligner model folder not found.' }
if (-not (Test-Path $ScriptFile -PathType Leaf)) { throw 'Exact private narration script not found.' }
$env:HF_HUB_OFFLINE = '1'
$env:TRANSFORMERS_OFFLINE = '1'
$env:HF_DATASETS_OFFLINE = '1'
$env:HF_HUB_DISABLE_TELEMETRY = '1'
& $Python -m tools.run_local_alignment --sample-dir $SampleDir --script-file $ScriptFile --model-dir $ModelDir --locale $Locale --license-name $LicenseName --license-reviewed --timeout $TimeoutSeconds
if ($LASTEXITCODE -ne 0) { throw ('Local alignment was BLOCKED or failed (exit code ' + $LASTEXITCODE + '). No words automatically approved. Check model, locale and private input binding.') }
Write-Host 'Private UNREVIEWED word proposal and unchanged original Piper manifest available.' -ForegroundColor Green
Write-Host 'Next: human-reviewed word ground truth, full listen and tools.audio_acceptance evaluation. No publishing authorized.'