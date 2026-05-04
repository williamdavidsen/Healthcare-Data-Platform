param(
    [Parameter(Mandatory = $true)]
    [string]$BackupPath,
    [string]$ContainerName = "healthcare_postgres",
    [string]$Database = "healthcare",
    [string]$User = "healthcare"
)

$ErrorActionPreference = "Stop"

$resolvedBackup = Resolve-Path -LiteralPath $BackupPath
$containerPath = "/tmp/restore-healthcare.dump"

docker cp $resolvedBackup "$ContainerName`:$containerPath"
docker exec $ContainerName pg_restore --clean --if-exists -U $User -d $Database $containerPath
docker exec $ContainerName rm -f $containerPath | Out-Null

Write-Host "Database restored from $resolvedBackup"
