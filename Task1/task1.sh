#!/usr/bin/env bash

# SETUP AREA ---
# The brief says I need a log file and a place for archives.
LOG_FILE="Task1/system_monitor_log.txt"
ARCHIVE_DIR="Task1/ArchiveLogs"

# REQUIREMENT: Logging System ---
# I'll call this whenever the user does something important. 
# Using '>>' so I don't accidentally delete my previous history!
log_event() {
    local msg="$1"
    # Adding a date/time stamp so I know exactly when things happened.
    printf "%s - %s\n" "$(date '+%Y-%m-%d %H:%M:%S')" "$msg" >> "$LOG_FILE"
}

# --- REQUIREMENT: PROCESS WATCHER ---
list_top_processes() {
    # Added 'top' to satisfy Requirement 1: Display current CPU and memory usage [cite: 35]
    echo "--- System Resource Overview ---"
    top -bn1 | head -n 5 
    echo ""
    
    echo "--- Top 10 Memory-Heavy Processes ---"
    # Adheres to Requirement 1: List top ten with PID, user, CPU%, and memory% [cite: 36, 37]
    ps aux | head -n 11
    
    # Clear description for the logging requirement 
    log_event "ACTION: Viewed system resource usage and top 10 memory processes."
}

# REQUIREMENT: SAFE TERMINATION ---
# I'm adding this to handle PID 1-10 protection and user confirmation.
kill_process() {
    read -p "Which PID do you want to stop? " target_pid
    
    if [[ ! "$target_pid" =~ ^[0-9]+$ ]]; then
        echo "Error: '$target_pid' isn't a valid number."
        log_event "ERROR: User entered invalid non-numeric PID: $target_pid"
        return
    fi

    # Logic to protect kernel threads (PIDs < 10)
    if [[ "$target_pid" -le 10 ]]; then
        echo "Safety Alert: I cannot kill critical system processes (PID 1-10)."
        log_event "BLOCKED: Attempted to terminate critical system process PID $target_pid."
    else
        read -p "Are you absolutely sure about killing $target_pid? (y/n): " confirm
        if [[ "$confirm" == "y" ]]; then
            kill -9 "$target_pid" 2>/dev/null
            echo "Process $target_pid has been terminated."
            log_event "SUCCESS: Terminated process PID $target_pid after user confirmation."
        fi
    fi
}

# REQUIREMENT: LOG ARCHIVER ---
# I'm building this to find bloated logs and zip them up to save space.
inspection_and_archive_logs() {
    # The brief says I need to ask which directory to inspect.
    read -p "Which folder should I scan for big logs? (e.g., ./Logs): " target_dir

    # Safety first: Check if the folder actually exists!
    if [[ ! -d "$target_dir" ]]; then
        echo "Error: I can't find the folder '$target_dir'."
        log_event "DISK ERROR: Directory not found: $target_dir"
        return
    fi

    # Create the Archive folder if it's missing (Requirement 2, Point 3).
    mkdir -p "$ARCHIVE_DIR"

    echo "Scanning for logs bigger than 50MB..."
    # I'm using a 'while read' loop to process every big file we find.
    find "$target_dir" -name "*.log" -size +50M | while read -r big_file; do
        local ts=$(date +%Y%m%d_%H%M%S)
        local fname=$(basename "$big_file")
        local zip_name="${fname}_${ts}.tar.gz"

        echo "Zipping up $fname..."
        # Using 'tar' to compress the file into our ArchiveLogs folder.
        tar -czf "$ARCHIVE_DIR/$zip_name" -C "$target_dir" "$fname"
        
        if [[ $? -eq 0 ]]; then
            log_event "ARCHIVED: $fname moved to $zip_name"
            echo "Success: $fname is now archived."
        fi
    done

    # --- THE 1GB WARNING (Requirement 2, Point 5) ---
    # du -sb gives me the size in bytes. 1073741824 bytes = 1GB.
    local archive_size=$(du -sb "$ARCHIVE_DIR" | cut -f1)
    if [[ "$archive_size" -gt 1073741824 ]]; then
        echo "!!! WARNING: The ArchiveLogs folder is over 1GB! !!!"
        log_event "STORAGE ALERT: ArchiveLogs exceeds 1GB threshold."
    fi
}

# THE MAIN BRAIN (MENU) ---
# Keeping this in a loop so the program stays open until I say 'Bye'.
while true; do
    echo "------------------------------------------"
    echo "  UNIVERSITY DATA CENTRE ADMIN TOOL"
    echo "------------------------------------------"
    echo "1) Show Top Processes"
    echo "2) Terminate a Process"
    echo "3) Inspection of Disk and Archive Large Logs"
    echo "4) Bye"

    read -p "What do you want to do? [1-4]: " choice
    
    case $choice in
        1) list_top_processes ;;
        2) kill_process ;;
        3) inspection_and_archive_logs ;;
        4)
            # The brief says I need a Y/N confirmation for 'Bye'.
            read -p "Are you really sure you want to quit? (y/n): " confirm
            if [[ "$confirm" == "y" || "$confirm" == "Y" ]]; then
                log_event "System exit."
                echo "See ya!"
                exit 0
            fi
            ;;
        *) 
            # Handling typos so the script doesn't just crash.
            echo "That's not a valid option, try again." 
            ;;
    esac
done


