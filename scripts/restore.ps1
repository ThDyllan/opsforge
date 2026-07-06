param(
    [Parameter(Position = 0)]
    [string]$BackupFile,

    [switch]$MainDatabase
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($BackupFile)) {
    throw "Provide a backup file: .\scripts\restore.ps1 -BackupFile .\backups\opsforge_backup_YYYYMMDD_HHMMSS.dump"
}

if (-not (Test-Path -LiteralPath $BackupFile -PathType Leaf)) {
    throw "Backup file not found: $BackupFile"
}

$backupPath = (Resolve-Path -LiteralPath $BackupFile).Path
if ((Get-Item -LiteralPath $backupPath).Length -eq 0) {
    throw "The backup file is empty."
}

$dbService = "db"
$apiService = "api"
$verificationDatabase = "opsforge_restore_verify"
$containerBackupPath = "/tmp/opsforge_restore.dump"
$verificationDatabaseCreated = $false
$apiStopped = $false

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

if ($MainDatabase) {
    $confirmation = Read-Host "This will replace objects in database '$dbName'. Type RESTORE to continue"
    if ($confirmation -cne "RESTORE") {
        Write-Host "Restore cancelled."
        return
    }
}

docker compose cp $backupPath "${dbService}:$containerBackupPath"
if ($LASTEXITCODE -ne 0) {
    throw "Could not copy the backup into the database container."
}

try {
    docker compose exec -T $dbService pg_restore --list $containerBackupPath | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "The backup is not a valid pg_restore archive."
    }

    if ($MainDatabase) {
        docker compose stop $apiService
        if ($LASTEXITCODE -ne 0) {
            throw "Could not stop the API service before restore."
        }
        $apiStopped = $true

        docker compose exec -T $dbService pg_restore `
            "--username=$dbUser" `
            "--dbname=$dbName" `
            --clean `
            --if-exists `
            --no-owner `
            --no-privileges `
            --exit-on-error `
            $containerBackupPath

        if ($LASTEXITCODE -ne 0) {
            throw "Restore into the main database failed."
        }

        Write-Host "Main database restore completed."
    }
    else {
        docker compose exec -T $dbService dropdb `
            "--username=$dbUser" `
            --if-exists `
            $verificationDatabase
        if ($LASTEXITCODE -ne 0) {
            throw "Could not prepare the temporary verification database."
        }

        docker compose exec -T $dbService createdb `
            "--username=$dbUser" `
            $verificationDatabase
        if ($LASTEXITCODE -ne 0) {
            throw "Could not create the temporary verification database."
        }
        $verificationDatabaseCreated = $true

        docker compose exec -T $dbService pg_restore `
            "--username=$dbUser" `
            "--dbname=$verificationDatabase" `
            --no-owner `
            --no-privileges `
            --exit-on-error `
            $containerBackupPath
        if ($LASTEXITCODE -ne 0) {
            throw "Restore verification failed."
        }

        $tableCountOutput = docker compose exec -T $dbService psql `
            "--username=$dbUser" `
            "--dbname=$verificationDatabase" `
            --tuples-only `
            --no-align `
            --command="SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';"
        if ($LASTEXITCODE -ne 0) {
            throw "Could not inspect the restored database."
        }

        $tableCount = [int]([string]$tableCountOutput).Trim()
        if ($tableCount -lt 1) {
            throw "Restore verification found no public tables."
        }

        Write-Host "Restore verified in temporary database '$verificationDatabase' ($tableCount public tables)."
    }
}
finally {
    if ($verificationDatabaseCreated) {
        docker compose exec -T $dbService dropdb `
            "--username=$dbUser" `
            --if-exists `
            $verificationDatabase | Out-Null
    }

    if ($apiStopped) {
        docker compose start $apiService | Out-Null
    }

    docker compose exec -T $dbService rm -f $containerBackupPath | Out-Null
}
