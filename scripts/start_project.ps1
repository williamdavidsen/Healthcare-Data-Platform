param(
    [switch]$WithPostgres,
    [switch]$UseSample,
    [switch]$UseOwid,
    [switch]$WriteDb,
    [switch]$RunDbt,
    [switch]$UseStreamlit,
    [switch]$SkipInstall,
    [switch]$NoBrowser
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$projectRoot = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
Set-Location -LiteralPath $projectRoot

$venvPython = Join-Path $projectRoot ".venv/Scripts/python.exe"
if (-not (Test-Path -LiteralPath $venvPython)) {
    Write-Host "Creating virtual environment..."
    python -m venv .venv
}

if (-not $SkipInstall) {
    Write-Host "Installing dependencies..."
    & $venvPython -m pip install -r requirements.txt

    Write-Host "Installing frontend dependencies..."
    npm install --prefix frontend
}

if ($WithPostgres -or $WriteDb) {
    Write-Host "Starting PostgreSQL..."
    docker compose up -d postgres
}

if ($UseSample) {
    Write-Host "Loading sample data..."
    & $venvPython -m src.ingestion.load_sample
}
else {
    $owidArgs = @("-m", "src.ingestion.load_owid")
    if ($WriteDb) {
        $owidArgs += "--write-db"
    }
    Write-Host "Loading current OWID data..."
    try {
        & $venvPython @owidArgs
        if ($LASTEXITCODE -ne 0) {
            throw "OWID loader exited with code $LASTEXITCODE"
        }
    }
    catch {
        Write-Host "OWID load failed; falling back to sample data."
        & $venvPython -m src.ingestion.load_sample
    }
}

if ($RunDbt -or $WriteDb) {
    Write-Host "Running dbt models and tests..."
    & (Join-Path $projectRoot "scripts/run_dbt.ps1")
    $env:USE_DATABASE = "true"
    $env:MART_SCHEMA = "analytics"
    $env:MART_TABLE = "mart_country_health_trends"
}

$logDir = Join-Path $projectRoot ".logs"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

Start-Process -FilePath powershell.exe `
    -ArgumentList @(
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-Command",
        "& '$((Join-Path $projectRoot "scripts/run_api.ps1"))'"
    ) `
    -RedirectStandardOutput (Join-Path $logDir "api.out.log") `
    -RedirectStandardError (Join-Path $logDir "api.err.log") `
    -WindowStyle Hidden

if ($UseStreamlit) {
    Start-Process -FilePath powershell.exe `
        -ArgumentList @(
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            "& '$((Join-Path $projectRoot "scripts/run_dashboard.ps1"))'"
        ) `
        -RedirectStandardOutput (Join-Path $logDir "dashboard.out.log") `
        -RedirectStandardError (Join-Path $logDir "dashboard.err.log") `
        -WindowStyle Hidden
}
else {
    Start-Process -FilePath powershell.exe `
        -ArgumentList @(
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            "& '$((Join-Path $projectRoot "scripts/run_frontend.ps1"))'"
        ) `
        -RedirectStandardOutput (Join-Path $logDir "frontend.out.log") `
        -RedirectStandardError (Join-Path $logDir "frontend.err.log") `
        -WindowStyle Hidden
}

Start-Sleep -Seconds 3

if (-not $NoBrowser) {
    if ($UseStreamlit) {
        Start-Process "http://127.0.0.1:8502"
    }
    else {
        Start-Process "http://127.0.0.1:5173"
    }
}

Write-Host ""
Write-Host "Project is running."
Write-Host "API: http://127.0.0.1:8002/docs"
Write-Host "React frontend: http://127.0.0.1:5173"
Write-Host "Streamlit dashboard: http://127.0.0.1:8502 (use -UseStreamlit)"
Write-Host "Logs: $logDir"
