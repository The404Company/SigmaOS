import os
import requests
import shutil
from datetime import datetime
from colorama import Fore, Style

def update_sigma():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    sigmaos_path = os.path.join(base_dir, "SigmaOS.py")
    
    # Create backup
    if os.path.exists(sigmaos_path):
        backup_path = sigmaos_path + f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(sigmaos_path, backup_path)
        print(f"{Fore.CYAN}Created backup at: {backup_path}{Style.RESET_ALL}")

    # Download latest version
    url = "https://raw.githubusercontent.com/Lominub44/SigmaOS/main/SigmaOS.py"
    print(f"{Fore.CYAN}Downloading latest version...{Style.RESET_ALL}")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        with open(sigmaos_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print(f"{Fore.GREEN}Successfully updated SigmaOS.py to latest version!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Please restart SigmaOS to apply the update.{Style.RESET_ALL}")
    
    except Exception as e:
        print(f"{Fore.RED}Error updating SigmaOS.py: {str(e)}{Style.RESET_ALL}")
        if os.path.exists(backup_path):
            print(f"{Fore.YELLOW}Restoring from backup...{Style.RESET_ALL}")
            shutil.copy2(backup_path, sigmaos_path)
            print(f"{Fore.GREEN}Restore complete.{Style.RESET_ALL}")

if __name__ == "__main__":
    update_sigma()
