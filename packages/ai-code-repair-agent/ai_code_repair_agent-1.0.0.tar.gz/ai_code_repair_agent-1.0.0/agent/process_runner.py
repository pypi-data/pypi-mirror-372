import subprocess
import logging
from typing import List, Callable

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [ProcessRunner] - %(message)s')

ERROR_SIGNATURE = "Traceback (most recent call last):"

def run_and_watch(script_path: str, script_args: List[str]) -> str:
    command = ["python", script_path] + script_args
    logging.info(f"Executing command: {' '.join(command)}")

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False
        )

        if result.stdout:
            print("\n--- Script Output (stdout) ---")
            print(result.stdout)
        if result.stderr:
            print("\n--- Script Error Output (stderr) ---")
            print(result.stderr)

        if ERROR_SIGNATURE in result.stderr:
            logging.warning("Error signature detected in stderr!")
            return result.stderr
        
        logging.info(f"Script finished with exit code: {result.returncode}")
        return ""

    except FileNotFoundError:
        logging.error(f"Error: The script '{script_path}' was not found.")
        return f"Error: The script '{script_path}' was not found."
    except Exception as e:
        logging.error(f"An unexpected error occurred while running the script: {e}")
        return str(e)