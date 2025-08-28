import argparse
from pathlib import Path

def parse_arguments():
    """Sets up the argument parser and returns the parsed arguments."""
    parser = argparse.ArgumentParser(
        description="A CLI tool to extract project source code into structured Markdown files.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    # General Flags
    parser.add_argument(
        '--instructions',
        action='store_true',
        default=False,  # ADDED: This ensures the attribute always exists.
        help="Show the detailed instruction guide on startup."
    )
    parser.add_argument(
        '--root',
        type=Path,
        default=Path.cwd(),
        help="The root directory of the project to extract. Defaults to the current directory."
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default=None,
        help="Custom name for the output directory. Defaults to 'CODEBASE_EXTRACTS'."
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Simulate the extraction process without writing any files."
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help="Enable verbose logging for debugging."
    )
    parser.add_argument(
        '--log-file',
        type=str,
        default=None,
        help="Path to save the log file."
    )

    # Non-interactive mode flags
    parser.add_argument(
        '--exclude-large-files',
        action='store_true',
        help="Non-interactive: Exclude files larger than 1MB."
    )
    parser.add_argument(
        '--mode',
        choices=['everything', 'specific'],
        default=None,
        help="Non-interactive: Set the extraction mode."
    )
    parser.add_argument(
        '--depth',
        type=int,
        default=None,
        help="Non-interactive: Set the folder scan depth for 'specific' mode."
    )
    parser.add_argument(
        '--select-folders',
        nargs='+',
        default=[],
        help="Non-interactive: A space-separated list of folders/sub-folders to extract."
    )
    parser.add_argument(
        '--select-root',
        action='store_true',
        help="Non-interactive: Include files from the root directory in the extraction."
    )

    return parser.parse_args()