# Backup and Restore

## Purpose

Phase 3 adds a simple local PostgreSQL backup and restore procedure for OpsForge. It demonstrates how project data can be exported, checked, and restored without installing PostgreSQL tools on the host.

## Prerequisites

- Run commands from the repository root in PowerShell.
- Docker and Docker Compose must be available.
- The Compose database service must be running and healthy.

Start the local environment if needed:

```powershell
docker compose up -d
```

## Create a Backup

Run:

```powershell
.\scripts\backup.ps1
```

The script:

1. reads the database name and user from the running `db` service;
2. runs `pg_dump` in PostgreSQL custom format inside the database container;
3. copies the archive to the host with `docker compose cp`;
4. removes the temporary archive from the container;
5. confirms that the local backup is not empty.

Backups are stored in `backups/` with names such as:

```text
opsforge_backup_YYYYMMDD_HHMMSS.dump
```

## Verify a Restore Safely

The default restore mode avoids changing the main OpsForge database. Run:

```powershell
.\scripts\restore.ps1 -BackupFile .\backups\opsforge_backup_YYYYMMDD_HHMMSS.dump
```

The script first checks the archive with `pg_restore --list`. It then creates a temporary database named `opsforge_restore_verify`, restores the archive, confirms that public tables exist, and removes the temporary database.

This verification is local only and is not part of GitHub Actions.

## Restore the Main Database

Only use a main-database restore after verifying the archive and deciding that replacing the current local database objects is intended:

```powershell
.\scripts\restore.ps1 `
    -BackupFile .\backups\opsforge_backup_YYYYMMDD_HHMMSS.dump `
    -MainDatabase
```

The script displays the target database and requires the exact confirmation `RESTORE`. It then stops the API service, runs `pg_restore --clean --if-exists`, and starts the API service again.

Main-database restore is destructive because existing database objects can be replaced. The temporary verification mode should always be used first.

## Why Custom `.dump` Format Is Used

PostgreSQL custom format is designed for `pg_restore`, supports archive inspection, and provides a controlled restore process. The archive is created inside the container and copied to the host so PowerShell does not redirect binary dump data.

## Git and Secret Safety

Generated backups are runtime artifacts and may contain application data. The `backups/` contents are ignored by Git except for `backups/README.md`.

Never commit:

- generated `.dump` files;
- `.env`;
- database passwords or other secrets.

## Limitations

The Phase 3 procedure intentionally has:

- no backup encryption;
- no offsite or cloud storage;
- no automatic schedule;
- no automatic retention or rotation;
- no CI backup or restore test.

These limits are acceptable for the current local RNCP educational scope but are not a production backup strategy.
