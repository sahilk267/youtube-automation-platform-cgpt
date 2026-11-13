$ErrorActionPreference = 'Stop'
Set-Location (Split-Path -Parent $PSScriptRoot)
if (-not (Test-Path '.venv')) { py -3.12 -m venv .venv }
& '.\.venv\Scripts\python.exe' -m pip install -r requirements.txt
& '.\.venv\Scripts\python.exe' tools/check_environment.py
if ($LASTEXITCODE -ne 0) { throw 'Missing environment requirements' }
& '.\.venv\Scripts\python.exe' -m pytest -q
if ($LASTEXITCODE -ne 0) { throw 'Automated tests failed' }
Write-Host 'Open http://127.0.0.1:8000 in your browser after server startup' -ForegroundColor Green
& '.\.venv\Scripts\python.exe' -m uvicorn app.main:app --host 127.0.0.1 --port 8000
