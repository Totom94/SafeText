import os
import threading
import time
from datetime import datetime, timedelta

log_dir = 'message_logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)


def log_message(sender, message, recipient):
    # Ensures log files are named after each user and logs the direct exchange between users
    sender_filename = os.path.join(log_dir, f"{sender}_messages.txt")
    recipient_filename = os.path.join(log_dir, f"{recipient}_messages.txt")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{timestamp} - From: {sender} To: {recipient} - {message}\n"

    # Log to sender's file
    with open(sender_filename, 'a') as sender_file:
        sender_file.write(log_entry)

    # Log to recipient's file
    with open(recipient_filename, 'a') as recipient_file:
        recipient_file.write(log_entry)


def delete_old_logs():
    while True:
        now = datetime.now()
        for filename in os.listdir(log_dir):
            filepath = os.path.join(log_dir, filename)
            file_creation_time = datetime.fromtimestamp(os.path.getctime(filepath))
            if now - file_creation_time > timedelta(hours=8):
                os.remove(filepath)
                print(f"Deleted old log file: {filepath}")
        time.sleep(3600)  # Check every hour


# Start the thread that cleans up old log files
threading.Thread(target=delete_old_logs, daemon=True).start()
