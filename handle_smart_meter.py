import os
from dotenv import load_dotenv
from smart_meter import SmartMeter

smartMeter = SmartMeter(
    os.getenv("SMART_METER_KEY", "None"),
    os.getenv("COM_PORT", "None"),
    os.getenv("LOG_FILE_PATH", "/app/logs/"),
    os.getenv("DEBUG", "false").lower() == "true"
)

load_dotenv()
