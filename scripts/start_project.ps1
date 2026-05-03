Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$projectRoot = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
Set-Location -LiteralPath $projectRoot

python -m src.ingestion.load_sample

Start-Process -FilePath powershell.exe `
    -ArgumentList @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", (Join-Path $projectRoot "scripts/run_api.ps1")) `
    -WindowStyle Hidden

Start-Process -FilePath powershell.exe `
    -ArgumentList @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", (Join-Path $projectRoot "scripts/run_dashboard.ps1")) `
    -WindowStyle Hidden

Write-Host "API: http://127.0.0.1:8002/docs"
Write-Host "Dashboard: http://127.0.0.1:8502"
