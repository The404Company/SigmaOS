import subprocess
import sys
import os
import threading
import json
from colorama import init, Fore, Back, Style

REPO_URL = "https://github.com/The404Company/SigmaOS-packages"
PACKAGES_DIR = "packages"
ALIASES_FILE = "aliases.json"
THEME_FILE = "theme.sct" # no, its not 'Windows Script Component'. SCT stands for 'SigmaOS Color Theme'. File-icon looks nice though :)
VERSION = "0.1.4"

class Theme:
    def __init__(self):
        self.theme = {}
        self.load_theme()
        self._create_color_variables()
    
    def load_theme(self):
        """Load theme from file or create default if it doesn't exist"""
        if not os.path.exists(THEME_FILE):
            self.create_default_theme()
        
        try:
            with open(THEME_FILE, 'r') as f:
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
            "banner_sct": "cyan",
            "version_sct": "yellow",
            "success_sct": "green",
            "error_sct": "red",
            "warning_sct": "yellow",
            "info_sct": "cyan",
            "header_sct": "yellow",
            "command_sct": "green",
            "description_sct": "white",
            "author_sct": "cyan",
            "loading_sct": "cyan",
            "prompt_sct": "green",
            "suggestion_sct": "cyan",
            "relevance_sct": "blue",
            "system_info_sct": "yellow",
            "timer_sct": "green",
            "alias_sct": "green",
            "package_sct": "green",
            "package_version_sct": "cyan",
            "package_author_sct": "cyan",
            "package_description_sct": "white",
            "package_installed_sct": "green",
            "package_not_installed_sct": "yellow",
            "package_error_sct": "red",
            "package_loading_sct": "cyan",
            "package_skipped_sct": "yellow",
            "package_cleanup_sct": "green",
            "package_download_sct": "cyan",
            "package_install_sct": "cyan",
            "package_uninstall_sct": "yellow",
            "package_reset_sct": "red",
            "package_setup_sct": "cyan",
            "package_essential_sct": "green",
            "package_already_installed_sct": "yellow",
            "package_not_found_sct": "red",
            "package_download_error_sct": "red",
            "package_install_error_sct": "red",
            "package_uninstall_error_sct": "red",
            "package_reset_error_sct": "red",
            "package_setup_error_sct": "red",
            "package_essential_error_sct": "red",
            "package_already_installed_error_sct": "red",
            "package_not_found_error_sct": "red",
            "package_download_success_sct": "green",
            "package_install_success_sct": "green",
            "package_uninstall_success_sct": "green",
            "package_reset_success_sct": "green",
            "package_setup_success_sct": "green",
            "package_essential_success_sct": "green",
            "package_already_installed_success_sct": "green",
            "package_not_found_success_sct": "green"
        }
        
        with open(THEME_FILE, 'w') as f:
            json.dump(default_theme, f, indent=4)
        self.theme = default_theme

# Initialize theme
theme = Theme()

