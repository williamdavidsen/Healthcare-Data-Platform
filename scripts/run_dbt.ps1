Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$projectRoot = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
Set-Location -LiteralPath $projectRoot

$venvDbt = Join-Path $projectRoot ".venv/Scripts/dbt.exe"
if (Test-Path -LiteralPath $venvDbt) {
    & $venvDbt run --project-dir dbt --profiles-dir dbt
    if ($LASTEXITCODE -ne 0) {
        throw "dbt run failed with exit code $LASTEXITCODE"
    }
    & $venvDbt test --project-dir dbt --profiles-dir dbt
    if ($LASTEXITCODE -ne 0) {
        throw "dbt test failed with exit code $LASTEXITCODE"
    }
}
else {
    dbt run --project-dir dbt --profiles-dir dbt
    if ($LASTEXITCODE -ne 0) {
        throw "dbt run failed with exit code $LASTEXITCODE"
    }
    dbt test --project-dir dbt --profiles-dir dbt
    if ($LASTEXITCODE -ne 0) {
        throw "dbt test failed with exit code $LASTEXITCODE"
    }
}
