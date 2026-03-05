#!/bin/bash

########################################################################
# BKDS Common Functions Library
#
# This script contains common functions used by various BKDS scripts.
# It includes functions for logging, locking, rate limiting, and UI dialogs.
#
########################################################################

# --- Global Variables (will be set by sourcing scripts) ---
: "${BKDS_UTIL_PYTHON:?BKDS_UTIL_PYTHON not set}"
: "${BKDS_UTIL_SHELL:?BKDS_UTIL_SHELL not set}"
: "${BKDS_UTIL_MP3:?BKDS_UTIL_MP3 not set}"
: "${BKDS_UTIL_DATA:?BKDS_UTIL_DATA not set}"
: "${BKDS_AUTO_SCHED_LOCKS:?BKDS_AUTO_SCHED_LOCKS not set}"

# --- Logging Function ---
log_msg() {
    local program_name="$1"
    local message="$2"  # Changed from $3 to $2
    local log_script="$BKDS_UTIL_PYTHON/bkds_LogMsg.py"
    python3 "$log_script" "$program_name" "" "$message" && echo "$message"  # Passing an empty string for batch_id
}

# --- Execution Lock ---
acquire_execution_lock() {
    local program_name="$1"
    local script_hash="$2"
    local lockout_limit_sec="${3:-15}" # Default to 15 seconds if not provided
    local execution_lock_file="$BKDS_AUTO_SCHED_LOCKS/${program_name}_execution.lock"

    log_msg "$program_name" "$0" "Acquiring execution lock: $execution_lock_file"
    if [[ -f "$execution_lock_file" ]]; then
        local lock_age=$(( $(date +%s) - $(stat -c %Y "$execution_lock_file") ))
        if [[ $lock_age -gt $lockout_limit_sec ]]; then
            log_msg "$program_name" "$0" "Lock file is older than $lockout_limit_sec seconds. Removing: $execution_lock_file"
            rm -f "$execution_lock_file"
        else
            log_msg "$program_name" "$0" "Another instance is running (lock file age: ${lock_age}s). Retrying..."
            for i in {1..3}; do
                sleep 5
                if [[ ! -f "$execution_lock_file" ]]; then
                    log_msg "$program_name" "$0" "Lock file removed. Proceeding..."
                    break
                elif [[ $i -eq 3 ]]; then
                    log_msg "$program_name" "$0" "Failed to acquire lock after multiple retries. Exiting."
                    exit 1
                fi
            done
        fi
    fi
    touch "$execution_lock_file" || { log_msg "$program_name" "$0" "Failed to create lock file. Exiting."; exit 1; }
}

release_execution_lock() {
    local program_name="$1"
    local execution_lock_file="$BKDS_AUTO_SCHED_LOCKS/${program_name}_execution.lock"

    if [[ -f "$execution_lock_file" ]]; then
        rm -f "$execution_lock_file"
        log_msg "$program_name" "$0" "Lock released: $execution_lock_file"
    fi
}

# --- Rate Limiting ---

