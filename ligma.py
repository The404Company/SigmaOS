#!/usr/bin/env python3
"""
Ligma Package Manager for SigmaOS
This module handles all package management functionality for SigmaOS.
"""

# Ligma package manager version
VERSION = "1.1.0"

import os
import sys
import json
import shutil
import platform
import subprocess
import time
import requests
from zipfile import ZipFile

# Get directory of this file
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Configuration
OFFICIAL_REPO = "The404Company/SigmaOS-packages"
REPO_URL = f"https://github.com/{OFFICIAL_REPO}"
PACKAGES_DIR = os.path.join(CURRENT_DIR, "packages")
SOURCES_FILE = os.path.join(CURRENT_DIR, "ligma.sigs")

# Verified external sources list - curated list of trusted package repositories
VERIFIED_SOURCES = [
    # Add verified sources here
]

# Try to import colorama for styling
try:
    from colorama import Fore, Style
    # Pre-define styles
    SUCCESS_STYLE = Fore.GREEN
    ERROR_STYLE = Fore.RED
    WARNING_STYLE = Fore.YELLOW
    INFO_STYLE = Fore.CYAN
    RESET_STYLE = Style.RESET_ALL
except ImportError:
    # Fallback if colorama isn't installed
    SUCCESS_STYLE = ""
    ERROR_STYLE = ""
    WARNING_STYLE = ""
    INFO_STYLE = ""
    RESET_STYLE = ""

# Log function (simplified version)
def log_info(message):
    """Simple logging function"""
    # Get the logging function from SigmaOS if available
    try:
        from SigmaOS import log_info as sigma_log_info
        sigma_log_info(message)
    except ImportError:
        print(f"[INFO] {message}")

def log_error(message, exception=None):
    """Simple error logging function"""
    try:
        from SigmaOS import log_error as sigma_log_error
        sigma_log_error(message, exception=exception)
    except ImportError:
        print(f"[ERROR] {message}")
        if exception:
            print(f"Exception: {exception}")

def log_warning(message):
    """Simple warning logging function"""
    try:
        from SigmaOS import log_warning as sigma_log_warning
        sigma_log_warning(message)
    except ImportError:
        print(f"[WARNING] {message}")

def log_success(message):
    """Simple success logging function"""
    try:
        from SigmaOS import log_success as sigma_log_success
        sigma_log_success(message)
    except ImportError:
        print(f"[SUCCESS] {message}")

def log_debug(message):
    """Simple debug logging function"""
    try:
        from SigmaOS import log_debug as sigma_log_debug
        sigma_log_debug(message)
    except ImportError:
        print(f"[DEBUG] {message}")

def loading_animation(message, duration=2, task=None):
    """
    Show a loading animation for a fixed duration or while a task runs.
    If task is provided, it should be a function (optionally with args/kwargs).
    """
    # Try to use SigmaOS loading_animation if available
    try:
        from SigmaOS import loading_animation as sigma_loading_animation
        return sigma_loading_animation(message, duration, task)
    except ImportError:
        # Fallback simple loading animation
        if task:
            print(f"{INFO_STYLE}{message}...{RESET_STYLE}")
            result = task()
            print(f"{SUCCESS_STYLE}✓ {message}{RESET_STYLE}")
            return result
        else:
            print(f"{INFO_STYLE}{message}...{RESET_STYLE}")
            time.sleep(duration)
            print(f"{SUCCESS_STYLE}✓ {message}{RESET_STYLE}")

def get_github_file_content(package_name, filename, source=None):
    """Fetch raw file content from GitHub
    
    Args:
        package_name (str): Name of the package
        filename (str): Name of the file to fetch
        source (str, optional): Specific source to check. If None, checks all sources.
    """
    if source:
        # Check specific source
        url = f"https://raw.githubusercontent.com/{source}/main/{package_name}/{filename}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.text.strip()
        except:
            pass
        return None
        
    # Check all configured sources
    sources = load_sources()
    # Try official repo first
    if OFFICIAL_REPO in sources:
        sources.remove(OFFICIAL_REPO)
        sources.insert(0, OFFICIAL_REPO)
    
    for src in sources:
        url = f"https://raw.githubusercontent.com/{src}/main/{package_name}/{filename}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.text.strip()
        except:
            continue
    return None

def parse_description_file(content):
    """Parse the sections from a description.txt file"""
    sections = {
        'description': 'No description available',
        'author': 'Unknown',
        'version': '0.0',
        'requirements': []
    }
    
    current_section = None
    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('[') and line.endswith(']'):
            current_section = line[1:-1].lower()
            continue
            
        if current_section:
            if current_section == 'requirements':
                if line:
                    sections[current_section].append(line)
            else:
                sections[current_section] = line
                
    return sections

def get_package_description(package_name, source=None, installed=True):
    """Get package description from local file or GitHub
    
    Args:
        package_name (str): Name of the package
        source (str, optional): Specific source to check for online content
        installed (bool): Whether to check local installation first
    """
    if installed and is_valid_package(package_name):
        desc_file = os.path.join(PACKAGES_DIR, package_name, "description.txt")
        try:
            if os.path.exists(desc_file):
                with open(desc_file, 'r', encoding='utf-8') as f:
                    return parse_description_file(f.read())
        except:
            pass
    
    # Try to fetch from GitHub for non-installed packages
    content = get_github_file_content(package_name, "description.txt", source=source)
    if content:
        return parse_description_file(content)
    
    return {'description': 'No description available', 'author': 'Unknown', 'version': '0.0', 'requirements': []}

