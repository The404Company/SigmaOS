import os
import msvcrt
import sys
from colorama import Fore, Style, init

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_banner():
    clear_screen()
    print(f"{Fore.CYAN}╔══ Yapper Text Editor ══╗")
    print(f"║ {Fore.WHITE}Press Ctrl+X to exit{Fore.CYAN} ║")
    print(f"╚════════════════════════╝{Style.RESET_ALL}")
    print()

def get_key():
    key = msvcrt.getch()
    # Check for special keys (arrows, etc)
    if key == b'\xe0':  # Special key prefix
        key = msvcrt.getch()  # Get the actual key code
        return {
            b'H': 'up',
            b'P': 'down',
            b'K': 'left',
            b'M': 'right'
        }.get(key, None)
    elif key == b'\x18':  # Ctrl+X
        return 'exit'
    elif key == b'\r':  # Enter
        return 'enter'
    elif key == b'\x08':  # Backspace
        return 'backspace'
    elif key == b'\xe0':  # Handle additional special keys
        return None
    else:
        try:
            return key.decode('ascii')
        except:
            return None

def editor(filename=None):
    init(autoreset=True)
    show_banner()
    
    # Create documents directory in root folder
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    docs_dir = os.path.join(root_dir, "documents")
    if not os.path.exists(docs_dir):
        os.makedirs(docs_dir)
    
    # Handle filename input or argument
    if filename is None:
        filename = input(f"{Fore.GREEN}Enter filename: {Style.RESET_ALL}")
    filepath = os.path.join(docs_dir, filename)
    
    # Load existing file content or start with empty content
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read().splitlines()
            if not content:  # Handle empty files
                content = [""]
        print(f"{Fore.GREEN}Loaded existing file: {filename}{Style.RESET_ALL}")
    else:
        content = [""]  # Start with one empty line
        if filename:  # Only show if filename was provided
            print(f"{Fore.YELLOW}New file: {filename}{Style.RESET_ALL}")
    
    cursor_y = 0
    cursor_x = 0
    
    def refresh_screen():
        # Use ANSI escape codes for efficient screen updates
        sys.stdout.write("\033[H")  # Move cursor to home position
        sys.stdout.write("\033[J")  # Clear screen from cursor down
        print(f"{Fore.CYAN}Editing: {filename} {Fore.WHITE}(Ctrl+X to save and exit){Style.RESET_ALL}\n")
        
        for i, line in enumerate(content):
            if i == cursor_y:
                # Print line with cursor using a single print
                sys.stdout.write(line[:cursor_x] + "█" + line[cursor_x:] + "\n")
            else:
                sys.stdout.write(line + "\n")
        sys.stdout.flush()
    
    refresh_screen()
    
    while True:
        key = get_key()
        if key is None:
            continue
            
        if key == 'exit':
            break
        elif key == 'enter':
            # Split line at cursor
            current = content[cursor_y]
            content[cursor_y] = current[:cursor_x]
            content.insert(cursor_y + 1, current[cursor_x:])
            cursor_y += 1
            cursor_x = 0
        elif key == 'backspace':
            if cursor_x > 0:
                # Remove character before cursor
                current = content[cursor_y]
                content[cursor_y] = current[:cursor_x-1] + current[cursor_x:]
                cursor_x -= 1
            elif cursor_y > 0:
                # Merge with previous line
                cursor_y -= 1
                cursor_x = len(content[cursor_y])
                content[cursor_y] += content.pop(cursor_y + 1)
        elif key == 'left':
            if cursor_x > 0:
                cursor_x -= 1
            elif cursor_y > 0:
                # Move to end of previous line
                cursor_y -= 1
                cursor_x = len(content[cursor_y])
        elif key == 'right':
            if cursor_x < len(content[cursor_y]):
                cursor_x += 1
            elif cursor_y < len(content) - 1:
                # Move to start of next line
                cursor_y += 1
                cursor_x = 0
        elif key == 'up':
            if cursor_y > 0:
                cursor_y -= 1
                # Keep horizontal position if possible
                cursor_x = min(cursor_x, len(content[cursor_y]))
        elif key == 'down':
            if cursor_y < len(content) - 1:
                cursor_y += 1
                # Keep horizontal position if possible
                cursor_x = min(cursor_x, len(content[cursor_y]))
        elif isinstance(key, str) and key.isprintable():
            # Insert character at cursor
            current = content[cursor_y]
            content[cursor_y] = current[:cursor_x] + key + current[cursor_x:]
            cursor_x += 1
        
        refresh_screen()
    
    # Save file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(content))
    
    print(f"\n{Fore.GREEN}File saved to: {filepath}{Style.RESET_ALL}")
    # Clear screen and show OS banner after exit
    os.system('python ' + os.path.join(root_dir, 'SigmaOS.py'))

if __name__ == "__main__":
    # Handle command line argument
    filename = sys.argv[1] if len(sys.argv) > 1 else None
    editor(filename)
