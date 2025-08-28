import os
import sys
import time
import datetime
import uuid
import shutil
import argparse
import logging
from pathlib import Path
from typing import List, Optional

import questionary
from halo import Halo
from termcolor import colored
from prompt_toolkit.styles import Style
from questionary import Validator, ValidationError

# Import from our modules
from . import config
from . import ui
from . import file_handler
from . import cli

class NumberValidator(Validator):
    """Validates that the input is a positive integer."""
    def validate(self, document):
        try:
            value = int(document.text)
            if value <= 0:
                raise ValidationError(
                    message="Please enter a positive number.",
                    cursor_position=len(document.text))
        except ValueError:
            raise ValidationError(
                message="Please enter a valid number.",
                cursor_position=len(document.text))

def setup_logging(verbose: bool, log_file: str = None):
    """Configures the logging system."""
    log_level = logging.DEBUG if verbose else logging.INFO
    log_format = logging.Formatter('%(message)s')
    
    logger = logging.getLogger()
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.setLevel(log_level)
    
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(log_format)
    logger.addHandler(stream_handler)

    if log_file:
        try:
            file_handler_log = logging.FileHandler(log_file)
            file_handler_log.setFormatter(log_format)
            logger.addHandler(file_handler_log)
        except Exception as e:
            logging.error(colored(f"Error: Could not write to log file at {log_file}. {e}", "red"))


