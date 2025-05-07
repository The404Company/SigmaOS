#!/usr/bin/env python3
# Import only built-in libraries first
import subprocess
import sys
import os
import time
import threading
import json
import platform
import importlib.util
import uuid

# Version number
VERSION = "0.1.b"

# Define basic console colors for early use before colorama is loaded
try:
    # First try to import colorama for basic styling
    import colorama
    from colorama import Fore, Style
    colorama.init(autoreset=True)
    # Pre-define basic styles for use during initialization
    SUCCESS_STYLE = Fore.GREEN
    ERROR_STYLE = Fore.RED
    WARNING_STYLE = Fore.YELLOW
    INFO_STYLE = Fore.CYAN
    RESET_STYLE = Style.RESET_ALL
except ImportError:
    # Fallback if colorama isn't installed yet
    SUCCESS_STYLE = ""
    ERROR_STYLE = ""
    WARNING_STYLE = ""
    INFO_STYLE = ""
    RESET_STYLE = ""

# Global variable for log file
LOG_FILE = None

# Check and download ligma.py if needed
def check_and_download_ligma(force_update=False):
    """Check if ligma.py exists, download it if not, or update it if outdated"""
    ligma_path = os.path.join(os.path.dirname(__file__), "ligma.py")
    ligma_url = "https://raw.githubusercontent.com/The404Company/SigmaOS/main/ligma.py"
    
    try:
        # Check if file exists
        if not os.path.exists(ligma_path) or force_update:
            print(f"{INFO_STYLE}{'Updating' if force_update else 'Downloading'} ligma.py from GitHub...{RESET_STYLE}")
            response = requests.get(ligma_url)
            if response.status_code == 200:
                with open(ligma_path, "w", encoding="utf-8") as f:
                    f.write(response.text)
                print(f"{SUCCESS_STYLE}ligma.py {'updated' if force_update else 'downloaded'} successfully.{RESET_STYLE}")
            else:
                print(f"{ERROR_STYLE}Failed to download ligma.py. Status code: {response.status_code}{RESET_STYLE}")
                return False
        else:
            # Check if file is up to date
            try:
                response = requests.get(ligma_url)
                if response.status_code == 200:
                    current_content = ""
                    with open(ligma_path, "r", encoding="utf-8") as f:
                        current_content = f.read()
                    
                    if current_content != response.text:
                        print(f"{INFO_STYLE}Updating ligma.py...{RESET_STYLE}")
                        with open(ligma_path, "w", encoding="utf-8") as f:
                            f.write(response.text)
                        print(f"{SUCCESS_STYLE}ligma.py updated successfully.{RESET_STYLE}")
            except Exception as e:
                print(f"{WARNING_STYLE}Could not check for ligma.py updates: {e}{RESET_STYLE}")
                pass  # Continue even if update check fails
        
        return True
    except Exception as e:
        print(f"{ERROR_STYLE}Error handling ligma.py: {e}{RESET_STYLE}")
        return False

# Enhanced logging system
def log(message, level="INFO", print_to_console=False, traceback=None):
    """
    Enhanced logging function that writes messages to a log file and optionally to the console.
    
    Args:
        message (str): The message to log
        level (str): Log level: "INFO", "WARNING", "ERROR", "DEBUG"
        print_to_console (bool): Whether to also print the message to the console
        traceback (Exception): Exception object to include traceback information
    
    Returns:
        None
    """
    global LOG_FILE
    
    # Prepare logs directory path
    logs_dir = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(logs_dir, exist_ok=True)
    
    # Create log file if it doesn't exist
    if LOG_FILE is None:
        start_time = time.strftime("%Y-%m-%d_%H-%M-%S")
        LOG_FILE = os.path.join(logs_dir, f"SigmaOS_{start_time}.log")
    
    # Format the message with timestamp and level
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] [{level}] {message}"
    
    # Add traceback information if provided
    if traceback is not None:
        import traceback as tb
        trace_info = "".join(tb.format_exception(type(traceback), traceback, traceback.__traceback__))
        log_message += f"\nTraceback:\n{trace_info}"
    
    # Write to log file
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_message + "\n")
    except Exception as e:
        # If we can't write to the log file, at least print to console
        print(f"{ERROR_STYLE}Error writing to log file: {e}{RESET_STYLE}")
        print_to_console = True
    
    # Print to console if requested
    if print_to_console:
        style = {
            "INFO": INFO_STYLE,
            "WARNING": WARNING_STYLE,
            "ERROR": ERROR_STYLE,
            "DEBUG": INFO_STYLE,
            "SUCCESS": SUCCESS_STYLE
        }.get(level, INFO_STYLE)
        
        print(f"{style}[{level}] {message}{RESET_STYLE}")

def log_info(message, print_to_console=False):
    """Log an informational message"""
    log(message, level="INFO", print_to_console=print_to_console)

def log_warning(message, print_to_console=False):
    """Log a warning message"""
    log(message, level="WARNING", print_to_console=print_to_console)

def log_error(message, exception=None, print_to_console=False):
    """Log an error message with optional exception traceback"""
    log(message, level="ERROR", print_to_console=print_to_console, traceback=exception)

def log_debug(message, print_to_console=False):
    """Log a debug message"""
    log(message, level="DEBUG", print_to_console=print_to_console)

def log_success(message, print_to_console=False):
    """Log a success message"""
    log(message, level="SUCCESS", print_to_console=print_to_console)

# Safe module import function
def safe_import(module_name):
    """Safely import a module and return None if it's not available"""
    try:
        return importlib.import_module(module_name)
    except ImportError:
        return None

# Check if we're on Python 3.12+ where distutils is removed
USING_PYTHON_312_PLUS = sys.version_info >= (3, 12)
if USING_PYTHON_312_PLUS and platform.system() == "Linux":
    print(f"{WARNING_STYLE}Running on Python 3.12+ on Linux. Some features may be limited.{RESET_STYLE}")
    log_warning("Running on Python 3.12+ on Linux. Some features may be limited.")

