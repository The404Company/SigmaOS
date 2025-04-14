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

REPO_URL = "https://github.com/Lominub44/SigmaOS"
PACKAGES_DIR = "packages"
ALIASES_FILE = "aliases.json"

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

def list_packages():
    headers = {'Accept': 'application/vnd.github.v3+json'}
    response = requests.get(f"https://api.github.com/repos/Lominub44/SigmaOS/contents/", headers=headers)
    loading_animation("Fetching packages...")
    if response.status_code == 200:
        data = response.json()
        packages_found = False
        print(f"\n{Fore.CYAN}Available packages:{Style.RESET_ALL}")
        for item in data:
            if item["type"] == "dir" and not item["name"].startswith('.'):
                packages_found = True
                print(f"{Fore.GREEN}  ▶ {item['name']}")
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
        return

    print(f"{Fore.CYAN}Running {package_name}/main.py...{Style.RESET_ALL}")
    # Pass any additional arguments after the package name
    args = [sys.executable, package_dir] + sys.argv[2:]
    subprocess.run(args)

def is_valid_package(package_name):
    return os.path.exists(os.path.join(PACKAGES_DIR, package_name, "main.py"))

def interactive_shell():
    show_banner()
    aliases = load_aliases()
    while True:
        try:
            command = input(f"{Fore.GREEN}SigmaOS {Fore.WHITE}> ")

            if command.lower() in ["exit", "sigma quit"]:
                loading_animation("Shutting down SigmaOS")
                break

            # Split command into parts
            parts = command.split()
            
            # Handle package calls with arguments (e.g. "yapper test.txt")
            if parts and is_valid_package(parts[0]):
                sys.argv = parts  # Set sys.argv to include command arguments
                run_package(parts[0])
                continue

            # Check if command is an alias
            if parts and parts[0] in aliases:
                command = aliases[parts[0]]
                if len(parts) > 1:
                    command += " " + " ".join(parts[1:])
                parts = command.split()

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
                    break
                else:
                    print(f"{Fore.RED}Unknown command: {command}{Style.RESET_ALL}")
            
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

        except KeyboardInterrupt:
            print(f"\n{Fore.RED}Interrupted!{Style.RESET_ALL}")
            loading_animation("Shutting down SigmaOS")
            break

if __name__ == "__main__":
    interactive_shell()
