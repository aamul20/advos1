import time
import os
from datetime import datetime

# --- System Config & Paths ---
# I'm keeping these in the Task2 folder to stay organized.
QUEUE_FILE = "Task2/job_queue.txt"
COMPLETED_FILE = "Task2/completed_jobs.txt"
LOG_FILE = "Task2/scheduler_log.txt"

def log_scheduler_event(student_id, job_name, event_type):
    """
    Requirement 3: Keeping a history of everything that happens.
    Brief says I need: ID, Name, Scheduling Type, and Timestamp.
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        # 'RR' stands for Round Robin so the log is clear.
        f.write(f"[{now}] ID:{student_id} | Job:{job_name} | Event:{event_type} | Mode:RR\n")

def load_jobs():
    """Helper to pull jobs from the text file into Python memory."""
    jobs = []
    if not os.path.exists(QUEUE_FILE):
        return jobs
    with open(QUEUE_FILE, "r") as f:
        for line in f:
            parts = line.strip().split(',')
            if len(parts) == 4:
                jobs.append({
                    "student_id": parts[0],
                    "name": parts[1],
                    "time_left": int(parts[2]),
                    "priority": int(parts[3])
                })
    return jobs

def save_queue(jobs):
    """
    Updating the live state of job_queue.txt so we don't lose progress if it crashes.
    This fulfills the 'Data Storage' requirement for pending jobs.
    """
    with open(QUEUE_FILE, "w") as live_file:
        for job in jobs:
            live_file.write(f"{job['student_id']},{job['name']},{job['time_left']},{job['priority']}\n")

def save_completed_job(job):
    """
    Requirement 4: Move finished jobs to the completed storage.
    We change the 'time' field to 'Completed' for the final record.
    """
    with open(COMPLETED_FILE, "a") as finished_file:
        finished_file.write(f"{job['student_id']},{job['name']},Completed,{job['priority']}\n")

def submit_job():
    """Requirement 1 & 2: Letting users add their own jobs."""
    print("\n--- JOB SUBMISSION PORTAL ---")
    stdid = input("Student ID: ")
    name = input("Job Name (e.g. PhysicsSim): ")
    try:
        duration = int(input("How many seconds will this take? "))
        priority = int(input("Priority (1=Low, 10=High): "))
        
        # Validation for the 1-10 range mentioned in the brief.
        if 1 <= priority <= 10:
            with open(QUEUE_FILE, "a") as f:
                f.write(f"{stdid},{name},{duration},{priority}\n")
            print(f"Got it. '{name}' is now waiting in the queue.")
            log_scheduler_event(stdid, name, "SUBMISSION")
        else:
            print("Whoops! Priority needs to be between 1 and 10.")
    except ValueError:
        print("That's not a number! Please enter integers for time and priority.")

def view_jobs(filename, title):
    """Displays the contents of our data files in a readable table.

    This function is defensive: it skips blank lines, uses the csv
    module for safer splitting, strips whitespace from fields, and
    pads rows with missing columns so printing never raises an
    IndexError.
    """
    print(f"\n--- {title} ---")
    if not os.path.exists(filename) or os.stat(filename).st_size == 0:
        print("No records found.")
        return

    # Use consistent column widths (Pri given a small width for alignment)
    print(f"{'ID':<10} {'Job Name':<20} {'Time/Status':<15} {'Pri':<4}")
    import csv
    with open(filename, "r", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            # Skip empty rows
            if not row:
                continue
            # Trim whitespace from each column
            row = [col.strip() for col in row]
            # Ensure we have at least four fields to avoid IndexError
            while len(row) < 4:
                row.append("")
            print(f"{row[0]:<10} {row[1]:<20} {row[2]:<15} {row[3]:<4}")

def run_round_robin():
    """Requirement 2: The actual 'Round Robin' logic."""
    jobs = load_jobs()
    if not jobs:
        print("The queue is empty. Nothing to schedule right now.")
        return

    # Quantum set to 5 seconds as per the brief.
    quantum = 5
    print("\nStarting the scheduler... (Each job gets 5s slices)")
    
    while jobs:
        current = jobs.pop(0)
        print(f"\n[RUNNING] Student {current['student_id']}'s job: {current['name']}")
        
        # We simulate the work. I'm using 2s for a faster demo, 
        # but the logic still subtracts 5s of 'virtual' time.
        time.sleep(2) 

        if current['time_left'] > quantum:
            # This is NOT completed. It just loses 5 seconds.
            current['time_left'] -= quantum
            print(f"  ! Slice Expired. {current['name']} still has {current['time_left']}s left.")
            jobs.append(current) 
            # We do NOT call save_completed_job here.
            log_scheduler_event(current['student_id'], current['name'], "SLICE_EXPIRED")
        else:
            # This IS actually finished.
            print(f"  Job Finished!")
            current['time_left'] = 0 # Ensure it shows 0
            save_completed_job(current)
            log_scheduler_event(current['student_id'], current['name'], "EXECUTION_COMPLETE")
        
        save_queue(jobs) # Keeping the text file synced

def main_menu():
    """The main interface for managing the HPC system."""
    while True:
        print("\n========================================")
        print("     HPC JOB SCHEDULER SYSTEM")
        print("========================================")
        print("1. View Pending Jobs")
        print("2. Submit a Job Request")
        print("3. Run Round Robin Scheduler")
        print("4. View Completed Jobs")
        print("5. Exit")
        
        choice = input("Select an option [1-5]: ")
        
        if choice == '1': view_jobs(QUEUE_FILE, "PENDING QUEUE")
        elif choice == '2': submit_job()
        elif choice == '3': run_round_robin()
        elif choice == '4': view_jobs(COMPLETED_FILE, "COMPLETED JOBS")
        elif choice == '5':
            confirm = input("Are you sure you want to quit? (y/n): ")
            if confirm.lower() == 'y':
                print("Logging out. Goodbye!")
                break
        else:
            print("Invalid choice, try again.")

if __name__ == "__main__":
    main_menu()