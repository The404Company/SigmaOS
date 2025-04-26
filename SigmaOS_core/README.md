# SigmaOS_core
Core utilities for SigmaOS packages that provide common functionality for terminal operations.

## Quick Start
```python
from SigmaOS_core import clear_screen, loading_animation, press_enter_to_continue
from colorama import Fore, Style  # Required for colored output

# Clear terminal
clear_screen()

# Simple loading animation
loading_animation("Processing data", duration=2)

# Loading with a task
result = loading_animation("Downloading files", task=lambda: download_files())

# Wait for user input
press_enter_to_continue()
```

## Available Functions

### `clear_screen()`
Clears the terminal screen in a cross-platform way.

### `loading_animation(message, duration=2, task=None)`
Shows an animated loading indicator with optional task execution.

Parameters:
- `message`: Text to display next to the animation
- `duration`: How long to show the animation (default: 2 seconds)
- `task`: Optional callable to execute during animation
- Returns: Task result if a task was provided

### `press_enter_to_continue()`
Displays a "Press Enter to continue..." prompt.

## Example Package
```python
from SigmaOS_core import clear_screen, loading_animation
from colorama import Fore, Style

def main():
    clear_screen()
    print(f"{Fore.CYAN}MyPackage v1.0{Style.RESET_ALL}")
    
    # Show loading while processing
    result = loading_animation("Processing data", 
                             task=lambda: process_data())
    
    print(f"Result: {result}")

if __name__ == "__main__":
    main()
```

## Demo
Check out [demo.py](demo.py) for more usage examples.

## Dependencies
- colorama (automatically installed by SigmaOS)

## Note
This module is not part of SigmaOS and should be used in SigmaOS packages.