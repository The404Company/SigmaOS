import os
import sys
from colorama import Fore, Style, init, Back
import msvcrt

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_banner():
    clear_screen()
    print(f"{Fore.CYAN}╔══ DoccX Viewer ══╗")
    print(f"║ {Fore.WHITE}Use arrow keys to navigate{Fore.CYAN} ║")
    print(f"║ {Fore.WHITE}ESC to exit          {Fore.CYAN} ║")
    print(f"╚═══════════════════╝{Style.RESET_ALL}")
    print()

def get_documents_dir():
    # We are in packages/DoccX/main.py, so go up 2 levels to get to root
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    docs_dir = os.path.join(root_dir, "documents")
    if not os.path.exists(docs_dir):
        os.makedirs(docs_dir)
    return docs_dir

def list_documents():
    docs_dir = get_documents_dir()
    files = [f for f in os.listdir(docs_dir) if os.path.isfile(os.path.join(docs_dir, f))]
    
    if not files:
        print(f"{Fore.YELLOW}No documents found in {docs_dir}{Style.RESET_ALL}")
        return None
    
    # Calculate total size
    total_size = sum(os.path.getsize(os.path.join(docs_dir, f)) for f in files)
    size_str = f"{total_size/1024:.1f}KB" if total_size < 1024*1024 else f"{total_size/(1024*1024):.1f}MB"
    
    print(f"{Fore.CYAN}Documents in directory ({len(files)} files, {size_str} total):{Style.RESET_ALL}")
    
    # Add search functionality
    search = input(f"{Fore.WHITE}Search (or press Enter to list all): {Style.RESET_ALL}").lower()
    matching_files = [f for f in files if search in f.lower()] if search else files
    
    if not matching_files:
        print(f"{Fore.YELLOW}No matching files found{Style.RESET_ALL}")
        return None
        
    for i, file in enumerate(matching_files, 1):
        size = os.path.getsize(os.path.join(docs_dir, file))
        size_str = f"{size/1024:.1f}KB" if size < 1024*1024 else f"{size/(1024*1024):.1f}MB"
        print(f"{Fore.GREEN}{i}. {file} {Fore.CYAN}({size_str}){Style.RESET_ALL}")
    
    while True:
        try:
            choice = input(f"\n{Fore.WHITE}Enter file number to view (or press Enter to exit): {Style.RESET_ALL}")
            if not choice:
                return None
            idx = int(choice) - 1
            if 0 <= idx < len(matching_files):
                return os.path.join(docs_dir, matching_files[idx])
        except ValueError:
            print(f"{Fore.RED}Please enter a valid number{Style.RESET_ALL}")

def view_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.readlines()
        
        if not content:
            print(f"{Fore.YELLOW}File is empty{Style.RESET_ALL}")
            input("Press Enter to continue...")
            return

        page_size = 20  # Lines per page
        current_page = 0
        total_pages = (len(content) + page_size - 1) // page_size
        search_highlight = None  # Store search term

        while True:
            clear_screen()
            print(f"{Fore.CYAN}File: {os.path.basename(filepath)}")
            print(f"Page {current_page + 1} of {total_pages} ({len(content)} lines){Style.RESET_ALL}")
            print("─" * 50)

            # Display current page with line numbers
            start = current_page * page_size
            end = min(start + page_size, len(content))
            max_line_num_width = len(str(end))
            
            for i, line in enumerate(content[start:end], start + 1):
                # Format line number
                line_num = f"{i:>{max_line_num_width}}"
                
                # Highlight search term if exists
                displayed_line = line.rstrip()
                if search_highlight and search_highlight in displayed_line.lower():
                    displayed_line = displayed_line.replace(
                        search_highlight, 
                        f"{Fore.BLACK}{Back.YELLOW}{search_highlight}{Style.RESET_ALL}"
                    )
                
                print(f"{Fore.CYAN}{line_num} │ {Style.RESET_ALL}{displayed_line}")

            print("\n" + "─" * 50)
            print(f"{Fore.WHITE}← → arrows to change page | Home/End for first/last page")
            print(f"/ to search | ESC to exit{Style.RESET_ALL}")

            # Handle keyboard input
            key = msvcrt.getch()
            if key == b'\x1b':  # ESC
                break
            elif key == b'/':  # Search
                search_term = input(f"\n{Fore.WHITE}Search: {Style.RESET_ALL}").lower()
                if search_term:
                    search_highlight = search_term
                    # Find first occurrence and jump to that page
                    for i, line in enumerate(content):
                        if search_term in line.lower():
                            current_page = i // page_size
                            break
            elif key == b'\xe0':  # Special key prefix
                key = msvcrt.getch()
                if key == b'K':  # Left arrow
                    current_page = max(0, current_page - 1)
                elif key == b'M':  # Right arrow
                    current_page = min(total_pages - 1, current_page + 1)
                elif key == b'H':  # Home
                    current_page = 0
                elif key == b'F':  # End
                    current_page = total_pages - 1

    except Exception as e:
        print(f"{Fore.RED}Error reading file: {e}{Style.RESET_ALL}")
        input("Press Enter to continue...")

def main():
    init(autoreset=True)
    show_banner()

    # If filename provided as argument, try to open it directly
    if len(sys.argv) > 1:
        filepath = os.path.join(get_documents_dir(), sys.argv[1])
        if os.path.exists(filepath):
            view_file(filepath)
            return

    # Otherwise show file list
    while True:
        show_banner()
        filepath = list_documents()
        if filepath is None:
            break
        view_file(filepath)

    # Just clear screen and exit - let SigmaOS handle the return
    clear_screen()

if __name__ == "__main__":
    main()
