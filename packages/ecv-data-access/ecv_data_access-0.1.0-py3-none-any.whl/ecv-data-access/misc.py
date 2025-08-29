import requests
import os
import sys
import inspect
from datetime import datetime

def stream_to_file(resp: requests.Response, filepath: str = ""):

    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        log_print(f"HTTP error occurred: {e}")
        log_print(f"Response text: {resp.text}")
        return None
    
    log_print(f"Response status code: {resp.status_code}")
    if resp.status_code != 200:
        log_print(f"Error: {resp.text}")
        return None
            
    downloaded = 0
    log_threshold = 1 * 1024 * 1024   # 1 MB
    next_log = log_threshold

    with open(filepath, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            if not chunk:
                continue
            f.write(chunk)
            downloaded += len(chunk)

            # If we've passed the next threshold, log it
            if downloaded >= next_log:
                mb = downloaded / 1024 / 1024
                log_print(f"Downloaded: {mb:.2f} MB")
                next_log += log_threshold

    # Final report (in case total < 1 MB or to finish the line)
    mb = downloaded / 1024 / 1024
    
    log_print(f"Download complete: {mb:.2f} MB")

    return filepath



def log_print(*args, **kwargs):
    """
    Custom logging function that prints messages with timestamp and caller information.

    The output format is:
    [YYYY-MM-DD HH:MM:SS] [filename:function_name] message

    Example:
    [2025-07-15 15:15:00] [main.py:process_data] Data processing started
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    current_frame = inspect.currentframe()
    caller_frame = current_frame.f_back if current_frame else None

    if caller_frame:
        caller_filename = os.path.basename(caller_frame.f_code.co_filename)
        caller_function = caller_frame.f_code.co_name
    else:
        caller_filename = "<unknown>"
        caller_function = "<unknown>"

    message_text = ' '.join(str(arg) for arg in args)
    formatted_message = f"[{timestamp}] [{caller_filename}:{caller_function}] {message_text}"

    print(formatted_message, **kwargs)
    
def is_iterable(obj):
    """Check if an object is iterable."""
    try:
        iter(obj)
        return True
    except TypeError:
        return False