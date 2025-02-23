import os
from dotenv import load_dotenv
from smart_meter import SmartMeter

smartMeter = SmartMeter(
    os.getenv("SMART_METER_KEY", "None"),
    os.getenv("COM_PORT", "None"),
    os.getenv("LOG_FILE_PATH", "/app/logs/app.log"),
    os.getenv("DEBUG", "false").lower() == "true"
)

load_dotenv()

smart_meter_key = os.getenv("SMART_METER_KEY", "None")
debug_mode = os.getenv("DEBUG", "false").lower() == "true"
log_file_path = os.getenv("LOG_FILE_PATH", "/app/logs/app.log")
comport = os.getenv("COM_PORT", "None")


print([smart_meter_key, debug_mode, log_file_path, comport])