def get_package_version(package_name):
    """Show the version of a package"""
    desc = get_package_description(package_name, is_valid_package(package_name))
    installed_text = "installed" if is_valid_package(package_name) else "available"
    print(f"\n{INFO_STYLE}Package {package_name} ({installed_text}){RESET_STYLE}")
    print(f"{SUCCESS_STYLE}Version: {desc['version']}{RESET_STYLE}")

def show_package_info(package_name):
    """Show the full package description with highlighted section headers"""
    desc_file = None
    
    # First try to get the local file if installed
    if is_valid_package(package_name):
        desc_file = os.path.join(PACKAGES_DIR, package_name, "description.txt")
        source = "installed"
    else:
        # If not installed, try to get from GitHub
        content = get_github_file_content(package_name, "description.txt")
        if content:
            # Create a temporary file
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
                f.write(content)
                desc_file = f.name
            source = "online repository"
    
    if not desc_file or not os.path.exists(desc_file):
        print(f"{ERROR_STYLE}No description available for {package_name}{RESET_STYLE}")
        return
    
    try:
        with open(desc_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        print(f"\n{INFO_STYLE}Package information for {package_name} (from {source}):{RESET_STYLE}\n")
        
        # Format the content with highlighted section headers
        for line in content.splitlines():
            if line.startswith('[') and line.endswith(']'):
                print(f"{SUCCESS_STYLE}{line}{RESET_STYLE}")
            else:
                print(line)
    except Exception as e:
        print(f"{ERROR_STYLE}Error reading description: {e}{RESET_STYLE}")
    finally:
        # Clean up temporary file if we created one
        if source == "online repository" and desc_file and os.path.exists(desc_file):
            os.unlink(desc_file)

def show_installed_packages():
    """Show only installed packages"""
    installed_packages = []
    if os.path.exists(PACKAGES_DIR):
        installed_packages = [d for d in os.listdir(PACKAGES_DIR) 
                            if os.path.isdir(os.path.join(PACKAGES_DIR, d)) 
                            and not d.startswith('.') 
                            and d != "SigmaOS-packages-main"]
    
    try:
        # Try to get styles from SigmaOS if available
        from SigmaOS import package_sth, description_sth, package_status_sth, SUCCESS_STYLE, WARNING_STYLE, ERROR_STYLE
    except ImportError:
        # Fallback styles
        package_sth = SUCCESS_STYLE
        description_sth = RESET_STYLE
        package_status_sth = INFO_STYLE
    
    if installed_packages:
        print(f"\n{SUCCESS_STYLE}Installed Packages:{RESET_STYLE}")
        for i, pkg in enumerate(installed_packages):
            if i > 0:  # Add empty line before each package except the first one
                print()
            desc = get_package_description(pkg)
            print(f"{package_sth}{pkg} {description_sth}- {desc['description']}")
            print(f"{package_status_sth}{desc['author']} {description_sth}- v{desc['version']}")
    else:
        print(f"{WARNING_STYLE}No packages installed. Use 'ligma browse' to see available packages.{RESET_STYLE}")

def search_packages(search_term):
    """Search for packages by name or description"""
    search_term = search_term.lower()
    
    # Get installed packages first (for status tracking)
    installed_packages = []
    if os.path.exists(PACKAGES_DIR):
        installed_packages = [d for d in os.listdir(PACKAGES_DIR) 
                            if os.path.isdir(os.path.join(PACKAGES_DIR, d)) 
                            and not d.startswith('.')]
    
    # Search all configured sources
    sources = load_sources()
    if OFFICIAL_REPO in sources:
        sources.remove(OFFICIAL_REPO)
        sources.insert(0, OFFICIAL_REPO)  # Search official repo first
        
    found_packages = {}  # Use dict to avoid duplicates, store source info
    
    for source in sources:
        print(f"{INFO_STYLE}Searching in {source}...{RESET_STYLE}")
        headers = {'Accept': 'application/vnd.github.v3+json'}
        response = requests.get(f"https://api.github.com/repos/{source}/contents/", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            package_names = [item["name"] for item in data 
                           if item["type"] == "dir" and not item["name"].startswith('.')]
            
            # First check name matches
            for pkg in package_names:
                if search_term in pkg.lower() and pkg not in found_packages:
                    found_packages[pkg] = source
            
            # Then check descriptions
            for pkg in package_names:
                if pkg not in found_packages:  # Skip if already found by name
                    desc = get_package_description(pkg, source=source, installed=(pkg in installed_packages))
                    if search_term in desc['description'].lower():
                        found_packages[pkg] = source
    
    try:
        # Try to get styles from SigmaOS if available
        from SigmaOS import package_sth, description_sth, package_status_sth, SUCCESS_STYLE, WARNING_STYLE, ERROR_STYLE
    except ImportError:
        # Fallback styles
        package_sth = SUCCESS_STYLE
        description_sth = RESET_STYLE
        package_status_sth = INFO_STYLE
    
    if found_packages:
        print(f"\n{SUCCESS_STYLE}Found {len(found_packages)} package(s) matching '{search_term}':{RESET_STYLE}")
        
        for pkg, source in found_packages.items():
            is_installed = pkg in installed_packages
            status = f"{SUCCESS_STYLE}[Installed]{RESET_STYLE}" if is_installed else f"{WARNING_STYLE}[Available]{RESET_STYLE}"
            source_text = f"{INFO_STYLE}[{source}]{RESET_STYLE}"
            
            desc = get_package_description(pkg, source=source, installed=is_installed)
            print(f"\n{package_sth}{pkg} {status} {source_text}")
            print(f"{description_sth}{desc['description']}")
            print(f"{package_status_sth}Author: {desc['author']} - Version: {desc['version']}")
    else:
        print(f"{WARNING_STYLE}No packages found matching '{search_term}'{RESET_STYLE}")

def browse_source(source):
    """Browse packages from a specific source repository
    
    Args:
        source (str): The source repository in format username/repo
    """
    try:
        # Try to get styles from SigmaOS if available
        from SigmaOS import (
            package_sth, description_sth, package_status_sth, command_sth,
            header_sth, SUCCESS_STYLE, WARNING_STYLE, ERROR_STYLE, INFO_STYLE
        )
    except ImportError:
        # Fallback styles
        package_sth = SUCCESS_STYLE
        description_sth = RESET_STYLE
        package_status_sth = INFO_STYLE
        command_sth = SUCCESS_STYLE
        header_sth = INFO_STYLE
    
    try:
        # Get installed packages first for status tracking
        installed_packages = []
        if os.path.exists(PACKAGES_DIR):
            installed_packages = [d for d in os.listdir(PACKAGES_DIR) 
                               if os.path.isdir(os.path.join(PACKAGES_DIR, d)) 
                               and not d.startswith('.')]

        # Get packages from the specified source
        headers = {'Accept': 'application/vnd.github.v3+json'}
        response = requests.get(f"https://api.github.com/repos/{source}/contents/", headers=headers)
        loading_animation(f"Fetching packages from {source}...")

        if response.status_code == 200:
            data = response.json()
            available_packages = [item["name"] for item in data 
                               if item["type"] == "dir" and not item["name"].startswith('.')]

            if not available_packages:
                print(f"{WARNING_STYLE}No packages found in {source}.{RESET_STYLE}")
                return

            print(f"\n{INFO_STYLE}Available packages in {source}:{RESET_STYLE}")
            for i, pkg in enumerate(available_packages):
                if i > 0:  # Add empty line before each package except the first one
                    print()
                try:
                    # Try to get package description from this source
                    desc_url = f"https://raw.githubusercontent.com/{source}/main/{pkg}/description.txt"
                    desc_response = requests.get(desc_url)
                    if desc_response.status_code == 200:
                        desc = parse_description_file(desc_response.text)
                        status = f"{SUCCESS_STYLE}[Installed]{RESET_STYLE}" if pkg in installed_packages else f"{WARNING_STYLE}[Available]{RESET_STYLE}"
                        print(f"{package_sth}{pkg} {status} {description_sth}- {desc['description']}")
                        print(f"{package_status_sth}{desc['author']} {description_sth}- v{desc['version']}")
                    else:
                        print(f"{package_sth}{pkg} {WARNING_STYLE}[No description available]{RESET_STYLE}")
                except Exception as e:
                    print(f"{package_sth}{pkg} {ERROR_STYLE}[Error: {str(e)}]{RESET_STYLE}")
        else:
            print(f"{ERROR_STYLE}Error fetching from {source}. Status code: {response.status_code}{RESET_STYLE}")
            if response.status_code == 404:
                print(f"{INFO_STYLE}Repository may not exist or may be private.{RESET_STYLE}")
    except Exception as e:
        print(f"{ERROR_STYLE}Error browsing source {source}: {e}{RESET_STYLE}")

def browse_packages():
    """Browse available packages"""
    try:
        # Try to get styles from SigmaOS if available
        from SigmaOS import (
            command_sth, description_sth, header_sth,
            SUCCESS_STYLE, WARNING_STYLE, ERROR_STYLE, INFO_STYLE
        )
    except ImportError:
        # Fallback styles
        command_sth = SUCCESS_STYLE
        description_sth = RESET_STYLE
        header_sth = INFO_STYLE
    
    sources = load_sources()
    
    if len(sources) > 1:
        # Multiple sources configured
        print(f"{INFO_STYLE}Use one of these commands to browse packages:{RESET_STYLE}")
        print(f"{command_sth}  ligma browse official{description_sth}      - Browse the official repository")
        print(f"{command_sth}  ligma browse <user>/<repo>{description_sth} - Browse a specific source")
        print(f"\n{INFO_STYLE}Available sources:{RESET_STYLE}")
        for source in sources:
            print(f"{description_sth}  ▶ {source}")
        return
    
    # If only official source is configured, show its packages directly
    browse_source(OFFICIAL_REPO)

def show_ligma_version():
    """Display the ligma package manager version"""
    try:
        # Try to get styles from SigmaOS if available
        from SigmaOS import description_sth
    except ImportError:
        # Fallback style
        description_sth = RESET_STYLE
        
    print(f"\n{INFO_STYLE}Ligma Package Manager v{VERSION}{RESET_STYLE}")
    print(f"{description_sth}The lightweight package manager for SigmaOS{RESET_STYLE}")

def show_ligma_help():
    """Show detailed help for all ligma commands"""
    try:
        # Try to get styles from SigmaOS if available
        from SigmaOS import command_sth, description_sth, header_sth, INFO_STYLE, SUCCESS_STYLE, RESET_STYLE
    except ImportError:
        # Fallback styles
        command_sth = SUCCESS_STYLE
        description_sth = RESET_STYLE
        header_sth = INFO_STYLE
        INFO_STYLE = INFO_STYLE
        SUCCESS_STYLE = SUCCESS_STYLE
        RESET_STYLE = RESET_STYLE
    
    print(f"\n{header_sth}╔══ Ligma Package Manager Help ══════════════════════════╗{RESET_STYLE}")
    
    # Package Browsing
    print(f"\n{INFO_STYLE}Package Browsing:{RESET_STYLE}")
    browse_commands = [
        ("ligma list", "Show installed packages only"),
        ("ligma browse", "Browse all available packages"),
        ("ligma search <term>", "Search for packages by name or description")
    ]
    for cmd, desc in browse_commands:
        print(f"{command_sth}  {cmd:<30}{description_sth} - {desc}")
    
    # Package Management
    print(f"\n{INFO_STYLE}Package Management:{RESET_STYLE}")
    manage_commands = [
        ("ligma install <pkg>", "Install a package"),
        ("ligma install <pkg1> <pkg2> ?m", "Install multiple packages"),
        ("ligma uninstall <pkg>", "Uninstall a package")
    ]
    for cmd, desc in manage_commands:
        print(f"{command_sth}  {cmd:<30}{description_sth} - {desc}")
    
    # Package Information
    print(f"\n{INFO_STYLE}Package Information:{RESET_STYLE}")
    info_commands = [
        ("ligma <pkg> ?v", "Show package version"),
        ("ligma <pkg> ?version", "Show package version"),
        ("ligma <pkg> ?i", "Show full package information"),
        ("ligma <pkg> ?info", "Show full package information")
    ]
    for cmd, desc in info_commands:
        print(f"{command_sth}  {cmd:<30}{description_sth} - {desc}")
    
    # Updates
    print(f"\n{INFO_STYLE}Package Updates:{RESET_STYLE}")
    update_commands = [
        ("ligma ?u", "Check all packages for updates"),
        ("ligma ?update", "Check all packages for updates"),
        ("ligma <pkg> ?u", "Update specific package"),
        ("ligma <pkg> ?update", "Update specific package")
    ]
    for cmd, desc in update_commands:
        print(f"{command_sth}  {cmd:<30}{description_sth} - {desc}")
    
    # Source Management
    print(f"\n{INFO_STYLE}Source Management:{RESET_STYLE}")
    source_commands = [
        ("ligma src add <user>/<repo>", "Add a package source"),
        ("ligma src remove <user>/<repo>", "Remove a package source"),
        ("ligma src list", "List all package sources"),
        ("ligma src verified", "Show verified package sources"),
        ("ligma browse official", "Browse official package repository"),
        ("ligma browse <user>/<repo>", "Browse a specific source repository")
    ]
    for cmd, desc in source_commands:
        print(f"{command_sth}  {cmd:<30}{description_sth} - {desc}")

    # Help
    print(f"\n{INFO_STYLE}Help and Version:{RESET_STYLE}")
    help_commands = [
        ("ligma ?h", "Show this help"),
        ("ligma ?help", "Show this help"),
        ("ligma ?v", "Show ligma version"),
        ("ligma ?version", "Show ligma version")
    ]
    for cmd, desc in help_commands:
        print(f"{command_sth}  {cmd:<30}{description_sth} - {desc}")
    
    print(f"\n{header_sth}╚{'═' * 58}╝{RESET_STYLE}")

# Keep this for backward compatibility, redirects to the new browse_packages function
def list_packages():
    """Redirects to browse_packages for backward compatibility"""
    browse_packages()

def try_download_from_source(package_name, source, package_dir, headers, is_update=False):
    """Try to download a package from a specific source"""
    package_url = f"https://api.github.com/repos/{source}/contents/{package_name}"
    try:
        response = requests.get(package_url, headers=headers)
        if response.status_code != 200:
            return False, 0, 0

        files_data = response.json()
        download_count = 0
        error_count = 0

        for file_info in files_data:
            if file_info['type'] == 'file':
                file_name = file_info['name']
                download_url = file_info['download_url']
                try:
                    file_response = requests.get(download_url)
                    if file_response.status_code == 200:
                        file_path = os.path.join(package_dir, file_name)
                        with open(file_path, 'wb') as f:
                            f.write(file_response.content)
                        download_count += 1
                    else:
                        error_count += 1
                except:
                    error_count += 1
            elif file_info['type'] == 'dir':
                subdir_name = file_info['name']
                subdir_path = os.path.join(package_dir, subdir_name)
                os.makedirs(subdir_path, exist_ok=True)
                subdir_url = file_info['url']
                
                try:
                    subdir_response = requests.get(subdir_url, headers=headers)
                    if subdir_response.status_code == 200:
                        subdir_files = subdir_response.json()
                        for subfile in subdir_files:
                            if subfile['type'] == 'file':
                                subfile_name = subfile['name']
                                subfile_download_url = subfile['download_url']
                                try:
                                    subfile_response = requests.get(subfile_download_url)
                                    if subfile_response.status_code == 200:
                                        subfile_path = os.path.join(subdir_path, subfile_name)
                                        with open(subfile_path, 'wb') as f:
                                            f.write(subfile_response.content)
                                        download_count += 1
                                    else:
                                        error_count += 1
                                except:
                                    error_count += 1
                except:
                    pass

        return True, download_count, error_count
    except:
        return False, 0, 0

def download_package(package_name, is_update=False):
    """
    Download and install a package from any configured source
    
    Args:
        package_name (str): Name of the package to download
        is_update (bool): Whether this is an update operation
    """
    if not os.path.exists(PACKAGES_DIR):
        os.makedirs(PACKAGES_DIR)
        log_info(f"Created packages directory at {PACKAGES_DIR}")

    package_dir = os.path.join(PACKAGES_DIR, package_name)

    if os.path.exists(package_dir) and not is_update:
        print(f"{WARNING_STYLE}Package {package_name} already installed. Use 'ligma {package_name} ?update' to update.{RESET_STYLE}")
        log_warning(f"Package {package_name} already downloaded.")
        return False

    # Delete the package directory if this is an update
    if is_update and os.path.exists(package_dir):
        try:
            shutil.rmtree(package_dir)
            log_info(f"Removed existing package directory for update: {package_dir}")
        except Exception as e:
            print(f"{ERROR_STYLE}Error removing existing package for update: {e}{RESET_STYLE}")
            log_error(f"Error removing package directory for update", exception=e)
            return False

    # Try sources in order: official first, then additional sources
    sources = load_sources()
    if OFFICIAL_REPO in sources:
        sources.remove(OFFICIAL_REPO)
        sources.insert(0, OFFICIAL_REPO)  # Ensure official repo is first

    headers = {'Accept': 'application/vnd.github.v3+json'}
    os.makedirs(package_dir, exist_ok=True)

    for source in sources:
        print(f"{INFO_STYLE}Trying source: {source}...{RESET_STYLE}")
        success, download_count, error_count = try_download_from_source(
            package_name, source, package_dir, headers, is_update
        )
        
        if success:
            # Verify the package has the necessary files
            if not os.path.exists(os.path.join(package_dir, "main.py")):
                print(f"{WARNING_STYLE}Warning: main.py not found in package. This package might not be runnable.{RESET_STYLE}")
            
            # Install package requirements
            desc = get_package_description(package_name, installed=True)
            if desc['requirements']:
                print(f"\n{INFO_STYLE}Installing dependencies...{RESET_STYLE}")
                log_info(f"Installing dependencies for {package_name}: {desc['requirements']}")
                core_libs = {"colorama", "requests", "datetime", "json"}
                for req in desc['requirements']:
                    if req.lower() in core_libs:
                        print(f"{WARNING_STYLE}Skipping {req} (already included in SigmaOS).{RESET_STYLE}")
                        log_info(f"Skipping requirement {req} (core library)")
                    else:
                        try:
                            loading_animation(f"Installing {req}", task=lambda req=req: subprocess.run(
                                [sys.executable, "-m", "pip", "install", req], 
                                stdout=subprocess.DEVNULL, 
                                stderr=subprocess.DEVNULL
                            ))
                            log_info(f"Installed requirement {req}")
                        except Exception as e:
                            print(f"{ERROR_STYLE}Error installing {req}: {e}{RESET_STYLE}")
                            log_error(f"Error installing requirement {req}", exception=e)
            
            # Report results
            if error_count == 0:
                print(f"{SUCCESS_STYLE}Package {package_name} successfully {'updated' if is_update else 'installed'} from {source}.{RESET_STYLE}")
                log_info(f"Package {package_name} successfully {'updated' if is_update else 'installed'}. Downloaded {download_count} files.")
                return True
            else:
                print(f"{WARNING_STYLE}Package {package_name} {'updated' if is_update else 'installed'} from {source} with {error_count} errors. Some functionality may be limited.{RESET_STYLE}")
                log_warning(f"Package {package_name} {'updated' if is_update else 'installed'} with {error_count} errors.")
                return True

    # If we get here, no source had the package
    print(f"{ERROR_STYLE}Package {package_name} not found in any configured source.{RESET_STYLE}")
    log_error(f"Package {package_name} not found in any source")
    return False

def uninstall_package(package_name):
    """Uninstall a package by removing its directory"""
    package_dir = os.path.join(PACKAGES_DIR, package_name)
    
    if not os.path.exists(package_dir):
        print(f"{ERROR_STYLE}Package {package_name} is not installed.{RESET_STYLE}")
        log_error(f"Package {package_name} is not installed (uninstall attempt).")
        return False
        
    try:
        print(f"{WARNING_STYLE}Uninstalling {package_name}...{RESET_STYLE}")
        log_info(f"Uninstalling package {package_name}")
        loading_animation(f"Removed {package_name}", task=lambda: shutil.rmtree(package_dir))
        # Don't show redundant success message
        log_info(f"Package {package_name} successfully uninstalled.")
        return True
    except PermissionError as e:
        print(f"{ERROR_STYLE}Permission error uninstalling {package_name}. Try closing any applications using it.{RESET_STYLE}")
        log_error(f"Permission error uninstalling {package_name}", exception=e)
        return False
    except Exception as e:
        print(f"{ERROR_STYLE}Error uninstalling {package_name}: {e}{RESET_STYLE}")
        log_error(f"Error uninstalling {package_name}", exception=e)
        return False

def install_multiple_packages(package_names):
    """Install multiple packages at once
    
    Args:
        package_names (list): List of package names to install
    """
    if not package_names:
        print(f"{ERROR_STYLE}No packages specified.{RESET_STYLE}")
        return

    print(f"\n{INFO_STYLE}Installing {len(package_names)} packages...{RESET_STYLE}")
    log_info(f"Installing multiple packages: {', '.join(package_names)}")
    
    installed_count = 0
    failed_packages = []
    
    for pkg in package_names:
        print(f"\n{INFO_STYLE}Installing {pkg} ({installed_count + 1}/{len(package_names)})...{RESET_STYLE}")
        if download_package(pkg):
            installed_count += 1
        else:
            failed_packages.append(pkg)
    
    # Report summary
    if installed_count == len(package_names):
        print(f"\n{SUCCESS_STYLE}All {len(package_names)} packages installed successfully!{RESET_STYLE}")
        log_success(f"All {len(package_names)} packages installed successfully")
    else:
        print(f"\n{WARNING_STYLE}Installed {installed_count} of {len(package_names)} packages.{RESET_STYLE}")
        if failed_packages:
            print(f"{ERROR_STYLE}Failed packages: {', '.join(failed_packages)}{RESET_STYLE}")
            log_warning(f"Partial installation. Failed packages: {', '.join(failed_packages)}")

def run_package(package_name):
    """
    Execute a package by its name
    
    NOTE: This function is maintained for compatibility.
    The primary implementation is in SigmaOS.py.
    """
    # Parse the package path with dot notation
    parts = package_name.split('.')
    base_package = parts[0]
    
    # Handle different path formats
    if len(parts) == 1:
        # Default case: just the package name, run main.py
        file_path = os.path.join(PACKAGES_DIR, base_package, "main.py")
    else:
        # Nested case: handle arbitrary depth
        if len(parts) == 2:
            # Legacy format: package.file runs package/file.py
            file_path = os.path.join(PACKAGES_DIR, parts[0], f"{parts[1]}.py")
        else:
            # New format: package.dir1.dir2.file runs package/dir1/dir2/file.py
            # Last part is the file name, all others are directory components
            file_name = parts[-1]
            path_components = parts[:-1]
            file_path = os.path.join(PACKAGES_DIR, *path_components, f"{file_name}.py")

    if not os.path.exists(file_path):
        print(f"{ERROR_STYLE}File not found: {file_path}{RESET_STYLE}")
        log_error(f"File not found: {file_path}")
        return False

    print(f"{INFO_STYLE}Running {file_path}...{RESET_STYLE}")
    log_info(f"Running package: {package_name} from {file_path}")
    
    # Get additional arguments from sys.argv if we're receiving them directly, 
    # otherwise we need to get them from somewhere else
    args = None
    if isinstance(sys.argv, list) and len(sys.argv) > 1 and sys.argv[0] == package_name:
        # If sys.argv was set to 'parts' earlier, use the proper arguments
        args = [sys.executable, file_path] + sys.argv[1:]
        log_debug(f"Running with args: {args}")
    else:
        # Fallback for compatibility
        args = [sys.executable, file_path]
        log_debug(f"Running with default args: {args}")
    
    # Set environment variable to prevent recursive shell instances
    env = os.environ.copy()
    env['SIGMAOS_SUBPROCESS'] = '1'
    
    try:
        # Only create new shell if not already a subprocess
        if os.environ.get('SIGMAOS_SUBPROCESS') != '1':
            if platform.system() == "Windows":
                subprocess.run(args, env=env)
            else:
                # On Linux/Mac, use python3 explicitly
                args[0] = "python3"
                subprocess.run(args, env=env)
        else:
            # If we're already a subprocess, run directly without shell
            if platform.system() == "Windows":
                subprocess.run(args)
            else:
                args[0] = "python3"
                subprocess.run(args)
        log_success(f"Package {package_name} executed successfully")
        return True
    except subprocess.SubprocessError as e:
        log_error(f"Error running package {package_name}", exception=e)
        print(f"{ERROR_STYLE}Error running package: {e}{RESET_STYLE}")
        return False
    except Exception as e:
        log_error(f"Unexpected error running package {package_name}", exception=e)
        print(f"{ERROR_STYLE}Unexpected error: {e}{RESET_STYLE}")
        return False

def is_valid_package(package_name):
    """
    Check if a package exists and can be executed
    
    NOTE: This function is maintained for compatibility.
    The primary implementation is in SigmaOS.py.
    """
    # Parse the package path with dot notation
    parts = package_name.split('.')
    base_package = parts[0]
    
    # Check if the base package directory exists
    base_package_dir = os.path.join(PACKAGES_DIR, base_package)
    if not os.path.exists(base_package_dir):
        return False
    
    # Handle different path formats
    if len(parts) == 1:
        # Just the package name, check if main.py exists
        return os.path.exists(os.path.join(base_package_dir, "main.py"))
    elif len(parts) == 2:
        # package.file format, check if file.py exists
        return os.path.exists(os.path.join(base_package_dir, f"{parts[1]}.py"))
    else:
        # Nested format: check if the nested file exists
        file_name = parts[-1]
        path_components = parts[:-1]
        return os.path.exists(os.path.join(PACKAGES_DIR, *path_components, f"{file_name}.py")) 

def check_all_updates():
    """Check for updates for all installed packages"""
    # Define style variables at the beginning to avoid NameError
    try:
        # Try to get styles from SigmaOS if available
        from SigmaOS import command_sth, description_sth
    except ImportError:
        # Fallback styles
        command_sth = SUCCESS_STYLE
        description_sth = RESET_STYLE
        
    installed_packages = []
    if os.path.exists(PACKAGES_DIR):
        installed_packages = [d for d in os.listdir(PACKAGES_DIR) 
                            if os.path.isdir(os.path.join(PACKAGES_DIR, d)) 
                            and not d.startswith('.') 
                            and d != "SigmaOS-packages-main"]

    if not installed_packages:
        print(f"{WARNING_STYLE}No packages installed.{RESET_STYLE}")
        return
    
    print(f"{INFO_STYLE}Checking for updates for {len(installed_packages)} packages...{RESET_STYLE}")
    
    updates_available = []
    error_packages = []
    
    for pkg in installed_packages:
        try:
            local_version = get_package_description(pkg, installed=True)['version']
            online_content = get_github_file_content(pkg, "description.txt")
            
            if online_content:
                online_desc = parse_description_file(online_content)
                online_version = online_desc['version']
                
                if local_version != online_version:
                    updates_available.append((pkg, local_version, online_version))
                    print(f"{WARNING_STYLE}Update available for {pkg}: {local_version} → {online_version}{RESET_STYLE}")
            else:
                error_packages.append(pkg)
                print(f"{ERROR_STYLE}Error checking update for {pkg}: Could not fetch online description{RESET_STYLE}")
        except Exception as e:
            error_packages.append(pkg)
            print(f"{ERROR_STYLE}Error checking update for {pkg}: {e}{RESET_STYLE}")
    
    if not updates_available:
        print(f"{SUCCESS_STYLE}All packages are up to date!{RESET_STYLE}")
        return
    
    # Ask the user which packages to update
    print(f"\n{INFO_STYLE}Updates available for {len(updates_available)} packages:{RESET_STYLE}")
    for i, (pkg, local_v, online_v) in enumerate(updates_available):
        print(f"{i+1}. {pkg}: {local_v} → {online_v}")
    
    print(f"\n{INFO_STYLE}Options:{RESET_STYLE}")
    print(f"{command_sth}  all{description_sth}     - Update all packages")
    print(f"{command_sth}  none{description_sth}    - Skip updates")
    print(f"{command_sth}  #,#,#{description_sth}   - Update specific packages by number (comma-separated)")
    
    choice = input(f"\n{WARNING_STYLE}Enter your choice: {RESET_STYLE}")
    
    if choice.lower() == 'none':
        print(f"{INFO_STYLE}No packages updated.{RESET_STYLE}")
        return
    
    packages_to_update = []
    
    if choice.lower() == 'all':
        packages_to_update = [pkg for pkg, _, _ in updates_available]
    else:
        try:
            # Parse comma-separated numbers
            indices = [int(x.strip()) - 1 for x in choice.split(',')]
            for idx in indices:
                if 0 <= idx < len(updates_available):
                    packages_to_update.append(updates_available[idx][0])
                else:
                    print(f"{ERROR_STYLE}Invalid selection: {idx+1}{RESET_STYLE}")
        except Exception as e:
            print(f"{ERROR_STYLE}Invalid input: {e}{RESET_STYLE}")
            return
    
    if not packages_to_update:
        print(f"{INFO_STYLE}No valid packages selected for update.{RESET_STYLE}")
        return
    
    # Update the selected packages
    print(f"\n{INFO_STYLE}Updating {len(packages_to_update)} packages...{RESET_STYLE}")
    
    updated_count = 0
    failed_updates = []
    
    for pkg in packages_to_update:
        print(f"\n{INFO_STYLE}Updating {pkg}...{RESET_STYLE}")
        if download_package(pkg, is_update=True):
            updated_count += 1
        else:
            failed_updates.append(pkg)
    
    # Report summary
    if updated_count == len(packages_to_update):
        print(f"\n{SUCCESS_STYLE}All {len(packages_to_update)} packages updated successfully!{RESET_STYLE}")
    else:
        print(f"\n{WARNING_STYLE}Updated {updated_count} of {len(packages_to_update)} packages.{RESET_STYLE}")
        if failed_updates:
            print(f"{ERROR_STYLE}Failed updates: {', '.join(failed_updates)}{RESET_STYLE}")

def update_package(package_name):
    """Update a specific package
    
    Args:
        package_name (str): Name of the package to update
    """
    if not is_valid_package(package_name):
        print(f"{ERROR_STYLE}Package {package_name} is not installed.{RESET_STYLE}")
        return False
    
    # Check for version mismatch
    local_version = get_package_description(package_name, installed=True)['version']
    
    try:
        # Get the online version
        online_content = get_github_file_content(package_name, "description.txt")
        if online_content:
            online_desc = parse_description_file(online_content)
            online_version = online_desc['version']
            
            if local_version == online_version:
                print(f"{INFO_STYLE}Package {package_name} is already at the latest version ({local_version}).{RESET_STYLE}")
                confirm = input(f"{WARNING_STYLE}Force update anyway? (y/N): {RESET_STYLE}")
                if confirm.lower() != 'y':
                    print(f"{INFO_STYLE}Update cancelled.{RESET_STYLE}")
                    return False
            else:
                print(f"{INFO_STYLE}Updating {package_name} from version {local_version} to {online_version}...{RESET_STYLE}")
        else:
            print(f"{WARNING_STYLE}Could not check online version for {package_name}.{RESET_STYLE}")
            confirm = input(f"{WARNING_STYLE}Continue with update? (y/N): {RESET_STYLE}")
            if confirm.lower() != 'y':
                print(f"{INFO_STYLE}Update cancelled.{RESET_STYLE}")
                return False
    except Exception as e:
        print(f"{WARNING_STYLE}Error checking online version: {e}{RESET_STYLE}")
        confirm = input(f"{WARNING_STYLE}Continue with update? (y/N): {RESET_STYLE}")
        if confirm.lower() != 'y':
            print(f"{INFO_STYLE}Update cancelled.{RESET_STYLE}")
            return False
    
    # Proceed with the update
    return download_package(package_name, is_update=True)

# Load and save source configurations
def load_sources():
    """Load package sources from ligma.sigs file"""
    if not os.path.exists(SOURCES_FILE):
        # Create default sources file with just the official repo
        save_sources([OFFICIAL_REPO])
        return [OFFICIAL_REPO]
    try:
        with open(SOURCES_FILE, 'r') as f:
            sources = json.load(f)
            if not isinstance(sources, list):
                return [OFFICIAL_REPO]
            return sources
    except Exception as e:
        log_error(f"Error loading sources", exception=e)
        return [OFFICIAL_REPO]

def save_sources(sources):
    """Save package sources to ligma.sigs file"""
    try:
        with open(SOURCES_FILE, 'w') as f:
            json.dump(sources, f, indent=2)
        return True
    except Exception as e:
        log_error(f"Error saving sources", exception=e)
        return False

def add_source(source):
    """Add a new package source"""
    try:
        # Validate source format
        if not '/' in source:
            print(f"{ERROR_STYLE}Invalid source format. Use 'username/repo' format.{RESET_STYLE}")
            return False
            
        # Verify the source repository exists
        username, repo = source.split('/')
        url = f"https://api.github.com/repos/{username}/{repo}"
        response = requests.get(url)
        if response.status_code != 200:
            print(f"{ERROR_STYLE}Repository not found or inaccessible: {source}{RESET_STYLE}")
            return False

        sources = load_sources()
        if source in sources:
            print(f"{WARNING_STYLE}Source {source} already exists.{RESET_STYLE}")
            return False
            
        sources.append(source)
        if save_sources(sources):
            print(f"{SUCCESS_STYLE}Added source: {source}{RESET_STYLE}")
            return True
        return False
    except Exception as e:
        log_error(f"Error adding source", exception=e)
        return False

def remove_source(source):
    """Remove a package source"""
    if source == OFFICIAL_REPO:
        print(f"{ERROR_STYLE}Cannot remove the official package repository.{RESET_STYLE}")
        return False
        
    sources = load_sources()
    if source not in sources:
        print(f"{WARNING_STYLE}Source not found: {source}{RESET_STYLE}")
        return False
        
    sources.remove(source)
    if save_sources(sources):
        print(f"{SUCCESS_STYLE}Removed source: {source}{RESET_STYLE}")
        return True
    return False

def list_sources():
    """List all configured package sources"""
    try:
        # Try to get styles from SigmaOS if available
        from SigmaOS import header_sth, description_sth, SUCCESS_STYLE, INFO_STYLE, WARNING_STYLE
    except ImportError:
        # Fallback styles
        header_sth = INFO_STYLE
        description_sth = RESET_STYLE
    
    sources = load_sources()
    print(f"\n{header_sth}Package Sources:{RESET_STYLE}")
    
    print(f"\n{INFO_STYLE}Official Repository:{RESET_STYLE}")
    print(f"{SUCCESS_STYLE}  ▶ {OFFICIAL_REPO} (official){RESET_STYLE}")
    
    other_sources = [s for s in sources if s != OFFICIAL_REPO]
    if other_sources:
        print(f"\n{INFO_STYLE}Additional Sources:{RESET_STYLE}")
        for source in other_sources:
            print(f"{description_sth}  ▶ {source}")
    else:
        print(f"\n{WARNING_STYLE}No additional sources configured.{RESET_STYLE}")

def show_verified_sources():
    """Show list of verified external sources"""
    try:
        # Try to get styles from SigmaOS if available
        from SigmaOS import header_sth, SUCCESS_STYLE, WARNING_STYLE, INFO_STYLE
    except ImportError:
        # Fallback styles
        header_sth = INFO_STYLE
    
    print(f"\n{header_sth}Verified Package Sources:{RESET_STYLE}")
    if VERIFIED_SOURCES:
        for source in VERIFIED_SOURCES:
            print(f"{SUCCESS_STYLE}  ▶ {source}{RESET_STYLE}")
    else:
        print(f"{WARNING_STYLE}No verified sources available yet.{RESET_STYLE}")
    print(f"\n{INFO_STYLE}Note: Verified sources are curated and trusted package repositories.{RESET_STYLE}")