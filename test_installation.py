"""
Installation test for Groupie

This script tests that the command-line entry point 'gr' is installed correctly.
"""
import os
import subprocess
import sys

def test_command_line():
    """Test that the 'gr' command-line tool is available"""
    try:
        # Use the gr command from the virtual environment
        venv_path = os.path.join(os.getcwd(), ".venv", "Scripts")
        gr_path = os.path.join(venv_path, "gr.exe" if sys.platform == "win32" else "gr")
        
        # Run 'gr --version' and check that it returns successfully
        result = subprocess.run([gr_path, '--version'], 
                               capture_output=True, 
                               text=True,
                               check=True)
        print(f"Command 'gr --version' executed successfully:")
        print(f"  {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: Command 'gr --version' failed with code {e.returncode}")
        print(f"  {e.stderr.strip()}")
        return False
    except FileNotFoundError:
        print("Error: Command 'gr' not found. Is it installed?")
        print("Try running: pip install -e .")
        return False

if __name__ == "__main__":
    success = test_command_line()
    sys.exit(0 if success else 1)
