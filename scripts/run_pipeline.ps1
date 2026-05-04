Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$projectRoot = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
Set-Location -LiteralPath $projectRoot

$venvPython = Join-Path $projectRoot ".venv/Scripts/python.exe"
if (-not (Test-Path -LiteralPath $venvPython)) {
    Write-Host "Creating virtual environment..."
    python -m venv .venv
}

Write-Host "Starting PostgreSQL..."
docker compose up -d postgres

Write-Host "Waiting for PostgreSQL..."
$ready = $false
for ($i = 0; $i -lt 30; $i++) {
    docker exec healthcare_postgres pg_isready -U healthcare -d healthcare *> $null
    if ($LASTEXITCODE -eq 0) {
        $ready = $true
        break
    }
    Start-Sleep -Seconds 2
}

if (-not $ready) {
    throw "PostgreSQL did not become ready in time"
}

Write-Host "Loading OWID data into PostgreSQL..."
& $venvPython -m src.ingestion.load_owid --write-db
if ($LASTEXITCODE -ne 0) {
    throw "OWID load failed with exit code $LASTEXITCODE"
}

Write-Host "Running dbt..."
& (Join-Path $projectRoot "scripts/run_dbt.ps1")

Write-Host "Pipeline completed."
