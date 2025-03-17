import os
from dotenv import load_dotenv
from smart_meter import SmartMeter

load_dotenv()
smartMeter = SmartMeter(
    os.getenv("SMART_METER_KEY", "None"),
    os.getenv("COM_PORT", "None"),
    os.getenv("LOG_FILE_PATH", None),
    os.getenv("VERBOSE", "false").lower() == "true"
)