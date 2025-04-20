import os
import sys
import shutil
from colorama import Fore, Style, init
import re
import time

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_banner():
    clear_screen()
    print(f"{Fore.CYAN}╔═══ LigmaDev ════╗")
    print(f"║ Package Creator ║")
    print(f"╚═════════════════╝{Style.RESET_ALL}")

def loading_animation(text):
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    for i in range(10):
        print(f"\r{Fore.CYAN}{frames[i % len(frames)]} {text}", end="")
        time.sleep(0.1)
    print(f"\r{Fore.GREEN}✓ {text}{Style.RESET_ALL}")

def validate_package_name(name):
    """Validate package name format"""
    if not re.match(r'^[A-Za-z][A-Za-z0-9_]*$', name):
        return False
    return True

def create_example_package():
    """Create example package to demonstrate package structure"""
    example_dir = os.path.join(os.path.dirname(__file__), "packages", "ExamplePackage")
    os.makedirs(example_dir, exist_ok=True)
    
    # Create main.py with UTF-8 encoding
    with open(os.path.join(example_dir, "main.py"), 'w', encoding='utf-8') as f:
        f.write('''import os
from colorama import Fore, Style, init

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_banner():
    clear_screen()
    print(f"{Fore.CYAN}┌─── Example Package ───┐")
    print(f"│ Hello World!          │")
    print(f"└───────────────────────┘{Style.RESET_ALL}")

def main():
    init(autoreset=True)
    show_banner()
    print(f"\\n{Fore.GREEN}This is an example package!{Style.RESET_ALL}")
    input(f"\\n{Fore.YELLOW}Press Enter to exit...{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
''')

    # Create description.txt
    with open(os.path.join(example_dir, "description.txt"), 'w') as f:
        f.write('''[description]
An example package showing basic SigmaOS package structure

[author]
Your Name

[version]
1.0

[requirements]
colorama
''')

def create_technical_guide():
    """Create technical documentation for package development"""
    guide_dir = os.path.join(os.path.dirname(__file__), "docs")
    os.makedirs(guide_dir, exist_ok=True)
    
    with open(os.path.join(guide_dir, "technical_guide.md"), 'w', encoding='utf-8') as f:
        f.write('''# SigmaOS Package Development Guide

## Package Structure
Each package must contain:
1. `main.py` - Entry point executed by SigmaOS
2. `description.txt` - Package metadata and requirements

### description.txt Format
```
[description]
Brief package description

[author]
Your name or username

[version]
1.0

[requirements]
colorama
requests
or any other dependencies that your package needs...
```

## SigmaOS Integration
- Packages are stored in `SigmaOS/packages/` directory
- SigmaOS executes `main.py` when package name is typed
- Use colorama for consistent styling
- Handle keyboard interrupts gracefully

## Best Practices
1. Always include clear_screen() function
2. Show package banner
3. Use colorama for styling
4. Handle user input safely
5. Clean up resources on exit

## Example Package Structure
```python
import os
from colorama import Fore, Style, init

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_banner():
    clear_screen()
    print(f"{Fore.CYAN}╔═══ Package Name ═══╗{Style.RESET_ALL}")
    print(f"║ Description        ║")
    print(f"╚════════════════════╝")

def main():
    init(autoreset=True)
    show_banner()
    # Your code here
    
if __name__ == "__main__":
    main()
```

## Color Guidelines
- Cyan (Fore.CYAN): Banners, headers
- Green (Fore.GREEN): Success messages, prompts
- Yellow (Fore.YELLOW): Warnings, important notes
- Red (Fore.RED): Errors
- White (Fore.WHITE): Regular text

## Error Handling
```python
try:
    # Your code
except KeyboardInterrupt:
    print(f"\\n{Fore.RED}Operation cancelled!{Style.RESET_ALL}")
except Exception as e:
    print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
```

## Package Testing
1. put your package-folder in `SigmaOS/packages/` directory.
2. Open SigmaOS and type the package name to execute.
''')

