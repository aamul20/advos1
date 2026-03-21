#!/bin/bash
# --- University Secure Submission System ---
# I created this script to manage the OS-level environment for a secure file submission system, as required by Task 3.
# It handles directory setup, permission management, and then hands off control to the Python script that implements the core security logic.


echo "******************************************"
echo "  INITIALIZING SECURE SUBMISSION SYSTEM"
echo "******************************************"

# 1. Environment Check: Ensure the Submissions vault exists
# This prevents the Python script from failing due to missing paths.
if [ ! -d "Task3/Submissions" ]; then
    mkdir -p Task3/Submissions
    echo "[ADMIN] Created 'Submissions' directory for secure storage."
fi

# 2. Permission Security: Restricted access to logs
# Ensuring only the admin has read/write access to the sensitive logs.
touch Task3/submission_log.txt
chmod 600 Task3/submission_log.txt

# 3. Handover to Python
# Launching the core security logic for file validation and access control.
python3 Task3/secure_submission.py