import os
import subprocess
import requests
import time
import datetime
import json
import sys
from zipfile import ZipFile
from colorama import init, Fore, Back, Style
import shutil
import readchar

REPO_URL = "https://github.com/Lominub44/SigmaOS"
PACKAGES_DIR = "packages"
ALIASES_FILE = "aliases.json"

COMMAND_HISTORY = []
MAX_HISTORY = 100
ALL_COMMANDS = {
    'help': [],
    'exit': [],
    'clear': [],
    'setup': [],
    'ligma': ['list', 'install'],
    'alias': ['list', 'add', 'remove'],
    'sigma': ['help', 'quit']
}

init(autoreset=True)  # Initialize colorama

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_banner():
    clear_screen()
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"{Fore.CYAN}╔══════════════════════════════════════╗")
    print(f"║ {Fore.WHITE}σ {Fore.YELLOW}SigmaOS v0.1 {Fore.WHITE}⌚ {current_time}{Fore.CYAN} ║")
    print(f"╚══════════════════════════════════════╝{Style.RESET_ALL}")

def loading_animation(message, duration=2):
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    end_time = time.time() + duration
    i = 0
    while time.time() < end_time:
        print(f"\r{Fore.CYAN}{frames[i]} {message}", end="")
        time.sleep(0.1)
        i = (i + 1) % len(frames)
    print(f"\r{Fore.GREEN}✓ {message}{Style.RESET_ALL}")

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
    print(f"{Fore.GREEN}Added alias: {name} → {command}{Style.RESET_ALL}")

def remove_alias(name):
    aliases = load_aliases()
    if name in aliases:
        del aliases[name]
        save_aliases(aliases)
        print(f"{Fore.GREEN}Removed alias: {name}{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}Alias not found: {name}{Style.RESET_ALL}")

def list_aliases():
    aliases = load_aliases()
    if aliases:
        print(f"\n{Fore.CYAN}Configured aliases:{Style.RESET_ALL}")
        for name, command in aliases.items():
            print(f"{Fore.GREEN}  {name} {Fore.WHITE}→ {command}")
    else:
        print(f"{Fore.YELLOW}No aliases configured.{Style.RESET_ALL}")

def show_help():
    print(f"\n{Fore.YELLOW}╔══ SigmaOS Commands ══╗{Style.RESET_ALL}")
    commands = [
        ("help", "Show this help message"),
        ("exit", "Exit SigmaOS"),
        ("clear", "Clear the screen"),
        ("setup", "Install essential packages"),
        ("ligma list", "List available packages"),
        ("ligma install <pkg>", "Install a package"),
        ("alias list", "List all aliases"),
        ("alias add <name> <cmd>", "Add new alias"),
        ("alias remove <name>", "Remove alias"),
        ("<package>", "Run a package directly")
    ]
    for cmd, desc in commands:
        print(f"{Fore.CYAN}  {cmd:<20}{Fore.WHITE} - {desc}")
    print(f"{Fore.YELLOW}╚{'═' * 24}╝{Style.RESET_ALL}")

def setup_essential_packages():
    essential_packages = ["LigmaUpdate", "SigmaUpdate", "yapper"]
    
    print(f"\n{Fore.CYAN}Installing essential packages...{Style.RESET_ALL}")
    print(f"{Fore.WHITE}The following packages will be installed:{Style.RESET_ALL}")
    for pkg in essential_packages:
        print(f"{Fore.GREEN}  ▶ {pkg}")
    
    confirm = input(f"\n{Fore.YELLOW}Do you want to proceed? (y/N): {Style.RESET_ALL}")
    if confirm.lower() != 'y':
        print(f"{Fore.RED}Setup cancelled.{Style.RESET_ALL}")
        return
    
    for pkg in essential_packages:
        try:
            if not is_valid_package(pkg):
                print(f"\n{Fore.CYAN}Installing {pkg}...{Style.RESET_ALL}")
                download_package(pkg)
            else:
                print(f"{Fore.YELLOW}Package {pkg} is already installed.{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Error installing {pkg}: {e}{Style.RESET_ALL}")

def get_github_file_content(package_name, filename):
    """Fetch raw file content from GitHub"""
    url = f"https://raw.githubusercontent.com/Lominub44/SigmaOS/main/{package_name}/{filename}"
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
    
    return {'description': 'No description available', 'author': 'Unknown', 'requirements': []}

