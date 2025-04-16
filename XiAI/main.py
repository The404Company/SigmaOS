import os
import sys
import time
import requests
from colorama import Fore, Style, init
from llama_cpp import Llama

# Color output
init(autoreset=True)

MODEL_URL = "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q4_0.gguf"
MODEL_FILE = "mistral-7b-instruct-v0.1.Q4_0.gguf"

SYSTEM_PROMPT = "You are XiAi – the smart, local assistant for SigmaOS. Be helpful, clear, and concise."

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def download_model():
    if not os.path.exists(MODEL_FILE):
        print(f"{Fore.YELLOW}Downloading model... This may take a few minutes.{Style.RESET_ALL}")
        with requests.get(MODEL_URL, stream=True) as r:
            r.raise_for_status()
            with open(MODEL_FILE, 'wb') as f:
                total = 0
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        total += len(chunk)
                        print(f"\rDownloaded {total / 1_000_000:.2f} MB", end="")
        print(f"\n{Fore.GREEN}Download complete!{Style.RESET_ALL}")
    else:
        print(f"{Fore.GREEN}Model already downloaded.{Style.RESET_ALL}")

def show_banner():
    clear_screen()
    print(f"{Fore.CYAN}╔═══ XiAi Assistant ═══╗")
    print(f"║ 1. Start Chat        ║")
    print(f"║ 0. Exit              ║")
    print(f"╚══════════════════════╝{Style.RESET_ALL}")

def chat():
    try:
        llm = Llama(model_path=MODEL_FILE, n_ctx=2048, verbose=False)
        print(f"\n{Fore.YELLOW}XiAi is ready! Ask a question or type 'exit'.{Style.RESET_ALL}")
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        while True:
            user_input = input(f"{Fore.WHITE}\nYou: {Style.RESET_ALL}")
            if user_input.lower() in ['exit', 'quit']:
                print(f"{Fore.CYAN}XiAi: See you next time!{Style.RESET_ALL}")
                break
            messages.append({"role": "user", "content": user_input})
            output = llm.create_chat_completion(messages)
            reply = output['choices'][0]['message']['content']
            print(f"{Fore.GREEN}XiAi:{Style.RESET_ALL} {reply}")
            messages.append({"role": "assistant", "content": reply})
    except Exception as e:
        print(f"{Fore.RED}Error during chat: {e}{Style.RESET_ALL}")

def main():
    download_model()
    while True:
        show_banner()
        choice = input(f"\n{Fore.WHITE}Choose an option (0-1): {Style.RESET_ALL}")

        if choice == "1":
            chat()
        elif choice == "0":
            clear_screen()
            sys.exit(0)
        else:
            print(f"{Fore.RED}Invalid choice!{Style.RESET_ALL}")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
