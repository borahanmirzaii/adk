# n8n Workflows

This directory contains n8n workflow definitions for automation.

## Database Backup Workflow

The `backup_workflow.json` workflow automates daily database backups:

1. **Cron Trigger**: Runs daily at 2:00 AM
2. **Execute Backup**: Runs the backup script
3. **Check Success**: Validates backup completion
4. **Upload to Storage**: Uploads backup to Supabase Storage (if configured)
5. **Notifications**: Sends success/error notifications via Telegram (if configured)

### Setup

1. Import the workflow into n8n:
   - Open n8n UI (http://localhost:5678)
   - Go to Workflows > Import from File
   - Select `backup_workflow.json`

2. Configure credentials:
   - **Supabase API**: Add your Supabase service key
   - **Telegram API** (optional): Add Telegram bot token and chat ID

3. Configure environment variables:
   - `BACKUP_DIR`: Directory for backups (default: ./backups)
   - `RETENTION_DAYS`: Days to keep backups (default: 7)
   - `SUPABASE_STORAGE_BUCKET`: Supabase storage bucket name
   - `TELEGRAM_CHAT_ID`: Telegram chat ID for notifications

4. Activate the workflow in n8n

### Manual Backup

You can also run backups manually:

```bash
./scripts/backup_database.sh
```

### Restore from Backup

To restore a backup:

```bash
./scripts/restore_database.sh ./backups/backup_20240101_120000.sql.gz
```

**Warning**: This will overwrite the current database!

