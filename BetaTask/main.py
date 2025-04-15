import os
import sys
import psutil
import time
from colorama import Fore, Style, init
from threading import Thread, Event
import statistics
import msvcrt  # Add this import for non-blocking keyboard input
from math import ceil

# Add global state for system metrics
system_metrics = {
    'cpu_percent': 0,
    'cpu_freq': 0,
    'cpu_count': psutil.cpu_count(),  # Add CPU count
    'mem_used': '0B',
    'mem_total': '0B',
    'mem_percent': 0,
    'disk_used': '0B',
    'disk_total': '0B',
    'disk_percent': 0,
    'cpu_history': []  # Store CPU history for averaging
}
stop_monitoring = Event()

def move_cursor(x, y):
    """Move cursor to position"""
    sys.stdout.write(f"\033[{y};{x}H")

def clear_line():
    """Clear line from cursor position"""
    sys.stdout.write("\033[K")

def clear_screen():
    """Clear screen and reset cursor"""
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()

def show_banner():
    move_cursor(1, 1)
    print(f"{Fore.CYAN}╔═══ BetaTask Manager ═══╗")
    print(f"║ {Fore.WHITE}Process Monitor v1.0   {Fore.CYAN}║")
    print(f"╚════════════════════════╝{Style.RESET_ALL}")

def get_size(bytes):
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024:
            return f"{bytes:.1f}{unit}"
        bytes /= 1024

def monitor_system():
    """Continuously monitor system resources in background"""
    while not stop_monitoring.is_set():
        # CPU measurements
        cpu_percent = psutil.cpu_percent(interval=0.5)
        system_metrics['cpu_history'].append(cpu_percent)
        if len(system_metrics['cpu_history']) > 4:  # Keep last 4 measurements
            system_metrics['cpu_history'].pop(0)
        
        system_metrics.update({
            'cpu_percent': statistics.mean(system_metrics['cpu_history']),
            'cpu_freq': psutil.cpu_freq().current,
            'cpu_count': psutil.cpu_count(),
            
            # Memory info
            'mem_used': get_size(psutil.virtual_memory().used),
            'mem_total': get_size(psutil.virtual_memory().total),
            'mem_percent': psutil.virtual_memory().percent,
            
            # Disk info
            'disk_used': get_size(psutil.disk_usage('/').used),
            'disk_total': get_size(psutil.disk_usage('/').total),
            'disk_percent': psutil.disk_usage('/').percent
        })
        time.sleep(0.5)  # Update twice per second

def display_system_info():
    """Display current system metrics"""
    # Calculate bars
    cpu_bar = "█" * int(system_metrics['cpu_percent'] / 5) + "░" * (20 - int(system_metrics['cpu_percent'] / 5))
    mem_bar = "█" * int(system_metrics['mem_percent'] / 5) + "░" * (20 - int(system_metrics['mem_percent'] / 5))
    disk_bar = "█" * int(system_metrics['disk_percent'] / 5) + "░" * (20 - int(system_metrics['disk_percent'] / 5))
    
    # Move to correct position and update
    move_cursor(1, 5)
    print(f"{Fore.YELLOW}System Resources:{Style.RESET_ALL}")
    move_cursor(1, 6)
    print(f"{Fore.CYAN}CPU  [{Fore.WHITE}{cpu_bar}{Fore.CYAN}] {system_metrics['cpu_percent']:>5.1f}% ({system_metrics['cpu_count']} cores @ {system_metrics['cpu_freq']:.0f}MHz)")
    move_cursor(1, 7)
    print(f"{Fore.CYAN}MEM  [{Fore.WHITE}{mem_bar}{Fore.CYAN}] {system_metrics['mem_percent']:>5.1f}% ({system_metrics['mem_used']}/{system_metrics['mem_total']})")
    move_cursor(1, 8)
    print(f"{Fore.CYAN}DISK [{Fore.WHITE}{disk_bar}{Fore.CYAN}] {system_metrics['disk_percent']:>5.1f}% ({system_metrics['disk_used']}/{system_metrics['disk_total']})")

def get_process_list():
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            pinfo = proc.info
            pinfo['memory_mb'] = proc.memory_info().rss / (1024 * 1024)
            processes.append(pinfo)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    # Sort by CPU usage and get top 10
    return sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:10]

