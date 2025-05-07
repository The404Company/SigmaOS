from SigmaOS_core import *
from colorama import *
import time

def demo_task():
    """A simple task to demonstrate the loading animation with a task"""
    time.sleep(3)
    return "Task completed!"

def demo_env_vars():
    """Demonstrates the environment variable functions"""
    print(f"\n{Fore.CYAN}Demonstrating Environment Variable Functions:{Style.RESET_ALL}")
    
    # Part 1: Verbose mode (explicit output for demonstration)
    print(f"\n{Fore.YELLOW}1. Verbose Mode - With Explicit Output:{Style.RESET_ALL}")
    
    # Set environment variables with silent=False for demonstration
    print(f"\n{Fore.YELLOW}Setting environment variables (verbose):{Style.RESET_ALL}")
    set_env("demo_string", "Hello SigmaOS!", silent=False)
    set_env("demo_number", 42, silent=False)
    
    # Get environment variables and show them manually
    print(f"\n{Fore.YELLOW}Getting environment variables:{Style.RESET_ALL}")
    print(f"demo_string: {get_env('demo_string')}")
    print(f"demo_number: {get_env('demo_number')}")
    
    # List all environment variables (not silent)
    print(f"\n{Fore.YELLOW}Listing all environment variables (verbose):{Style.RESET_ALL}")
    list_env_vars(silent=False)
    
    # Delete an environment variable with output
    print(f"\n{Fore.YELLOW}Deleting environment variable 'demo_string' (verbose):{Style.RESET_ALL}")
    delete_env("demo_string", silent=False)
    
    # Part 2: Silent mode (how packages should typically use it)
    print(f"\n{Fore.YELLOW}2. Silent Mode - How Packages Should Use It:{Style.RESET_ALL}")
    
    # Silent operations - no direct output
    print(f"\n{Fore.YELLOW}Setting environment variables silently:{Style.RESET_ALL}")
    
    # These operations won't produce any output themselves
    set_env("silent_string", "This was set silently")
    set_env("silent_list", ["apple", "banana", "cherry"])
    set_env("silent_dict", {"name": "SigmaOS", "version": "0.2.x"})
    
    # Show how to read variables silently and use them
    print(f"\n{Fore.YELLOW}Using environment variables in code:{Style.RESET_ALL}")
    silent_string = get_env("silent_string")
    silent_list = get_env("silent_list")
    silent_dict = get_env("silent_dict")
    
    # Show the values manually in your code when needed
    print(f"We retrieved silently: {silent_string}")
    print(f"We retrieved a list silently: {', '.join(silent_list)}")
    print(f"We retrieved version info silently: {silent_dict['version']}")
    
    # Example of silently deleting without feedback
    print(f"\n{Fore.YELLOW}Silently cleaning up our environment variables:{Style.RESET_ALL}")
    delete_env("silent_string")  # No output
    delete_env("silent_list")    # No output
    delete_env("silent_dict")    # No output
    delete_env("demo_number")    # No output
    
    # Example of handling non-existent variables
    print(f"\n{Fore.YELLOW}Handling non-existent variables with defaults:{Style.RESET_ALL}")
    user_pref = get_env("user_preference", "default_value")  # Will return "default_value"
    print(f"Retrieved preference with default: {user_pref}")
    
    # Get all vars silently for programmatic use
    all_vars = list_env_vars(silent=True)
    print(f"\nNumber of environment variables remaining: {len(all_vars)}")

def main():
    # Clear the screen at start
    clear_screen()
    
    press_enter_to_continue()

    suck("https://raw.githubusercontent.com/The404Company/The404Company.github.io/refs/heads/main/T404C_logo.png", save_to_documents=True, filename="i_just_downnloaded_this.png", hidden=False)

    # Show simple loading animation
    print("Demonstrating simple loading animation:")
    loading_animation("Loading resources", duration=3)
    
    # Demonstrate loading with a task
    print("\nDemonstrating loading animation with a task:")
    result = loading_animation("Processing data", task=demo_task)
    print(f"Task result: {result}")
    
    # Demonstrate environment variable functions
    demo_env_vars()
    
    # Demonstrate press enter to continue
    press_enter_to_continue()
    
    # Final clear screen
    clear_screen()
    log("Demo completed!") # doesn't work here...

if __name__ == "__main__":
    main()