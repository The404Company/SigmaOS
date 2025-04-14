import os
import shutil
import sys
from colorama import Fore, Style, init
import time

# Add root dir to path and import early
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(root_dir)
from SigmaOS import download_package

def loading_animation(message, duration=1):
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    end_time = time.time() + duration
    i = 0
    while time.time() < end_time:
        print(f"\r{Fore.CYAN}{frames[i]} {message}", end="")
        time.sleep(0.1)
        i = (i + 1) % len(frames)
    print(f"\r{Fore.GREEN}✓ {message}{Style.RESET_ALL}")

def update_packages():
    init(autoreset=True)
    
    # Get root directory and packages directory
    packages_dir = os.path.join(root_dir, "packages")

    if not os.path.exists(packages_dir):
        print(f"{Fore.RED}No packages directory found!{Style.RESET_ALL}")
        return

    # Get list of installed packages (excluding self)
    current_pkg = os.path.basename(os.path.dirname(__file__))  # Should be "LigmaUpdate"
    packages = [d for d in os.listdir(packages_dir) 
               if os.path.isdir(os.path.join(packages_dir, d)) 
               and d != current_pkg  # Protect ourselves from deletion
               and d != "SigmaOS-main"]  # Ignore leftover dirs

    if not packages:
        print(f"{Fore.YELLOW}No packages to update!{Style.RESET_ALL}")
        return

    print(f"{Fore.CYAN}Found {len(packages)} installed packages:{Style.RESET_ALL}")
    for pkg in packages:
        print(f"{Fore.GREEN}  ▶ {pkg}")

    # Confirm with user
    confirm = input(f"\n{Fore.YELLOW}Do you want to update all packages? (y/N): {Style.RESET_ALL}")
    if confirm.lower() != 'y':
        print(f"{Fore.RED}Update cancelled.{Style.RESET_ALL}")
        return

    # Store packages list and delete old versions
    packages_to_update = packages.copy()  # Keep original list
    print(f"\n{Fore.CYAN}Removing old packages...{Style.RESET_ALL}")
    for pkg in packages:
        pkg_path = os.path.join(packages_dir, pkg)
        try:
            if pkg != current_pkg:  # Extra safety check
                shutil.rmtree(pkg_path)
                loading_animation(f"Removed {pkg}")
        except Exception as e:
            print(f"{Fore.RED}Error removing {pkg}: {e}{Style.RESET_ALL}")
            packages_to_update.remove(pkg)  # Don't try to reinstall failed removals

    # Reinstall packages
    print(f"\n{Fore.CYAN}Reinstalling packages...{Style.RESET_ALL}")
    for pkg in packages_to_update:
        try:
            loading_animation(f"Installing {pkg}")
            download_package(pkg)
            time.sleep(0.5)  # Small delay between installations
        except Exception as e:
            print(f"{Fore.RED}Error installing {pkg}: {e}{Style.RESET_ALL}")

    print(f"\n{Fore.GREEN}Package update complete!{Style.RESET_ALL}")
    time.sleep(1)
    
    # Return to SigmaOS
    os.system(f'python {os.path.join(root_dir, "SigmaOS.py")}')

if __name__ == "__main__":
    update_packages()
