import subprocess
import sys
from pathlib import Path

SCRIPT_PATH = Path(__file__).parent / "arcas_parser.sh"

def main():
    if not SCRIPT_PATH.exists():
        print(f"Error: {SCRIPT_PATH} not found")
        sys.exit(1)
    subprocess.run([str(SCRIPT_PATH)] + sys.argv[1:])
