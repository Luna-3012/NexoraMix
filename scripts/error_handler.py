# scripts/error_handler.py
import os
import traceback
from datetime import datetime
from utils.constants import LOG_DIR

os.makedirs(LOG_DIR, exist_ok=True)
MISSING_PAGES_LOG = os.path.join(LOG_DIR, "missing_pages.log")
ERROR_LOG = os.path.join(LOG_DIR, "errors.log")

def log_missing(brand, reason=None):
    timestamp = datetime.now().isoformat()
    reason_text = reason if reason is not None else "unknown"
    with open(MISSING_PAGES_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {brand}\t{reason_text}\n")

def log_error(context, exc):
    timestamp = datetime.now().isoformat()
    with open(ERROR_LOG, "a", encoding="utf-8") as f:
        f.write(f"--- [{timestamp}]\n")
        f.write(f"Context: {context}\n")
        f.write(traceback.format_exc())
        f.write("\n")