def ensure_base_libraries():
    # Install essential libraries needed for the splash screen
    base_requirements = ['colorama', 'psutil', 'gputil', 'requests', 'readchar', 'datetime', 'uuid']
    for lib in base_requirements:
        try:
            __import__(lib)
        except ImportError:
            print(f"Installing required library: {lib}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

# Only  run setup if packages directory doesn't exist
if not os.path.exists(PACKAGES_DIR):
    ensure_base_libraries()

# Now we can safely import these
import requests
import time
import datetime
import json
from zipfile import ZipFile
from colorama import init, Fore, Back, Style
import shutil
import readchar
import psutil
import GPUtil
import platform
import math


COMMAND_HISTORY = []
MAX_HISTORY = 100
ALL_COMMANDS = {
    'help': [],
    'exit': [],
    'clear': [],
    'setup': [],
    'reset': [],
    'ligma': ['list', 'install', 'uninstall'],  # Added uninstall
    'alias': ['list', 'add', 'remove'],
    'sigma': ['help', 'quit'],
    'sysinfo': [],
    'now': [],
    'sendlogs': [],
    'timer': [],
}

init(autoreset=True)  # Initialize colorama

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_banner():
    clear_screen()
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"{banner_sct}╔═════════════════════════╗")
    print(f"║ {command_sct}σ SigmaOS {version_sct}v{VERSION}{description_sct}        ║")
    print(f"╚═════════════════════════╝{Style.RESET_ALL}")

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
            print(f"\r{loading_sct}{frames[i]} {message}", end="", flush=True)
            time.sleep(0.1)
            i = (i + 1) % len(frames)
        print(f"\r{success_sct}✓ {message}{Style.RESET_ALL}")

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
            print(f"\r{loading_sct}{frames[i]} {message}", end="", flush=True)
            time.sleep(0.1)
            i = (i + 1) % len(frames)
        print(f"\r{success_sct}✓ {message}{Style.RESET_ALL}")

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
    print(f"{success_sct}Added alias: {name} → {command}{Style.RESET_ALL}")

def remove_alias(name):
    aliases = load_aliases()
    if name in aliases:
        del aliases[name]
        save_aliases(aliases)
        print(f"{success_sct}Removed alias: {name}{Style.RESET_ALL}")
    else:
        print(f"{error_sct}Alias not found: {name}{Style.RESET_ALL}")

def list_aliases():
    aliases = load_aliases()
    if aliases:
        print(f"\n{header_sct}Configured aliases:{Style.RESET_ALL}")
        for name, command in aliases.items():
            print(f"{alias_sct}  {name} {description_sct}→ {command}")
    else:
        print(f"{warning_sct}No aliases configured.{Style.RESET_ALL}")

def show_help():
    print(f"\n{header_sct}╔══ SigmaOS Help ══════════════════════════╗{Style.RESET_ALL}")
    
    # System Commands
    print(f"\n{info_sct}System Commands:{Style.RESET_ALL}")
    system_commands = [
        ("help", "Show this help message"),
        ("exit, sigma quit", "Exit SigmaOS"),
        ("clear", "Clear the screen"),
        ("setup", "Install essential packages"),
        ("reset", "Reset SigmaOS to default state"),
        ("sysinfo", "Show system information"),
        ("now", "Show current date and time"),
        ("sendlogs", "Send logs to Discord"),
        ("timer <duration> <unit>", "Set a timer (s/m/h). Hidden feature: Type a command during the timer (invisible), press Enter, and it will execute when the timer finishes!"),
        ]
    for cmd, desc in system_commands:
        print(f"{command_sct}  {cmd:<25}{description_sct} - {desc}")

    # Package Management
    print(f"\n{info_sct}Package Management:{Style.RESET_ALL}")
    pkg_commands = [
        ("ligma list", "List available packages"),
        ("ligma install <pkg>", "Install a package"),
        ("ligma uninstall <pkg>", "Uninstall a package"),
        ("<package>", "Run a package directly")
    ]
    for cmd, desc in pkg_commands:
        print(f"{command_sct}  {cmd:<25}{description_sct} - {desc}")

    # Alias Management
    print(f"\n{info_sct}Alias Management:{Style.RESET_ALL}")
    alias_commands = [
        ("alias list", "List all aliases"),
        ("alias add <name> <cmd>", "Add new alias"),
        ("alias remove <name>", "Remove alias")
    ]
    for cmd, desc in alias_commands:
        print(f"{command_sct}  {cmd:<25}{description_sct} - {desc}")

    # Keyboard Shortcuts
    print(f"\n{info_sct}Keyboard Shortcuts:{Style.RESET_ALL}")
    shortcuts = [
        ("Tab", "Auto-complete commands"),
        ("Up/Down", "Navigate command history"),
        ("Left/Right", "Move cursor"),
        ("Ctrl+C", "Interrupt current operation")
    ]
    for key, desc in shortcuts:
        print(f"{warning_sct}  {key:<25}{description_sct} - {desc}")

    print(f"\n{header_sct}╚{'═' * 41}╝{Style.RESET_ALL}")

