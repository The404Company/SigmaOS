from SigmaOS_core import clear_screen, press_enter_to_continue, loading_animation
from colorama import *
import time

def demo_task():
    """A simple task to demonstrate the loading animation with a task"""
    time.sleep(3)
    return "Task completed!"

def main():
    # Clear the screen at start
    clear_screen()
    
    # Show simple loading animation
    print("Demonstrating simple loading animation:")
    loading_animation("Loading resources", duration=3)
    
    # Demonstrate loading with a task
    print("\nDemonstrating loading animation with a task:")
    result = loading_animation("Processing data", task=demo_task)
    print(f"Task result: {result}")
    
    # Demonstrate press enter to continue
    press_enter_to_continue()
    
    # Final clear screen
    clear_screen()
    print("Demo completed!")

if __name__ == "__main__":
    main()