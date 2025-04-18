import os, sys, json, requests, shutil, subprocess
from zipfile import ZipFile
from colorama import Fore, Style
import re

PACKAGES_DIR = "packages"
SOURCES_FILE = "sources.json"

def loading_animation(text):
    print(f"{Fore.BLUE}{text}...{Style.RESET_ALL}")

def ensure_sources_file():
    if not os.path.exists(SOURCES_FILE):
        with open(SOURCES_FILE, 'w') as f:
            json.dump([], f)

def get_sources():
    ensure_sources_file()
    with open(SOURCES_FILE, 'r') as f:
        return json.load(f)

def print_sources():
    sources = get_sources()
    if not sources:
        print(f"{Fore.YELLOW}No sources added yet.{Style.RESET_ALL}")
    else:
        print(f"{Fore.CYAN}Registered sources:{Style.RESET_ALL}")
        for i, src in enumerate(sources, 1):
            print(f"  {Fore.GREEN}{i}.{Style.RESET_ALL} {src}")


def save_sources(sources):
    with open(SOURCES_FILE, 'w') as f:
        json.dump(sources, f, indent=2)

def add_source(source):
    # Check if the source matches the pattern "user/repo"
    if not re.match(r"^[\w\-]+/[\w\-]+$", source):
        print(f"{Fore.RED}Invalid source format. Use 'username/repo'.{Style.RESET_ALL}")
        return

    sources = get_sources()
    if source not in sources:
        sources.append(source)
        save_sources(sources)
        print(f"{Fore.GREEN}Source '{source}' added!{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}Source already exists.{Style.RESET_ALL}")

def remove_source(source):
    sources = get_sources()
    if source in sources:
        sources.remove(source)
        save_sources(sources)
        print(f"{Fore.RED}Source '{source}' removed.{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}Source not found.{Style.RESET_ALL}")

def get_github_file_content(user, repo, package_name, filename):
    url = f"https://raw.githubusercontent.com/{user}/{repo}/main/{package_name}/{filename}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text.strip()
    except:
        pass
    return None

def parse_description_file(content):
    sections = {'description': 'No description available', 'author': 'Unknown', 'version': '0.0', 'requirements': []}
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
                sections[current_section].append(line)
            else:
                sections[current_section] = line
    return sections

def list_packages():
    sources = get_sources()
    if not sources:
        print(f"{Fore.RED}No sources found. Use 'sourcerer add <user>/<repo>' to add one.{Style.RESET_ALL}")
        return

    for source in sources:
        user, repo = source.split("/") if "/" in source else (None, None)
        if not user or not repo:
            print(f"{Fore.YELLOW}Skipping invalid source: {source}{Style.RESET_ALL}")
            continue

        url = f"https://api.github.com/repos/{user}/{repo}/contents/"
        response = requests.get(url)
        loading_animation(f"Fetching from {user}/{repo}")

        if response.status_code == 200:
            data = response.json()
            print(f"\n{Fore.CYAN}{user}/{repo}:{Style.RESET_ALL}")
            for item in data:
                if item["type"] == "dir":
                    desc = get_github_file_content(user, repo, item["name"], "description.txt")
                    if desc:
                        meta = parse_description_file(desc)
                        print(f"\n{Fore.WHITE}{item['name']} - {meta['description']}")
                        print(f"{Fore.CYAN}{meta['author']} - v{meta['version']}")
        else:
            print(f"{Fore.RED}Failed to fetch from {source}{Style.RESET_ALL}")

def install_package(package_name):
    sources = get_sources()
    for source in sources:
        user, repo = source.split("/")
        zip_url = f"https://github.com/{user}/{repo}/archive/refs/heads/main.zip"
        response = requests.get(zip_url)

        if response.status_code != 200:
            continue

        loading_animation(f"Downloading from {user}/{repo}")
        zip_path = os.path.join(PACKAGES_DIR, f"{repo}.zip")
        os.makedirs(PACKAGES_DIR, exist_ok=True)

        with open(zip_path, "wb") as f:
            f.write(response.content)

        with ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(PACKAGES_DIR)
        os.remove(zip_path)

        extracted_folder = os.path.join(PACKAGES_DIR, f"{repo}-main", package_name)
        target_path = os.path.join(PACKAGES_DIR, package_name)

        if os.path.exists(extracted_folder):
            if os.path.exists(target_path):
                shutil.rmtree(target_path)
            shutil.move(extracted_folder, target_path)

            # Install dependencies
            desc_file = os.path.join(target_path, "description.txt")
            if os.path.exists(desc_file):
                with open(desc_file, 'r') as f:
                    desc = parse_description_file(f.read())
                    if desc['requirements']:
                        for req in desc['requirements']:
                            loading_animation(f"Installing {req}")
                            subprocess.run([sys.executable, "-m", "pip", "install", req],
                                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # Clean up
            shutil.rmtree(os.path.join(PACKAGES_DIR, f"{repo}-main"))
            print(f"{Fore.GREEN}Package {package_name} installed from {source}.{Style.RESET_ALL}")
            return

    print(f"{Fore.RED}Package {package_name} not found in any source.{Style.RESET_ALL}")

def main_loop():
    print(f"{Fore.CYAN}Welcome to Sourcerer! Type 'help' for commands.{Style.RESET_ALL}")
    while True:
        cmd = input("> ").strip().lower()
        if cmd == "exit":
            break
        elif cmd.startswith("add "):
            add_source(cmd.split(" ", 1)[1])
        elif cmd.startswith("remove "):
            remove_source(cmd.split(" ", 1)[1])
        elif cmd == "list":
            list_packages()
        elif cmd.startswith("install "):
            install_package(cmd.split(" ", 1)[1])
        elif cmd == "sources":
            print_sources()
        elif cmd == "verified":
            print(f"""{Fore.GREEN}Verified sources:{Style.RESET_ALL}
    - Lominub44/SigmaOS_pkg_test""")
        elif cmd == "help":
            print(f"""{Fore.GREEN}Commands:{Style.RESET_ALL}
    - add <src>: Add a GitHub source (e.g., user/repo)
    - remove <src>: Remove a GitHub source
    - list: List all packages from sources
    - install <pkg>: Install a package
    - sources: Show all sources
    - verified: Show verified sources
    - help: Show this help message
    - exit: Exit the program""")
        else:
            print(f"{Fore.RED}Unknown command. Type 'help'{Style.RESET_ALL}")

if __name__ == "__main__":
    main_loop()