def list_packages():
    # Get installed packages first
    installed_packages = []
    if os.path.exists(PACKAGES_DIR):
        installed_packages = [d for d in os.listdir(PACKAGES_DIR) 
                            if os.path.isdir(os.path.join(PACKAGES_DIR, d)) 
                            and not d.startswith('.') 
                            and d != "SigmaOS-main"]

    # Get available packages from repo
    headers = {'Accept': 'application/vnd.github.v3+json'}
    response = requests.get(f"https://api.github.com/repos/Lominub44/SigmaOS/contents/", headers=headers)
    loading_animation("Fetching packages...")
    
    if response.status_code == 200:
        data = response.json()
        available_packages = [item["name"] for item in data 
                            if item["type"] == "dir" and not item["name"].startswith('.')]
        
        print(f"\n{Fore.CYAN}Available packages:{Style.RESET_ALL}")
        packages_found = False
        
        # Show installed packages first
        if installed_packages:
            print(f"\n{Fore.GREEN}Installed:{Style.RESET_ALL}")
            for pkg in installed_packages:
                desc = get_package_description(pkg)
                print(f"{Fore.GREEN}  ✓ {pkg:<15}{Fore.WHITE} - {desc['description']}")
                print(f"{Fore.CYAN}    Author: {desc['author']}")
                if desc['requirements']:
                    print(f"{Fore.YELLOW}    Requires: {', '.join(desc['requirements'])}")
                packages_found = True
        
        # Show available but not installed packages
        not_installed = [pkg for pkg in available_packages if pkg not in installed_packages]
        if not_installed:
            print(f"\n{Fore.YELLOW}Not Installed:{Style.RESET_ALL}")
            for pkg in not_installed:
                desc = get_package_description(pkg, installed=False)
                print(f"{Fore.WHITE}  ▶ {pkg:<15} - {desc['description']}")
                print(f"{Fore.CYAN}    Author: {desc['author']}")
                if desc['requirements']:
                    print(f"{Fore.YELLOW}    Requires: {', '.join(desc['requirements'])}")
                packages_found = True
        
        if not packages_found:
            print(f"{Fore.RED}No packages found in repository.{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}Error fetching repositories. Status code: {response.status_code}{Style.RESET_ALL}")
        print(f"{Fore.RED}Response: {response.text}{Style.RESET_ALL}")

def download_package(package_name):
    if not os.path.exists(PACKAGES_DIR):
        os.makedirs(PACKAGES_DIR)

    package_dir = os.path.join(PACKAGES_DIR, package_name)

    if os.path.exists(package_dir):
        print(f"{Fore.YELLOW}Package {package_name} already downloaded.{Style.RESET_ALL}")
        return

    download_url = f"{REPO_URL}/archive/refs/heads/main.zip"

    loading_animation(f"Downloading {package_name}")
    zip_path = os.path.join(PACKAGES_DIR, f"{package_name}.zip")
    response = requests.get(download_url)

    if response.status_code == 200:
        with open(zip_path, "wb") as f:
            f.write(response.content)

        with ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(PACKAGES_DIR)

        os.remove(zip_path)

        extracted_folder = os.path.join(PACKAGES_DIR, "SigmaOS-main", package_name)
        if os.path.exists(extracted_folder):
            if os.path.exists(package_dir):
                shutil.rmtree(package_dir)
            os.rename(extracted_folder, package_dir)
            
            # Install package requirements
            desc = get_package_description(package_name)
            if desc['requirements']:
                print(f"\n{Fore.CYAN}Installing dependencies...{Style.RESET_ALL}")
                for req in desc['requirements']:
                    loading_animation(f"Installing {req}")
                    subprocess.run([sys.executable, "-m", "pip", "install", req], 
                                 stdout=subprocess.DEVNULL, 
                                 stderr=subprocess.DEVNULL)
            
            # Clean up SigmaOS-main folder
            sigmamain_dir = os.path.join(PACKAGES_DIR, "SigmaOS-main")
            if os.path.exists(sigmamain_dir):
                shutil.rmtree(sigmamain_dir)
            print(f"{Fore.GREEN}Package {package_name} successfully installed.{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}Package {package_name} not found in downloaded archive.{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}Error downloading package {package_name}.{Style.RESET_ALL}")

def run_package(package_name):
    package_dir = os.path.join(PACKAGES_DIR, package_name, "main.py")

    if not os.path.exists(package_dir):
        print(f"{Fore.RED}main.py not found in {package_name}.{Style.RESET_ALL}")
        return False

    print(f"{Fore.CYAN}Running {package_name}/main.py...{Style.RESET_ALL}")
    # Pass any additional arguments after the package name
    args = [sys.executable, package_dir] + sys.argv[2:]
    subprocess.run(args)
    return True  # Indicate successful package execution

def is_valid_package(package_name):
    return os.path.exists(os.path.join(PACKAGES_DIR, package_name, "main.py"))

