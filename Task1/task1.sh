#!/usr/bin/env bash

# --- SETUP AREA ---
# The brief says I need a log file and a place for archives.
LOG_FILE="system_monitor_log.txt"
ARCHIVE_DIR="ArchiveLogs"

# --- THE LOGGING ENGINE ---
# I'll call this whenever the user does something important. 
# Using '>>' so I don't accidentally delete my previous history!
log_event() {
    local msg="$1"
    # Adding a date/time stamp so I know exactly when things happened.
    printf "%s - %s\n" "$(date '+%Y-%m-%d %H:%M:%S')" "$msg" >> "$LOG_FILE"
}

# --- REQUIREMENT 1: PROCESS WATCHER ---
list_top_processes() {
    echo "--- Top 10 Memory-Heavy Processes ---"
    # I'm using 'head -n 11' because the 1st line 
    # is just labels (PID, USER, etc.). I need 10 rows of REAL data below it.
    ps -eo pid,user,pcpu,pmem --sort=-pmem | head -n 11
    
    log_event "User checked the process list."
}

# --- THE MAIN BRAIN (MENU) ---
# Keeping this in a loop so the program stays open until I say 'Bye'.
while true; do
    echo "------------------------------------------"
    echo "  UNIVERSITY DATA CENTRE ADMIN TOOL"
    echo "------------------------------------------"
    echo "1) Show Top Processes"
    echo "2) Bye"
    
    read -p "What do you want to do? [1-2]: " choice
    
    case $choice in
        1) 
            list_top_processes 
            ;;
        2) 
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