Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

& (Join-Path $projectRoot "scripts/start_project.ps1") @args
