"""For logging to console"""
from datetime import datetime

# prints supplied message argument to console
def console_log(message):
    """Log message to console with date and time"""
    timestamp = str(datetime.now())
    print(f"{timestamp[:-7]}: SYSTEM: {message}")
