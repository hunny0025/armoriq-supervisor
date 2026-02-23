"""
Main entry point. Sets up the sandbox environment and runs the REPL.
"""

import os
import sys
from supervisor import Supervisor

def setup_sandbox():
    """Create required directories and dummy files inside the sandbox."""
    os.makedirs("workspace/temp", exist_ok=True)
    os.makedirs("workspace/logs", exist_ok=True)
    os.makedirs("system", exist_ok=True)  # simulated protected area

    # Dummy files
    if not os.path.exists("workspace/temp/file.tmp"):
        with open("workspace/temp/file.tmp", 'w') as f:
            f.write("Temporary file content.\n")

    if not os.path.exists("workspace/log.txt"):
        with open("workspace/log.txt", 'w') as f:
            f.write("This is a log file.\n")

    # Create a dummy system file to demonstrate blocking (but not used by executor)
    if not os.path.exists("system/config"):
        with open("system/config", 'w') as f:
            f.write("[mock system config]\n")

def main():
    setup_sandbox()
    supervisor = Supervisor()
    print("ArmorIQ Supervisor – Production-Level Autonomous Control")
    print("Type your command (or 'exit' to quit). Commands: clean workspace, organize files, clean and organize workspace, delete system config, show history")
    while True:
        try:
            user_input = input("> ").strip()
            if user_input.lower() in ('exit', 'quit'):
                break
            if not user_input:
                continue
            supervisor.process(user_input)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
