"""
This script provides a utility to combine QSS stylesheet that is provided in this module with the
QSS stylesheet that is user provided.

NOTE: Reinstalling module will require to re-run this script to update the combined stylesheet.
"""

import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help="Path to input QSS file to combine with module's QSS")
    args = parser.parse_args()

    script_dir = Path(__file__).parent.resolve()
    stylesheet_path_file = script_dir / "stylesheet" / "base_stylesheet.qss.in"
    input_file = Path(args.input_file).resolve()
    output_file = Path(script_dir, "stylesheet", "extension", "JZ_QSS", "stylesheet.qss.in")

    # combine stylesheet from stylesheet_path_file and input_file and write to output_file
    if not stylesheet_path_file.exists():
        raise FileNotFoundError(f"Base stylesheet file {stylesheet_path_file} does not exist.")

    if not input_file.exists():
        raise FileNotFoundError(f"Input file {input_file} does not exist.")

    if not output_file.parent.exists():
        output_file.parent.mkdir(parents=True)

    with stylesheet_path_file.open("r") as base_stylesheet_file:
        base_stylesheet_content = base_stylesheet_file.read()

    with input_file.open("r") as input_qss_file:
        input_stylesheet_content = input_qss_file.read()

    combined_stylesheet_content = (
        base_stylesheet_content + "\n\n/* ************************************************ */\n"
        "/* User provided stylesheet */\n"
        "/* ************************************************ */\n\n" + input_stylesheet_content
    )

    with output_file.open("w") as output_qss_file:
        output_qss_file.write(combined_stylesheet_content)


if __name__ == "__main__":
    main()