def main():
    """Main function to run the CLI application."""
    exit_message = colored("\nExtraction aborted by user. Closing Code Extractor. Goodbye.", "red")

    try:
        args = cli.parse_arguments()
        setup_logging(args.verbose, args.log_file)

        output_dir_name = args.output_dir if args.output_dir else config.OUTPUT_DIR_NAME
        config.EXCLUDED_DIRS.add(output_dir_name)

        root_path = args.root.resolve() if args.root else Path.cwd()
        if not root_path.is_dir():
            logging.error(colored(f"Error: The provided root path is not a valid directory: {root_path}", "red"))
            return
        
        is_fully_automated = args.mode is not None

        # --- Startup Sequence ---
        if not is_fully_automated:
            ui.clear_screen()
            # CHANGED: Pass the new 'instructions' flag to the banner function
            ui.print_banner(show_instructions=args.instructions)
            # CHANGED: Logic is now inverted to show instructions only when the flag is present
            if args.instructions:
                ui.show_instructions(output_dir_name)
        else:
            # NOTE: For automated runs, the banner is always minimal. This is correct.
            ui.print_banner(show_instructions=False)
        
        # --- Collect Settings (Interactively or from Args) ---
        select_style = Style([('qmark', 'fg:#FFA500'), ('pointer', 'fg:#FFA500'), ('highlighted', 'fg:black bg:#FFA500'), ('selected', 'fg:black bg:#FFA500')])
        
        exclude_large = args.exclude_large_files
        if not is_fully_automated:
            logging.info("=== Extraction Settings ===")
            exclude_large_choice = questionary.select("[1/2] -- Exclude files larger than 1MB?", choices=["yes", "no"], style=select_style, instruction=" ").ask()
            if exclude_large_choice is None: raise KeyboardInterrupt
            exclude_large = exclude_large_choice == "yes"
            print()

        selection_mode = args.mode
        if not is_fully_automated:
            selection_mode = questionary.select("[2/2] -- What do you want to extract?", choices=["everything", "specific"], style=select_style, instruction=" ").ask()
            if selection_mode is None: raise KeyboardInterrupt

        folders_to_process = set()
        process_root_files = False
        
        run_ref = str(uuid.uuid4())
        run_timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

        if selection_mode == "everything":
            folders_to_process.update([p for p in root_path.iterdir() if p.is_dir() and p.name not in config.EXCLUDED_DIRS])
            process_root_files = True
        else: # 'specific' mode
            scan_depth = args.depth
            if scan_depth is None and not is_fully_automated:
                depth_str = questionary.text("-- How many levels deep should we scan for folders?", default="3", validate=NumberValidator, style=select_style).ask()
                if depth_str is None: raise KeyboardInterrupt
                scan_depth = int(depth_str)
            elif scan_depth is None:
                scan_depth = 3

            selected_paths = []
            if args.select_folders or args.select_root:
                if args.select_root: process_root_files = True
                selected_paths = [root_path / p for p in args.select_folders]
            elif not is_fully_automated:
                checkbox_style = Style([('qmark', 'fg:#FFA500'), ('pointer', 'fg:#FFA500'), ('highlighted', 'fg:#FFA500'), ('selected', 'fg:#FFA500'), ('checkbox-selected', 'fg:#FFA500')])
                folder_choices = file_handler.get_folder_choices(root_path, max_depth=scan_depth)
                selected_options = questionary.checkbox("-- Select folders/sub-folders to extract:", choices=folder_choices, style=checkbox_style, instruction="(Arrows to move, Space to select, A to toggle, I to invert)").ask()
                if selected_options is None: raise KeyboardInterrupt
                if "ROOT_SENTINEL" in selected_options:
                    process_root_files = True; selected_options.remove("ROOT_SENTINEL")
                selected_paths = [root_path / p for p in selected_options]
            
            sorted_paths = sorted(selected_paths, key=lambda p: len(p.parts))
            final_paths = set()
            for path in sorted_paths:
                if not any(path.is_relative_to(parent) for parent in final_paths): final_paths.add(path)
            folders_to_process.update(final_paths)

        if not is_fully_automated: print()
        total_files_extracted = 0

        # --- Processing ---
        for folder_path in sorted(list(folders_to_process)):
            with Halo(text=f"Extracting {folder_path.relative_to(root_path)}...", spinner="dots"):
                time.sleep(0.1)
                # CHANGED: Unpack the new char_count and word_count values
                folder_md, folder_count, char_count, word_count = file_handler.extract_code_from_folder(folder_path, exclude_large)
            
            if folder_count > 0:
                # CHANGED: Add new metrics to the metadata dictionary
                metadata = {
                    "run_ref": run_ref, 
                    "run_timestamp": run_timestamp, 
                    "folder_name": str(folder_path.relative_to(root_path)), 
                    "file_count": folder_count,
                    "char_count": char_count,
                    "word_count": word_count
                }
                if not args.dry_run:
                    file_handler.write_to_markdown_file(folder_md, metadata, root_path, output_dir_name)
                logging.info(f"✅ Extracted {folder_count} file(s) from: {folder_path.relative_to(root_path)}")
                logging.info(f"📜 {char_count:,} character(s), {word_count:,} word(s)")
                if args.dry_run: logging.info(colored(" (Dry Run: No file written)", "yellow"))
                total_files_extracted += folder_count
            else:
                logging.warning(f"‼️ No extractable files in: {folder_path.relative_to(root_path)}")
            logging.info("")

        if process_root_files:
            root_display_name = f"root [{root_path.name}] (files in root folder only, excl. sub-folders)"
            with Halo(text=f"Extracting {root_display_name}...", spinner="dots"):
                time.sleep(0.1)
                # CHANGED: Unpack the new char_count and word_count values
                root_md, root_count, char_count, word_count = file_handler.extract_code_from_root(root_path, exclude_large)
            
            if root_count > 0:
                # CHANGED: Add new metrics to the metadata dictionary
                metadata = {
                    "run_ref": run_ref, 
                    "run_timestamp": run_timestamp, 
                    "folder_name": root_display_name, 
                    "file_count": root_count,
                    "char_count": char_count,
                    "word_count": word_count
                }
                if not args.dry_run:
                    file_handler.write_to_markdown_file(root_md, metadata, root_path, output_dir_name)
                total_files_extracted += root_count
                logging.info(f"✅ Extracted {root_count} file(s) from the root directory")
                logging.info(f"📜 {char_count:,} character(s), {word_count:,} word(s)")
                if args.dry_run: logging.info(colored(" (Dry Run: No file written)", "yellow"))
            else:
                logging.warning("‼️ No extractable files in the root directory")
            logging.info("")
        
        # --- Final Summary ---
        if total_files_extracted > 0:
            output_dir_path = Path(output_dir_name).resolve()
            logging.info(colored(f"Success! A total of {total_files_extracted} file(s) have been extracted.", "grey", "on_green"))
            if not args.dry_run:
                logging.info(f"Files saved in: {colored(str(output_dir_path), 'green')}")
        else:
            logging.warning("Extraction complete, but no files matched the criteria.")
        
        ui.print_footer()

    except (KeyboardInterrupt, TypeError):
        print(exit_message)
        sys.exit(0)
    except Exception as e:
        logging.error(colored(f"\n[!] An unexpected error occurred: {e}", "red"))
        import traceback
        traceback.print_exc()
        sys.exit(1)