import os
import sys
import time
import curses
import psutil
from colorama import Fore, Style, init
from datetime import datetime

class ProcessManager:
    def __init__(self):
        self.sort_by = "cpu"
        self.processes = []
        self.selected_index = 0
        self.start_index = 0
        self.page_size = 20

    def get_processes(self):
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
            try:
                info = proc.info
                info['cpu_percent'] = proc.cpu_percent()
                info['memory_percent'] = proc.memory_percent()
                processes.append(info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Sort processes
        if self.sort_by == "cpu":
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        elif self.sort_by == "memory":
            processes.sort(key=lambda x: x['memory_percent'], reverse=True)
        elif self.sort_by == "name":
            processes.sort(key=lambda x: x['name'].lower())
        elif self.sort_by == "pid":
            processes.sort(key=lambda x: x['pid'])
            
        self.processes = processes

    def draw_header(self, stdscr, width):
        header = f" {'PID':>6} | {'Name':<20} | {'CPU%':>6} | {'Memory%':>8} | {'Status':<8}"
        stdscr.addstr(0, 0, "─" * width)
        stdscr.addstr(1, 0, header)
        stdscr.addstr(2, 0, "─" * width)

    def draw_processes(self, stdscr, height):
        for idx, proc in enumerate(self.processes[self.start_index:self.start_index + self.page_size]):
            if idx + 3 >= height:
                break
                
            line = f" {proc['pid']:>6} | {proc['name'][:20]:<20} | {proc['cpu_percent']:>6.1f} | {proc['memory_percent']:>7.1f}% | {proc['status']:<8}"
            
            if idx == self.selected_index - self.start_index:
                stdscr.attron(curses.A_REVERSE)
                stdscr.addstr(idx + 3, 0, line)
                stdscr.attroff(curses.A_REVERSE)
            else:
                stdscr.addstr(idx + 3, 0, line)

    def draw_usage_graph(self, stdscr, height, width):
        # Get system-wide CPU and memory usage
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        
        # Draw CPU bar
        cpu_bar = "█" * int(cpu_percent / 100 * 20)
        cpu_line = f"CPU Usage: [{cpu_bar:<20}] {cpu_percent:>5.1f}%"
        stdscr.addstr(height-3, 2, cpu_line)
        
        # Draw memory bar
        mem_bar = "█" * int(memory.percent / 100 * 20)
        mem_line = f"Memory:   [{mem_bar:<20}] {memory.percent:>5.1f}%"
        stdscr.addstr(height-2, 2, mem_line)

    def draw_help(self, stdscr, height, width):
        help_text = " [↑/↓] Navigate  [S]ort  [K]ill  [Q]uit "
        stdscr.addstr(height-1, 0, "─" * width)
        stdscr.addstr(height-1, (width - len(help_text)) // 2, help_text)

    def run(self, stdscr):
        curses.curs_set(0)  # Hide cursor
        stdscr.timeout(1000)  # Update every second
        
        while True:
            self.get_processes()
            height, width = stdscr.getmaxyx()
            
            stdscr.clear()
            self.draw_header(stdscr, width)
            self.draw_processes(stdscr, height)
            self.draw_usage_graph(stdscr, height, width)
            self.draw_help(stdscr, height, width)
            
            try:
                key = stdscr.getch()
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    # Cycle through sort options
                    sort_options = ["cpu", "memory", "name", "pid"]
                    current_idx = sort_options.index(self.sort_by)
                    self.sort_by = sort_options[(current_idx + 1) % len(sort_options)]
                elif key == ord('k'):
                    # Kill selected process
                    selected_proc = self.processes[self.selected_index]
                    try:
                        psutil.Process(selected_proc['pid']).terminate()
                    except:
                        pass
                elif key == curses.KEY_UP and self.selected_index > 0:
                    self.selected_index -= 1
                    if self.selected_index < self.start_index:
                        self.start_index = self.selected_index
                elif key == curses.KEY_DOWN and self.selected_index < len(self.processes) - 1:
                    self.selected_index += 1
                    if self.selected_index >= self.start_index + self.page_size:
                        self.start_index = self.selected_index - self.page_size + 1
            except:
                pass
            
            stdscr.refresh()

def main():
    if os.name != 'nt':
        print(f"{Fore.RED}This package only works on Windows systems.{Style.RESET_ALL}")
        return
        
    pm = ProcessManager()
    curses.wrapper(pm.run)

if __name__ == "__main__":
    main()
