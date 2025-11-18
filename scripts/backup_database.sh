#!/bin/bash
# Database backup script for Supabase PostgreSQL

set -e

# Configuration
BACKUP_DIR="${BACKUP_DIR:-./backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/backup_${TIMESTAMP}.sql"
RETENTION_DAYS="${RETENTION_DAYS:-7}"

# Database connection (from environment or defaults)
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-54322}"
DB_NAME="${DB_NAME:-postgres}"
DB_USER="${DB_USER:-postgres}"
DB_PASSWORD="${DB_PASSWORD:-postgres}"

# Create backup directory if it doesn't exist
mkdir -p "${BACKUP_DIR}"

echo "Starting database backup..."
echo "Database: ${DB_NAME}@${DB_HOST}:${DB_PORT}"
echo "Backup file: ${BACKUP_FILE}"

# Set PGPASSWORD environment variable for non-interactive backup
export PGPASSWORD="${DB_PASSWORD}"

# Perform backup using pg_dump
pg_dump \
    -h "${DB_HOST}" \
    -p "${DB_PORT}" \
    -U "${DB_USER}" \
    -d "${DB_NAME}" \
    -F c \
    -f "${BACKUP_FILE}" \
    --verbose

# Unset PGPASSWORD
unset PGPASSWORD

# Compress backup
if command -v gzip &> /dev/null; then
    echo "Compressing backup..."
    gzip "${BACKUP_FILE}"
    BACKUP_FILE="${BACKUP_FILE}.gz"
fi

# Get backup size
BACKUP_SIZE=$(du -h "${BACKUP_FILE}" | cut -f1)
echo "Backup completed: ${BACKUP_FILE} (${BACKUP_SIZE})"

# Clean up old backups
if [ -n "${RETENTION_DAYS}" ]; then
    echo "Cleaning up backups older than ${RETENTION_DAYS} days..."
    find "${BACKUP_DIR}" -name "backup_*.sql*" -type f -mtime +${RETENTION_DAYS} -delete
    echo "Cleanup completed"
fi

# Upload to Supabase Storage if configured
if [ -n "${SUPABASE_STORAGE_BUCKET}" ] && [ -n "${SUPABASE_URL}" ] && [ -n "${SUPABASE_SERVICE_KEY}" ]; then
    echo "Uploading backup to Supabase Storage..."
    BACKUP_FILENAME=$(basename "${BACKUP_FILE}")
    
    # Use Supabase Storage API to upload
    curl -X POST \
        "${SUPABASE_URL}/storage/v1/object/${SUPABASE_STORAGE_BUCKET}/${BACKUP_FILENAME}" \
        -H "Authorization: Bearer ${SUPABASE_SERVICE_KEY}" \
        -H "Content-Type: application/octet-stream" \
        --data-binary "@${BACKUP_FILE}" \
        -o /dev/null
    
    if [ $? -eq 0 ]; then
        echo "Backup uploaded to Supabase Storage: ${SUPABASE_STORAGE_BUCKET}/${BACKUP_FILENAME}"
    else
        echo "Warning: Failed to upload backup to Supabase Storage"
    fi
fi

echo "Backup process completed successfully"
exit 0

