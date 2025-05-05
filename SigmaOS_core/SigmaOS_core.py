# SigmaOS_core v1.2
from colorama import Fore, Style
import os
import time
import threading
import datetime
import inspect
import requests
from urllib.parse import urlparse


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

def suck(url, save_to_documents=False, filename=None, hidden=False):
    """
    Download a file from the internet.
    
    Args:
        url (str): The URL of the file to download
        save_to_documents (bool): If True, save to ../../documents, otherwise save to current directory
        filename (str, optional): Custom filename to save as. If None, uses the filename from the URL
        hidden (bool): If True, suppresses all output messages
    
    Returns:
        str: Path to the downloaded file, or None if download failed
    """
    try:
        # Get the filename from URL if not provided
        if filename is None:
            filename = os.path.basename(urlparse(url).path)
            if not filename:
                filename = "downloaded_file"
        
        # Determine save location
        if save_to_documents:
            # Get the documents directory (two levels up)
            save_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../documents"))
            os.makedirs(save_dir, exist_ok=True)
        else:
            # Save in the current directory
            save_dir = os.path.dirname(__file__)
        
        save_path = os.path.join(save_dir, filename)
        
        def download_task():
            # Start the download
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # Get total size for progress tracking
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            # Download the file
            with open(save_path, 'wb') as f:
                for data in response.iter_content(chunk_size=1024):
                    size = f.write(data)
                    downloaded += size
                    # Update progress message
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        return f"Downloading {filename} ({progress:.1f}%)"
                    else:
                        return f"Downloading {filename} ({downloaded/1024:.1f} KB)"
            
            return f"Downloaded {filename}"
        
        # Use loading_animation with the download task if not hidden
        if not hidden:
            loading_animation(f"Downloading {filename}", task=download_task)
            print(f"{Fore.GREEN}✓ Downloaded {filename} to {save_path}{Style.RESET_ALL}")
        else:
            # Just run the task without animation
            download_task()
        
        return save_path
        
    except requests.exceptions.RequestException as e:
        if not hidden:
            print(f"{Fore.RED}Error downloading file: {e}{Style.RESET_ALL}")
        return None
    except Exception as e:
        if not hidden:
            print(f"{Fore.RED}Unexpected error: {e}{Style.RESET_ALL}")
        return None