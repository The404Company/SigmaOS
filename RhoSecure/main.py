import os
import sys
import json
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
from colorama import Fore, Style, init
import getpass

PASSWORDS_FILE = "passwords.enc"
SALT_FILE = "salt"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_banner():
    clear_screen()
    print(f"{Fore.CYAN}╔═══ ρ RhoSecure ═══╗")
    print(f"║ Password Manager  ║")
    print(f"╚═══════════════════╝{Style.RESET_ALL}")

def get_master_key(salt):
    """Generate encryption key from master password"""
    password = getpass.getpass(f"{Fore.GREEN}Enter master password: {Style.RESET_ALL}")
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return Fernet(key)

def initialize_storage():
    """Initialize password storage with a new master password"""
    if not os.path.exists(SALT_FILE):
        salt = os.urandom(16)
        with open(SALT_FILE, 'wb') as f:
            f.write(salt)
    
    if not os.path.exists(PASSWORDS_FILE):
        salt = open(SALT_FILE, 'rb').read()
        fernet = get_master_key(salt)
        empty_db = {'passwords': {}}
        with open(PASSWORDS_FILE, 'wb') as f:
            f.write(fernet.encrypt(json.dumps(empty_db).encode()))
        print(f"{Fore.GREEN}Password storage initialized!{Style.RESET_ALL}")

def load_passwords():
    """Load and decrypt passwords"""
    try:
        salt = open(SALT_FILE, 'rb').read()
        fernet = get_master_key(salt)
        with open(PASSWORDS_FILE, 'rb') as f:
            encrypted_data = f.read()
        decrypted_data = fernet.decrypt(encrypted_data)
        return json.loads(decrypted_data)
    except:
        print(f"{Fore.RED}Invalid master password or corrupted data!{Style.RESET_ALL}")
        return None

def save_passwords(data):
    """Encrypt and save passwords"""
    salt = open(SALT_FILE, 'rb').read()
    fernet = get_master_key(salt)
    encrypted_data = fernet.encrypt(json.dumps(data).encode())
    with open(PASSWORDS_FILE, 'wb') as f:
        f.write(encrypted_data)

def add_password(service, username, password):
    """Add or update a password entry"""
    data = load_passwords()
    if data:
        data['passwords'][service] = {
            'username': username,
            'password': password
        }
        save_passwords(data)
        print(f"{Fore.GREEN}Password saved for {service}{Style.RESET_ALL}")

def get_password(service):
    """Retrieve a password entry"""
    data = load_passwords()
    if data and service in data['passwords']:
        entry = data['passwords'][service]
        print(f"\n{Fore.CYAN}Service: {service}")
        print(f"Username: {entry['username']}")
        print(f"Password: {entry['password']}{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}No password found for {service}{Style.RESET_ALL}")

def list_passwords():
    """List all stored services"""
    data = load_passwords()
    if data and data['passwords']:
        print(f"\n{Fore.CYAN}Stored passwords:{Style.RESET_ALL}")
        for service in sorted(data['passwords'].keys()):
            entry = data['passwords'][service]
            print(f"\n{Fore.GREEN}Service: {service}")
            print(f"{Fore.CYAN}Username: {entry['username']}{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}No passwords stored yet.{Style.RESET_ALL}")

def delete_password(service):
    """Delete a password entry"""
    data = load_passwords()
    if data and service in data['passwords']:
        del data['passwords'][service]
        save_passwords(data)
        print(f"{Fore.GREEN}Password deleted for {service}{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}No password found for {service}{Style.RESET_ALL}")

def show_help():
    """Show help message"""
    print(f"""
{Fore.CYAN}Commands:{Style.RESET_ALL}
    add <service> <username> <password> : Add/update password
    get <service>                       : Retrieve password
    list                                : List all services
    delete <service>                    : Delete password
    help                                : Show this help
    exit                                : Exit RhoSecure
    """)

def handle_command(command):
    """Process a command"""
    parts = command.strip().split()
    if not parts:
        return True

    cmd = parts[0].lower()
    args = parts[1:]

    if cmd == "exit":
        return False
    elif cmd == "help":
        show_help()
    elif cmd == "list":
        list_passwords()
    elif cmd == "add" and len(args) >= 3:
        add_password(args[0], args[1], " ".join(args[2:]))
    elif cmd == "get" and len(args) == 1:
        get_password(args[0])
    elif cmd == "delete" and len(args) == 1:
        delete_password(args[0])
    else:
        print(f"{Fore.RED}Invalid command. Type 'help' for usage.{Style.RESET_ALL}")
    return True

def interactive_shell():
    """Run interactive shell"""
    show_banner()
    show_help()
    while True:
        try:
            command = input(f"\n{Fore.GREEN}RhoSecure>{Style.RESET_ALL} ")
            if not handle_command(command):
                break
        except KeyboardInterrupt:
            print(f"\n{Fore.RED}Exiting...{Style.RESET_ALL}")
            break

# does not work when directly executed form SigmaOS
def main():
    init(autoreset=True)
    initialize_storage()
    
    # Handle command-line arguments
    if len(sys.argv) > 1:
        handle_command(" ".join(sys.argv[1:]))
    else:
        interactive_shell()

if __name__ == "__main__":
    main()