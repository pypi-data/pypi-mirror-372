import logging
import sys
import io
import os
import time
import datetime
from colorama import init, Fore, Style
init()

# --- Always Set UTF-8 Encoding for Console and Files (for all platforms, to fix unicode issues) ---
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Safe print function to handle unicode errors (use this instead of print)
def safe_print(*args, **kwargs):
    try:
        print(*args, **kwargs)
        sys.stdout.flush()  # Force flush to prevent buffering/hanging
    except UnicodeEncodeError:
        # Replace problematic chars and retry
        safe_args = [arg.encode('utf-8', errors='replace').decode('utf-8') if isinstance(arg, str) else arg for arg in args]
        print(*safe_args, **kwargs)
        sys.stdout.flush()

# Define UnicodeSafeFormatter class (unchanged)
class UnicodeSafeFormatter(logging.Formatter):
    """Custom formatter to handle Unicode characters safely"""
    def format(self, record):
        try:
            return super().format(record)
        except UnicodeEncodeError:
            record.msg = record.msg.encode('utf-8', errors='replace').decode('utf-8')
            return super().format(record)

# Redirect print to logging with original text (including colors for terminal, stripped for log) (unchanged)
class StreamToLogger:
    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''
        # Create a duplicate of the original stdout to avoid closure issues
        self.original_stdout_fd = os.dup(sys.stdout.fileno())
        self.original_stdout = os.fdopen(self.original_stdout_fd, 'w', encoding='utf-8', newline='')

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            # Print to terminal with original text (preserves colors)
            self.original_stdout.write(line + '\n')
            self.original_stdout.flush()
            # Remove ANSI color codes before logging to file (log only once)
            clean_line = line.replace('\033[31m', '').replace('\033[32m', '').replace('\033[0m', '')
            if clean_line.strip():  # Avoid logging empty lines
                self.logger.log(self.log_level, clean_line.rstrip())

    def flush(self):
        self.original_stdout.flush()

# Update logging setup (unchanged)
def setup_logging():
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)  # Create logs/ folder if it doesn't exist
    log_file = os.path.join(log_dir, 'kite_bracket_orders.log')
    # Get the root logger and clear any existing handlers to prevent console output
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.handlers = []  # Clear all existing handlers (prevents default StreamHandler)
    # Add only the FileHandler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(UnicodeSafeFormatter('%(asctime)s [%(levelname)s] %(message)s'))
    logger.addHandler(file_handler)
    # Redirect print to logger (terminal and log file output)
    sys.stdout = StreamToLogger(logger, logging.INFO)

# --- Market Hours Check --- (unchanged)
def is_market_open():
    now = datetime.datetime.now().time()
    return datetime.time(9, 15) <= now <= datetime.time(15, 30)

def is_weekend():
    """Check if it's Saturday or Sunday"""
    return datetime.datetime.now().weekday() >= 5

def current_timestamp():
    """Return current timestamp as string"""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# --- Check if Order is Filled --- (updated to use safe_print)
def is_filled(kite, order_id):
    try:
        history = kite.order_history(order_id)
        return any(o['status'] == 'COMPLETE' for o in history)
    except Exception as e:
        safe_print(f"⚠️ is_filled error: {e}")
        return False

# --- Cancel Order Safely --- (updated to use safe_print)
def cancel_order_safe(kite, order_id):
    try:
        kite.cancel_order(variety=kite.VARIETY_REGULAR, order_id=order_id)
        safe_print(f"🚫 Cancelled order: {order_id}")
    except Exception as e:
        safe_print(f"⚠️ Cancel error: {e}")

# --- Retry Wrapper (Loop until success) --- (updated to use safe_print)
def retry_until_success(func, *args, interval=30, reconnect_func=None, periodic_msg=None):
    while True:
        try:
            if func(*args):
                return True
        except Exception as e:
            safe_print(f"🔁 Retry error: {e}")
            if reconnect_func:
                reconnect_func()  # Call reconnection (e.g., reload Kite)
            if periodic_msg:
                safe_print(periodic_msg)  # Print msg ONCE after error/reconnection
        time.sleep(interval)