import uuid
import os
import json

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
        print(f"{error_sct}Error handling UUID: {e}{Style.RESET_ALL}")
        return str(uuid.uuid4())

def send_logs_to_discord():
    """
    Sends all log files in the 'logs' folder to a Discord webhook,
    then deletes the log files.
    """
    logs_dir = os.path.join(os.path.dirname(__file__), "logs")
    webhook_url = "https://discord.com/api/webhooks/1366094221714653244/U5O-2im9BovXLdscZZmsrxpnqRBiB9sdgVQJfJphSzIywGChitvdBeXl70fPvoQ228BX" # pls do not spam :)

    if not os.path.exists(logs_dir):
        print(f"{warning_sct}No logs directory found.{Style.RESET_ALL}")
        return

    log_files = [f for f in os.listdir(logs_dir) if f.endswith(".log")]
    if not log_files:
        print(f"{warning_sct}No log files to send.{Style.RESET_ALL}")
        return

    # Get user UUID
    user_uuid = get_user_uuid()

    # Ask for confirmation
    print(f"\n{warning_sct}Warning: External packages might include personal data in logs.{Style.RESET_ALL}")
    print(f"{warning_sct}Do you want to send the logs to Discord? (Y/n): {Style.RESET_ALL}", end="")
    confirm = input().strip().lower()
    if confirm != 'y' and confirm != '':
        print(f"{error_sct}Log sending cancelled.{Style.RESET_ALL}")
        return

    message = f"User UUID: {user_uuid}\n"
    for log_file in log_files:
        log_path = os.path.join(logs_dir, log_file)
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
            message += f"\n{log_file}:\n{content}\n"
        except Exception as e:
            print(f"{error_sct}Error reading {log_file}: {e}{Style.RESET_ALL}")

    if not message.strip():
        print(f"{warning_sct}No log content to send.{Style.RESET_ALL}")
        return

    # Discord message limit is 2000 characters, so chunk if needed
    max_length = 1900  # leave room for formatting
    messages = [message[i:i+max_length] for i in range(0, len(message), max_length)]

    for msg in messages:
        data = {"content": msg}
        response = requests.post(webhook_url, json=data)
        if response.status_code == 204 or response.status_code == 200:
            print(f"{success_sct}Logs sent to Discord webhook.{Style.RESET_ALL}")
        else:
            print(f"{error_sct}Failed to send logs: {response.status_code} {response.text}{Style.RESET_ALL}")

    # Delete log files after sending
    for log_file in log_files:
        try:
            os.remove(os.path.join(logs_dir, log_file))
        except Exception as e:
            print(f"{error_sct}Error deleting {log_file}: {e}{Style.RESET_ALL}")

def setup_essential_packages():
    essential_packages = ["LigmaUpdate", "SigmaUpdate", "yapper", "DoccX"]
    
    print(f"\n{info_sct}Installing essential packages...{Style.RESET_ALL}")
    print(f"{description_sct}The following packages will be installed:{Style.RESET_ALL}")
    for pkg in essential_packages:
        print(f"{command_sct}  ▶ {pkg}")
    
    confirm = input(f"\n{warning_sct}Do you want to proceed? (y/N): {Style.RESET_ALL}")
    if confirm.lower() != 'y':
        print(f"{error_sct}Setup cancelled.{Style.RESET_ALL}")
        return
    
    for pkg in essential_packages:
        try:
            if not is_valid_package(pkg):
                print(f"\n{info_sct}Installing {pkg}...{Style.RESET_ALL}")
                download_package(pkg)
            else:
                print(f"{warning_sct}Package {pkg} is already installed.{Style.RESET_ALL}")
        except Exception as e:
            print(f"{error_sct}Error installing {pkg}: {e}{Style.RESET_ALL}")
    
    # Clean up SigmaOS-packages-main folder after all installations
    sigmamain_dir = os.path.join(PACKAGES_DIR, "SigmaOS-packages-main")
    if os.path.exists(sigmamain_dir):
        shutil.rmtree(sigmamain_dir)
        print(f"\n{success_sct}Cleaned up temporary files{Style.RESET_ALL}")

