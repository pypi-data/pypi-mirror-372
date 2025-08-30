from colorama import init, Fore, Style

init(autoreset=True)

def report_success(original_code: str, fixed_code: str):

    print("\n" + "="*50)
    print(Fore.GREEN + Style.BRIGHT + "✅ AUTO-REPAIR SUCCESSFUL: A verified fix has been generated.")
    print("="*50)
    
    print(Fore.YELLOW + "\n--- ORIGINAL BUGGY CODE ---")
    print(Fore.RED + original_code)
    
    print(Fore.YELLOW + "\n--- AI-GENERATED FIXED CODE ---")
    print(Fore.GREEN + fixed_code)
    
    print("\n" + "="*50)
    print(Style.BRIGHT + "The agent has successfully identified, fixed, and verified the bug.")

def report_failure(reason: str):

    print("\n" + "="*50)
    print(Fore.RED + Style.BRIGHT + "❌ AUTO-REPAIR FAILED: Could not generate a verified fix.")
    print("="*50)
    
    print(Fore.YELLOW + "\n--- REASON FOR FAILURE ---")
    print(reason)
    
    print("\n" + "="*50)
    print(Style.BRIGHT + "The agent is stopping. Please review the logs for more details.")
