import os
import threading
import time
from datetime import datetime, timedelta

log_dir = 'message_logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)


def log_message(user, message, destination):
    filename = os.path.join(log_dir, f"{user}_messages.txt")
    with open(filename, 'a') as file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"{timestamp} - From: {user} To: {destination} - {message}\n")


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
