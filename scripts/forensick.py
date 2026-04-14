import json
import datetime
import os

LOG_FILE = "output/forensick_log.json"


def log_event(event_type, detail):
    os.makedirs("output", exist_ok=True)
    entry = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "event": event_type,
        "detail": detail
    }
    log = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            try:
                log = json.load(f)
            except json.JSONDecodeError:
                log = []
    log.append(entry)
    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)
