"""
Executor: performs file operations inside a sandboxed environment.
Now supports 'read' actions for monitoring and status checks.
All actions are executed inside a sandbox to prevent unintended system impact.
"""

import os
import shutil


class Executor:
    SANDBOX_ROOT = "workspace"

    def __init__(self, base_dir=None):
        self.base_dir = base_dir if base_dir else os.getcwd()
        self.sandbox_root = self.base_dir

    def _resolve_path(self, relative_path: str) -> str:
        """Convert relative path to absolute; enforce sandbox boundary."""
        abs_path = os.path.abspath(os.path.join(self.base_dir, relative_path))
        if not abs_path.startswith(self.sandbox_root):
            raise ValueError(f"Path '{relative_path}' attempts to escape project directory")
        sandbox_abs = os.path.join(self.base_dir, self.SANDBOX_ROOT)
        if not abs_path.startswith(sandbox_abs):
            raise ValueError(f"Path '{relative_path}' is outside sandbox '{self.SANDBOX_ROOT}'")
        return abs_path

    def execute(self, action: dict) -> tuple[bool, str]:
        """Execute the action. Returns (success, message)."""
        action_type = action.get("action")
        try:
            if action_type == "delete":
                return self._handle_delete(action)
            elif action_type == "create":
                return self._handle_create(action)
            elif action_type == "move":
                return self._handle_move(action)
            elif action_type == "read":
                return self._handle_read(action)
            else:
                return False, f"Unknown action type: {action_type}"
        except ValueError as e:
            return False, f"Sandbox violation: {str(e)}"
        except Exception as e:
            return False, f"Execution error: {str(e)}"

    def _handle_delete(self, action: dict) -> tuple[bool, str]:
        path = action.get("path")
        if not path:
            return False, "No path provided for delete"
        abs_path = self._resolve_path(path)
        if not os.path.exists(abs_path):
            return False, f"File not found: {path} (safe handling)"
        if os.path.isfile(abs_path):
            os.remove(abs_path)
            return True, f"Deleted file: {path}"
        elif os.path.isdir(abs_path):
            count = 0
            for filename in os.listdir(abs_path):
                file_path = os.path.join(abs_path, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    count += 1
            return True, f"Deleted {count} file(s) in: {path}"
        return False, f"Path is neither a file nor directory: {path}"

    def _handle_create(self, action: dict) -> tuple[bool, str]:
        path = action.get("path")
        if not path:
            return False, "No path provided for create"
        abs_path = self._resolve_path(path)
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, 'w') as f:
            f.write("# ArmorIQ Test File\nCreated by ArmorIQ OrganizerAgent\n")
        return True, f"Created file: {path}"

    def _handle_move(self, action: dict) -> tuple[bool, str]:
        source = action.get("source")
        dest = action.get("dest")
        if not source or not dest:
            return False, "Missing source or dest for move"
        abs_source = self._resolve_path(source)
        abs_dest = self._resolve_path(dest)
        if not os.path.exists(abs_source):
            return False, f"Source not found: {source} (safe handling)"
        os.makedirs(os.path.dirname(abs_dest), exist_ok=True)
        shutil.move(abs_source, abs_dest)
        return True, f"Moved: {source} → {dest}"

    def _handle_read(self, action: dict) -> tuple[bool, str]:
        """Read-only monitoring operations. Never modifies any file."""
        path = action.get("path", "workspace")
        read_mode = action.get("read_mode", "status")
        abs_path = self._resolve_path(path)

        if not os.path.exists(abs_path):
            return False, f"Path not found: {path}"

        if read_mode == "status":
            total_files = 0
            total_size = 0
            temp_files = 0
            for dirpath, _, filenames in os.walk(abs_path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    total_files += 1
                    total_size += os.path.getsize(fp)
                    if "temp" in dirpath:
                        temp_files += 1
            size_kb = round(total_size / 1024, 2)
            msg = (
                f"Workspace Status:\n"
                f"  Total Files  : {total_files}\n"
                f"  Temp Files   : {temp_files}\n"
                f"  Total Size   : {size_kb} KB"
            )
            return True, msg

        elif read_mode == "preview":
            if not os.path.isdir(abs_path):
                return False, f"Preview target is not a directory: {path}"
            files = [f for f in os.listdir(abs_path) if os.path.isfile(os.path.join(abs_path, f))]
            if not files:
                return True, f"Preview: No files found in {path}"
            file_list = "\n".join(f"  - {f}" for f in files)
            return True, f"Preview — Files that would be deleted from '{path}':\n{file_list}\n[No changes applied — preview only]"

        return False, f"Unknown read_mode: {read_mode}"
