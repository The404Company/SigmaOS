# SigmaOS_core v1.3 - i just hope the env stuff wors, i have no idea what i just wrote lol.
from colorama import Fore, Style
import os
import time
import threading
import datetime
import inspect
import requests
import json
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

def _get_env_file_path():
    """Returns the path to the user.env file."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "../../user.env"))

def _load_env_vars():
    """Loads environment variables from the user.env file."""
    env_path = _get_env_file_path()
    if not os.path.exists(env_path):
        return {}
    
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                return {}
            return json.loads(content)
    except json.JSONDecodeError:
        # Only report actual errors
        print(f"{Fore.RED}Error: user.env file is corrupted.{Style.RESET_ALL}")
        return {}
    except Exception as e:
        print(f"{Fore.RED}Error reading environment variables: {e}{Style.RESET_ALL}")
        return {}

def _save_env_vars(env_vars):
    """Saves environment variables to the user.env file."""
    env_path = _get_env_file_path()
    env_dir = os.path.dirname(env_path)
    os.makedirs(env_dir, exist_ok=True)
    
    try:
        with open(env_path, 'w', encoding='utf-8') as f:
            json.dump(env_vars, f, indent=2)
        return True
    except Exception as e:
        print(f"{Fore.RED}Error saving environment variables: {e}{Style.RESET_ALL}")
        return False

def get_env(name, default=None):
    """
    Gets an environment variable value.
    
    Args:
        name (str): Name of the environment variable
        default: Value to return if the variable doesn't exist
    
    Returns:
        Value of the environment variable, or default if not found
    """
    env_vars = _load_env_vars()
    return env_vars.get(name, default)

def set_env(name, value, silent=True):
    """
    Sets an environment variable.
    
    Args:
        name (str): Name of the environment variable
        value: Value to set
        silent (bool): If True (default), suppresses success messages
    
    Returns:
        bool: True if successful, False otherwise
    """
    env_vars = _load_env_vars()
    env_vars[name] = value
    success = _save_env_vars(env_vars)
    
    if success and not silent:
        print(f"{Fore.GREEN}Environment variable '{name}' set successfully.{Style.RESET_ALL}")
    elif not success:
        # Always show errors
        print(f"{Fore.RED}Failed to set environment variable '{name}'.{Style.RESET_ALL}")
    
    if success:
        log(f"Environment variable '{name}' set")
    
    return success

def delete_env(name, silent=True):
    """
    Deletes an environment variable.
    
    Args:
        name (str): Name of the environment variable to delete
        silent (bool): If True (default), suppresses messages
    
    Returns:
        bool: True if successful and variable existed, False otherwise
    """
    env_vars = _load_env_vars()
    if name not in env_vars:
        if not silent:
            print(f"{Fore.YELLOW}Environment variable '{name}' does not exist.{Style.RESET_ALL}")
        return False
    
    del env_vars[name]
    success = _save_env_vars(env_vars)
    
    if success and not silent:
        print(f"{Fore.GREEN}Environment variable '{name}' deleted successfully.{Style.RESET_ALL}")
    elif not success:
        # Always show errors
        print(f"{Fore.RED}Failed to delete environment variable '{name}'.{Style.RESET_ALL}")
    
    if success:
        log(f"Environment variable '{name}' deleted")
    
    return success

def list_env_vars(silent=False):
    """
    Lists all environment variables.
    
    Args:
        silent (bool): If True, suppresses all output
    
    Returns:
        dict: Dictionary of all environment variables
    """
    env_vars = _load_env_vars()
    if not silent:
        if not env_vars:
            print(f"{Fore.YELLOW}No environment variables found.{Style.RESET_ALL}")
        else:
            print(f"{Fore.CYAN}Environment Variables:{Style.RESET_ALL}")
            for name, value in env_vars.items():
                print(f"{Fore.GREEN}{name}{Style.RESET_ALL}: {value}")
    
    return env_vars