import os
import socket
import sys
import time
import dns.resolver
import speedtest
from scapy.all import ARP, Ether, srp
from colorama import Fore, Style, init
import subprocess

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_banner():
    clear_screen()
    print(f"{Fore.CYAN}╔═══ OmegaNet Tools ═══╗")
    print(f"║ 1. Ping Tool          ║")
    print(f"║ 2. Port Scanner       ║")
    print(f"║ 3. DNS Lookup         ║")
    print(f"║ 4. Speed Test         ║")
    print(f"║ 5. Device Discovery   ║")
    print(f"║ 0. Exit              ║")
    print(f"╚════════════════════════╝{Style.RESET_ALL}")

def ping_host():
    host = input(f"\n{Fore.WHITE}Enter hostname/IP to ping: {Style.RESET_ALL}")
    count = 4
    print(f"\n{Fore.CYAN}Pinging {host}...{Style.RESET_ALL}")
    
    for i in range(count):
        try:
            output = subprocess.run(['ping', '-n', '1', host], 
                                  capture_output=True, text=True)
            if "TTL=" in output.stdout:
                print(f"{Fore.GREEN}Reply from {host}: time={output.stdout.split('time=')[1].split('ms')[0]}ms{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}Request timed out{Style.RESET_ALL}")
        except:
            print(f"{Fore.RED}Error pinging host{Style.RESET_ALL}")
        time.sleep(1)

def scan_ports():
    target = input(f"\n{Fore.WHITE}Enter hostname/IP to scan: {Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Scanning common ports...{Style.RESET_ALL}")
    
    common_ports = [21, 22, 23, 25, 53, 80, 443, 445, 3389, 8080]
    open_ports = []
    
    for port in common_ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((target, port))
        if result == 0:
            open_ports.append(port)
        sock.close()
        
    if open_ports:
        print(f"\n{Fore.GREEN}Open ports on {target}:{Style.RESET_ALL}")
        for port in open_ports:
            print(f"{Fore.CYAN}  ▶ Port {port}{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}No open ports found{Style.RESET_ALL}")

def dns_lookup():
    domain = input(f"\n{Fore.WHITE}Enter domain to lookup: {Style.RESET_ALL}")
    record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT']
    
    print(f"\n{Fore.CYAN}DNS Records for {domain}:{Style.RESET_ALL}")
    for record in record_types:
        try:
            answers = dns.resolver.resolve(domain, record)
            print(f"\n{Fore.GREEN}{record} Records:{Style.RESET_ALL}")
            for rdata in answers:
                print(f"{Fore.WHITE}  ▶ {rdata}{Style.RESET_ALL}")
        except:
            continue

def speed_test():
    print(f"\n{Fore.YELLOW}Initializing speed test...{Style.RESET_ALL}")
    st = speedtest.Speedtest()
    
    print(f"{Fore.CYAN}Testing download speed...{Style.RESET_ALL}")
    download_speed = st.download() / 1_000_000  # Convert to Mbps
    
    print(f"{Fore.CYAN}Testing upload speed...{Style.RESET_ALL}")
    upload_speed = st.upload() / 1_000_000  # Convert to Mbps
    
    print(f"\n{Fore.GREEN}Results:{Style.RESET_ALL}")
    print(f"Download: {Fore.CYAN}{download_speed:.2f} Mbps{Style.RESET_ALL}")
    print(f"Upload: {Fore.CYAN}{upload_speed:.2f} Mbps{Style.RESET_ALL}")

def discover_devices():
    print(f"\n{Fore.YELLOW}Scanning local network...{Style.RESET_ALL}")
    
    # Create ARP request packet
    arp = ARP(pdst="192.168.1.0/24")
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp
    
    try:
        result = srp(packet, timeout=3, verbose=0)[0]
        
        devices = []
        for sent, received in result:
            devices.append({'ip': received.psrc, 'mac': received.hwsrc})
        
        print(f"\n{Fore.GREEN}Found {len(devices)} devices:{Style.RESET_ALL}")
        for device in devices:
            print(f"{Fore.CYAN}IP: {device['ip']:15} MAC: {device['mac']}{Style.RESET_ALL}")
            
    except Exception as e:
        print(f"{Fore.RED}Error scanning network: {e}{Style.RESET_ALL}")

def main():
    init(autoreset=True)
    
    while True:
        show_banner()
        choice = input(f"\n{Fore.WHITE}Select option (0-5): {Style.RESET_ALL}")
        
        if choice == "1":
            ping_host()
        elif choice == "2":
            scan_ports()
        elif choice == "3":
            dns_lookup()
        elif choice == "4":
            speed_test()
        elif choice == "5":
            discover_devices()
        elif choice == "0":
            clear_screen()
            sys.exit(0)
        else:
            print(f"{Fore.RED}Invalid option!{Style.RESET_ALL}")
        
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