def clear_screen():
    """Clear the console screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def show_text_splash():
    """Show a simple text splash screen without using any external libraries"""
    clear_screen()
    splash_text = fr"""
   _____ _                       ____  _____ 
  / ___/(_)___ _____ ___  ____ _/ __ \/ ___/
  \__ \/ / __ `/ __ `__ \/ __ `/ / / /\__ \ 
 ___/ / / /_/ / / / / / / /_/ / /_/ /___/ / 
/____/_/\__, /_/ /_/ /_/\__,_/\____//____/   v{VERSION}
       /____/                               
                        by The404Company

Installing dependencies...
"""
    print(splash_text)

def show_system_info():
    """Show basic system information using only built-in libraries"""
    print("\nDetecting system information...")
    
    # Get CPU info
    cpu = "Unknown CPU"
    if platform.system() == "Windows":
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
            cpu = winreg.QueryValueEx(key, "ProcessorNameString")[0]
            cpu = (cpu.replace("(R)", "")
                     .replace("(TM)", "")
                     .replace("CPU ", "")
                     .replace("Processor", "")
                     .replace("-Core", "")
                     .replace("  ", " ")
                     .strip())
            if "@" in cpu:
                cpu = cpu.split("@")[0].strip()
        except:
            pass
    elif platform.system() == "Linux":
        try:
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    if line.startswith("model name"):
                        cpu = line.split(":")[1].strip()
                        break
        except:
            pass
    
    # Get memory info
    memory = "Unknown"
    try:
        import psutil
        total_memory = psutil.virtual_memory().total / (1024**3)
        memory = f"{total_memory:.1f} GB"
    except:
        pass
    
    # Get GPU info
    gpu = "Unknown GPU"
    if platform.system() == "Windows":
        try:
            cmd = "wmic path win32_VideoController get name"
            output = subprocess.check_output(cmd, shell=True).decode()
            gpu_lines = [line.strip() for line in output.split('\n') if line.strip()]
            if len(gpu_lines) > 1:
                gpu = gpu_lines[1]
                if "AMD" in gpu:
                    gpu = gpu.replace("AMD ", "AMD Radeon ")
                elif "NVIDIA" in gpu:
                    gpu = gpu.replace("NVIDIA GeForce", "NVIDIA")
        except:
            pass
    elif platform.system() == "Linux":
        try:
            # First try lspci
            try:
                output = subprocess.check_output("lspci | grep -i vga", shell=True).decode()
                if output:
                    gpu = output.split(":")[-1].strip()
            except:
                pass
            
            # Try glxinfo if lspci didn't work
            if gpu == "Unknown GPU":
                try:
                    output = subprocess.check_output("glxinfo | grep 'OpenGL renderer'", shell=True).decode()
                    if output:
                        gpu = output.split(":")[-1].strip()
                except:
                    pass
        except:
            pass
    
    # Display system info
    print(f"CPU: {cpu}")
    print(f"GPU: {gpu}")
    print(f"Memory: {memory}")
    
    # Wait for 3 seconds
    time.sleep(3)
    clear_screen()

def install_dependencies():
    """Install all required external libraries"""
    dependencies = [
        'colorama',
        'requests',
        'psutil',
        'readchar',
        'uuid'
    ]
    
    # Add Linux-specific dependencies
    if platform.system() == "Linux":
        dependencies.extend([
            'distro',  # For better Linux distribution detection
        ])
        
        # Only add pygobject if we're not in a headless environment
        if os.environ.get('DISPLAY'):
            dependencies.append('pygobject')  # For GUI support on Linux
        
        # Check for newer Python versions (3.12+) where distutils is removed
        # GPUtil depends on distutils so we'll skip it for newer versions
        if sys.version_info >= (3, 12):
            print(f"{WARNING_STYLE}Python 3.12+ detected. Skipping GPUtil installation (incompatible).{RESET_STYLE}")
        else:
            dependencies.append('GPUtil')
    else:
        # On Windows, always add GPUtil
        dependencies.append('GPUtil')
    
    # First, check which dependencies are already installed
    missing_deps = []
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✓ {dep} already installed")
        except ImportError:
            missing_deps.append(dep)
    
    # If nothing to install, return early
    if not missing_deps:
        print(f"\n{SUCCESS_STYLE}All essential packages installed successfully!{RESET_STYLE}")
        return
        
    # Now install the missing dependencies
    for dep in missing_deps:
        print(f"Installing {dep}...")
        try:
            # Use python3 explicitly on Linux
            python_cmd = "python3" if platform.system() == "Linux" else sys.executable
            
            # Use a more reliable method to determine if we need --break-system-packages
            # First try without the flag
            if platform.system() == "Linux":
                try:
                    # Try the standard installation first
                    subprocess.check_call(
                        [python_cmd, "-m", "pip", "install", dep],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.PIPE
                    )
                    print(f"✓ {dep} installed successfully")
                except subprocess.CalledProcessError:
                    # If it fails, try with --break-system-packages
                    print(f"{INFO_STYLE}Standard installation failed. Trying with --break-system-packages flag.{RESET_STYLE}")
                    try:
                        subprocess.check_call(
                            [python_cmd, "-m", "pip", "install", "--break-system-packages", dep],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.PIPE
                        )
                        print(f"✓ {dep} installed successfully (with --break-system-packages)")
                    except subprocess.CalledProcessError as e:
                        print(f"× Error installing {dep}")
                        print(f"{WARNING_STYLE}Please manually install the missing dependencies:{RESET_STYLE}")
                        print(f"python3 -m pip install --break-system-packages {' '.join(missing_deps)}")
                        sys.exit(1)
            else:
                # Windows installation
                subprocess.check_call(
                    [python_cmd, "-m", "pip", "install", dep],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE
                )
                print(f"✓ {dep} installed successfully")
        except Exception as e:
            print(f"{ERROR_STYLE}Error installing {dep}: {e}")
            if platform.system() == "Linux":
                print(f"{WARNING_STYLE}Please manually install the missing dependencies:{RESET_STYLE}")
                print(f"python3 -m pip install --break-system-packages {' '.join(missing_deps)}")
            else:
                print(f"{WARNING_STYLE}Please manually install the missing dependencies:{RESET_STYLE}")
                print(f"pip install {' '.join(missing_deps)}")
            sys.exit(1)
    
    print(f"\n{SUCCESS_STYLE}All essential packages installed successfully!{RESET_STYLE}")

# Load ligma module after dependencies are installed
def load_ligma_module():
    """Import the ligma module dynamically"""
    try:
        # First check and download/update ligma.py
        if not check_and_download_ligma():
            return None
            
        # Import the module
        spec = importlib.util.spec_from_file_location(
            "ligma", 
            os.path.join(os.path.dirname(__file__), "ligma.py")
        )
        ligma = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ligma)
        return ligma
    except Exception as e:
        print(f"{ERROR_STYLE}Error loading ligma module: {e}{RESET_STYLE}")
        log_error(f"Error loading ligma module", exception=e)
        return None

# The ligma module will be loaded after dependencies are installed
ligma_module = None

# Check if this is first execution by looking for initialization marker file
INIT_MARKER = os.path.join(os.path.dirname(__file__), ".initialized")

# Only show splash and install dependencies on first run
if not os.path.exists(INIT_MARKER):
    show_text_splash()
    install_dependencies()
    show_system_info()  # Show system info for 2 seconds
    
    # Create marker file to avoid running setup again
    try:
        with open(INIT_MARKER, "w") as f:
            f.write(f"SigmaOS initialized on {time.strftime('%Y-%m-%d %H:%M:%S')}")
    except Exception as e:
        print(f"Warning: Could not create initialization marker: {e}")

# Now import all the libraries
import requests
from colorama import init, Fore, Back, Style
import shutil
import readchar
import psutil
import platform
import math
import datetime
from zipfile import ZipFile

# Now load the ligma module after dependencies are installed
ligma_module = load_ligma_module()

# Try to import GPUtil safely
GPUtil = safe_import('GPUtil')
if GPUtil is None and not USING_PYTHON_312_PLUS:
    print(f"{WARNING_STYLE}GPUtil module not available. Some GPU features will be limited.{RESET_STYLE}")
elif GPUtil is None and USING_PYTHON_312_PLUS:
    print(f"{WARNING_STYLE}GPUtil not supported on Python 3.12+. Using alternative GPU detection.{RESET_STYLE}")

# Initialize colorama
init(autoreset=True)

# Configuration
REPO_URL = "https://github.com/The404Company/SigmaOS-packages"
PACKAGES_DIR = "packages"
ALIASES_FILE = "aliases.json"
THEMES_DIR = "themes"
USER_SETTINGS_FILE = "user.sigs"

def load_user_settings():
    """Load user settings from user.sigs file"""
    if not os.path.exists(USER_SETTINGS_FILE):
        return {"theme": "default"}
    try:
        with open(USER_SETTINGS_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading user settings: {e}")
        return {"theme": "default"}

def save_user_settings(settings):
    """Save user settings to user.sigs file"""
    with open(USER_SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=4)

def get_current_theme():
    """Get the current theme name from user settings"""
    settings = load_user_settings()
    return settings.get("theme", "default")

def set_theme(theme_name):
    """Set the current theme in user settings"""
    settings = load_user_settings()
    settings["theme"] = theme_name
    save_user_settings(settings)
    print(f"{SUCCESS_STYLE}Theme set to {theme_name}. Please restart SigmaOS to apply changes.{RESET_STYLE}")

def list_themes():
    """List all available themes"""
    if not os.path.exists(THEMES_DIR):
        os.makedirs(THEMES_DIR)
        # Create default theme if it doesn't exist
        default_theme = {
            "banner_sth": "cyan",
            "version_sth": "yellow",
            "success_sth": "green",
            "error_sth": "red",
            "warning_sth": "yellow",
            "info_sth": "cyan",
            "header_sth": "yellow",
            "command_sth": "green",
            "description_sth": "white",
            "author_sth": "cyan",
            "loading_sth": "cyan",
            "prompt_sth": "green",
            "suggestion_sth": "cyan",
            "relevance_sth": "blue",
            "system_info_sth": "yellow",
            "timer_sth": "green",
            "alias_sth": "green",
            "package_sth": "green",
            "package_version_sth": "cyan",
            "package_author_sth": "cyan",
            "package_description_sth": "white",
            "package_installed_sth": "green",
            "package_not_installed_sth": "yellow",
            "package_error_sth": "red",
            "package_loading_sth": "cyan",
            "package_skipped_sth": "yellow",
            "package_cleanup_sth": "green",
            "package_download_sth": "cyan",
            "package_install_sth": "cyan",
            "package_uninstall_sth": "yellow",
            "package_reset_sth": "red",
            "package_setup_sth": "cyan",
            "package_essential_sth": "green",
            "package_already_installed_sth": "yellow",
            "package_not_found_sth": "red",
            "package_download_error_sth": "red",
            "package_install_error_sth": "red",
            "package_uninstall_error_sth": "red",
            "package_reset_error_sth": "red",
            "package_setup_error_sth": "red",
            "package_essential_error_sth": "red",
            "package_already_installed_error_sth": "red",
            "package_not_found_error_sth": "red",
            "package_download_success_sth": "green",
            "package_install_success_sth": "green",
            "package_uninstall_success_sth": "green",
            "package_reset_success_sth": "green",
            "package_setup_success_sth": "green",
            "package_essential_success_sth": "green",
            "package_already_installed_success_sth": "green",
            "package_not_found_success_sth": "green"
        }
        with open(os.path.join(THEMES_DIR, "default.sth"), 'w') as f:
            json.dump(default_theme, f, indent=4)

    themes = [f[:-4] for f in os.listdir(THEMES_DIR) if f.endswith('.sth')]
    current_theme = get_current_theme()
    
    if themes:
        print(f"\n{header_sth}Available themes:{RESET_STYLE}")
        for theme in themes:
            if theme == current_theme:
                print(f"{SUCCESS_STYLE}  {theme} (current){RESET_STYLE}")
            else:
                print(f"{description_sth}  {theme}")
    else:
        print(f"{WARNING_STYLE}No themes found.{RESET_STYLE}")

class Theme:
    def __init__(self):
        self.theme = {}
        self.load_theme()
        self._create_color_variables()
    
    def load_theme(self):
        """Load theme from file or create default if it doesn't exist"""
        if not os.path.exists(THEMES_DIR):
            os.makedirs(THEMES_DIR)
        
        theme_name = get_current_theme()
        theme_file = os.path.join(THEMES_DIR, f"{theme_name}.sth")
        
        if not os.path.exists(theme_file):
            # If theme file doesn't exist, copy default theme
            default_theme = os.path.join(THEMES_DIR, "default.sth")
            if os.path.exists(default_theme):
                with open(default_theme, 'r') as src, open(theme_file, 'w') as dst:
                    dst.write(src.read())
            else:
                self.create_default_theme()
                return
        
        try:
            with open(theme_file, 'r') as f:
                self.theme = json.load(f)
        except Exception as e:
            print(f"Error loading theme: {e}")
            self.create_default_theme()
    
    def _create_color_variables(self):
        """Create global color variables from theme"""
        for color_name, color_value in self.theme.items():
            # Create a global variable for each color
            globals()[color_name] = getattr(Fore, color_value.upper(), Fore.WHITE)
    
    def create_default_theme(self):
        """Create default theme file"""
        default_theme = {
            # Core UI Elements
            "banner_sth": "cyan",          # Banner box and lines
            "command_sth": "green",        # Commands, sigma symbol, and SigmaOS text
            "version_sth": "yellow",       # Version number
            "description_sth": "white",    # General text and descriptions
            
            # Status Messages
            "success_sth": "green",        # Success messages
            "error_sth": "red",            # Error messages
            "warning_sth": "yellow",       # Warning messages
            "info_sth": "cyan",            # Information messages
            
            # UI Components
            "header_sth": "yellow",        # Section headers
            "prompt_sth": "green",         # Command prompt
            "loading_sth": "cyan",         # Loading animations
            "timer_sth": "green",          # Timer display
            
            # Interactive Elements
            "suggestion_sth": "cyan",      # Command suggestions
            "relevance_sth": "blue",       # Suggestion relevance
            "alias_sth": "green",          # Alias commands
            
            # System Information
            "system_info_sth": "yellow",   # System information
            
            # Package Management
            "package_sth": "green",        # Package names
            "package_status_sth": "cyan",  # Package status (installed, version, etc.)
            "package_error_sth": "red"     # Package errors
        }
        
        default_theme_file = os.path.join(THEMES_DIR, "default.sth")
        with open(default_theme_file, 'w') as f:
            json.dump(default_theme, f, indent=4)
        self.theme = default_theme

# Initialize theme
theme = Theme()

def ensure_base_libraries():
    # This function is no longer needed as we installed dependencies at startup
    pass

# Only run setup if packages directory doesn't exist
if not os.path.exists(PACKAGES_DIR):
    pass  # Packages will be set up when needed, dependencies are already installed

COMMAND_HISTORY = []
MAX_HISTORY = 100
ALL_COMMANDS = {
    'help': [],
    'exit': [],
    'clear': [],
    'setup': [],
    'reset': [],
    'ligma': ['list', 'install', 'uninstall', 'browse', 'search', '?v', '?version', '?i', '?info', '?h', '?help'],
    'alias': ['list', 'add', 'remove'],
    'sysinfo': [],
    'now': [],
    'sendlogs': [],
    'timer': [],
    'theme': ['list', 'set', 'edit', 'create', 'delete', 'show'],
    'update-ligma': [],
}

init(autoreset=True)  # Initialize colorama

def show_banner():
    clear_screen()
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"{banner_sth}╔═════════════════════════╗{RESET_STYLE}")
    print(f"{banner_sth}║ {RESET_STYLE}{command_sth}σ{RESET_STYLE} {command_sth}SigmaOS{RESET_STYLE} {version_sth}v{VERSION}{RESET_STYLE}        {banner_sth}║{RESET_STYLE}")
    print(f"{banner_sth}╚═════════════════════════╝{RESET_STYLE}")

def loading_animation(message, duration=2, task=None):
    """
    Show a loading animation for a fixed duration or while a task runs.
    If task is provided, it should be a function (optionally with args/kwargs).
    """
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    stop_event = threading.Event()
    result = {}

    def animate():
        i = 0
        while not stop_event.is_set():
            print(f"\r{loading_sth}{frames[i]} {message}", end="", flush=True)
            time.sleep(0.1)
            i = (i + 1) % len(frames)
        print(f"\r{SUCCESS_STYLE}✓ {message}{RESET_STYLE}")

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
            print(f"\r{loading_sth}{frames[i]} {message}", end="", flush=True)
            time.sleep(0.1)
            i = (i + 1) % len(frames)
        print(f"\r{SUCCESS_STYLE}✓ {message}{RESET_STYLE}")

def load_aliases():
    if not os.path.exists(ALIASES_FILE):
        save_aliases({})  # Create empty file if it doesn't exist
    try:
        with open(ALIASES_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_aliases(aliases):
    with open(ALIASES_FILE, 'w') as f:
        json.dump(aliases, f, indent=2)

def add_alias(name, command):
    aliases = load_aliases()
    aliases[name] = command
    save_aliases(aliases)
    print(f"{SUCCESS_STYLE}Added alias: {name} → {command}{RESET_STYLE}")

def remove_alias(name):
    aliases = load_aliases()
    if name in aliases:
        del aliases[name]
        save_aliases(aliases)
        print(f"{SUCCESS_STYLE}Removed alias: {name}{RESET_STYLE}")
    else:
        print(f"{ERROR_STYLE}Alias not found: {name}{RESET_STYLE}")

def list_aliases():
    aliases = load_aliases()
    if aliases:
        print(f"\n{header_sth}Configured aliases:{RESET_STYLE}")
        for name, command in aliases.items():
            print(f"{alias_sth}  {name} {description_sth}→ {command}")
    else:
        print(f"{WARNING_STYLE}No aliases configured.{RESET_STYLE}")

def show_help():
    print(f"\n{header_sth}╔══ SigmaOS Help ══════════════════════════╗{RESET_STYLE}")
    
    # System Commands
    print(f"\n{INFO_STYLE}System Commands:{RESET_STYLE}")
    system_commands = [
        ("help", "Show this help message"),
        ("exit, sigma quit", "Exit SigmaOS"),
        ("clear", "Clear the screen"),
        ("setup", "Install essential packages"),
        ("reset", "Reset SigmaOS to default state"),
        ("sysinfo", "Show system information"),
        ("now", "Show current date and time"),
        ("sendlogs", "Send logs to Discord"),
        ("update-ligma", "Force update ligma.py to the latest version"),
        ("timer <duration> <unit>", "Set a timer (s/m/h). Hidden feature: Type a command during the timer (invisible), press Enter, and it will execute when the timer finishes!"),
        ]
    for cmd, desc in system_commands:
        print(f"{command_sth}  {cmd:<25}{description_sth} - {desc}")

    # Theme Management
    print(f"\n{INFO_STYLE}Theme Management:{RESET_STYLE}")
    theme_commands = [
        ("theme list", "List all available themes"),
        ("theme set <name>", "Set theme (requires restart)"),
        ("theme edit <name> [value]", "Edit theme colors (all or specific value)"),
        ("theme create <name>", "Create a new theme"),
        ("theme delete <name>", "Delete a theme"),
        ("theme show <name>", "Show theme contents"),
        ]
    for cmd, desc in theme_commands:
        print(f"{command_sth}  {cmd:<25}{description_sth} - {desc}")
    print(f"{description_sth}  Available colors: black, blue, cyan, green, magenta, red, white, yellow, lightblack_ex, lightblue_ex, lightcyan_ex, lightgreen_ex, lightmagenta_ex, lightred_ex, lightwhite_ex, lightyellow_ex{RESET_STYLE}")

    # Package Management
    print(f"\n{INFO_STYLE}Package Management:{RESET_STYLE}")
    pkg_commands = [
        ("ligma list", "List installed packages"),
        ("ligma browse", "Browse all available packages"),
        ("ligma search <term>", "Search for packages"),
        ("ligma install <pkg>", "Install a package"),
        ("ligma uninstall <pkg>", "Uninstall a package"),
        ("ligma <pkg> ?v", "Show package version"),
        ("ligma <pkg> ?i", "Show package info"),
        ("ligma ?help", "Show ligma help"),
        ("<package>", "Run a package directly")
    ]
    for cmd, desc in pkg_commands:
        print(f"{command_sth}  {cmd:<25}{description_sth} - {desc}")

    # Alias Management
    print(f"\n{INFO_STYLE}Alias Management:{RESET_STYLE}")
    alias_commands = [
        ("alias list", "List all aliases"),
        ("alias add <name> <cmd>", "Add new alias"),
        ("alias remove <name>", "Remove alias")
    ]
    for cmd, desc in alias_commands:
        print(f"{command_sth}  {cmd:<25}{description_sth} - {desc}")

    # Keyboard Shortcuts
    print(f"\n{INFO_STYLE}Keyboard Shortcuts:{RESET_STYLE}")
    shortcuts = [
        ("Tab", "Auto-complete commands"),
        ("Up/Down", "Navigate command history"),
        ("Left/Right", "Move cursor"),
        ("Ctrl+C", "Interrupt current operation")
    ]
    for key, desc in shortcuts:
        print(f"{WARNING_STYLE}  {key:<25}{description_sth} - {desc}")

    print(f"\n{header_sth}╚{'═' * 41}╝{RESET_STYLE}")

def get_user_uuid():
    """Get or create a unique, anonymized UUID for the user."""
    uuid_file = os.path.join(os.path.dirname(__file__), "user_uuid.json")
    try:
        if os.path.exists(uuid_file):
            with open(uuid_file, "r") as f:
                data = json.load(f)
                return data.get("uuid", str(uuid.uuid4()))
        else:
            user_uuid = str(uuid.uuid4())
            with open(uuid_file, "w") as f:
                json.dump({"uuid": user_uuid}, f)
            return user_uuid
    except Exception as e:
        print(f"{ERROR_STYLE}Error handling UUID: {e}{RESET_STYLE}")
        return str(uuid.uuid4())

def send_logs_to_discord():
    """
    Sends all log files in the 'logs' folder to a Discord webhook,
    then deletes the log files. Filters out INFO level logs to reduce noise.
    """
    logs_dir = os.path.join(os.path.dirname(__file__), "logs")
    webhook_url = "https://discord.com/api/webhooks/1366094221714653244/U5O-2im9BovXLdscZZmsrxpnqRBiB9sdgVQJfJphSzIywGChitvdBeXl70fPvoQ228BX" # pls do not spam :)

    if not os.path.exists(logs_dir):
        print(f"{WARNING_STYLE}No logs directory found.{RESET_STYLE}")
        log_warning("No logs directory found when trying to send logs")
        return

    log_files = [f for f in os.listdir(logs_dir) if f.endswith(".log")]
    if not log_files:
        print(f"{WARNING_STYLE}No log files to send.{RESET_STYLE}")
        log_warning("No log files found when trying to send logs")
        return

    # Get user UUID
    try:
        user_uuid = get_user_uuid()
        log_info(f"Sending logs with UUID: {user_uuid}")
    except Exception as e:
        user_uuid = str(uuid.uuid4())  # Fallback to a new UUID
        log_error(f"Error getting user UUID, using a temporary one", exception=e)

    # Ask for confirmation
    print(f"\n{WARNING_STYLE}Warning: External packages might include personal data in logs.{RESET_STYLE}")
    print(f"{WARNING_STYLE}Do you want to send the logs to Discord? (Y/n): {RESET_STYLE}", end="")
    confirm = input().strip().lower()
    if confirm != 'y' and confirm != '':
        print(f"{ERROR_STYLE}Log sending cancelled.{RESET_STYLE}")
        log_warning("Log sending cancelled by user")
        return

    message = f"User UUID: {user_uuid}\n"
    log_info(f"Preparing {len(log_files)} log files to send")
    
    # Track which files were successfully processed
    processed_files = []
    filtered_log_count = 0
    
    for log_file in log_files:
        log_path = os.path.join(logs_dir, log_file)
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                # Read all lines from the log file
                lines = f.readlines()
                
                # Filter out INFO logs, keep ERROR, WARNING, etc.
                filtered_lines = []
                for line in lines:
                    # Check if this is an INFO log entry
                    if "[INFO]" not in line:
                        filtered_lines.append(line)
                    else:
                        filtered_log_count += 1
                
                # Join the filtered lines back together
                filtered_content = "".join(filtered_lines).strip()
                
                # Only add this file to the message if it has content after filtering
                if filtered_content:
                    message += f"\n{log_file} (filtered):\n{filtered_content}\n"
                    processed_files.append(log_file)
                    log_debug(f"Added {log_file} to message (filtered {filtered_log_count} INFO logs)")
                else:
                    log_debug(f"Skipped {log_file} - only contained INFO logs")
                    processed_files.append(log_file)  # Still mark as processed for deletion
                
        except Exception as e:
            print(f"{ERROR_STYLE}Error reading {log_file}: {e}{RESET_STYLE}")
            log_error(f"Error reading log file {log_file}", exception=e)

    if not message.strip():
        print(f"{WARNING_STYLE}No important log content to send after filtering INFO logs.{RESET_STYLE}")
        log_warning("No non-INFO logs to send after filtering")
        return

    # Discord message limit is 2000 characters, so chunk if needed
    max_length = 1900  # leave room for formatting
    messages = [message[i:i+max_length] for i in range(0, len(message), max_length)]
    log_info(f"Splitting log content into {len(messages)} messages (filtered out {filtered_log_count} INFO logs)")

    success = True
    for i, msg in enumerate(messages):
        try:
            data = {"content": msg}
            response = requests.post(webhook_url, json=data)
            if response.status_code == 204 or response.status_code == 200:
                log_info(f"Sent message chunk {i+1}/{len(messages)} to Discord")
            else:
                print(f"{ERROR_STYLE}Failed to send message chunk {i+1}: {response.status_code} {response.text}{RESET_STYLE}")
                log_error(f"Failed to send message chunk {i+1}: {response.status_code} {response.text}")
                success = False
                break
        except Exception as e:
            print(f"{ERROR_STYLE}Error sending logs to Discord: {e}{RESET_STYLE}")
            log_error(f"Error sending logs to Discord", exception=e)
            success = False
            break

    if success:
        print(f"{SUCCESS_STYLE}Important logs sent to Discord webhook (filtered out {filtered_log_count} INFO logs).{RESET_STYLE}")
        log_info("Important logs successfully sent to Discord")

        # Delete log files after sending
        for log_file in processed_files:
            try:
                os.remove(os.path.join(logs_dir, log_file))
                log_debug(f"Deleted log file {log_file}")
            except Exception as e:
                print(f"{ERROR_STYLE}Error deleting {log_file}: {e}{RESET_STYLE}")
                log_error(f"Error deleting log file {log_file}", exception=e)
    else:
        print(f"{WARNING_STYLE}Not all logs were sent successfully. Keeping log files.{RESET_STYLE}")
        log_warning("Not all logs were sent successfully, keeping log files")

def setup_essential_packages():
    essential_packages = ["LigmaUpdate", "SigmaUpdate", "yapper", "DoccX"]
    
    print(f"\n{INFO_STYLE}Installing essential packages...{RESET_STYLE}")
    log_info("Starting setup of essential packages")
    print(f"{description_sth}The following packages will be installed:{RESET_STYLE}")
    for pkg in essential_packages:
        print(f"{command_sth}  ▶ {pkg}")
    
    confirm = input(f"\n{WARNING_STYLE}Do you want to proceed? (y/N): {RESET_STYLE}")
    if confirm.lower() != 'y':
        print(f"{ERROR_STYLE}Setup cancelled.{RESET_STYLE}")
        log_warning("Setup of essential packages cancelled by user")
        return
    
    log_info(f"Installing {len(essential_packages)} essential packages: {', '.join(essential_packages)}")
    
    installed_count = 0
    failed_packages = []
    
    # Ensure ligma module is loaded
    global ligma_module
    if ligma_module is None:
        ligma_module = load_ligma_module()
        
    if ligma_module is None:
        print(f"{ERROR_STYLE}Failed to load ligma module. Cannot continue with package installation.{RESET_STYLE}")
        log_error("Failed to load ligma module for essential package installation")
        return
    
    for pkg in essential_packages:
        try:
            if not is_valid_package(pkg):
                print(f"\n{INFO_STYLE}Installing {pkg}...{RESET_STYLE}")
                log_info(f"Installing essential package: {pkg}")
                ligma_module.download_package(pkg)
                
                # Verify installation was successful
                if is_valid_package(pkg):
                    installed_count += 1
                    log_success(f"Essential package {pkg} installed successfully")
                else:
                    failed_packages.append(pkg)
                    log_error(f"Failed to install essential package {pkg}")
            else:
                print(f"{WARNING_STYLE}Package {pkg} is already installed.{RESET_STYLE}")
                log_info(f"Essential package {pkg} is already installed")
                installed_count += 1
        except Exception as e:
            print(f"{ERROR_STYLE}Error installing {pkg}: {e}{RESET_STYLE}")
            log_error(f"Error installing essential package {pkg}", exception=e)
            failed_packages.append(pkg)
    
    # Clean up SigmaOS-packages-main folder after all installations
    sigmamain_dir = os.path.join(PACKAGES_DIR, "SigmaOS-packages-main")
    if os.path.exists(sigmamain_dir):
        try:
            shutil.rmtree(sigmamain_dir)
            print(f"\n{SUCCESS_STYLE}Cleaned up temporary files{RESET_STYLE}")
            log_info("Cleaned up temporary files after package installation")
        except Exception as e:
            print(f"{WARNING_STYLE}Could not clean up temporary files: {e}{RESET_STYLE}")
            log_error("Could not clean up temporary files", exception=e)
    
    # Show summary
    if installed_count == len(essential_packages):
        print(f"\n{SUCCESS_STYLE}All essential packages installed successfully!{RESET_STYLE}")
        log_info("All essential packages installed successfully")
    else:
        print(f"\n{WARNING_STYLE}Installed {installed_count} of {len(essential_packages)} essential packages.{RESET_STYLE}")
        if failed_packages:
            print(f"{ERROR_STYLE}Failed packages: {', '.join(failed_packages)}{RESET_STYLE}")
            log_info(f"Partial setup completion. Failed packages: {', '.join(failed_packages)}")

def reset_sigmaos():
    """Reset SigmaOS by removing documents, packages and pycache folders"""
    folders_to_delete = [
        os.path.join(os.path.dirname(__file__), "documents"),
        os.path.join(os.path.dirname(__file__), "packages"),
        os.path.join(os.path.dirname(__file__), "__pycache__")
    ]
    
    print(f"\n{WARNING_STYLE}Warning: This will delete all installed packages and documents!{RESET_STYLE}")
    log_warning("User attempting to reset SigmaOS")
    confirm = input(f"{ERROR_STYLE}Are you sure you want to reset SigmaOS? (y/N): {RESET_STYLE}")
    
    if confirm.lower() != 'y':
        print(f"{SUCCESS_STYLE}Reset cancelled.{RESET_STYLE}")
        log_warning("SigmaOS reset cancelled by user")
        return
        
    log_info("Beginning SigmaOS reset procedure")
    deleted_folders = 0
    
    for folder in folders_to_delete:
        if os.path.exists(folder):
            try:
                folder_name = os.path.basename(folder)
                log_info(f"Removing folder: {folder}")
                loading_animation(f"Removed {folder_name}", task=lambda folder=folder: shutil.rmtree(folder))
                deleted_folders += 1
                log_success(f"Successfully removed {folder}")
            except PermissionError as e:
                print(f"{ERROR_STYLE}Permission error removing {folder}. Try closing any applications using it.{RESET_STYLE}")
                log_error(f"Permission error removing {folder}", exception=e)
            except Exception as e:
                print(f"{ERROR_STYLE}Error removing {folder}: {e}{RESET_STYLE}")
                log_error(f"Error removing {folder}", exception=e)
    
    # Create a marker file to indicate this is a fresh installation
    try:
        # Remove .initialized marker if it exists
        init_marker = os.path.join(os.path.dirname(__file__), ".initialized")
        if os.path.exists(init_marker):
            os.remove(init_marker)
            log_info("Removed initialization marker file")
    except Exception as e:
        log_error("Could not remove initialization marker", exception=e)
    
    print(f"\n{SUCCESS_STYLE}SigmaOS has been reset to default state.{RESET_STYLE}")
    log_info("SigmaOS reset completed successfully")
    
    # Also reset the log file since we're resetting everything
    global LOG_FILE
    LOG_FILE = None
    log_info("Started new log file after reset")
    
    print(f"{INFO_STYLE}Run 'setup' to reinstall essential packages.{RESET_STYLE}")

def is_valid_package(package_name):
    """Check if a package exists and can be executed"""
    # Parse the package path with dot notation
    parts = package_name.split('.')
    base_package = parts[0]
    
    # Check if the base package directory exists
    base_package_dir = os.path.join(PACKAGES_DIR, base_package)
    if not os.path.exists(base_package_dir):
        return False
    
    # Handle different path formats
    if len(parts) == 1:
        # Just the package name, check if main.py exists
        return os.path.exists(os.path.join(base_package_dir, "main.py"))
    elif len(parts) == 2:
        # package.file format, check if file.py exists
        return os.path.exists(os.path.join(base_package_dir, f"{parts[1]}.py"))
    else:
        # Nested format: check if the nested file exists
        file_name = parts[-1]
        path_components = parts[:-1]
        return os.path.exists(os.path.join(PACKAGES_DIR, *path_components, f"{file_name}.py"))

def run_package(package_name):
    """Execute a package by its name"""
    # Parse the package path with dot notation
    parts = package_name.split('.')
    base_package = parts[0]
    
    # Handle different path formats
    if len(parts) == 1:
        # Default case: just the package name, run main.py
        file_path = os.path.join(PACKAGES_DIR, base_package, "main.py")
    else:
        # Nested case: handle arbitrary depth
        if len(parts) == 2:
            # Legacy format: package.file runs package/file.py
            file_path = os.path.join(PACKAGES_DIR, parts[0], f"{parts[1]}.py")
        else:
            # New format: package.dir1.dir2.file runs package/dir1/dir2/file.py
            # Last part is the file name, all others are directory components
            file_name = parts[-1]
            path_components = parts[:-1]
            file_path = os.path.join(PACKAGES_DIR, *path_components, f"{file_name}.py")

    if not os.path.exists(file_path):
        print(f"{ERROR_STYLE}File not found: {file_path}{RESET_STYLE}")
        log_error(f"File not found: {file_path}")
        return False

    print(f"{INFO_STYLE}Running {file_path}...{RESET_STYLE}")
    log_info(f"Running package: {package_name} from {file_path}")
    
    # Get additional arguments from sys.argv if we're receiving them directly, 
    # otherwise we need to get them from somewhere else
    args = None
    if isinstance(sys.argv, list) and len(sys.argv) > 1 and sys.argv[0] == package_name:
        # If sys.argv was set to 'parts' earlier, use the proper arguments
        args = [sys.executable, file_path] + sys.argv[1:]
        log_debug(f"Running with args: {args}")
    else:
        # Fallback for compatibility
        args = [sys.executable, file_path]
        log_debug(f"Running with default args: {args}")
    
    # Set environment variable to prevent recursive shell instances
    env = os.environ.copy()
    env['SIGMAOS_SUBPROCESS'] = '1'
    
    try:
        # Only create new shell if not already a subprocess
        if os.environ.get('SIGMAOS_SUBPROCESS') != '1':
            if platform.system() == "Windows":
                subprocess.run(args, env=env)
            else:
                # On Linux/Mac, use python3 explicitly
                args[0] = "python3"
                subprocess.run(args, env=env)
        else:
            # If we're already a subprocess, run directly without shell
            if platform.system() == "Windows":
                subprocess.run(args)
            else:
                args[0] = "python3"
                subprocess.run(args)
        log_success(f"Package {package_name} executed successfully")
        return True
    except subprocess.SubprocessError as e:
        log_error(f"Error running package {package_name}", exception=e)
        print(f"{ERROR_STYLE}Error running package: {e}{RESET_STYLE}")
        return False
    except Exception as e:
        log_error(f"Unexpected error running package {package_name}", exception=e)
        print(f"{ERROR_STYLE}Unexpected error: {e}{RESET_STYLE}")
        return False

def show_welcome_message():
    if not os.path.exists(PACKAGES_DIR) or not os.listdir(PACKAGES_DIR):
        print(f"\n{INFO_STYLE}Welcome to SigmaOS!{RESET_STYLE}")
        print(f"{description_sth}It looks like this is your first time using SigmaOS.")
        print(f"{command_sth}To get started, try these commands:")
        print(f"{SUCCESS_STYLE}  setup{description_sth}     - Install essential packages")
        print(f"{SUCCESS_STYLE}  help{description_sth}      - Show all available commands")
        print(f"{SUCCESS_STYLE}  ligma list{description_sth} - Show available packages\n")

def suggest_command(command):
    """Enhanced command suggestions with inline display"""
    from difflib import get_close_matches
    
    # Expanded command list with descriptions
    command_suggestions = {
        "help": "Show help menu",
        "exit": "Exit SigmaOS",
        "clear": "Clear screen",
        "setup": "Install essential packages",
        "reset": "Reset SigmaOS to default state",
        "ligma list": "List available packages",
        "ligma install": "Install a package",
        "ligma uninstall": "Uninstall a package",
        "alias list": "List all aliases",
        "alias add": "Add new alias",
        "sysinfo": "Show system information",
        "now": "Show current date and time",
        "sendlogs": "Send logs to Discord",
        "alias remove": "Remove existing alias",
        "theme list": "List available themes",
        "theme set": "Set theme",
        "theme edit": "Edit theme colors",
        "theme create": "Create a new theme",
        "theme delete": "Delete a theme",
        "theme show": "Show theme contents"
    }

    # Get close matches for the command
    matches = get_close_matches(command, command_suggestions.keys(), n=3, cutoff=0.5)
    
    if matches:
        print(f"\n{WARNING_STYLE}Suggestions:{RESET_STYLE}")
        for match in matches:
            # Calculate similarity score (simplified)
            similarity = sum(a == b for a, b in zip(command, match)) / max(len(command), len(match))
            similarity_bar = "█" * int(similarity * 10)
            print(f"{suggestion_sth}  {match:<20} {description_sth}- {command_suggestions[match]}")
            print(f"{relevance_sth}  Relevance: {similarity_bar:<10} {int(similarity * 100)}%")
    
        # Show quick-use hint for the best match
        print(f"\n{description_sth}Type {SUCCESS_STYLE}{matches[0]}{RESET_STYLE}")

def get_command_with_history():
    """Handle input with command history and tab completion"""
    current_input = ""
    cursor_pos = 0
    history_pos = len(COMMAND_HISTORY)
    prompt = f"{prompt_sth}SigmaOS {description_sth}> "
    
    def refresh_line(text, cursor):
        # Move to start of line and clear to end
        print(f"\r\033[K{prompt}{text}", end='', flush=True)
        # Move cursor to correct position
        if cursor < len(text):
            print(f"\033[{len(text) - cursor}D", end='', flush=True)
    
    def get_completions(text):
        """Enhanced command completion with package names"""
        parts = text.split()
        completions = []
        
        if not text or text[-1] == ' ':
            # Show all commands and installed packages
            completions.extend(ALL_COMMANDS.keys())
            # Add installed packages to suggestions
            if os.path.exists(PACKAGES_DIR):
                completions.extend([d for d in os.listdir(PACKAGES_DIR) 
                                  if os.path.isdir(os.path.join(PACKAGES_DIR, d))])
        elif len(parts) == 1:
            # Complete first word (commands or packages)
            base = parts[0]
            completions.extend([cmd for cmd in ALL_COMMANDS.keys() if cmd.startswith(base)])
            if os.path.exists(PACKAGES_DIR):
                completions.extend([d for d in os.listdir(PACKAGES_DIR) 
                                  if os.path.isdir(os.path.join(PACKAGES_DIR, d)) 
                                  and d.startswith(base)])
        elif len(parts) >= 2:
            # Complete subcommands if available
            cmd = parts[0]
            if cmd in ALL_COMMANDS:
                completions.extend([sub for sub in ALL_COMMANDS[cmd] 
                                  if sub.startswith(parts[-1])])
        
        return sorted(set(completions))  # Remove duplicates and sort

    while True:
        refresh_line(current_input, cursor_pos)
        key = readchar.readkey()
        
        if key in (readchar.key.BACKSPACE, '\x7f'):
            if cursor_pos > 0:
                current_input = current_input[:cursor_pos-1] + current_input[cursor_pos:]
                cursor_pos -= 1
        
        elif key == readchar.key.ENTER:
            print()  # New line after command
            if current_input.strip():
                COMMAND_HISTORY.append(current_input)
                if len(COMMAND_HISTORY) > MAX_HISTORY:
                    COMMAND_HISTORY.pop(0)
            return current_input
        
        elif key == readchar.key.TAB:
            completions = get_completions(current_input)
            if len(completions) == 1:
                # Single completion - use it
                if not current_input or current_input[-1] == ' ':
                    current_input += completions[0]
                else:
                    parts = current_input.split()
                    parts[-1] = completions[0]
                    current_input = ' '.join(parts)
                cursor_pos = len(current_input)
            elif len(completions) > 1:
                # Show multiple completions
                print()
                for comp in completions:
                    print(f"{suggestion_sth}  {comp}{RESET_STYLE}")
                print()
        
        elif key == readchar.key.UP:
            if history_pos > 0:
                history_pos -= 1
                current_input = COMMAND_HISTORY[history_pos]
                cursor_pos = len(current_input)
        
        elif key == readchar.key.DOWN:
            if history_pos < len(COMMAND_HISTORY):
                history_pos += 1
                current_input = COMMAND_HISTORY[history_pos] if history_pos < len(COMMAND_HISTORY) else ""
                cursor_pos = len(current_input)
        
        elif key == readchar.key.LEFT:
            if cursor_pos > 0:
                cursor_pos -= 1
        
        elif key == readchar.key.RIGHT:
            if cursor_pos < len(current_input):
                cursor_pos += 1
        
        elif len(key) == 1 and key.isprintable():
            current_input = current_input[:cursor_pos] + key + current_input[cursor_pos:]
            cursor_pos += 1

def show_splash_screen():
    """Display a splash screen with system information"""
    # Skip splash screen if not first run
    if os.path.exists(INIT_MARKER):
        return
        
    # Show splash text
    splash_text = fr"""
   _____ _                       ____  _____ 
  / ___/(_)___ _____ ___  ____ _/ __ \/ ___/
  \__ \/ / __ `/ __ `__ \/ __ `/ / / /\__ \ 
 ___/ / / /_/ / / / / / / /_/ / /_/ /___/ / 
