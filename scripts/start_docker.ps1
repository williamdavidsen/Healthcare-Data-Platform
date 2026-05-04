Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$projectRoot = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
Set-Location -LiteralPath $projectRoot

Write-Host "Building Docker images..."
docker compose build api frontend pipeline

Write-Host "Starting PostgreSQL..."
docker compose up -d postgres

Write-Host "Running containerized pipeline..."
docker compose --profile pipeline run --rm pipeline

Write-Host "Starting API and frontend..."
docker compose up -d api frontend

Write-Host ""
Write-Host "Docker stack is running."
Write-Host "React frontend: http://127.0.0.1:5173"
Write-Host "API docs: http://127.0.0.1:8002/docs"