# Function to calculate the next allowed run time
calculate_next_run() {
  local daily_limit="$1"
  local weekly_limit="$2"
  local weekly_days="$3"
  local daily_count="$4"
  local weekly_count="$5"
  local weekly_start="$6"

  local current_time=$(date +%s)
  local next_run=$current_time

  # If daily limit is exceeded, calculate next run time tomorrow at 8 AM
  if (( daily_count >= daily_limit )); then
    next_run=$(date -d "tomorrow 8 AM" +%s)
  fi

  # If weekly limit is exceeded, calculate next run time based on weekly_days at 8 AM
  if (( weekly_count >= weekly_limit )); then
    local days_until_reset=$((weekly_days - $(( (current_time - weekly_start) / 86400 )) ))
    local next_weekly_run=$(date -d "+$days_until_reset days 8 AM" +%s)
    if (( next_weekly_run > next_run )); then
      next_run=$next_weekly_run
    fi
  fi

  # Ensure the time is not before 8 AM or after 5 PM
  local next_run_hour=$(date -d "@$next_run" +%H)
  if (( 10#$next_run_hour < 8 )); then  # Force decimal interpretation
    next_run=$(date -d "@$next_run +8 hours" +%s)
  elif (( 10#$next_run_hour >= 17 )); then  # Force decimal interpretation
    next_run=$(date -d "@$next_run +1 day 8 hours" +%s)
  fi
  local next_run_formatted=$(date -d "@$next_run" "+%B %d at %I:%M %p")
  echo "$next_run_formatted"
}

check_rate_limit() {
  local program_name="$1"
  local rate_limit_file="$2"
  local lastrun_file="$3"
  local default_daily_limit="$4"
  local default_weekly_limit="$5"
  local default_weekly_days="$6"
  local ui_message_base="$7"
  local ui_message_trailer="$8"
  local ui_zenity_title="$9"
  local ui_zenity_timeout="${10}"
  local audio_gen_file_prefix="${11}"
  
  # Load rate limits from JSON file
  if [[ -f "$rate_limit_file" ]]; then
      daily_limit=$(jq -r ".daily_limit // $default_daily_limit" "$rate_limit_file")
      weekly_limit=$(jq -r ".weekly_limit // $default_weekly_limit" "$rate_limit_file")
      weekly_days=$(jq -r ".weekly_days // $default_weekly_days" "$rate_limit_file")
      log_msg "$program_name" "$0" "Loaded rate limits from config."
  else
      daily_limit=$default_daily_limit
      weekly_limit=$default_weekly_limit
      weekly_days=$default_weekly_days
      log_msg "$program_name" "$0" "Config file not found. Using defaults."
  fi

  current_time=$(date +%s)

  # Load last run data from .lastrun file
  if [[ -f "$lastrun_file" ]]; then
      # If the file exists, read the values
      last_run=$(jq '.last_run' "$lastrun_file")
      daily_count=$(jq '.daily_count' "$lastrun_file")
      weekly_count=$(jq '.weekly_count' "$lastrun_file")
      weekly_start=$(jq '.weekly_start' "$lastrun_file")
  else
      # If the file doesn't exist, initialize the values
      last_run=0
      daily_count=0
      weekly_count=0
      weekly_start=$current_time
      # Create the lastrun file
      mkdir -p "$(dirname "$lastrun_file")"
      cat > "$lastrun_file" <<EOF
{
"last_run": $last_run,
"daily_count": $daily_count,
"weekly_count": $weekly_count,
"weekly_start": $weekly_start
}
EOF
  fi

  # Check if it's a new day
  if [[ $((current_time - last_run)) -ge 86400 ]]; then
      daily_count=0
  fi

  # Check if it's a new week
  if [[ $((current_time - weekly_start)) -ge $((weekly_days * 86400)) ]]; then
      weekly_count=0
      weekly_start=$current_time
  fi

  # Increment counters
  daily_count=$((daily_count + 1))
  weekly_count=$((weekly_count + 1))

  # Check if rate limits are exceeded
  if [[ $daily_count -gt $daily_limit ]] || [[ $weekly_count -gt $weekly_limit ]]; then
      log_msg "$program_name" "$0" "Rate limit exceeded."
      next_run=$(calculate_next_run "$daily_limit" "$weekly_limit" "$weekly_days" "$daily_count" "$weekly_count" "$weekly_start")
      show_wait_dialog "$program_name" "$batch_id" "$next_run" "$ui_message_base" "$ui_message_trailer" "$ui_zenity_title" "$ui_zenity_timeout" "$audio_gen_file_prefix"
      exit 1
  fi

  # Update .lastrun file with new values in JSON format
  cat > "$lastrun_file" << EOF
{
"last_run": $current_time,
"daily_count": $daily_count,
"weekly_count": $weekly_count,
"weekly_start": $weekly_start
}
EOF
}

# --- UI Dialog ---
show_wait_dialog() {
    local program_name="$1"
    local batch_id="$2"
    local wait_time="$3"
    local ui_message_base="$4"
    local ui_message_trailer="$5"
    local ui_zenity_title="$6"
    local ui_zenity_timeout="${7}"
    local audio_gen_file_prefix="${8}"
    local audio_gen_script="$BKDS_UTIL_SHELL/bkds_AudioGen.sh"
    local message="$ui_message_base $wait_time $ui_message_trailer"

    # Check if DISPLAY is set and not empty
    if [[ -n "$DISPLAY" ]]; then
        zenity --info --timeout="$ui_zenity_timeout" --title="$ui_zenity_title" --text="$message" &
    else
        log_msg "$program_name" "$0" "No display available. Skipping Zenity dialog."
    fi

    "$audio_gen_script" "$batch_id" "$audio_gen_file_prefix" "$message"
}