def reset_sigmaos():
    """Reset SigmaOS by removing documents, packages and pycache folders"""
    folders_to_delete = [
        os.path.join(os.path.dirname(__file__), "documents"),
        os.path.join(os.path.dirname(__file__), "packages"),
        os.path.join(os.path.dirname(__file__), "__pycache__")
    ]
    
    print(f"\n{warning_sct}Warning: This will delete all installed packages and documents!{Style.RESET_ALL}")
    confirm = input(f"{error_sct}Are you sure you want to reset SigmaOS? (y/N): {Style.RESET_ALL}")
    
    if confirm.lower() != 'y':
        print(f"{success_sct}Reset cancelled.{Style.RESET_ALL}")
        return
        
    for folder in folders_to_delete:
        if os.path.exists(folder):
            try:
                loading_animation(f"Removed {os.path.basename(folder)}", task=lambda: shutil.rmtree(folder))
            except Exception as e:
                print(f"{error_sct}Error removing {folder}: {e}{Style.RESET_ALL}")
    
    print(f"\n{success_sct}SigmaOS has been reset to default state.{Style.RESET_ALL}")

def get_github_file_content(package_name, filename):
    """Fetch raw file content from GitHub"""
    url = f"https://raw.githubusercontent.com/The404Company/SigmaOS-packages/main/{package_name}/{filename}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text.strip()
    except:
        pass
    return None

def parse_description_file(content):
    """Parse the sections from a description.txt file"""
    sections = {
        'description': 'No description available',
        'author': 'Unknown',
        'version': '0.0',
        'requirements': []
    }
    
    current_section = None
    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('[') and line.endswith(']'):
            current_section = line[1:-1].lower()
            continue
            
        if current_section:
            if current_section == 'requirements':
                if line:
                    sections[current_section].append(line)
            else:
                sections[current_section] = line
                
    return sections

def get_package_description(package_name, installed=True):
    """Get package description from local file or GitHub"""
    if installed and is_valid_package(package_name):
        desc_file = os.path.join(PACKAGES_DIR, package_name, "description.txt")
        try:
            if os.path.exists(desc_file):
                with open(desc_file, 'r', encoding='utf-8') as f:
                    return parse_description_file(f.read())
        except:
            pass
    else:
        # Try to fetch from GitHub for non-installed packages
        content = get_github_file_content(package_name, "description.txt")
        if content:
            return parse_description_file(content)
    
    return {'description': 'No description available', 'author': 'Unknown', 'version': '0.0', 'requirements': []}

