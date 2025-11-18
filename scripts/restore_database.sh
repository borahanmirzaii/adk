#!/bin/bash
# Database restore script for Supabase PostgreSQL

set -e

# Configuration
BACKUP_FILE="${1}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-54322}"
DB_NAME="${DB_NAME:-postgres}"
DB_USER="${DB_USER:-postgres}"
DB_PASSWORD="${DB_PASSWORD:-postgres}"

# Validate backup file
if [ -z "${BACKUP_FILE}" ]; then
    echo "Usage: $0 <backup_file>"
    echo "Example: $0 ./backups/backup_20240101_120000.sql.gz"
    exit 1
fi

if [ ! -f "${BACKUP_FILE}" ]; then
    echo "Error: Backup file not found: ${BACKUP_FILE}"
    exit 1
fi

echo "Starting database restore..."
echo "Database: ${DB_NAME}@${DB_HOST}:${DB_PORT}"
echo "Backup file: ${BACKUP_FILE}"

# Confirm restore
read -p "WARNING: This will overwrite the current database. Continue? (yes/no): " confirm
if [ "${confirm}" != "yes" ]; then
    echo "Restore cancelled"
    exit 0
fi

# Set PGPASSWORD environment variable
export PGPASSWORD="${DB_PASSWORD}"

# Check if backup is compressed
if [[ "${BACKUP_FILE}" == *.gz ]]; then
    echo "Decompressing backup..."
    TEMP_FILE=$(mktemp)
    gunzip -c "${BACKUP_FILE}" > "${TEMP_FILE}"
    BACKUP_FILE="${TEMP_FILE}"
    CLEANUP_TEMP=true
else
    CLEANUP_TEMP=false
fi

# Determine backup format
if file "${BACKUP_FILE}" | grep -q "PostgreSQL custom database dump"; then
    # Custom format backup
    echo "Restoring custom format backup..."
    pg_restore \
        -h "${DB_HOST}" \
        -p "${DB_PORT}" \
        -U "${DB_USER}" \
        -d "${DB_NAME}" \
        --clean \
        --if-exists \
        --verbose \
        "${BACKUP_FILE}"
else
    # SQL format backup
    echo "Restoring SQL format backup..."
    psql \
        -h "${DB_HOST}" \
        -p "${DB_PORT}" \
        -U "${DB_USER}" \
        -d "${DB_NAME}" \
        -f "${BACKUP_FILE}" \
        --verbose
fi

# Cleanup temp file if created
if [ "${CLEANUP_TEMP}" = true ]; then
    rm -f "${TEMP_FILE}"
fi

# Unset PGPASSWORD
unset PGPASSWORD

echo "Database restore completed successfully"
exit 0

