# Prepara ambiente isolado, compila React e inicia SIMCOTER 0.8 local.
$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)
if (!(Test-Path ".venv\Scripts\python.exe")) { python -m venv .venv }
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
$python = Join-Path (Get-Location) ".venv\Scripts\python.exe"
& $python -m pip install -e ".[test]"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Push-Location frontend
try {
    npm.cmd ci
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    npm.cmd run build
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} finally {
    Pop-Location
}
& $python scripts/start_local.py
exit $LASTEXITCODE