def list_packages():
    # Get installed packages first
    installed_packages = []
    if os.path.exists(PACKAGES_DIR):
        installed_packages = [d for d in os.listdir(PACKAGES_DIR) 
                            if os.path.isdir(os.path.join(PACKAGES_DIR, d)) 
                            and not d.startswith('.') 
                            and d != "SigmaOS-packages-main"]

    # Get available packages from repo
    headers = {'Accept': 'application/vnd.github.v3+json'}
    response = requests.get(f"https://api.github.com/repos/The404Company/SigmaOS-packages/contents/", headers=headers)
    loading_animation("Fetching packages...")
    
    if response.status_code == 200:
        data = response.json()
        available_packages = [item["name"] for item in data 
                            if item["type"] == "dir" and not item["name"].startswith('.')]
        
        print(f"\n{info_sct}Available packages:{Style.RESET_ALL}")
        packages_found = False
        
        # Show installed packages first
        if installed_packages:
            print(f"\n{success_sct}Installed:{Style.RESET_ALL}")
            for i, pkg in enumerate(installed_packages):
                if i > 0:  # Add empty line before each package except the first one
                    print()
                desc = get_package_description(pkg)
                print(f"{package_installed_sct}{pkg} {description_sct}- {desc['description']}")
                print(f"{package_version_sct}{desc['author']} {description_sct}- v{desc['version']}")
                packages_found = True
        
        # Show available but not installed packages
        not_installed = [pkg for pkg in available_packages if pkg not in installed_packages]
        if not_installed:
            print(f"\n{warning_sct}Not Installed:{Style.RESET_ALL}")
            for i, pkg in enumerate(not_installed):
                if i > 0:  # Add empty line before each package except the first one
                    print()
                desc = get_package_description(pkg, installed=False)
                print(f"{description_sct}{pkg} - {desc['description']}")
                print(f"{package_version_sct}{desc['author']} - v{desc['version']}")
                packages_found = True
        
        if not packages_found:
            print(f"{error_sct}No packages found in repository.{Style.RESET_ALL}")
    else:
        print(f"{error_sct}Error fetching repositories. Status code: {response.status_code}{Style.RESET_ALL}")
        print(f"{error_sct}Response: {response.text}{Style.RESET_ALL}")

def download_package(package_name):
    if not os.path.exists(PACKAGES_DIR):
        os.makedirs(PACKAGES_DIR)

    package_dir = os.path.join(PACKAGES_DIR, package_name)

    if os.path.exists(package_dir):
        print(f"{warning_sct}Package {package_name} already downloaded.{Style.RESET_ALL}")
        return

    download_url = f"{REPO_URL}/archive/refs/heads/main.zip"

    loading_animation(f"Downloading {package_name}", task=lambda: requests.get(download_url))
    zip_path = os.path.join(PACKAGES_DIR, f"{package_name}.zip")
    response = requests.get(download_url)

    if response.status_code == 200:
        with open(zip_path, "wb") as f:
            f.write(response.content)

        with ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(PACKAGES_DIR)

        os.remove(zip_path)

        extracted_folder = os.path.join(PACKAGES_DIR, "SigmaOS-packages-main", package_name)
        if os.path.exists(extracted_folder):
            if os.path.exists(package_dir):
                shutil.rmtree(package_dir)
            os.rename(extracted_folder, package_dir)
            
            # Install package requirements
            desc = get_package_description(package_name)
            if desc['requirements']:
                print(f"\n{info_sct}Installing dependencies...{Style.RESET_ALL}")
                core_libs = {"colorama", "requests", "datetime", "json"}
                for req in desc['requirements']:
                    if req.lower() in core_libs:
                        print(f"{warning_sct}Skipping {req} (already included in SigmaOS).{Style.RESET_ALL}")
                    else:
                        loading_animation(f"Installing {req}", task=lambda req=req: subprocess.run([sys.executable, "-m", "pip", "install", req], 
                                     stdout=subprocess.DEVNULL, 
                                     stderr=subprocess.DEVNULL))
            
            # Clean up SigmaOS-packages-main folder
            sigmamain_dir = os.path.join(PACKAGES_DIR, "SigmaOS-packages-main")
            if os.path.exists(sigmamain_dir):
                loading_animation("Cleaning up temporary files", task=lambda: shutil.rmtree(sigmamain_dir))
            print(f"{success_sct}Package {package_name} successfully installed.{Style.RESET_ALL}")
        else:
            print(f"{error_sct}Package {package_name} not found in downloaded archive.{Style.RESET_ALL}")
    else:
        print(f"{error_sct}Error downloading package {package_name}.{Style.RESET_ALL}")

def uninstall_package(package_name):
    """Uninstall a package by removing its directory"""
    package_dir = os.path.join(PACKAGES_DIR, package_name)
    
    if not os.path.exists(package_dir):
        print(f"{error_sct}Package {package_name} is not installed.{Style.RESET_ALL}")
        return False
        
    try:
        print(f"{warning_sct}Uninstalling {package_name}...{Style.RESET_ALL}")
        loading_animation(f"Removed {package_name}", task=lambda: shutil.rmtree(package_dir))
        return True
    except Exception as e:
        print(f"{error_sct}Error uninstalling {package_name}: {e}{Style.RESET_ALL}")
        return False

