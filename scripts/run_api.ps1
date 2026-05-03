Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$projectRoot = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
Set-Location -LiteralPath $projectRoot

$venvPython = Join-Path $projectRoot ".venv/Scripts/python.exe"
if (Test-Path -LiteralPath $venvPython) {
    & $venvPython -m uvicorn api.main:app --host 127.0.0.1 --port 8002
}
else {
    python -m uvicorn api.main:app --host 127.0.0.1 --port 8002
}
