Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$projectRoot = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
Set-Location -LiteralPath $projectRoot

$screenshotDir = Join-Path $projectRoot "docs/screenshots"
New-Item -ItemType Directory -Force -Path $screenshotDir | Out-Null

npx playwright screenshot --full-page http://127.0.0.1:5173 (Join-Path $screenshotDir "dashboard.png")