def run_package(package_name):
    package_dir = os.path.join(PACKAGES_DIR, package_name, "main.py")

    if not os.path.exists(package_dir):
        print(f"{error_sct}main.py not found in {package_name}.{Style.RESET_ALL}")
        return False

    print(f"{info_sct}Running {package_name}/main.py...{Style.RESET_ALL}")
    # Pass any additional arguments after the package name
    args = [sys.executable, package_dir] + sys.argv[2:]
    
    # Set environment variable to prevent recursive shell instances
    env = os.environ.copy()
    env['SIGMAOS_SUBPROCESS'] = '1'
    
    # Only create new shell if not already a subprocess
    if os.environ.get('SIGMAOS_SUBPROCESS') != '1':
        subprocess.run(args, env=env)
    else:
        # If we're already a subprocess, run directly without shell
        subprocess.run(args)
    return True

def is_valid_package(package_name):
    return os.path.exists(os.path.join(PACKAGES_DIR, package_name, "main.py"))

def show_welcome_message():
    if not os.path.exists(PACKAGES_DIR) or not os.listdir(PACKAGES_DIR):
        print(f"\n{info_sct}Welcome to SigmaOS!{Style.RESET_ALL}")
        print(f"{description_sct}It looks like this is your first time using SigmaOS.")
        print(f"{command_sct}To get started, try these commands:")
        print(f"{success_sct}  setup{description_sct}     - Install essential packages")
        print(f"{success_sct}  help{description_sct}      - Show all available commands")
        print(f"{success_sct}  ligma list{description_sct} - Show available packages\n")

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
        "sigma help": "Show help menu",
        "sigma quit": "Exit SigmaOS"
    }

    # Get close matches for the command
    matches = get_close_matches(command, command_suggestions.keys(), n=3, cutoff=0.5)
    
    if matches:
        print(f"\n{warning_sct}Suggestions:{Style.RESET_ALL}")
        for match in matches:
            # Calculate similarity score (simplified)
            similarity = sum(a == b for a, b in zip(command, match)) / max(len(command), len(match))
            similarity_bar = "█" * int(similarity * 10)
            print(f"{suggestion_sct}  {match:<20} {description_sct}- {command_suggestions[match]}")
            print(f"{relevance_sct}  Relevance: {similarity_bar:<10} {int(similarity * 100)}%")
    
        # Show quick-use hint for the best match
        print(f"\n{description_sct}Type {success_sct}{matches[0]}{Style.RESET_ALL}")