def kill_process(pid):
    try:
        proc = psutil.Process(pid)
        proc.terminate()
        print(f"{Fore.GREEN}Process terminated successfully.{Style.RESET_ALL}")
    except psutil.NoSuchProcess:
        print(f"{Fore.RED}Process not found.{Style.RESET_ALL}")
    except psutil.AccessDenied:
        print(f"{Fore.RED}Access denied. Try running with administrator privileges.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
    time.sleep(2)

def display_processes(processes, start_line=10):
    """Display process list at specified line"""
    move_cursor(1, start_line)
    clear_line()
    print(f"{Fore.YELLOW}Top 10 Processes:{Style.RESET_ALL}")
    move_cursor(1, start_line + 1)
    clear_line()
    print(f"{Fore.WHITE}{'ID':<6} {'PID':<8} {'CPU%':>6} {'MEM%':>6} {'MEM(MB)':>8} {'Name'}{Style.RESET_ALL}")
    move_cursor(1, start_line + 2)
    clear_line()
    print("─" * 60)
    
    # Print each process on its own line with proper positioning
    for i, proc in enumerate(processes, 1):
        move_cursor(1, start_line + 2 + i)
        clear_line()
        print(f"{Fore.GREEN}{i:<6}{Style.RESET_ALL}"
              f"{proc['pid']:<8}"
              f"{proc['cpu_percent']:>6.1f}"
              f"{proc['memory_percent']:>6.1f}"
              f"{proc['memory_mb']:>8.1f}"
              f" {proc['name']}")
    
    # Clear any remaining lines that might have old process entries
    for i in range(len(processes), 10):
        move_cursor(1, start_line + 3 + i)
        clear_line()

def main():
    init(autoreset=True)
    
    # Initialize metrics before starting display
    system_metrics.update({
        'cpu_freq': psutil.cpu_freq().current,
        'mem_used': get_size(psutil.virtual_memory().used),
        'mem_total': get_size(psutil.virtual_memory().total),
        'mem_percent': psutil.virtual_memory().percent,
        'disk_used': get_size(psutil.disk_usage('/').used),
        'disk_total': get_size(psutil.disk_usage('/').total),
        'disk_percent': psutil.disk_usage('/').percent
    })
    
    # Start system monitoring thread
    monitor_thread = Thread(target=monitor_system, daemon=True)
    monitor_thread.start()
    
    # Clear screen once at startup
    clear_screen()
    
    processes = get_process_list()  # Initial process list
    command_buffer = ""
    command_line = 24  # Fixed position for command line
    
    while True:
        # Update display without clearing screen
        show_banner()
        display_system_info()
        display_processes(processes)
        
        # Show controls and command buffer at fixed position with proper spacing
        move_cursor(1, command_line - 2)
        clear_line()
        print()  # Add empty line after process list
        print(f"{Fore.WHITE}R: Refresh | Q: Quit | 1-10: Select process{Style.RESET_ALL}")
        move_cursor(1, command_line)
        clear_line()
        print(f"{Fore.WHITE}Command: {command_buffer}{Style.RESET_ALL}", end='', flush=True)
        
        # Non-blocking check for keyboard input
        if msvcrt.kbhit():
            key = msvcrt.getch()
            try:
                char = key.decode('utf-8').lower()
                if char == '\r':  # Enter key
                    if command_buffer == 'q':
                        stop_monitoring.set()
                        clear_screen()
                        sys.exit(0)
                    elif command_buffer == 'r':
                        processes = get_process_list()
                    else:
                        try:
                            idx = int(command_buffer) - 1
                            if 0 <= idx < len(processes):
                                pid = processes[idx]['pid']
                                name = processes[idx]['name']
                                print(f"\n{Fore.YELLOW}Terminate {name}? (y/N): {Style.RESET_ALL}", end='')
                                if msvcrt.getch().decode('utf-8').lower() == 'y':
                                    kill_process(pid)
                                    processes = get_process_list()  # Refresh after killing
                        except ValueError:
                            pass
                    command_buffer = ""
                elif char.isprintable():
                    command_buffer += char
            except UnicodeDecodeError:
                pass
        
        # Short sleep to prevent high CPU usage
        time.sleep(0.1)

if __name__ == "__main__":
    main()
