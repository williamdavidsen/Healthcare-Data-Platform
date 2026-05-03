Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$projectRoot = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
Set-Location -LiteralPath $projectRoot

$venvPython = Join-Path $projectRoot ".venv/Scripts/python.exe"
if (Test-Path -LiteralPath $venvPython) {
    & $venvPython -m streamlit run dashboard/app.py --server.headless true --server.port 8502
}
else {
    python -m streamlit run dashboard/app.py --server.headless true --server.port 8502
}
