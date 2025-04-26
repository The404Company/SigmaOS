from colorama import Fore, Style
import os
import time
import threading


def clear_screen():
    """Clears the terminal screen"""
    if os.name == 'nt':  # For Windows
        os.system('cls')
    else:  # For Unix/Linux/Mac
        os.system('clear')

def press_enter_to_continue():
    """Prompts the user to press Enter to continue."""
    input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

def loading_animation(message, duration=2, task=None):
    """Displays a loading animation in the terminal."""
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    stop_event = threading.Event()
    result = {}

    def animate():
        i = 0
        while not stop_event.is_set():
            print(f"\r{Fore.CYAN}{frames[i]} {message}", end="", flush=True)
            time.sleep(0.1)
            i = (i + 1) % len(frames)
        print(f"\r{Fore.GREEN}✓ {message}{Style.RESET_ALL}")

    if task is not None:
        thread = threading.Thread(target=animate)
        thread.start()
        try:
            result['value'] = task()
        finally:
            stop_event.set()
            thread.join()
        return result.get('value')
    else:
        end_time = time.time() + duration
        i = 0
        while time.time() < end_time:
            print(f"\r{Fore.CYAN}{frames[i]} {message}", end="", flush=True)
            time.sleep(0.1)
            i = (i + 1) % len(frames)
        print(f"\r{Fore.GREEN}✓ {message}{Style.RESET_ALL}")