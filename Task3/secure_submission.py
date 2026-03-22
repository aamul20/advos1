import os
import hashlib
import time
from datetime import datetime

# Administrative Settings
SECURITY_LOG = "Task3/submission_log.txt"
COLLECTION_DATA = "Task3/submissions_data.txt" 
MAX_BYTES = 5 * 1024 * 1024  # 5MB limit 

#  Live Security Tracking 
# Concept of Dictionaries are used here
lockout_strikes = {}     
access_timestamps = {}   

def setup_files():
    #We have to ensure our tracking files exist before we start.
    os.makedirs("Task3", exist_ok=True)
    if not os.path.exists(SECURITY_LOG): open(SECURITY_LOG, 'w').close()
    if not os.path.exists(COLLECTION_DATA): open(COLLECTION_DATA, 'w').close()

def get_file_hash(path):
    #Generates a fingerprint to detect identical content. 
    sha = hashlib.sha256()
    with open(path, 'rb') as f:
        while chunk := f.read(4096):
            sha.update(chunk)
    return sha.hexdigest()

def record_activity(std_id, resource, info):
    #This is the Logging System, uses datetime for timestamps.
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(SECURITY_LOG, "a") as f:
        f.write(f"[{timestamp}] ID: {std_id} | Resource: {resource} | Note: {info}\n")


def upload_assignment():
    #File Validation & Duplicate Detection.
    print("\n--- Assignment Upload Portal ---")
    sid = input("Student ID: ")
    filepath = input("File Path: ")

    if not os.path.exists(filepath):
        print("Error: File not found.")
        return

    # Validation: Format and Size 
    fname = os.path.basename(filepath)
    ext = os.path.splitext(fname)[1].lower()
    if ext not in ['.pdf', '.docx'] or os.path.getsize(filepath) > MAX_BYTES:
        print("Rejected: Invalid format or file exceeds 5MB.")
        record_activity(sid, fname, "REJECTED_VALIDATION")
        return

    # Check for identical name or content 
    file_hash = get_file_hash(filepath)
    if os.path.exists(COLLECTION_DATA):
        with open(COLLECTION_DATA, "r") as f:
            for line in f:
                if fname in line or file_hash in line:
                    print("Rejected: This file or content was already submitted.DUPLICARTE_REJECTED")
                    record_activity(sid, fname, "DUPLICATE_REJECTED")
                    return

    with open(COLLECTION_DATA, "a") as f:
        f.write(f"{sid},{fname},{file_hash}\n")
    
    print(f"SUCCESSful!!! '{fname}' is now in the vault.")
    record_activity(sid, fname, "SUBMISSION_SUCCESS")

def check_history(single_search=True):
    #Requirement: Check if submitted OR List all assignments.
    if not os.path.exists(COLLECTION_DATA) or os.stat(COLLECTION_DATA).st_size == 0:
        print("The vault is currently empty. Theres nothing")
        return

    if single_search:
        target = input("Enter filename to check: ")
        found = False
        with open(COLLECTION_DATA, "r") as f:
            for line in f:
                if target in line:
                    print(f"Match: {target} was submitted.")
                    found = True
                    break
        if not found: print("Sorry, Sorry, No record found.")
    else:
        print(f"\n{'ID':<15} {'Filename'}")
        with open(COLLECTION_DATA, "r") as f:
            for line in f:
                p = line.strip().split(',')
                print(f"{p[0]:<15} {p[1]}")

def login_simulation():
    #Requirement: Access Control & Suspicious Activity.
    print("\n--- $$ Access Control Login $$ ---")
    sid = input("Student ID: ")
    
    if lockout_strikes.get(sid, 0) >= 3:
        print("ACCOUNT LOCKED: 3 failed attempts.") 
        record_activity(sid, "LOGIN", "LOCKED_OUT")
        return

    pwd = input("Password: ")
    now = time.time()

    # Detects repeated login attempts within 60 seconds.
    if sid not in access_timestamps: access_timestamps[sid] = []
    access_timestamps[sid].append(now)
    recent = [t for t in access_timestamps[sid] if now - t <= 60]
    
    if len(recent) >= 2:
        print("Warning: Suspicious login speed detected.")
        record_activity(sid, "LOGIN", "SUSPICIOUS_PATTERN")

    if pwd == "Pass":
        print("Login Successful.")
        lockout_strikes[sid] = 0
    else:
        lockout_strikes[sid] = lockout_strikes.get(sid, 0) + 1
        print(f"Failed. {3 - lockout_strikes[sid]} attempts left.")
        record_activity(sid, "LOGIN", "FAILED_ATTEMPT")

def menu():
    #Requirement: Menu System and Exit Confirmation.
    while True:
        print("\n" + "$"*40)
        print("   SECURE SUBMISSION ADMIN TOOL")
        print("$"*40)
        print("1. Submit Assignment")
        print("2. Check for Specific Submission")
        print("3. List All Submissions")
        print("4. Login Simulation")
        print("5. Bye (Exit)")
        
        choice = input("Option [1-5]: ")
        
        if choice == '1': upload_assignment()
        elif choice == '2': check_history(single_search=True)
        elif choice == '3': check_history(single_search=False)
        elif choice == '4': login_simulation()
        elif choice == '5':
            if input("Confirm exit (Bye)? (y/n): ").lower() == 'y': 
                break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    menu()