import subprocess
import sys
from pathlib import Path

SCRIPT_PATH = Path(__file__).parent / "arcas_analyzer.sh"

def main():
    if not SCRIPT_PATH.exists():
        print(f"Error: Bash script {SCRIPT_PATH} not found")
        sys.exit(1)
    # Forward all CLI arguments to the Bash script
    subprocess.run([str(SCRIPT_PATH)] + sys.argv[1:])
