import argparse
import os
import sys
from pathlib import Path
import docker

from .process_runner import run_and_watch
from .error_parser import parse_traceback
from .context_manager import get_code_context
from .ai_core import generate_fix
from .sandbox_verifier import SandboxVerifier
from .reporter import report_success, report_failure

def handle_configuration():

    print("--- AI Code Repair Agent Configuration ---")
    api_key = input("Please enter your Google Gemini API key: ").strip()

    if not api_key:
        print("\nNo API key provided. Configuration cancelled.")
        return

    home_dir = Path.home()
    dotenv_path = home_dir / ".env"

    try:
        with open(dotenv_path, "w") as f:
            f.write(f"GOOGLE_API_KEY={api_key}\n")
        
        print(f"\n✅ Success! Your API key has been saved to: {dotenv_path}")
        print("You are now ready to use the agent.")
    except Exception as e:
        print(f"\n❌ Error: Could not save the API key. Please check your permissions for the directory {home_dir}.")
        print(f"Details: {e}")

def run_workflow(script_path: str, script_args: list):

    try:
        docker_client = docker.from_env()
        docker_client.ping()
    except docker.errors.DockerException:
        print("\n" + "="*60)
        print("❌ DOCKER ERROR: Could not connect to Docker.")
        print("The AI Code Repair Agent requires Docker to be installed and running")
        print("in order to create a secure sandbox for testing code fixes.")
        print("\nPlease ensure Docker Desktop is running and try again.")
        print("Download Docker Desktop from: https://www.docker.com/products/docker-desktop/")
        print("="*60)
        return

    project_path = os.path.dirname(os.path.abspath(script_path))
    script_name = os.path.basename(script_path)

    if "ModuleNotFoundError" in (initial_error := run_and_watch(script_path, script_args)):
        parsed_error = parse_traceback(initial_error)
        if parsed_error and parsed_error['error_type'] == 'ModuleNotFoundError':
            module_name = parsed_error['error_message'].split("'")[1]
            report_failure(
                f"Environment Error: The required module '{module_name}' is not installed.",
                advice=f"Try installing it with: pip install {module_name}"
            )
            return
            
    traceback_text = run_and_watch(script_path, script_args)
    if not traceback_text:
        print("\n✅ Script executed without crashing. No errors to fix!")
        return

    parsed_error_details = parse_traceback(traceback_text)
    if not parsed_error_details:
        report_failure(f"Could not parse the error traceback.\n\nFull Traceback:\n{traceback_text}")
        return

    source_file_path = parsed_error_details['file_path']
    original_buggy_function = get_code_context(
        source_file_path,
        parsed_error_details['line_number']
    )
    if not original_buggy_function:
        report_failure(f"Could not retrieve the source code context from file '{source_file_path}' around line {parsed_error_details['line_number']}.\nThis can happen if the error is outside a function.")
        return

    proposed_fix = generate_fix(parsed_error_details, original_buggy_function)
    if not proposed_fix:
        report_failure("The AI core failed to generate a proposed fix.")
        return

    verifier = SandboxVerifier(original_app_path=project_path)
    is_verified = verifier.verify_fix(
        original_code=original_buggy_function,
        patched_code=proposed_fix,
        entrypoint_script=script_name,
        test_command=[] 
    )

    if is_verified:
        report_success(original_buggy_function, proposed_fix)
    else:
        report_failure("The AI-generated fix did not pass verification in the sandbox.")

def main():
    if len(sys.argv) > 1 and sys.argv[1].lower() == 'configure':
        handle_configuration()
        return

    parser = argparse.ArgumentParser(
        description="AI Automated Code Repair Agent.",
        usage="agent <script_path> [script_args...]\n       agent configure"
    )
    parser.add_argument("script_path", help="Path to the Python script to fix, or 'configure' for setup.")
    parser.add_argument("script_args", nargs='*', help="Optional arguments for the script.")
    
    args = parser.parse_args()

    if not os.path.exists(args.script_path):
        print(f"Error: The file '{args.script_path}' was not found.")
        return
    
    print("="*60)
    print("🤖 AI Automated Code Repair Agent is now running.")
    print(f"▶️  Analyzing script: {args.script_path}")
    print("="*60)

    run_workflow(args.script_path, args.script_args)