def get_command_with_history():
    """Handle input with command history and tab completion"""
    current_input = ""
    cursor_pos = 0
    history_pos = len(COMMAND_HISTORY)
    prompt = f"{prompt_sct}SigmaOS {description_sct}> "
    
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
                    print(f"{suggestion_sct}  {comp}{Style.RESET_ALL}")
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
    """Display a splash screen and ensure all dependencies are installed"""
    # List of all required libraries
    required_libraries = {
        'requests': 'requests',
        'colorama': 'colorama',
        'psutil': 'psutil',
        'gputil': 'GPUtil',
        'readchar': 'readchar',
        'zipfile': 'Built-in',
        'json': 'Built-in',
        'uuid': 'uuid',
        'platform': 'Built-in',
        'math': 'Built-in',
        'shutil': 'Built-in',
        'subprocess': 'Built-in',
        'datetime': 'Built-in',
        'sys': 'Built-in',
        'os': 'Built-in'
    }

    # Get basic system info first
    cpu = "Unknown CPU"
    gpu = "Unknown GPU"

    # Show initial splash text
    splash_text = f"""
   _____ _                       ____  _____ 
  / ___/(_)___ _____ ___  ____ _/ __ \/ ___/
  \__ \/ / __ `/ __ `__ \/ __ `/ / / /\__ \ 
 ___/ / / /_/ / / / / / / /_/ / /_/ /___/ / 
/____/_/\__, /_/ /_/ /_/\__,_/\____//____/   v{VERSION}
       /____/                               
"""
    clear_screen()
    print(splash_text)
    
    # Check and install required libraries
    print(f"{info_sct}Checking dependencies...{Style.RESET_ALL}")
    for lib, pip_name in required_libraries.items():
        if pip_name != 'Built-in':
            try:
                __import__(lib)
                print(f"{success_sct}✓ {lib}{Style.RESET_ALL}")
            except ImportError:
                print(f"{warning_sct}Installing {lib}...{Style.RESET_ALL}")
                loading_animation(f"Installing {lib}", task=lambda: subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name],
                                   stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL))
                print(f"{success_sct}✓ {lib} installed{Style.RESET_ALL}")

    # Get system information
    print(f"\n{info_sct}Detecting system information...{Style.RESET_ALL}")
    
    try:
        if platform.system() == "Windows":
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

    try:
        gpus = GPUtil.getGPUs()
        if gpus:
            gpu = gpus[0].name
            gpu = (gpu.replace("NVIDIA GeForce", "NVIDIA")
                     .replace("AMD ", "AMD Radeon ")
                     .replace("Graphics", "")
                     .strip())
        else:
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
    except:
        pass

    total_memory = math.ceil(psutil.virtual_memory().total / (1024**3))
    
    # Show final system information
    clear_screen()
    print(splash_text)
    print(f"{info_sct}CPU:{description_sct} {cpu}")
    print(f"{info_sct}GPU:{description_sct} {gpu}")
    print(f"{info_sct}Memory:{description_sct} {total_memory}GB")
    time.sleep(3)  # Brief pause to show system info
    clear_screen()

def system_info():
    """Display system information"""
    print(f"\n{info_sct}System Information:{Style.RESET_ALL}")
    print(f"{warning_sct}OS: {platform.system()} {platform.release()} + SigmaOS v{VERSION}")
    print(f"{warning_sct}CPU: {psutil.cpu_count(logical=False)} cores")
    print(f"{warning_sct}Logical CPUs: {psutil.cpu_count(logical=True)}")
    print(f"{warning_sct}Memory: {math.ceil(psutil.virtual_memory().total / (1024**3))} GB")
    print(f"{warning_sct}Disk Space: {math.ceil(psutil.disk_usage('/').total / (1024**3))} GB")
    print(f"{warning_sct}Python Version: {platform.python_version()}")