def show_welcome_message():
    if not os.path.exists(PACKAGES_DIR) or not os.listdir(PACKAGES_DIR):
        print(f"\n{Fore.CYAN}Welcome to SigmaOS!{Style.RESET_ALL}")
        print(f"{Fore.WHITE}It looks like this is your first time using SigmaOS.")
        print(f"To get started, try these commands:")
        print(f"{Fore.GREEN}  setup{Fore.WHITE}     - Install essential packages")
        print(f"{Fore.GREEN}  help{Fore.WHITE}      - Show all available commands")
        print(f"{Fore.GREEN}  ligma list{Fore.WHITE} - Show available packages\n")

def suggest_command(command):
    """Suggest similar commands when user makes a typo"""
    from difflib import get_close_matches
    all_commands = ["help", "exit", "clear", "setup", "ligma list", "ligma install",
                   "alias list", "alias add", "alias remove", "sigma help", "sigma quit"]
    matches = get_close_matches(command, all_commands, n=1, cutoff=0.6)
    if matches:
        print(f"{Fore.YELLOW}Did you mean: {Fore.GREEN}{matches[0]}{Fore.YELLOW}?{Style.RESET_ALL}")

def get_command_with_history():
    """Handle input with command history and tab completion"""
    current_input = ""
    cursor_pos = 0
    history_pos = len(COMMAND_HISTORY)
    
    def clear_line():
        # Clear the entire line and move cursor back to start
        print('\r' + ' ' * (len(current_input) + len("SigmaOS > ") + 1), end='\r')
    
    def refresh_line(text, cursor):
        clear_line()
        prompt = f"{Fore.GREEN}SigmaOS {Fore.WHITE}> "
        print(f"{prompt}{text}", end='')
        # Move cursor back if needed
        if cursor < len(text):
            # Calculate actual cursor position including color codes
            total_len = len(text) + len(prompt)
            move_back = total_len - cursor - len(prompt)
            print(f"\033[{move_back}D", end='', flush=True)
    
    def get_completions(text):
        parts = text.split()
        if not text or text[-1] == ' ':
            # New word, show all possible commands
            return [cmd for cmd in ALL_COMMANDS.keys() if not parts or cmd.startswith(parts[0])]
        
        if len(parts) == 1:
            # Complete first word (command)
            return [cmd for cmd in ALL_COMMANDS.keys() if cmd.startswith(parts[0])]
        elif len(parts) >= 2:
            # Complete subcommands if available
            cmd = parts[0]
            if cmd in ALL_COMMANDS:
                return [sub for sub in ALL_COMMANDS[cmd] if sub.startswith(parts[-1])]
        return []

    while True:
        refresh_line(current_input, cursor_pos)
        key = readchar.readkey()
        
        if key in (readchar.key.BACKSPACE, '\x7f'):  # Handle both backspace codes
            if cursor_pos > 0:
                # Remove character before cursor
                current_input = current_input[:cursor_pos-1] + current_input[cursor_pos:]
                cursor_pos -= 1
                refresh_line(current_input, cursor_pos)
        
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
                    print(f"{Fore.CYAN}  {comp}{Style.RESET_ALL}")
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

def interactive_shell():
    show_banner()
    show_welcome_message()  # Show welcome message for new users
    aliases = load_aliases()
    while True:
        try:
            command = get_command_with_history()  # Replace input() with our new function

            if command.lower() in ["exit", "sigma quit"]:
                loading_animation("Shutting down SigmaOS")
                sys.exit(0)  # Use sys.exit for definitive exit

            # Split command into parts
            parts = command.split()
            
            # Handle package calls with arguments (e.g. "yapper test.txt")
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
                    print(f"{Fore.RED}Unknown command: {command}{Style.RESET_ALL}")
            
            elif main_command == "setup":
                setup_essential_packages()
            
            elif main_command == "ligma":
                if args:
                    subcommand = args[0]
                    if subcommand == "list":
                        list_packages()
                    elif subcommand == "install" and len(args) == 2:
                        download_package(args[1])
                    else:
                        print(f"{Fore.RED}Unknown command for ligma.{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}Usage: ligma: list | install <package>{Style.RESET_ALL}")
            
            elif main_command == "delta":
                delta_command(args)
            
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
                    print(f"{Fore.YELLOW}Usage: alias: list | add <name> <command> | remove <name>{Style.RESET_ALL}")

            elif is_valid_package(main_command):
                run_package(main_command)
            
            else:
                print(f"{Fore.RED}Unknown command: {main_command}. Try 'help' for available commands.{Style.RESET_ALL}")
                suggest_command(main_command)  # Suggest similar commands

        except KeyboardInterrupt:
            print(f"\n{Fore.RED}Interrupted!{Style.RESET_ALL}")
            loading_animation("Shutting down SigmaOS")
            sys.exit(0)  # Use sys.exit here too

if __name__ == "__main__":
    interactive_shell()
