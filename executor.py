"""
Executor: performs file operations inside a sandboxed environment.
All actions are executed inside a sandbox environment to prevent unintended system impact.
"""

import os
import shutil

class Executor:
    SANDBOX_ROOT = "workspace"  # relative to project root

    def __init__(self, base_dir=None):
        if base_dir is None:
            self.base_dir = os.getcwd()
        else:
            self.base_dir = base_dir
        self.sandbox_root = self.base_dir

    def _resolve_path(self, relative_path: str) -> str:
        """
        Convert a relative path to absolute and ensure it stays inside sandbox.
        Also enforces that the path is under the SANDBOX_ROOT directory.
        """
        abs_path = os.path.abspath(os.path.join(self.base_dir, relative_path))
        # Check that the path is within the project root
        if not abs_path.startswith(self.sandbox_root):
            raise ValueError(f"Path '{relative_path}' attempts to escape project directory")
        # Enforce sandbox: must be under workspace/
        sandbox_abs = os.path.join(self.base_dir, self.SANDBOX_ROOT)
        if not abs_path.startswith(sandbox_abs):
            raise ValueError(f"Path '{relative_path}' is outside sandbox '{self.SANDBOX_ROOT}'")
        return abs_path

    def execute(self, action: dict) -> tuple[bool, str]:
        """Execute the action. Returns (success, message)."""
        action_type = action.get("action")

        try:
            if action_type == "delete":
                path = action.get("path")
                if not path:
                    return False, "No path provided"
                abs_path = self._resolve_path(path)

                if not os.path.exists(abs_path):
                    return False, f"File not found: {path} (safe handling)"

                if os.path.isfile(abs_path):
                    os.remove(abs_path)
                    return True, f"Deleted file {path}"
                elif os.path.isdir(abs_path):
                    # Delete files inside directory (non‑recursive)
                    count = 0
                    for filename in os.listdir(abs_path):
                        file_path = os.path.join(abs_path, filename)
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                            count += 1
                    return True, f"Deleted {count} files in {path}"
                else:
                    return False, f"Path is not a file or directory: {path}"

            elif action_type == "create":
                path = action.get("path")
                if not path:
                    return False, "No path provided"
                abs_path = self._resolve_path(path)
                os.makedirs(os.path.dirname(abs_path), exist_ok=True)
                with open(abs_path, 'w') as f:
                    f.write("Created by ArmorIQ\n")
                return True, f"Created file {path}"

            elif action_type == "move":
                source = action.get("source")
                dest = action.get("dest")
                if not source or not dest:
                    return False, "Missing source or dest"
                abs_source = self._resolve_path(source)
                abs_dest = self._resolve_path(dest)

                if not os.path.exists(abs_source):
                    return False, f"File not found: {source} (safe handling)"

                os.makedirs(os.path.dirname(abs_dest), exist_ok=True)
                shutil.move(abs_source, abs_dest)
                return True, f"Moved {source} to {dest}"

            else:
                return False, f"Unknown action: {action_type}"
        except ValueError as e:
            # Sandbox violation
            return False, f"Sandbox violation: {str(e)}"
        except Exception as e:
            return False, f"Execution error: {str(e)}"