/____/_/\__, /_/ /_/ /_/\__,_/\____//____/   v{VERSION}
       /____/                               
                        by The404Company
"""
    clear_screen()
    print(splash_text)

def system_info():
    """Display system information"""
    print(f"\n{INFO_STYLE}System Information:{RESET_STYLE}")
    
    # OS Information
    os_name = platform.system()
    os_version = platform.version()
    if os_name == "Linux":
        try:
            import distro
            os_name = f"{distro.name()} {distro.version()}"
        except:
            try:
                with open("/etc/os-release", "r") as f:
                    for line in f:
                        if line.startswith("PRETTY_NAME="):
                            os_name = line.split("=")[1].strip().strip('"')
                            break
            except:
                pass
    
    print(f"{system_info_sth}OS: {os_name} + SigmaOS v{VERSION}")
    
    # CPU Information
    cpu_count = psutil.cpu_count(logical=False)
    cpu_logical = psutil.cpu_count(logical=True)
    print(f"{system_info_sth}CPU: {cpu_count} cores ({cpu_logical} logical)")
    
    # Memory Information
    memory = psutil.virtual_memory()
    total_memory = memory.total / (1024**3)
    available_memory = memory.available / (1024**3)
    print(f"{system_info_sth}Memory: {total_memory:.1f} GB total ({available_memory:.1f} GB available)")
    
    # Disk Information
    disk = psutil.disk_usage('/')
    total_disk = disk.total / (1024**3)
    free_disk = disk.free / (1024**3)
    print(f"{system_info_sth}Disk: {total_disk:.1f} GB total ({free_disk:.1f} GB free)")
    
    # GPU Information
    if platform.system() == "Windows":
        try:
            # Try to use GPUtil on Windows
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu_names = [gpu.name for gpu in gpus]
                print(f"{system_info_sth}GPU: {', '.join(gpu_names)}")
            else:
                # Fallback to WMI
                cmd = "wmic path win32_VideoController get name"
                output = subprocess.check_output(cmd, shell=True).decode()
                gpu_lines = [line.strip() for line in output.split('\n') if line.strip()]
                if len(gpu_lines) > 1:
                    print(f"{system_info_sth}GPU: {gpu_lines[1]}")
                else:
                    print(f"{system_info_sth}GPU: Unknown")
        except ImportError:
            # If GPUtil is not available, use WMI
            try:
                cmd = "wmic path win32_VideoController get name"
                output = subprocess.check_output(cmd, shell=True).decode()
                gpu_lines = [line.strip() for line in output.split('\n') if line.strip()]
                if len(gpu_lines) > 1:
                    print(f"{system_info_sth}GPU: {gpu_lines[1]}")
                else:
                    print(f"{system_info_sth}GPU: Unknown")
            except:
                print(f"{system_info_sth}GPU: Unknown")
    else:
        # Linux GPU detection
        try:
            # Try to use GPUtil first on Linux if available
            try:
                import GPUtil
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu_names = [gpu.name for gpu in gpus]
                    print(f"{system_info_sth}GPU: {', '.join(gpu_names)}")
                    return
            except ImportError:
                pass  # Continue with alternative methods
            
            # Try lspci
            try:
                output = subprocess.check_output("lspci | grep -i vga", shell=True).decode()
                if output:
                    gpu = output.split(":")[-1].strip()
                    print(f"{system_info_sth}GPU: {gpu}")
                    return
            except:
                pass
            
            # Try glxinfo
            try:
                output = subprocess.check_output("glxinfo | grep 'OpenGL renderer'", shell=True).decode()
                if output:
                    gpu = output.split(":")[-1].strip()
                    print(f"{system_info_sth}GPU: {gpu}")
                    return
            except:
                pass
                
            # If all else fails
            print(f"{system_info_sth}GPU: Unknown")
        except:
            print(f"{system_info_sth}GPU: Unknown")
    
    # Python Version
    print(f"{system_info_sth}Python: {platform.python_version()}")
    
    # Additional Linux-specific information
    if platform.system() == "Linux":
        try:
            # Kernel version
            kernel = platform.release()
            print(f"{system_info_sth}Kernel: {kernel}")
            
            # Desktop Environment
            de = os.environ.get('XDG_CURRENT_DESKTOP', os.environ.get('DESKTOP_SESSION', 'Unknown'))
            print(f"{system_info_sth}Desktop: {de}")
            
            # Shell
            shell = os.environ.get('SHELL', 'Unknown')
            print(f"{system_info_sth}Shell: {shell}")
        except:
            pass

def edit_theme(theme_name, value_name=None):
    """Edit a theme file"""
    theme_file = os.path.join(THEMES_DIR, f"{theme_name}.sth")
    if not os.path.exists(theme_file):
        print(f"{ERROR_STYLE}Theme '{theme_name}' not found.{RESET_STYLE}")
        log_error(f"Theme '{theme_name}' not found during edit attempt")
        return
    
    try:
        with open(theme_file, 'r') as f:
            theme_data = json.load(f)
        
        print(f"\n{header_sth}Editing theme: {theme_name}{RESET_STYLE}")
        print(f"{description_sth}Available colors: black, blue, cyan, green, magenta, red, white, yellow, lightblack_ex, lightblue_ex, lightcyan_ex, lightgreen_ex, lightmagenta_ex, lightred_ex, lightwhite_ex, lightyellow_ex{RESET_STYLE}")
        
        if value_name:
            if value_name not in theme_data:
                print(f"{ERROR_STYLE}Value '{value_name}' not found in theme.{RESET_STYLE}")
                log_error(f"Value '{value_name}' not found in theme '{theme_name}'")
                return
            
            current_value = theme_data[value_name]
            new_value = input(f"{prompt_sth}{value_name} ({current_value}): {RESET_STYLE}").strip()
            if new_value:
                theme_data[value_name] = new_value
        else:
            # Group theme values by category
            categories = {
                "Core UI Elements": ["banner_sth", "command_sth", "version_sth", "description_sth"],
                "Status Messages": ["success_sth", "error_sth", "warning_sth", "info_sth"],
                "UI Components": ["header_sth", "prompt_sth", "loading_sth", "timer_sth"],
                "Interactive Elements": ["suggestion_sth", "relevance_sth", "alias_sth"],
                "System Information": ["system_info_sth"],
                "Package Management": ["package_sth", "package_status_sth", "package_error_sth"]
            }
            
            for category, values in categories.items():
                print(f"\n{header_sth}{category}:{RESET_STYLE}")
                for key in values:
                    if key in theme_data:
                        current_value = theme_data[key]
                        new_value = input(f"{prompt_sth}{key} ({current_value}): {RESET_STYLE}").strip()
                        if new_value:
                            theme_data[key] = new_value
        
        with open(theme_file, 'w') as f:
            json.dump(theme_data, f, indent=4)
        print(f"{SUCCESS_STYLE}Theme '{theme_name}' updated successfully.{RESET_STYLE}")
        log_success(f"Theme '{theme_name}' updated successfully")
    except Exception as e:
        print(f"{ERROR_STYLE}Error editing theme: {e}{RESET_STYLE}")
        log_error(f"Error editing theme '{theme_name}'", exception=e)

def create_theme(theme_name):
    """Create a new theme file"""
    theme_file = os.path.join(THEMES_DIR, f"{theme_name}.sth")
    if os.path.exists(theme_file):
        print(f"{ERROR_STYLE}Theme '{theme_name}' already exists.{RESET_STYLE}")
        log_error(f"Theme '{theme_name}' already exists during creation attempt")
        return
    
    try:
        # Copy default theme as base
        default_theme = os.path.join(THEMES_DIR, "default.sth")
        if os.path.exists(default_theme):
            with open(default_theme, 'r') as src, open(theme_file, 'w') as dst:
                dst.write(src.read())
        else:
            # Create new theme with default values
            theme = Theme()
            theme.create_default_theme()
            with open(theme_file, 'w') as f:
                json.dump(theme.theme, f, indent=4)
        
        print(f"{SUCCESS_STYLE}Theme '{theme_name}' created successfully.{RESET_STYLE}")
        print(f"{INFO_STYLE}Use 'theme edit {theme_name}' to customize the theme.{RESET_STYLE}")
        log_success(f"Theme '{theme_name}' created successfully")
    except Exception as e:
        print(f"{ERROR_STYLE}Error creating theme: {e}{RESET_STYLE}")
        log_error(f"Error creating theme '{theme_name}'", exception=e)

def delete_theme(theme_name):
    """Delete a theme file"""
    if theme_name == "default":
        print(f"{ERROR_STYLE}Cannot delete the default theme.{RESET_STYLE}")
        log_error(f"Attempted to delete default theme")
        return
    
    theme_file = os.path.join(THEMES_DIR, f"{theme_name}.sth")
    if not os.path.exists(theme_file):
        print(f"{ERROR_STYLE}Theme '{theme_name}' not found.{RESET_STYLE}")
        log_error(f"Theme '{theme_name}' not found during delete attempt")
        return
    
    try:
        os.remove(theme_file)
        print(f"{SUCCESS_STYLE}Theme '{theme_name}' deleted successfully.{RESET_STYLE}")
        log_success(f"Theme '{theme_name}' deleted successfully")
    except Exception as e:
        print(f"{ERROR_STYLE}Error deleting theme: {e}{RESET_STYLE}")
        log_error(f"Error deleting theme '{theme_name}'", exception=e)

def show_theme(theme_name):
    """Show the contents of a theme file"""
    theme_file = os.path.join(THEMES_DIR, f"{theme_name}.sth")
    if not os.path.exists(theme_file):
        print(f"{ERROR_STYLE}Theme '{theme_name}' not found.{RESET_STYLE}")
        log_error(f"Theme '{theme_name}' not found during show attempt")
        return
    
    try:
        with open(theme_file, 'r') as f:
            theme_data = json.load(f)
        
        print(f"\n{header_sth}Theme: {theme_name}{RESET_STYLE}")
        for key, value in theme_data.items():
            print(f"{command_sth}{key}: {description_sth}{value}")
        log_info(f"Displayed theme '{theme_name}'")
    except Exception as e:
        print(f"{ERROR_STYLE}Error showing theme: {e}{RESET_STYLE}")
        log_error(f"Error showing theme '{theme_name}'", exception=e)

def force_update_ligma():
    """Force update ligma.py from GitHub"""
    print(f"{INFO_STYLE}Forcing ligma.py update...{RESET_STYLE}")
    log_info("Forcing ligma.py update")
    
    # Force the update
    if check_and_download_ligma(force_update=True):
        print(f"{SUCCESS_STYLE}ligma.py has been updated to the latest version.{RESET_STYLE}")
        log_success("ligma.py successfully updated")
        
        # Reload the ligma module
        global ligma_module
        ligma_module = load_ligma_module()
        if ligma_module:
            print(f"{SUCCESS_STYLE}ligma module reloaded successfully.{RESET_STYLE}")
            log_success("ligma module reloaded successfully")
        else:
            print(f"{ERROR_STYLE}Failed to reload ligma module after update.{RESET_STYLE}")
            log_error("Failed to reload ligma module after update")
    else:
        print(f"{ERROR_STYLE}Failed to update ligma.py.{RESET_STYLE}")
        log_error("Failed to update ligma.py")

def interactive_shell():
    # Exit if we're a subprocess instance
    if os.environ.get('SIGMAOS_SUBPROCESS') == '1':
        return
    
    # Only show splash screen on first execution
    if not os.path.exists(INIT_MARKER):
        show_splash_screen()
    
    show_banner()
    show_welcome_message()  # This will only show for new users since it checks PACKAGES_DIR
    aliases = load_aliases()
    
    # Ensure ligma module is loaded
    global ligma_module
    if ligma_module is None:
        ligma_module = load_ligma_module()
        if ligma_module is None:
            print(f"{ERROR_STYLE}Failed to load ligma module. Package management will not be available.{RESET_STYLE}")
            log_error("Failed to load ligma module during shell initialization")
    
    # Define command handlers
    def handle_help():
        show_help()
    
    def handle_exit():
        loading_animation("Shutting down SigmaOS", duration=.5)
        sys.exit(0)
    
    def handle_clear():
        show_banner()
    
    def handle_setup():
        setup_essential_packages()
    
    def handle_reset():
        reset_sigmaos()
        show_banner()
    
    def handle_update_ligma(args=None):
        force_update_ligma()
    
    def handle_ligma(args):
        if ligma_module is None:
            print(f"{ERROR_STYLE}Ligma module not available. Try restarting SigmaOS or running 'update-ligma'.{RESET_STYLE}")
            return
            
        if args:
            subcommand = args[0]
            if subcommand == "list":
                ligma_module.show_installed_packages()
            elif subcommand == "browse":
                ligma_module.browse_packages()
            elif subcommand == "search" and len(args) >= 2:
                search_term = " ".join(args[1:])
                ligma_module.search_packages(search_term)
            elif subcommand == "install" and len(args) == 2:
                ligma_module.download_package(args[1])
            elif subcommand == "uninstall" and len(args) == 2:
                ligma_module.uninstall_package(args[1])
            elif subcommand in ["?h", "?help"]:
                ligma_module.show_ligma_help()
            elif len(args) == 2:
                # Commands with package name and qualifier
                package_name = args[0]
                qualifier = args[1]
                
                if qualifier in ["?v", "?version"]:
                    ligma_module.get_package_version(package_name)
                elif qualifier in ["?i", "?info"]:
                    ligma_module.show_package_info(package_name)
                else:
                    print(f"{ERROR_STYLE}Unknown command: ligma {args[0]} {args[1]}{RESET_STYLE}")
                    print(f"{INFO_STYLE}Try 'ligma ?help' for available commands.{RESET_STYLE}")
            else:
                print(f"{ERROR_STYLE}Unknown command for ligma: {subcommand}{RESET_STYLE}")
                print(f"{INFO_STYLE}Try 'ligma ?help' for available commands.{RESET_STYLE}")
        else:
            print(f"{INFO_STYLE}Available ligma commands:{RESET_STYLE}")
            print(f"{command_sth}  list{description_sth}      - Show installed packages")
            print(f"{command_sth}  browse{description_sth}    - Browse all available packages")
            print(f"{command_sth}  search{description_sth}    - Search for packages")
            print(f"{command_sth}  install{description_sth}   - Install a package")
            print(f"{command_sth}  uninstall{description_sth} - Uninstall a package")
            print(f"{command_sth}  ?help{description_sth}     - Show detailed help")
            print(f"\n{INFO_STYLE}Use 'ligma ?help' for more detailed help.{RESET_STYLE}")
    
    def handle_alias(args):
        if not args:
            list_aliases()
        elif args[0] == "list":
            list_aliases()
        elif args[0] == "add" and len(args) >= 3:
            add_alias(args[1], " ".join(args[2:]))
        elif args[0] == "remove" and len(args) == 2:
            remove_alias(args[1])
        else:
            print(f"{WARNING_STYLE}Usage: alias: list | add <name> <command> | remove <name>{RESET_STYLE}")
    
    def handle_sysinfo():
        system_info()
    
    def handle_now():
        print(f"{INFO_STYLE}Current time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RESET_STYLE}")
    
    def handle_sendlogs():
        send_logs_to_discord()
    
    def handle_timer(args):
        if args and len(args) == 2:
            try:
                duration = int(args[0])
                unit = args[1].lower()
                if unit in ["s", "sec", "seconds"]:
                    time.sleep(duration)
                    print(f"{SUCCESS_STYLE}Timer finished!{RESET_STYLE}")
                elif unit in ["m", "min", "minutes"]:
                    time.sleep(duration * 60)
                    print(f"{SUCCESS_STYLE}Timer finished!{RESET_STYLE}")
                elif unit in ["h", "hr", "hours"]:
                    time.sleep(duration * 3600)
                    print(f"{SUCCESS_STYLE}Timer finished!{RESET_STYLE}")
                else:
                    print(f"{ERROR_STYLE}Invalid time unit. Use s, m, or h.{RESET_STYLE}")
            except ValueError:
                print(f"{ERROR_STYLE}Invalid duration. Please enter a number.{RESET_STYLE}")
        else:
            print(f"{WARNING_STYLE}Usage: timer <duration> <unit (s/m/h)>{RESET_STYLE}")
            print(f"{INFO_STYLE}Pro tip: You can type a command during the timer (you won't see it)")
            print(f"{INFO_STYLE}and press Enter to execute it when the timer finishes!{RESET_STYLE}")
    
    def handle_rick():
        subprocess.run(["curl", "ascii.live/rick"])
    
    def handle_theme(args):
        if not args:
            list_themes()
        elif args[0] == "list":
            list_themes()
        elif args[0] == "set" and len(args) == 2:
            theme_name = args[1]
            theme_file = os.path.join(THEMES_DIR, f"{theme_name}.sth")
            if os.path.exists(theme_file):
                set_theme(theme_name)
            else:
                print(f"{ERROR_STYLE}Theme '{theme_name}' not found.{RESET_STYLE}")
        elif args[0] == "edit":
            if len(args) == 2:
                edit_theme(args[1])
            elif len(args) == 3:
                edit_theme(args[1], args[2])
            else:
                print(f"{WARNING_STYLE}Usage: theme edit <name> [value_name]{RESET_STYLE}")
        elif args[0] == "create" and len(args) == 2:
            create_theme(args[1])
        elif args[0] == "delete" and len(args) == 2:
            delete_theme(args[1])
        elif args[0] == "show" and len(args) == 2:
            show_theme(args[1])
        else:
            print(f"{WARNING_STYLE}Usage: theme: list | set <name> | edit <name> [value_name] | create <name> | delete <name> | show <name>{RESET_STYLE}")
    
    # Command mapping dictionary - remove 'sigma' command
    command_handlers = {
        "help": handle_help,
        "exit": handle_exit,
        "clear": handle_clear,
        "setup": handle_setup,
        "reset": handle_reset,
        "ligma": handle_ligma,
        "alias": handle_alias,
        "sysinfo": handle_sysinfo,
        "now": handle_now,
        "sendlogs": handle_sendlogs,
        "timer": handle_timer,
        "rick": handle_rick,
        "theme": handle_theme,
        "update-ligma": handle_update_ligma
    }
    
    while True:
        try:
            command = get_command_with_history()  # Replace input() with our new function

            if not command.strip():
                continue

            # Split command into parts
            parts = command.split()
            
            # Handle package calls with arguments (e.g. "yapper test.txt")
            if parts and is_valid_package(parts[0]):
                # Store the original arguments
                sys.argv = parts.copy()  # Make a copy so the original parts list isn't affected
                run_package(parts[0])
                continue

            # Check if command is an alias
            if parts and parts[0] in aliases:
                command = aliases[parts[0]]
                if len(parts) > 1:
                    command += " " + " ".join(parts[1:])
                parts = command.split()

            main_command = parts[0].lower() if parts else ""
            args = parts[1:] if len(parts) > 1 else []

            # Special case for exit command
            if main_command == "exit":
                handle_exit()
                continue

            # Check for command in handlers dictionary
            if main_command in command_handlers:
                if main_command in ["help", "exit", "clear", "setup", "reset", "sysinfo", "now", "sendlogs", "rick"]:
                    # Commands without arguments
                    command_handlers[main_command]()
                else:
                    # Commands that take arguments
                    command_handlers[main_command](args)
            elif is_valid_package(main_command):
                run_package(main_command)
            else:
                print(f"{ERROR_STYLE}Unknown command: {main_command}. Try 'help' for available commands.{RESET_STYLE}")
                suggest_command(main_command)  # Suggest similar commands

        except KeyboardInterrupt:
            print(f"\n{ERROR_STYLE}Interrupted!{RESET_STYLE}")
            loading_animation("Shutting down SigmaOS")
            sys.exit(0)  # Use sys.exit here too

if __name__ == "__main__":
    try:
        log_info("Starting SigmaOS")
        interactive_shell()
    except KeyboardInterrupt:
        print(f"\n{ERROR_STYLE}Interrupted!{RESET_STYLE}")
        log_warning("SigmaOS interrupted by user")
        loading_animation("Shutting down SigmaOS")
        sys.exit(0)
    except Exception as e:
        print(f"\n{ERROR_STYLE}Unhandled exception: {e}{RESET_STYLE}")
        log_error("Unhandled exception in main program", exception=e)
        print(f"{INFO_STYLE}See logs for more details.{RESET_STYLE}")
        sys.exit(1)