def create_package(name):
    """Create new package with basic structure"""
    package_dir = os.path.join(os.path.dirname(__file__), "packages", name)
    
    try:
        os.makedirs(package_dir, exist_ok=True)
    except Exception as e:
        print(f"{Fore.RED}Error creating directory: {str(e)}{Style.RESET_ALL}")
        return False

    try:
        with open(os.path.join(package_dir, "main.py"), 'w', encoding='utf-8') as f:
            f.write(f'''import os
from colorama import Fore, Style, init

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_banner():
    clear_screen()
    print(f"{{Fore.CYAN}}┌─── {name} ───┐{{Style.RESET_ALL}}")
    print(f"│ Your Package    │")
    print(f"└─────────────────┘") # Adjust spaces and lines as needed

def main():
    init(autoreset=True)
    show_banner()
    # Your code here
    print(f"\\n{{Fore.GREEN}}Welcome to {name}!{{Style.RESET_ALL}}")
    input(f"\\n{{Fore.YELLOW}}Press Enter to exit...{{Style.RESET_ALL}}")

if __name__ == "__main__":
    main()
''')
    except Exception as e:
        print(f"{Fore.RED}Error creating main.py: {str(e)}{Style.RESET_ALL}")
        return False

    # Create description.txt
    try:
        with open(os.path.join(package_dir, "description.txt"), 'w') as f:
            f.write(f'''[description]
Your package description here

[author]
Your Name

[version]
1.0

[requirements]
colorama
''')
    except Exception as e:
        print(f"{Fore.RED}Error creating description.txt: {str(e)}{Style.RESET_ALL}")
        return False

    return True

def main():
    init(autoreset=True)
    
    while True:
        show_banner()
        print(f"\n{Fore.YELLOW}What would you like to do?{Style.RESET_ALL}")
        print(f"{Fore.GREEN}1.{Style.RESET_ALL} Create new package")
        print(f"{Fore.GREEN}2.{Style.RESET_ALL} View example package")
        print(f"{Fore.GREEN}3.{Style.RESET_ALL} Read technical guide")
        print(f"{Fore.GREEN}0.{Style.RESET_ALL} Exit")

        choice = input(f"\n{Fore.WHITE}Choose an option (0-3): {Style.RESET_ALL}")

        if choice == "0":
            clear_screen()
            sys.exit(0)

        elif choice == "1":
            show_banner()
            print(f"\n{Fore.CYAN}Create New Package{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Package name rules:{Style.RESET_ALL}")
            print("- Start with a letter")
            print("- Use only letters, numbers, and underscores")
            print("- No spaces or special characters")
            
            name = input(f"\n{Fore.GREEN}Enter package name: {Style.RESET_ALL}")
            
            if not validate_package_name(name):
                print(f"{Fore.RED}Invalid package name!{Style.RESET_ALL}")
                input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
                continue

            loading_animation("Creating package structure")
            
            if create_package(name):
                print(f"\n{Fore.GREEN}Package created successfully in packages/{name}/{Style.RESET_ALL}")
                print(f"\n{Fore.CYAN}Next steps:{Style.RESET_ALL}")
                print(f"1. Edit SigmaOS/packages/ligmadev/packages/{name}/main.py")
                print(f"2. Update SigmaOS/packages/ligmadev/packages/{name}/description.txt")
                print(f"3. Test your package")
                print(f"4. Share your package on Discord: https://discord.gg/KxUfgTszjN")
            else:
                print(f"\n{Fore.RED}Failed to create package!{Style.RESET_ALL}")
            
            input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

        elif choice == "2":
            show_banner()
            print(f"\n{Fore.CYAN}Creating example package...{Style.RESET_ALL}")
            create_example_package()
            print(f"\n{Fore.GREEN}Example package created in SigmaOS/packages/ligmadev/packages/ExamplePackage/{Style.RESET_ALL}")
            print(f"Review the files to see the recommended structure.")
            input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

        elif choice == "3":
            show_banner()
            print(f"\n{Fore.CYAN}Creating technical guide...{Style.RESET_ALL}")
            create_technical_guide()
            print(f"\n{Fore.GREEN}Technical guide created in SigmaOS/packages/ligmadev/docs/technical_guide.md{Style.RESET_ALL}")
            print(f"Open it in your favorite markdown viewer. https://dillinger.io/ is a good one.")
            input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

if __name__ == "__main__":
    main()