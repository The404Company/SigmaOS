#!/usr/bin/env python3
"""
Ligma Package Manager for SigmaOS
This module handles all package management functionality for SigmaOS.
"""

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
REPO_URL = "https://github.com/The404Company/SigmaOS-packages"
PACKAGES_DIR = os.path.join(CURRENT_DIR, "packages")

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

def get_github_file_content(package_name, filename):
    """Fetch raw file content from GitHub"""
    url = f"https://raw.githubusercontent.com/The404Company/SigmaOS-packages/main/{package_name}/{filename}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text.strip()
    except:
        pass
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

def get_package_description(package_name, installed=True):
    """Get package description from local file or GitHub"""
    if installed and is_valid_package(package_name):
        desc_file = os.path.join(PACKAGES_DIR, package_name, "description.txt")
        try:
            if os.path.exists(desc_file):
                with open(desc_file, 'r', encoding='utf-8') as f:
                    return parse_description_file(f.read())
        except:
            pass
    else:
        # Try to fetch from GitHub for non-installed packages
        content = get_github_file_content(package_name, "description.txt")
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
                            and not d.startswith('.') 
                            and d != "SigmaOS-packages-main"]
    
    # Get available packages from repo
    headers = {'Accept': 'application/vnd.github.v3+json'}
    print(f"{INFO_STYLE}Searching packages for '{search_term}'...{RESET_STYLE}")
    response = requests.get(f"https://api.github.com/repos/The404Company/SigmaOS-packages/contents/", headers=headers)
    
    try:
        # Try to get styles from SigmaOS if available
        from SigmaOS import package_sth, description_sth, package_status_sth, SUCCESS_STYLE, WARNING_STYLE, ERROR_STYLE
    except ImportError:
        # Fallback styles
        package_sth = SUCCESS_STYLE
        description_sth = RESET_STYLE
        package_status_sth = INFO_STYLE
    
    if response.status_code == 200:
        data = response.json()
        package_names = [item["name"] for item in data 
                       if item["type"] == "dir" and not item["name"].startswith('.')]
        
        matches = []
        
        # First quick check for name matches
        name_matches = [pkg for pkg in package_names if search_term in pkg.lower()]
        matches.extend(name_matches)
        
        # Then check descriptions for any remaining packages
        for pkg in package_names:
            if pkg not in name_matches:
                desc = get_package_description(pkg, installed=(pkg in installed_packages))
                if search_term in desc['description'].lower():
                    matches.append(pkg)
        
        # Remove duplicates
        matches = list(set(matches))
        
        if matches:
            print(f"\n{SUCCESS_STYLE}Found {len(matches)} package(s) matching '{search_term}':{RESET_STYLE}")
            
            for i, pkg in enumerate(matches):
                if i > 0:  # Add empty line before each package except the first one
                    print()
                
                is_installed = pkg in installed_packages
                status = f"{SUCCESS_STYLE}[Installed]{RESET_STYLE}" if is_installed else f"{WARNING_STYLE}[Available]{RESET_STYLE}"
                
                desc = get_package_description(pkg, installed=is_installed)
                print(f"{package_sth}{pkg} {status} {description_sth}- {desc['description']}")
                print(f"{package_status_sth}{desc['author']} {description_sth}- v{desc['version']}")
        else:
            print(f"{WARNING_STYLE}No packages found matching '{search_term}'{RESET_STYLE}")
    else:
        print(f"{ERROR_STYLE}Error searching packages. Status code: {response.status_code}{RESET_STYLE}")

def browse_packages():
    """Browse all available packages (formerly list_packages)"""
    # Get installed packages first
    installed_packages = []
    if os.path.exists(PACKAGES_DIR):
        installed_packages = [d for d in os.listdir(PACKAGES_DIR) 
                            if os.path.isdir(os.path.join(PACKAGES_DIR, d)) 
                            and not d.startswith('.') 
                            and d != "SigmaOS-packages-main"]

    # Get available packages from repo
    headers = {'Accept': 'application/vnd.github.v3+json'}
    response = requests.get(f"https://api.github.com/repos/The404Company/SigmaOS-packages/contents/", headers=headers)
    loading_animation("Fetching packages...")
    
    if response.status_code == 200:
        data = response.json()
        available_packages = [item["name"] for item in data 
                            if item["type"] == "dir" and not item["name"].startswith('.')]
        
        try:
            # Try to get styles from SigmaOS if available
            from SigmaOS import package_sth, description_sth, package_status_sth, SUCCESS_STYLE, WARNING_STYLE, ERROR_STYLE
        except ImportError:
            # Fallback styles
            package_sth = SUCCESS_STYLE
            description_sth = RESET_STYLE
            package_status_sth = INFO_STYLE
        
        print(f"\n{INFO_STYLE}Available packages:{RESET_STYLE}")
        packages_found = False
        
        # Show installed packages first
        if installed_packages:
            print(f"\n{SUCCESS_STYLE}Installed:{RESET_STYLE}")
            for i, pkg in enumerate(installed_packages):
                if i > 0:  # Add empty line before each package except the first one
                    print()
                desc = get_package_description(pkg)
                print(f"{package_sth}{pkg} {description_sth}- {desc['description']}")
                print(f"{package_status_sth}{desc['author']} {description_sth}- v{desc['version']}")
                packages_found = True
        
        # Show available but not installed packages
        not_installed = [pkg for pkg in available_packages if pkg not in installed_packages]
        if not_installed:
            print(f"\n{WARNING_STYLE}Not Installed:{RESET_STYLE}")
            for i, pkg in enumerate(not_installed):
                if i > 0:  # Add empty line before each package except the first one
                    print()
                desc = get_package_description(pkg, installed=False)
                print(f"{description_sth}{pkg} - {desc['description']}")
                print(f"{package_status_sth}{desc['author']} - v{desc['version']}")
                packages_found = True
        
        if not packages_found:
            print(f"{ERROR_STYLE}No packages found in repository.{RESET_STYLE}")
    else:
        print(f"{ERROR_STYLE}Error fetching repositories. Status code: {response.status_code}{RESET_STYLE}")
        print(f"{ERROR_STYLE}Response: {response.text}{RESET_STYLE}")

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
    
    # Help
    print(f"\n{INFO_STYLE}Help:{RESET_STYLE}")
    help_commands = [
        ("ligma ?h", "Show this help"),
        ("ligma ?help", "Show this help")
    ]
    for cmd, desc in help_commands:
        print(f"{command_sth}  {cmd:<30}{description_sth} - {desc}")
    
    print(f"\n{header_sth}╚{'═' * 58}╝{RESET_STYLE}")

