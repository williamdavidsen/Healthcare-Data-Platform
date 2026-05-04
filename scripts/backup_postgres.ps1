param(
    [string]$ContainerName = "healthcare_postgres",
    [string]$Database = "healthcare",
    [string]$User = "healthcare",
    [string]$OutputDir = "backups"
)

$ErrorActionPreference = "Stop"

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupPath = Join-Path $OutputDir "$Database-$timestamp.dump"
$containerPath = "/tmp/$Database-$timestamp.dump"

docker exec $ContainerName pg_dump -U $User -d $Database -Fc -f $containerPath
docker cp "$ContainerName`:$containerPath" $backupPath
docker exec $ContainerName rm -f $containerPath | Out-Null

Write-Host "Backup written to $backupPath"
