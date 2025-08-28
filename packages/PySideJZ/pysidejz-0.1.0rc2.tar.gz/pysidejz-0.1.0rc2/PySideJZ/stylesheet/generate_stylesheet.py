import os
import subprocess
import sys
from pathlib import Path

# ruff: noqa: T201,S603,EXE002

def main():
    script_dir = Path(__file__).parent.resolve()
    os.chdir(script_dir)

    cmd = [
        sys.executable, "configure.py",
        "--styles=all", "--extensions=all",
        "--resource", "breeze.qrc",
        "--pyrcc5", "pyside6-rcc",
        "--compiled-resource", "stylesheet.py",
    ]
    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError as ex:
        print(f"Error generating stylesheet: {ex}")
        sys.exit(1)

if __name__ == "__main__":
    main()