# Keep this for backward compatibility, redirects to the new browse_packages function
def list_packages():
    """Redirects to browse_packages for backward compatibility"""
    browse_packages()

def download_package(package_name):
    if not os.path.exists(PACKAGES_DIR):
        os.makedirs(PACKAGES_DIR)
        log_info(f"Created packages directory at {PACKAGES_DIR}")

    package_dir = os.path.join(PACKAGES_DIR, package_name)

    if os.path.exists(package_dir):
        print(f"{WARNING_STYLE}Package {package_name} already downloaded.{RESET_STYLE}")
        log_warning(f"Package {package_name} already downloaded.")
        return

    download_url = f"{REPO_URL}/archive/refs/heads/main.zip"

    try:
        response = loading_animation(f"Downloading {package_name}", task=lambda: requests.get(download_url))
        zip_path = os.path.join(PACKAGES_DIR, f"{package_name}.zip")

        if response.status_code == 200:
            try:
                with open(zip_path, "wb") as f:
                    f.write(response.content)
                log_info(f"Downloaded zip file for {package_name}")

                try:
                    with ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(PACKAGES_DIR)
                    log_info(f"Extracted zip file for {package_name}")

                    extracted_folder = os.path.join(PACKAGES_DIR, "SigmaOS-packages-main", package_name)
                    if os.path.exists(extracted_folder):
                        if os.path.exists(package_dir):
                            shutil.rmtree(package_dir)
                        os.rename(extracted_folder, package_dir)
                        log_info(f"Renamed extracted folder to {package_dir}")
                        
                        # Install package requirements
                        desc = get_package_description(package_name)
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
                        
                        # Clean up SigmaOS-packages-main folder
                        sigmamain_dir = os.path.join(PACKAGES_DIR, "SigmaOS-packages-main")
                        if os.path.exists(sigmamain_dir):
                            loading_animation("Cleaning up temporary files", task=lambda: shutil.rmtree(sigmamain_dir))
                            log_info("Cleaned up temporary files")
                        print(f"{SUCCESS_STYLE}Package {package_name} successfully installed.{RESET_STYLE}")
                        # Remove the duplicated log output that also displays to console
                        log_info(f"Package {package_name} successfully installed.")
                    else:
                        print(f"{ERROR_STYLE}Package {package_name} not found in downloaded archive.{RESET_STYLE}")
                        # Remove the duplicated log output that also displays to console
                        log_info(f"Package {package_name} not found in downloaded archive.")
                except Exception as extract_error:
                    print(f"{ERROR_STYLE}Error extracting package: {extract_error}{RESET_STYLE}")
                    log_error(f"Error extracting package {package_name}", exception=extract_error)
            except Exception as write_error:
                print(f"{ERROR_STYLE}Error writing zip file: {write_error}{RESET_STYLE}")
                log_error(f"Error writing zip file for {package_name}", exception=write_error)
            finally:
                # Always clean up the zip file
                if os.path.exists(zip_path):
                    try:
                        os.remove(zip_path)
                        log_info(f"Removed temporary zip file {zip_path}")
                    except Exception as cleanup_error:
                        log_error(f"Error removing temporary zip file", exception=cleanup_error)
        else:
            print(f"{ERROR_STYLE}Error downloading package {package_name}. Status code: {response.status_code}{RESET_STYLE}")
            log_error(f"Error downloading package {package_name}. Status code: {response.status_code}")
    except requests.RequestException as req_error:
        print(f"{ERROR_STYLE}Network error: {req_error}{RESET_STYLE}")
        log_error(f"Network error downloading package {package_name}", exception=req_error)
    except Exception as e:
        print(f"{ERROR_STYLE}Error downloading package {package_name}: {e}{RESET_STYLE}")
        log_error(f"Error downloading package {package_name}", exception=e)

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