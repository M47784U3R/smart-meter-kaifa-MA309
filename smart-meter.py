# smart-meter.py
import datetime

log_file = "/app/logs/script.log"

with open(log_file, "a") as log:
    log.write(f"Script started at {datetime.datetime.now()}\n")
    log.write("This is a log message from the script.\n")

print("\n--- Log File Content ---")
with open(log_file, "r") as log:
    print(log.read())
