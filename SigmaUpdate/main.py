import os
import requests
import shutil
import time
import psutil
import signal
import subprocess
from datetime import datetime
from colorama import Fore, Style

def loading_animation(message, duration=2):
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    end_time = time.time() + duration
    i = 0
    while time.time() < end_time:
        print(f"\r{Fore.CYAN}{frames[i]} {message}", end="")
        time.sleep(0.1)
        i = (i + 1) % len(frames)
    print(f"\r{Fore.GREEN}✓ {message}{Style.RESET_ALL}")

def force_terminate_sigmaos():
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and 'python' in cmdline[0].lower() and 'sigmaos.py' in cmdline[-1].lower():
                # Force kill the process
                if os.name == 'nt':  # Windows
                    os.kill(proc.pid, signal.SIGTERM)
                else:  # Linux/Mac
                    os.kill(proc.pid, signal.SIGKILL)
                return True
        except:
            continue
    return False

def update_sigma():
    # Get absolute paths - make sure we're in root directory
    current_dir = os.path.dirname(os.path.abspath(__file__))  # SigmaUpdate directory
    root_dir = os.path.dirname(os.path.dirname(current_dir))  # Go up two levels to root
    target_file = os.path.join(root_dir, "SigmaOS.py")
    temp_file = os.path.join(root_dir, "SigmaOS.py.temp")
    
    print(f"{Fore.CYAN}Update paths:{Style.RESET_ALL}")
    print(f"Root directory: {root_dir}")
    print(f"Target file: {target_file}")
    
    # Force terminate existing SigmaOS process
    print(f"{Fore.YELLOW}Terminating SigmaOS process...{Style.RESET_ALL}")
    if force_terminate_sigmaos():
        loading_animation("SigmaOS process terminated")
        time.sleep(1)
    
    try:
        # Download new version
        url = "https://raw.githubusercontent.com/Lominub44/SigmaOS/main/SigmaOS.py"
        loading_animation("Downloading latest version")
        response = requests.get(url)
        response.raise_for_status()
        
        # Make sure we write to root directory
        os.chdir(root_dir)  # Change working directory to root
        
        # First save to temp file in root directory
        with open(temp_file, 'wb') as f:
            f.write(response.content)
        
        # Create backup if original exists
        if os.path.exists(target_file):
            backup_path = os.path.join(root_dir, f"SigmaOS.py.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            shutil.copy2(target_file, backup_path)
            print(f"{Fore.CYAN}Backup created at: {backup_path}{Style.RESET_ALL}")
            os.remove(target_file)
        
        # Move new file into place in root directory
        shutil.move(temp_file, target_file)
        loading_animation("Installing update")
        
        if not os.path.exists(target_file):
            raise Exception("Failed to replace SigmaOS.py in root directory")
        
        print(f"{Fore.GREEN}File replacement successful!{Style.RESET_ALL}")
        time.sleep(1)
        
        # Start new instance from correct location
        print(f"{Fore.CYAN}Starting SigmaOS from: {target_file}{Style.RESET_ALL}")
        if os.name == 'nt':
            os.chdir(root_dir)  # Change to root directory first
            subprocess.Popen(['python', target_file], 
                           creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            subprocess.Popen(['python3', target_file], 
                           start_new_session=True, cwd=root_dir)
        
        print(f"{Fore.GREEN}Update complete! New instance started.{Style.RESET_ALL}")
        
    except Exception as e:
        print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
        if os.path.exists(temp_file):
            os.remove(temp_file)
        if 'backup_path' in locals() and os.path.exists(backup_path):
            shutil.copy2(backup_path, target_file)
            print(f"{Fore.GREEN}Restored from backup{Style.RESET_ALL}")

if __name__ == "__main__":
    update_sigma()
