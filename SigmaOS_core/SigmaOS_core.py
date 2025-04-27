# SigmaOS_core v1.1
from colorama import Fore, Style
import os
import time
import threading
import datetime
import inspect


def clear_screen():
    """Clears the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def press_enter_to_continue():
    """Prompts the user to press Enter to continue."""
    input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

def loading_animation(message, duration=2, task=None):
    """Displays a loading animation in the terminal."""
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    stop_event = threading.Event()
    result = {}

    def animate():
        i = 0
        while not stop_event.is_set():
            print(f"\r{Fore.CYAN}{frames[i]} {message}", end="", flush=True)
            time.sleep(0.1)
            i = (i + 1) % len(frames)
        print(f"\r{Fore.GREEN}✓ {message}{Style.RESET_ALL}")

    if task is not None:
        thread = threading.Thread(target=animate)
        thread.start()
        try:
            result['value'] = task()
        finally:
            stop_event.set()
            thread.join()
        return result.get('value')
    else:
        end_time = time.time() + duration
        i = 0
        while time.time() < end_time:
            print(f"\r{Fore.CYAN}{frames[i]} {message}", end="", flush=True)
            time.sleep(0.1)
            i = (i + 1) % len(frames)
        print(f"\r{Fore.GREEN}✓ {message}{Style.RESET_ALL}")

def log(message):
    """
    Logs a message to a file in ../../logs.
    The log file is named {package-name}_{Date_Time}.log,
    where {package-name} is the name of the folder this file is in.
    """
    # Get the path of the file that called log()
    frame = inspect.stack()[1]
    caller_file = frame.filename
    # Get the package/folder name
    package_name = os.path.basename(os.path.dirname(caller_file))
    # Prepare logs directory path (two levels up)
    logs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../logs"))
    os.makedirs(logs_dir, exist_ok=True)
    # Prepare log file name
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_filename = f"{package_name}_{now}.log"
    log_path = os.path.join(logs_dir, log_filename)
    # Write the log message
    with open(log_path, "a", encoding="utf-8") as f:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {message}\n")