"""
This script provides a utility to generate a new stylesheet for the PySide application, given
the QSS file that is provided in this module.

NOTE: Reinstalling module will require to re-run this script to update the generated stylesheet.
"""

# ruff: noqa: T201,S603

import argparse
import subprocess
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("qss_file", help="Path to user defined QSS file")
    args = parser.parse_args()

    script_dir = Path(__file__).parent.resolve()
    stylesheet_combinator_path = script_dir / "stylesheet_combinator.py"
    stylesheet_generator_path = script_dir / "stylesheet" / "generate_stylesheet.py"

    if not stylesheet_combinator_path.exists():
        raise FileNotFoundError("Could not find the script that combines package and QSS files")

    if not stylesheet_generator_path.exists():
        raise FileNotFoundError("Could not find the script that generates QSS binary file")

    cmd = [
        sys.executable,
        stylesheet_combinator_path,
        args.qss_file,
    ]

    try:
        print("Combining package stylesheet with provided user stylesheet...")
        subprocess.check_call(cmd)
        print("Stylesheets combined successfully!")
    except subprocess.CalledProcessError as ex:
        print(f"Error combining stylesheets: {ex}")

    cmd = [
        sys.executable,
        stylesheet_generator_path,
    ]

    try:
        print("Generating final stylesheet to be used")
        subprocess.check_call(cmd)
        print("Final stylesheet generated successfully!")
    except subprocess.CalledProcessError as ex:
        print(f"Error generating stylesheets: {ex}")
        sys.exit(1)


if __name__ == "__main__":
    main()





