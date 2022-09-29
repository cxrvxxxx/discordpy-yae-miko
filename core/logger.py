from datetime import datetime

# prints supplied message argument to console
def console_log(message):
    timestamp = str(datetime.now())
    print(f"{timestamp[:-7]}: SYSTEM: {message}")