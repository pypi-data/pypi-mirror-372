#!/bin/bash
#Main orchestration script that runs all enabled measurement tools
set -euo pipefail

# Set working paths relative to repo root
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
PY_DIR="$REPO_ROOT/collector"
DATA_DIR="$REPO_ROOT/Data"
CURRENTLY="$DATA_DIR/Currently"
HISTORY="$DATA_DIR/History"
ARCHIVE="$DATA_DIR/Archive"
LOG="$DATA_DIR/Logs/pipeline.log"

timestamp=$(date +"%Y-%m-%d %H:%M:%S")
archive_day=$(date +"%Y-%m-%d")
ARCHIVE_DAY_DIR="$ARCHIVE/$archive_day"

mkdir -p "$ARCHIVE_DAY_DIR"

if [ ! -f "$LOG" ]; then
    touch "$LOG"
    echo "[$timestamp] Pipeline log file created" >> "$LOG"
    echo "[$timestamp] Log location: $LOG" >> "$LOG"
    echo "[$timestamp] =================================" >> "$LOG"
fi

echo "[$timestamp] Starting pipeline..." >> "$LOG"

# Function to check if a command is enabled
is_command_enabled() {
    local cmd_name="$1"
    python3 -c "
import sys
sys.path.append('$PY_DIR')
try:
    import config
    enabled = config.PIPELINE_COMMANDS.get('$cmd_name', {}).get('enabled', True)  # Default True for backward compatibility
    sys.exit(0 if enabled else 1)
except:
    sys.exit(0)  # If no config, run everything (backward compatibility)
    "
}

# Function to get script name for a command
get_script_name() {
    local cmd_name="$1"
    local default_script="$2"
    python3 -c "
import sys
sys.path.append('$PY_DIR')
try:
    import config
    script = config.PIPELINE_COMMANDS.get('$cmd_name', {}).get('script', '$default_script')
    print(script)
except:
    print('$default_script')
    "
}


echo "[$timestamp] Executing enabled commands..." >> "$LOG"


if is_command_enabled "pathdiscovery"; then
    script=$(get_script_name "pathdiscovery" "pathdiscovery.py")
    echo "[$timestamp] Running pathdiscovery ($script)..." >> "$LOG"
    /usr/bin/python3 "$PY_DIR/$script" >> "$LOG"
else
    echo "[$timestamp] Skipping disabled command: pathdiscovery" >> "$LOG"
fi

if is_command_enabled "comparer"; then
    script=$(get_script_name "comparer" "comparer.py")
    echo "[$timestamp] Running comparer ($script)..." >> "$LOG"
    /usr/bin/python3 "$PY_DIR/$script" >> "$LOG"
else
    echo "[$timestamp] Skipping disabled command: comparer" >> "$LOG"
fi

if is_command_enabled "prober"; then
    script=$(get_script_name "prober" "prober.py")
    echo "[$timestamp] Running prober ($script)..." >> "$LOG"
    /usr/bin/python3 "$PY_DIR/$script" >> "$LOG"
else
    echo "[$timestamp] Skipping disabled command: prober" >> "$LOG"
fi

if is_command_enabled "mp-prober"; then
    script=$(get_script_name "mp-prober" "mp-prober.py")
    echo "[$timestamp] Running mp-prober ($script)..." >> "$LOG"
    /usr/bin/python3 "$PY_DIR/$script" >> "$LOG"
else
    echo "[$timestamp] Skipping disabled command: mp-prober" >> "$LOG"
fi

if is_command_enabled "traceroute"; then
    scrip=$(get_script_name "traceroute" "traceroute.py")
    echo "[$timestamp] Running traceroute ($script)..." >> "$LOG"
    /usr/bin/python3 "$PY_DIR/$script" >> "$LOG"
else
    echo "[$timestamp] Skipping disabled command: traceroute" >> "$LOG"
fi

if is_command_enabled "bandwidth"; then
    script=$(get_script_name "bandwidth" "bandwidth.py")
    echo "[$timestamp] Running bandwidth ($script)..." >> "$LOG"
    /usr/bin/python3 "$PY_DIR/$script" >> "$LOG"
else
    echo "[$timestamp] Skipping disabled command: bandwidth" >> "$LOG"
fi

if is_command_enabled "mp-bandwidth"; then
    script=$(get_script_name "mp-bandwidth" "mp-bandwidth.py")
    echo "[$timestamp] Running mp-bandwidth ($script)..." >> "$LOG"
    /usr/bin/python3 "$PY_DIR/$script" >> "$LOG"
else
    echo "[$timestamp] Skipping disabled command: mp-bandwidth" >> "$LOG"
fi

# Step 2: Move files from all History/<Tool>/AS-* into Archive/<date>/
for tool_dir in "$HISTORY"/*/; do
  find "$tool_dir" -type f -name '*.json' -print -exec mv {} "$ARCHIVE_DAY_DIR"/ \;
done

# Step 3: Move current path files to the appropriate History subdirs
if compgen -G "$CURRENTLY/*.json" > /dev/null; then
  for pathfile in "$CURRENTLY"/*.json; do
    # Extract IA/AS identifier from filename (assuming name format e.g. "AS-1*.json")
    filename=$(basename "$pathfile")
    as_dir="${filename%%_*.json}"  # e.g., "AS-1"

    # Choose a destination (e.g., for pathdiscovery, change as needed)
    dest_dir="$HISTORY/Showpaths/$as_dir"
    mkdir -p "$dest_dir"
    mv "$pathfile" "$dest_dir/"
    echo "Moved $filename to $dest_dir" >> "$LOG"
  done
else
  echo "No current path files found in $CURRENTLY" >> "$LOG"
fi

end_ts=$(date +"%Y-%m-%d %H:%M:%S")
echo "[$end_ts] Pipeline complete." >> "$LOG"
echo "" >> "$LOG"