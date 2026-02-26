#!/bin/bash

################################
# Main Setup Variables begin
program_name="$(basename "${0%.*}")"
shell="bash"

# Environment variables
shell_path="$BKDS_UTIL_SHELL"
data_path="$BKDS_UTIL_DATA/config"

# Variables
USERNAME="bkdsdev"
HOST="localhost"
PORT="5432"
SOURCE_DB="bkds"
TARGET_DB="bkds_prod"
DUMP_DIR="$data_path/dumps"
OBJECTS_FILE="$data_path/db_dump_restore.txt"

# Ensure the dump directory exists
mkdir -p "$DUMP_DIR"

# PostgreSQL password
export PGPASSWORD="hello"  # Replace with your actual password or use .pgpass for security

# Check if the target database exists
DB_CHECK=$(psql -U "$USERNAME" -h "$HOST" -p "$PORT" -lqt | cut -d \| -f 1 | grep -w "$TARGET_DB" | wc -l)
if [[ "$DB_CHECK" -eq 0 ]]; then
    echo "Target database $TARGET_DB does not exist. Creating it..."
    createdb -U "$USERNAME" -h "$HOST" -p "$PORT" "$TARGET_DB"
    if [[ $? -ne 0 ]]; then
        echo "Error: Failed to create target database $TARGET_DB"
        exit 1
    fi
else
    echo "Target database $TARGET_DB already exists."
fi

# Ensure necessary schemas exist in the target database
echo "Ensuring necessary schemas exist in $TARGET_DB..."
SCHEMAS=("dev" "wh")  # List of schemas you expect
for schema in "${SCHEMAS[@]}"; do
    SCHEMA_CHECK=$(psql -U "$USERNAME" -h "$HOST" -p "$PORT" -d "$TARGET_DB" -tAc "SELECT 1 FROM pg_namespace WHERE nspname = '$schema';")
    if [[ "$SCHEMA_CHECK" != "1" ]]; then
        echo "Schema $schema does not exist in $TARGET_DB. Creating it..."
        psql -U "$USERNAME" -h "$HOST" -p "$PORT" -d "$TARGET_DB" -c "CREATE SCHEMA $schema;"
        if [[ $? -ne 0 ]]; then
            echo "Error: Failed to create schema $schema in $TARGET_DB"
            exit 1
        fi
    else
        echo "Schema $schema already exists in $TARGET_DB."
    fi
done

# Dump and restore each object individually based on OBJECTS_FILE
while IFS= read -r line || [[ -n "$line" ]]; do
    # Remove leading/trailing whitespace
    line=$(echo "$line" | xargs)
    # Skip empty lines and lines starting with a comment character
    if [[ -n "$line" && ! "$line" =~ ^# ]]; then
        echo "Processing object: $line"

        # Extract schema and object name
        SCHEMA_NAME=$(echo "$line" | cut -d '.' -f1)
        OBJECT_NAME=$(echo "$line" | cut -d '.' -f2)

        # Determine object type (table or view)
        OBJECT_TYPE=$(psql -U "$USERNAME" -h "$HOST" -p "$PORT" -d "$SOURCE_DB" -tAc "
            SELECT CASE 
                WHEN EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_schema = '$SCHEMA_NAME' AND table_name = '$OBJECT_NAME' AND table_type = 'BASE TABLE'
                ) THEN 'TABLE'
                WHEN EXISTS (
                    SELECT 1 FROM information_schema.views 
                    WHERE table_schema = '$SCHEMA_NAME' AND table_name = '$OBJECT_NAME'
                ) THEN 'VIEW'
                ELSE 'UNKNOWN'
            END;
        ")

        if [[ "$OBJECT_TYPE" == "TABLE" ]]; then
            # Check if table exists in target DB
            TABLE_EXISTS=$(psql -U "$USERNAME" -h "$HOST" -p "$PORT" -d "$TARGET_DB" -tAc "
                SELECT 1 FROM information_schema.tables 
                WHERE table_schema = '$SCHEMA_NAME' AND table_name = '$OBJECT_NAME' AND table_type = 'BASE TABLE';
            ")
            if [[ "$TABLE_EXISTS" == "1" ]]; then
                # Check if table has more than 100 records
                RECORD_COUNT=$(psql -U "$USERNAME" -h "$HOST" -p "$PORT" -d "$TARGET_DB" -tAc "
                    SELECT COUNT(*) FROM \"$SCHEMA_NAME\".\"$OBJECT_NAME\";
                ")
                if [[ "$RECORD_COUNT" -gt 100 ]]; then
                    echo "Table $line exists in $TARGET_DB with $RECORD_COUNT records. Skipping restore."
                    continue
                else
                    echo "Table $line exists in $TARGET_DB but has less than or equal to 100 records. Proceeding to restore."
                fi
            else
                echo "Table $line does not exist in $TARGET_DB. Proceeding to restore."
            fi
        elif [[ "$OBJECT_TYPE" == "VIEW" ]]; then
            # Check if view exists in target DB
            VIEW_EXISTS=$(psql -U "$USERNAME" -h "$HOST" -p "$PORT" -d "$TARGET_DB" -tAc "
                SELECT 1 FROM information_schema.views 
                WHERE table_schema = '$SCHEMA_NAME' AND table_name = '$OBJECT_NAME';
            ")
            if [[ "$VIEW_EXISTS" == "1" ]]; then
                echo "View $line exists in $TARGET_DB. Skipping restore."
                continue
            else
                echo "View $line does not exist in $TARGET_DB. Proceeding to restore."
            fi
        else
            echo "Could not determine object type for $line. Skipping."
            continue
        fi

        echo "Dumping object: $line"
        DUMP_FILE="$DUMP_DIR/${line//./_}.dump"
        
        # Create a dump for the specific object
        pg_dump -U "$USERNAME" -h "$HOST" -p "$PORT" -d "$SOURCE_DB" \
        -F c -b -v -f "$DUMP_FILE" -t "$line"
        
        # Check if pg_dump succeeded
        if [[ $? -ne 0 ]]; then
            echo "Warning: pg_dump failed for $line. Skipping."
            continue
        fi
        
        # Restore the dump into the target database
        echo "Restoring object: $line to target database..."
        pg_restore -U "$USERNAME" -h "$HOST" -p "$PORT" -d "$TARGET_DB" -v "$DUMP_FILE" --no-owner --no-acl
        
        # Check if pg_restore succeeded
        if [[ $? -ne 0 ]]; then
            echo "Warning: pg_restore failed for $line. Skipping."
            continue
        fi
    fi
done < "$OBJECTS_FILE"

echo "Selective backup and restore completed successfully."
