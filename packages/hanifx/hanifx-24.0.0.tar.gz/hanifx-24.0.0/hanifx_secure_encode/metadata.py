import os
import json
from datetime import datetime

LOG_FOLDER = "hanifx_logs"

if not os.path.exists(LOG_FOLDER):
    os.makedirs(LOG_FOLDER)

def log_operation(file: str, status: str):
    """Save operation metadata to log folder"""
    data = {
        "file": file,
        "status": status,
        "timestamp": str(datetime.now())
    }
    log_file = os.path.join(LOG_FOLDER, "metadata_log.json")
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            logs = json.load(f)
    else:
        logs = []
    logs.append(data)
    with open(log_file, "w") as f:
        json.dump(logs, f, indent=4)
