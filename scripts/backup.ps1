$ErrorActionPreference = "Stop"

$dbService = "db"
$backupDirectory = Join-Path (Get-Location) "backups"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$fileName = "opsforge_backup_$timestamp.dump"
$hostBackupPath = Join-Path $backupDirectory $fileName
$containerBackupPath = "/tmp/$fileName"

$dbUserOutput = docker compose exec -T $dbService printenv POSTGRES_USER
if ($LASTEXITCODE -ne 0) {
    throw "The Docker Compose database service '$dbService' is not available."
}

$dbNameOutput = docker compose exec -T $dbService printenv POSTGRES_DB
if ($LASTEXITCODE -ne 0) {
    throw "Could not read POSTGRES_DB from the database container."
}

$dbUser = ([string]$dbUserOutput).Trim()
$dbName = ([string]$dbNameOutput).Trim()

docker compose exec -T $dbService pg_isready "--username=$dbUser" "--dbname=$dbName" | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "PostgreSQL is not ready."
}

New-Item -ItemType Directory -Force -Path $backupDirectory | Out-Null

try {
    docker compose exec -T $dbService pg_dump `
        "--username=$dbUser" `
        "--dbname=$dbName" `
        --format=custom `
        --no-owner `
        --no-privileges `
        "--file=$containerBackupPath"

    if ($LASTEXITCODE -ne 0) {
        throw "pg_dump failed."
    }

    docker compose cp "${dbService}:$containerBackupPath" $hostBackupPath
    if ($LASTEXITCODE -ne 0) {
        throw "Could not copy the backup from the database container."
    }
}
finally {
    docker compose exec -T $dbService rm -f $containerBackupPath | Out-Null
}

$backupFile = Get-Item -LiteralPath $hostBackupPath
if ($backupFile.Length -eq 0) {
    throw "The backup file is empty."
}

Write-Host "Backup created: $hostBackupPath"
Write-Host "Size: $($backupFile.Length) bytes"
