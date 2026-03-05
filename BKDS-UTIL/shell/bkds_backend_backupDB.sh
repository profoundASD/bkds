#!/bin/bash

# Configuration
DB_NAME="xxxx"                # Database name
DB_USER="xxxx"             # Database username
DB_PASSWORD="xxxx"            # Database password
DB_HOST="localhost"           # Database host
BACKUP_DIR="path/to/backup_dir"   # Replace with your desired backup directory

# Timestamp for the backup file
TIMESTAMP=$(date +"%Y%m%d%H%M%S")

# Backup file name
BACKUP_FILE="${BACKUP_DIR}/${DB_NAME}_backup_${TIMESTAMP}.sql"

# Ensure backup directory exists
mkdir -p "${BACKUP_DIR}"

# Export the password to avoid prompt
export PGPASSWORD="${DB_PASSWORD}"

# Dump the database schema and data
pg_dump -U "${DB_USER}" -h "${DB_HOST}" -F c -b -v -f "${BACKUP_FILE}" "${DB_NAME}"

# Check if pg_dump was successful
if [ $? -eq 0 ]; then
  echo "Database dump successful: ${BACKUP_FILE}"

  # Compress the backup file
  gzip "${BACKUP_FILE}"

  # Check if gzip was successful
  if [ $? -eq 0 ]; then
    echo "Backup compressed: ${BACKUP_FILE}.gz"
  else
    echo "Failed to compress the backup file"
  fi
else
  echo "Database dump failed"
fi

# Unset the password after the operation
unset PGPASSWORD
