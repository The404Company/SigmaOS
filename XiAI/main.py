import os
import sys
import time
import requests
from colorama import Fore, Style, init
from llama_cpp import Llama

# Initialize colorama
init(autoreset=True)

MODEL_URL = "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q4_0.gguf"
MODEL_FILE = "mistral-7b-instruct-v0.1.Q4_0.gguf"
SYSTEM_PROMPT_FILE = "XiAI.txt"
MAX_CONTEXT_MESSAGES = 10  

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
                        print(f"\rDownloaded {total / 1_000_000:.2f} MB", end="", flush=True)
        print(f"\n{Fore.GREEN}Download complete!{Style.RESET_ALL}")
    else:
        print(f"{Fore.GREEN}Model already downloaded.{Style.RESET_ALL}")

def load_system_prompt():
    if not os.path.exists(SYSTEM_PROMPT_FILE):
        print(f"{Fore.RED}Missing system prompt file: {SYSTEM_PROMPT_FILE}{Style.RESET_ALL}")
        sys.exit(1)
    with open(SYSTEM_PROMPT_FILE, 'r', encoding='utf-8') as f:
        return f.read()

def show_banner():
    clear_screen()
    print(f"{Fore.CYAN}╔═══ Ξ XiAI Assistant ═══╗")
    print(f"║ 1. Start Chat          ║")
    print(f"║ 0. Exit                ║")
    print(f"╚════════════════════════╝{Style.RESET_ALL}")

def typing_animation(text="XiAI is typing", duration=2.5, interval=0.4):
    """Simulates a typing animation like Discord."""
    print(f"{Fore.MAGENTA}{text}", end="", flush=True)
    start_time = time.time()
    dot_count = 0
    while time.time() - start_time < duration:
        print(".", end="", flush=True)
        dot_count += 1
        if dot_count > 3:
            print("\b\b\b   \b\b\b", end="", flush=True)  # erase dots
            dot_count = 0
        time.sleep(interval)
    print("\r" + " " * 30 + "\r", end="", flush=True)  # Clear the line

def chat():
    try:
        llm = Llama(model_path=MODEL_FILE, n_ctx=32768, verbose=False)
        system_prompt = load_system_prompt()
        print(f"\n{Fore.YELLOW}XiAI is ready! Ask a question or type 'exit'.{Style.RESET_ALL}")
        
        # Add disclaimer
        print(f"""{Fore.BLUE}⚠️  Note:
    - XiAI is still in development and may say incorrect or misleading things.
    - In rare cases, it may invent packages, functions, or facts that don’t exist.
    - The first response may take *up to a few minutes*, depending on your hardware. Please be patient.
    - If you experience any issues, please report them on GitHub.
    - Do never rely on XiAI for critical tasks.
    - It's reccomended to verify the information provided by X
{Style.RESET_ALL}""")

        messages = [{"role": "system", "content": system_prompt}]
        
        while True:
            try:
                user_input = input(f"{Fore.WHITE}\nYou: {Style.RESET_ALL}")
            except KeyboardInterrupt:
                print(f"\n{Fore.CYAN}XiAI: Session ended by user.{Style.RESET_ALL}")
                break

            if user_input.lower() in ['exit', 'quit']:
                print(f"{Fore.CYAN}XiAI: See you next time!{Style.RESET_ALL}")
                break

            messages.append({"role": "user", "content": user_input})
            trimmed_messages = [messages[0]] + messages[-(MAX_CONTEXT_MESSAGES * 2):]

            print(f"{Fore.GREEN}XiAI:{Style.RESET_ALL} ", end="", flush=True)

            try:
                response = ""
                for chunk in llm.create_chat_completion(trimmed_messages, stream=True):
                    content = chunk['choices'][0]['delta'].get('content', '')
                    print(content, end='', flush=True)
                    response += content
                print()  # for newline after response

                messages.append({"role": "assistant", "content": response})
            except Exception as e:
                print(f"{Fore.RED}\nAn error occurred: {e}{Style.RESET_ALL}")

    except Exception as e:
        print(f"{Fore.RED}Error during chat: {e}{Style.RESET_ALL}")

def main():
    download_model()
    while True:
        show_banner()
        try:
            choice = input(f"\n{Fore.WHITE}Choose an option (0-1): {Style.RESET_ALL}")
        except KeyboardInterrupt:
            print(f"\n{Fore.CYAN}Goodbye!{Style.RESET_ALL}")
            break

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
