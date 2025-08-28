import os
import shutil
from . import config
from . import __version__  
from termcolor import colored

# ... (LOGO_LARGE and LOGO_SMALL strings remain the same) ...

LOGO_LARGE = """
 ██████╗ ██████╗ ██████╗ ███████╗██████╗  █████╗ ███████╗███████╗    ███████╗██╗  ██╗████████╗██████╗  █████╗  ██████╗████████╗ ██████╗ ██████╗ 
██╔════╝██╔═══██╗██╔══██╗██╔════╝██╔══██╗██╔══██╗██╔════╝██╔════╝    ██╔════╝╚██╗██╔╝╚══██╔══╝██╔══██╗██╔══██╗██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗
██║     ██║   ██║██║  ██║█████╗  ██████╔╝███████║███████╗█████╗      █████╗   ╚███╔╝    ██║   ██████╔╝███████║██║        ██║   ██║   ██║██████╔╝
██║     ██║   ██║██║  ██║██╔══╝  ██╔══██╗██╔══██║╚════██║██╔══╝      ██╔══╝   ██╔██╗    ██║   ██╔══██╗██╔══██║██║        ██║   ██║   ██║██╔══██╗
╚██████╗╚██████╔╝██████╔╝███████╗██████╔╝██║  ██║███████║███████╗    ███████╗██╔╝ ██╗   ██║   ██║  ██║██║  ██║╚██████╗   ██║   ╚██████╔╝██║  ██║
 ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝╚═════╝ ╚═╝  ╚═╝╚══════╝╚══════╝    ╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝
"""

LOGO_SMALL = """
  ░█▀▀░█▀█░█▀▄░█▀▀░█▀▄░█▀█░█▀▀░█▀▀░░░█▀▀░█░█░▀█▀░█▀▄░█▀█░█▀▀░▀█▀░█▀█░█▀▄
  ░█░░░█░█░█░█░█▀▀░█▀▄░█▀█░▀▀█░█▀▀░░░█▀▀░▄▀▄░░█░░█▀▄░█▀█░█░░░░█░░█░█░█▀▄
  ░▀▀▀░▀▀▀░▀▀░░▀▀▀░▀▀░░▀░▀░▀▀▀░▀▀▀░░░▀▀▀░▀░▀░░▀░░▀░▀░▀░▀░▀▀▀░░▀░░▀▀▀░▀░▀
"""

def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner(show_instructions: bool = False): # CHANGED: Parameter name for clarity
    """Prints a banner that adjusts to the terminal width."""
    try:
        width = shutil.get_terminal_size((80, 20)).columns
    except OSError:
        width = 80

    if width > config.LOGO_BREAKPOINT:
        print(LOGO_LARGE)
    else:
        print(LOGO_SMALL)

    # Use the imported __version__ variable instead of config.SCRIPT_VERSION
    print(colored(f" Welcome to Code Extractor v{__version__} by Lukasz Lekowski ".center(width, "="), "white", "on_magenta"))
    print("\nThis tool consolidates your project's code into structured Markdown files.")
    print("It's ideal for providing context to AI models, archiving projects, or generating documentation.\n")


def show_instructions(output_dir_name: str):
    """Clears screen and shows detailed instructions, pausing for user input."""
    try:
        width = shutil.get_terminal_size((80, 20)).columns
    except OSError:
        width = 80
        
    input(colored("\nPress Enter to view detailed instructions...", "dark_grey"))
    clear_screen()
    print(colored("--- How It Works ---", "yellow"))
    print("The script will guide you through a series of steps:\n")

    print(colored("Step 1: General Settings", "cyan"))
    print("You will first be asked about basic settings, such as whether to exclude files larger than 1MB to keep the output clean.\n")

    print(colored("Step 2: Extraction Mode", "cyan"))
    print("You have two main modes to choose from:")
    print("  - 'Everything': This automatically finds and processes every valid folder and all root files. You will get one Markdown file for each top-level folder, plus one for the root files.")
    print("  - 'Specific folders/root': This lets you hand-pick exactly what you want to extract.\n")

    print(colored("Step 3: Detailed Selection (If you chose 'Specific')", "cyan"))
    print("If you choose to be specific, you'll be presented with more options:")
    print("  - Scan Depth: First, you'll decide how many sub-folder levels to scan and display.")
    print("  - Selection Tree: You'll see a tree-like list of your project's folders. The script handles parent/child selections intelligently:")
    print("    - If you select a parent folder, all of its sub-folders are automatically included. You don't need to check them individually.")
    print("    - To get a file for *only* a sub-folder, select the sub-folder but *not* its parent.")
    print("  - The 'root [...]' option specifically extracts *only* the files in your project's main directory.\n")
    
    print(colored("--- Output Details ---", "yellow"))
    print(f"All extracted content is saved into the '{output_dir_name}' directory. Each Markdown file generated will contain a YAML metadata header at the top with a unique reference ID, a timestamp, and more.\n")
    
    # CHANGED: Updated the tip to reflect the new '--instructions' flag
    tip = "TIP: To see this guide again, run the script with the --instructions flag."
    print(colored(tip, "black", "on_yellow"))

    input(colored("\nReady? Press Enter to begin...", "green"))
    clear_screen()

def print_footer():
    """Prints the final footer with links and credits."""
    try:
        width = shutil.get_terminal_size((80, 20)).columns
    except OSError:
        width = 80
        
    print("\n")
    print("-" * width)
    print("📦 Find this project on PyPI:")
    print(config.PYPI_URL + "\n")
    print("💡 Love this tool? Found a bug? Share your feedback on GitHub:")
    print(config.GITHUB_URL + "\n")
    print("🤝 Connect with the author on LinkedIn:")
    print(config.LINKEDIN_URL + "\n")