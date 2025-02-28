#!/usr/bin/env python3

import os
import sys
import subprocess
import time

# Define colors for terminal output (ANSI escape codes)
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

# Define the available scripts and their command formats
SCRIPTS = {
    "1": {
        "name": "geocoder_google_api.py",
        "description": "Google Maps Geocoding API (requires API key)",
        "format": "python geocoder_google_api.py [input_file] --api-key YOUR_KEY [--output output.csv] [--default-country COUNTRY]"
    },
    "2": {
        "name": "geocoder_osm_geopy.py",
        "description": "OpenStreetMap geocoding via geopy library (free, installs geopy if needed)",
        "format": "python geocoder_osm_geopy.py [input_file] [--output output.csv] [--default-country COUNTRY]"
    },
    "3": {
        "name": "geocoder_osm_http.py",
        "description": "OpenStreetMap geocoding via direct HTTP requests (free, no dependencies)",
        "format": "python geocoder_osm_http.py [input_file] [--output output.csv] [--default-country COUNTRY]"
    }
}

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    """Display the tool's ASCII art banner."""
    clear_screen()
    print(f"{RED}")
    print(r"""
  _____                          _               _____           _ 
 / ____|                        | |             |_   _|         | |
| |  __  ___  ___   ___ ___   __| | ___ _ __      | |  ___   ___| |
| | |_ |/ _ \/ _ \ / __/ _ \ / _` |/ _ \ '__|     | | / _ \ / _ \ |
| |__| |  __/ (_) | (_| (_) | (_| |  __/ |       _| || (_) |  __/ |
 \_____|\___|\___, |\___\___/ \__,_|\___|_|      |_____\___/ \___|_|
                __/ |                                               
               |___/                                                

    """)
    print(f"{YELLOW}╔═══════════════════════════════════════════════════════════╗{RESET}")
    print(f"{YELLOW}║ {GREEN}Address Location Finder for Multiple Geographic Sources {YELLOW}║{RESET}")
    print(f"{YELLOW}╚═══════════════════════════════════════════════════════════╝{RESET}")
    print(f"{DIM}V1.0.0{RESET}")
    print(f"{DIM}Created by Saksham Mathur{RESET}")
    print()

def loading_animation(text, duration=1.5):
    """Display a simple loading animation."""
    chars = "|/-\\"
    for _ in range(int(duration * 10)):
        for char in chars:
            sys.stdout.write(f'\r{text} {char}')
            sys.stdout.flush()
            time.sleep(0.1)
    print()

def show_menu():
    """Display the menu of available scripts."""
    print(f"\n{BLUE}╔═══════════════════════════════════{RESET}")
    print(f"{BLUE}║ {BOLD}AVAILABLE GEOCODING METHODS{RESET}    {BLUE}║{RESET}")
    print(f"{BLUE}╠═══════════════════════════════════╣{RESET}")
    
    for key, script in SCRIPTS.items():
        name = script["name"].replace(".py", "")
        print(f"{BLUE}║ {YELLOW}[{key}]{RESET} {GREEN}{name}{RESET}")
        print(f"{BLUE}║{RESET}     {script['description']}")
    
    print(f"{BLUE}║{RESET}")
    print(f"{BLUE}║ {YELLOW}[q]{RESET} Exit Program")
    print(f"{BLUE}╚═══════════════════════════════════{RESET}")

def execute_script(script_key):
    """Show format and execute the selected script."""
    if script_key not in SCRIPTS:
        print(f"{RED}Invalid selection. Please try again.{RESET}")
        return
    
    script = SCRIPTS[script_key]
    print(f"\n{GREEN}You selected:{RESET} {BOLD}{script['description']}{RESET}")
    print(f"{DIM}Command format: {script['format']}{RESET}")
    
    # Get input file from user
    input_file = input(f"\n{YELLOW}[+]{RESET} Enter input file path: ").strip()
    if not input_file:
        print(f"{RED}Error: Input file is required.{RESET}")
        return
    
    if not os.path.exists(input_file):
        print(f"{RED}Error: File '{input_file}' does not exist.{RESET}")
        return
    
    # Build the command based on the script
    command = f"python {script['name']} {input_file}"
    
    # Handle Google API key if needed
    if script_key == "1":  # Google script
        api_key = input(f"{YELLOW}[+]{RESET} Enter your Google API key: ").strip()
        if not api_key:
            print(f"{RED}Error: Google API key is required for this script.{RESET}")
            return
        command += f" --api-key {api_key}"
    
    # Get output file (optional)
    output_file = input(f"{YELLOW}[+]{RESET} Enter output file path (or press Enter for default): ").strip()
    if output_file:
        command += f" --output {output_file}"
    
    # Get default country (optional)
    default_country = input(f"{YELLOW}[+]{RESET} Enter default country (or press Enter to skip): ").strip()
    if default_country:
        command += f" --default-country {default_country}"
    
    print(f"\n{BLUE}[*]{RESET} Executing: {BOLD}{command}{RESET}")
    
    # Show loading animation
    loading_animation("Preparing to execute", 1)
    
    try:
        # Execute the command
        result = subprocess.run(command, shell=True, check=True, text=True, 
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Display output
        print(f"\n{GREEN}╔═══════════ OUTPUT ═══════════╗{RESET}")
        print(result.stdout)
        
        if result.stderr:
            print(f"\n{RED}╔═══════════ ERRORS ═══════════╗{RESET}")
            print(result.stderr)
            
        print(f"\n{GREEN}[✓] Execution completed successfully.{RESET}")
    except subprocess.CalledProcessError as e:
        print(f"\n{RED}[✗] Error executing script: {e}{RESET}")
        if e.stdout:
            print(f"\n{YELLOW}╔═══════════ OUTPUT ═══════════╗{RESET}")
            print(e.stdout)
        if e.stderr:
            print(f"\n{RED}╔═══════════ ERRORS ═══════════╗{RESET}")
            print(e.stderr)

def main():
    """Main function to run the tool."""
    print_banner()
    
    while True:
        show_menu()
        choice = input(f"\n{YELLOW}[?]{RESET} Enter your choice: ").strip().lower()
        
        if choice == 'q':
            print(f"\n{GREEN}Exiting Geocoder Tool. Goodbye!{RESET}")
            time.sleep(1)
            clear_screen()
            sys.exit(0)
        elif choice in SCRIPTS:
            execute_script(choice)
        else:
            print(f"{RED}Invalid choice. Please try again.{RESET}")
        
        input(f"\n{BLUE}Press Enter to continue...{RESET}")
        print_banner()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Program interrupted by user. Exiting...{RESET}")
        sys.exit(0)