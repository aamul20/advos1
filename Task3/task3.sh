#!/bin/bash
# Bash Submission Tool


DATA="Task3/submissions_data.txt"
LOG="Task3/submission_log.txt"
mkdir -p Task3 && touch "$DATA" "$LOG"

#lockout tracking
FAIL_COUNT=0
LAST_ATTEMPT=0

#while loop for the menu system, will keep running until user chooses to exit 
#by using Option 5 and confirming with 'y'.
while true; do
    echo -e "\n--- BASH SECURE SYSTEM ---\n1. Submit something \n2. Check File here\n3. List All and everything\n4. Try Logining\n5. Bye"
    read -p "Option: " choice

    case $choice in
    
        1) 
         # File Validation & Duplicates
            read -p "Student ID: " sid
            read -p "File Path: " path
            [ ! -f "$path" ] && echo "File not found" && continue
            
            # Simple extension and size check (5MB)
            if [[ "$path" == *.pdf || "$path" == *.docx ]] && [ $(wc -c < "$path") -le 5242880 ]; then
                FNAME=$(basename "$path")
                F_HASH=$(sha256sum "$path" | cut -d' ' -f1)
                
                #this checks for duplicates
                if grep -q "$FNAME" "$DATA" || grep -q "$F_HASH" "$DATA"; then
                    echo "Duplicate detected!"
                else
                    echo "$sid,$FNAME,$F_HASH" >> "$DATA"
                    echo "[$sid] Submitted $FNAME" >> "$LOG"
                    echo "Success."
                fi
            else
                echo "Rejected: Invalid format or > 5MB" #message of rejection
            fi ;;
            
        2)  
        # Check if the file exists and gives message of found or not found
            read -p "Filename: " target
            grep -q "$target" "$DATA" && echo "Found the file!!!!" || echo "Could NOT find the file" ;;
            
        3)  
        #  List all the files with their id and filename
            echo "ID | Filename"
            cut -d',' -f1,2 "$DATA" | tr ',' '|' ;;
            
        4)  
        #  Deals with Login and also looks for Suspicious Activity
            [ $FAIL_COUNT -ge 3 ] && echo "LOCKED" && continue
            read -p "User ID: " sid
            read -p "Password: " pwd; 
            echo ""
            
            NOW=$(date +%s)
            # Detect rapid attempts within 60s
            [ $((NOW - LAST_ATTEMPT)) -lt 60 ] && echo "Suspicious rapid activity!"
            LAST_ATTEMPT=$NOW
            
            if [ "$pwd" == "Pass" ]; then
                echo "The password was correct.Welcome "; FAIL_COUNT=0
            else
                FAIL_COUNT=$((FAIL_COUNT + 1))
                echo "Failed. It didnt work. Strikes: $FAIL_COUNT"
                echo "[$(date)] Login Fail: $sid" >> "$LOG"
            fi ;;
            
        5)  
        # Bye with confirmation
            read -p "Exit (y/n)? " cf
            [[ "$cf" == "y" ]] && break ;;
    esac
done