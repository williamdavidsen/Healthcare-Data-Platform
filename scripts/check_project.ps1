Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$projectRoot = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
Set-Location -LiteralPath $projectRoot

$venvPython = Join-Path $projectRoot ".venv/Scripts/python.exe"
$venvDbt = Join-Path $projectRoot ".venv/Scripts/dbt.exe"

if (-not (Test-Path -LiteralPath $venvPython)) {
    throw "Virtual environment not found. Run .\start.ps1 first."
}

Write-Host "Running Python tests..."
& $venvPython -m pytest
if ($LASTEXITCODE -ne 0) {
    throw "pytest failed with exit code $LASTEXITCODE"
}

Write-Host "Building React frontend..."
npm run build --prefix frontend
if ($LASTEXITCODE -ne 0) {
    throw "frontend build failed with exit code $LASTEXITCODE"
}

if (Test-Path -LiteralPath $venvDbt) {
    Write-Host "Parsing dbt project..."
    & $venvDbt parse --project-dir dbt --profiles-dir dbt
    if ($LASTEXITCODE -ne 0) {
        throw "dbt parse failed with exit code $LASTEXITCODE"
    }
}

Write-Host "Project checks completed."