def interactive_shell():
    # Exit if we're a subprocess instance
    if os.environ.get('SIGMAOS_SUBPROCESS') == '1':
        return
    
    # only show splash screen if packages directory doesn't exist
    if not os.path.exists(PACKAGES_DIR):
        show_splash_screen()

    show_banner()
    show_welcome_message()  # This will only show for new users since it checks PACKAGES_DIR
    aliases = load_aliases()
    
    while True:
        try:
            command = get_command_with_history()  # Replace input() with our new function

            if command.lower() in ["exit", "sigma quit"]:
                loading_animation("Shutting down SigmaOS")
                sys.exit(0)  # Use sys.exit for definitive exit

            # Split command into parts
            parts = command.split()
            
            # Handle package calls with arguments (e.g. "yapper test.txt" (bad example))
            if parts and is_valid_package(parts[0]):
                sys.argv = parts  # Set sys.argv to include command arguments
                run_package(parts[0])
                show_banner()  # Refresh banner after package execution
                continue

            # Check if command is an alias
            if parts and parts[0] in aliases:
                command = aliases[parts[0]]
                if len(parts) > 1:
                    command += " " + " ".join(parts[1:])
                parts = command.split()
                if command.lower() in ["exit", "sigma quit"]:  # Check if alias resolves to exit
                    loading_animation("Shutting down SigmaOS")
                    sys.exit(0)

            main_command = parts[0].lower() if parts else ""
            args = parts[1:]

            if not parts:
                continue

            if main_command == "clear":
                show_banner()
                continue

            if main_command in ["help", "sigma", "sigmaos"]:
                if not args or (main_command in ["sigma", "sigmaos"] and args[0] == "help"):
                    show_help()
                elif main_command == "sigma" and args[0] == "quit":
                    loading_animation("Shutting down SigmaOS")
                    sys.exit(0)
                else:
                    print(f"{error_sct}Unknown command: {command}{Style.RESET_ALL}")
            
            elif main_command == "setup":
                setup_essential_packages()
            
            elif main_command == "reset":
                reset_sigmaos()
                show_banner()
            
            elif main_command == "ligma":
                if args:
                    subcommand = args[0]
                    if subcommand == "list":
                        list_packages()
                    elif subcommand == "install" and len(args) == 2:
                        download_package(args[1])
                    elif subcommand == "uninstall" and len(args) == 2:
                        uninstall_package(args[1])
                    else:
                        print(f"{error_sct}Unknown command for ligma.{Style.RESET_ALL}")
                else:
                    print(f"{warning_sct}Usage: ligma: list | install <package> | uninstall <package>{Style.RESET_ALL}")
            
            elif main_command == "sysinfo":
                system_info()

            elif main_command == "now":
                print(f"{info_sct}Current time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Style.RESET_ALL}")
            
            elif main_command == "sendlogs":
                send_logs_to_discord()

            elif main_command == "timer":
                if args and len(args) == 2:
                    try:
                        duration = int(args[0])
                        unit = args[1].lower()
                        if unit in ["s", "sec", "seconds"]:
                            time.sleep(duration)
                            print(f"{success_sct}Timer finished!{Style.RESET_ALL}")
                        elif unit in ["m", "min", "minutes"]:
                            time.sleep(duration * 60)
                            print(f"{success_sct}Timer finished!{Style.RESET_ALL}")
                        elif unit in ["h", "hr", "hours"]:
                            time.sleep(duration * 3600)
                            print(f"{success_sct}Timer finished!{Style.RESET_ALL}")
                        else:
                            print(f"{error_sct}Invalid time unit. Use s, m, or h.{Style.RESET_ALL}")
                    except ValueError:
                        print(f"{error_sct}Invalid duration. Please enter a number.{Style.RESET_ALL}")
                else:
                    print(f"{warning_sct}Usage: timer <duration> <unit (s/m/h)>{Style.RESET_ALL}")
                    print(f"{info_sct}Pro tip: You can type a command during the timer (you won't see it)")
                    print(f"{info_sct}and press Enter to execute it when the timer finishes!{Style.RESET_ALL}")

            elif main_command == "rick":
                subprocess.run(["curl", "ascii.live/rick"])

            elif main_command == "alias":
                if not args:
                    list_aliases()
                elif args[0] == "list":
                    list_aliases()
                elif args[0] == "add" and len(args) >= 3:
                    add_alias(args[1], " ".join(args[2:]))
                elif args[0] == "remove" and len(args) == 2:
                    remove_alias(args[1])
                else:
                    print(f"{warning_sct}Usage: alias: list | add <name> <command> | remove <name>{Style.RESET_ALL}")

            elif is_valid_package(main_command):
                run_package(main_command)
            
            else:
                print(f"{error_sct}Unknown command: {main_command}. Try 'help' for available commands.{Style.RESET_ALL}")
                suggest_command(main_command)  # Suggest similar commands

        except KeyboardInterrupt:
            print(f"\n{error_sct}Interrupted!{Style.RESET_ALL}")
            loading_animation("Shutting down SigmaOS")
            sys.exit(0)  # Use sys.exit here too

if __name__ == "__main__":
    interactive_shell()
