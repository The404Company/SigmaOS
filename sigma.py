import os
import subprocess
import requests

# Basis-URL des GitHub-Repos, in dem alle Pakete liegen
REPO_URL = "https://github.com/username/repo"
PACKAGES_DIR = "packages"

# Funktion zum Auflisten der Pakete im Repo (ligma list)
def list_packages():
    response = requests.get(f"{REPO_URL}/contents/")
    if response.status_code == 200:
        data = response.json()
        for item in data:
            if item["type"] == "dir":  # Nur Ordner anzeigen
                print(item["name"])
    else:
        print("Fehler beim Abrufen der Repos.")

# Funktion zum Installieren eines Pakets (ligma install <paket>)
def download_package(package_name):
    package_dir = os.path.join(PACKAGES_DIR, package_name)

    # Wenn das Paket bereits existiert, überspringen
    if os.path.exists(package_dir):
        print(f"Paket {package_name} bereits heruntergeladen.")
        return

    # GitHub Repo URL für das Paket
    download_url = f"{REPO_URL}/archive/refs/heads/main.zip"

    # Das Paket als ZIP herunterladen
    print(f"Lade {package_name} herunter...")
    zip_path = os.path.join(PACKAGES_DIR, f"{package_name}.zip")
    response = requests.get(download_url)

    if response.status_code == 200:
        with open(zip_path, "wb") as f:
            f.write(response.content)
        subprocess.run(["unzip", zip_path, "-d", PACKAGES_DIR])
        os.remove(zip_path)  # ZIP nach dem Entpacken löschen
    else:
        print(f"Fehler beim Herunterladen des Pakets {package_name}.")

# Funktion zum Ausführen eines Pakets (ligma <paket>)
def run_package(package_name):
    package_dir = os.path.join(PACKAGES_DIR, package_name, "main.py")

    if not os.path.exists(package_dir):
        print(f"main.py in {package_name} nicht gefunden.")
        return

    print(f"Führe {package_name}/main.py aus...")
    subprocess.run(["python", package_dir])

# Funktion zum Ausführen eines Delta-Kommandos (delta <args>)
def delta_command(args):
    print(f"Delta Kommando ausgeführt mit Argumenten: {args}")

# Funktion für die interaktive Kommandozeile von SigmaOS
def interactive_shell():
    while True:
        try:
            # Benutzer nach einem Befehl fragen
            command = input("SigmaOS > ")

            # Wenn der Benutzer "exit" eingibt, die Shell beenden
            if command.lower() == "exit":
                print("Beende SigmaOS...")
                break

            # Zerlege den Befehl in das Hauptkommando und mögliche Argumente
            parts = command.split()

            if not parts:
                continue

            main_command = parts[0]
            args = parts[1:]

            # Verarbeite die verschiedenen Befehle
            if main_command == "ligma":
                if args:
                    subcommand = args[0]
                    if subcommand == "list":
                        list_packages()
                    elif subcommand == "install" and len(args) == 2:
                        download_package(args[1])
                    elif len(args) == 1:
                        run_package(args[0])
                    else:
                        print("Unbekannter Befehl für ligma.")
                else:
                    print("Verwendung von ligma: list | install <paket> | <paket>")
            
            elif main_command == "delta":
                delta_command(args)
            
            else:
                print(f"Unbekannter Befehl: {main_command}. Versuche 'ligma' oder 'delta'.")

        except KeyboardInterrupt:
            print("\nBeende SigmaOS...")
            break

# Hauptfunktion, um SigmaOS zu starten
if __name__ == "__main__":
    interactive_shell()
